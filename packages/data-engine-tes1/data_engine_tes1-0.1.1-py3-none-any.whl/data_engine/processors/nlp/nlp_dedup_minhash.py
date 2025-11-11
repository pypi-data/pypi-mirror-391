# -*- coding: utf-8 -*-
import math
import re
import warnings
from itertools import tee
from typing import List, Tuple, Set, Optional, Iterable

import numpy as np
import numpy.typing as npt
import xxhash

from pyspark.sql import functions as F
from pyspark.sql.types import LongType
from pyspark import StorageLevel

# optional imports
try:
    from graphframes import GraphFrame

    _HAS_GRAPHFRAMES = True
except Exception:
    GraphFrame = None
    _HAS_GRAPHFRAMES = False

try:
    # PySpark ML MinHashLSH alternative
    from pyspark.ml.feature import HashingTF, MinHashLSH, Tokenizer

    _HAS_MLHASH = True
except Exception:
    _HAS_MLHASH = False
from data_engine.core.base import BaseFilter

# constants
NON_ALPHA = re.compile(r"\W+", re.UNICODE)
DTYPE = np.uint32
MAX_HASH = 0xFFFFFFFF
MOD_PRIME = 4_294_967_291
SEED = 42
RNG = np.random.RandomState(SEED)


def _generate_edges(nodes: Iterable[int]) -> List[Tuple[int, int]]:
    nodes = list(nodes)
    if len(nodes) <= 1:
        return []
    m = min(nodes)
    return [(int(n), int(m)) for n in nodes if n != m]


def _ngrams(tokens: List[str], n: int, min_length: int = 5):
    if len(tokens) < min_length:
        return []
    if len(tokens) < n:
        return [tuple(tokens)]
    iterables = tee(iter(tokens), n)
    for i, it in enumerate(iterables):
        for _ in range(i):
            next(it, None)
    return zip(*iterables)


def _ngram_hashes(content: str, ngram_size: int, min_length: int = 5) -> Set[int]:
    if content is None:
        return set()
    tokens = [t for t in NON_ALPHA.split(content.lower()) if t]
    if len(tokens) < min_length:
        return set()
    grams = _ngrams(tokens, ngram_size, min_length)
    ng_bytes = {(" ".join(t)).encode("utf-8") for t in grams}
    return {xxhash.xxh32_intdigest(b) for b in ng_bytes}


def _generate_hash_values(
    content: str,
    idx: int,
    num_perm: int,
    ngram_size: int,
    min_length: int,
    hashranges: List[Tuple[int, int]],
    permutations: Tuple[npt.NDArray[np.uint64], npt.NDArray[np.uint64]],
) -> List[Tuple[int, bytes, int]]:
    a, b = permutations
    hashes = _ngram_hashes(content, ngram_size, min_length)
    if not hashes:
        return []
    # stable order
    hashes_arr = np.fromiter(sorted(hashes), dtype=np.uint64)
    # compute (num_hashes, num_perm) outer product mod prime (uint64 safe)
    p_hashes = (
        np.multiply.outer(hashes_arr, a.astype(np.uint64)) + b.astype(np.uint64)
    ) % np.uint64(MOD_PRIME)
    min_hashes = np.min(p_hashes, axis=0).astype(np.uint64)  # (num_perm,)
    min_hashes_u32 = (min_hashes & np.uint64(MAX_HASH)).astype(np.uint32)
    out = []
    for band_idx, (start, end) in enumerate(hashranges):
        band_slice = min_hashes_u32[start:end]
        # stable bytes (little-endian 4-byte uint)
        band_bytes = band_slice.astype("<u4").tobytes()
        out.append((band_idx, band_bytes, int(idx)))
    return out


def _heuristic_optimal_param(threshold: float, num_perm: int) -> Tuple[int, int]:
    best = (1, max(1, num_perm))
    min_score = float("inf")
    # search r in reasonable range
    max_r = min(64, num_perm)
    for r in range(1, max_r + 1):
        b = max(1, num_perm // r)
        s = threshold
        prob = 1.0 - (1.0 - s ** float(r)) ** float(b)
        # try to make P(threshold) close to 0.5 (steepness)
        score = abs(prob - 0.5)
        if score < min_score:
            min_score = score
            best = (b, r)
    return best


def _partitioned_save(df, chunk_size: int, max_partitions: int, output: str):
    total = df.count()
    parts = max(256, min(math.ceil(total / chunk_size), max_partitions))
    (
        df.repartition(parts)
        .withColumn("__pid__", F.spark_partition_id())
        .write.partitionBy("__pid__")
        .parquet(output, mode="overwrite", compression="snappy")
    )


class NlpFilterNearDedup(BaseFilter):
    """
    相似度去重工具
    使用minhash算法对文本进行相似度去重
    """

    def __init__(
        self,
        column_name: str = "text",
        index_column: Optional[str] = None,
        threshold: float = 0.7,
        ngram_size: int = 5,
        min_length: int = 5,
        num_perm: int = 256,
        bands: Optional[int] = None,
        rows_per_band: Optional[int] = None,
        checkpoint_dir: str = None,
        output_dir: Optional[str] = None,
        debug_assignment: bool = False,
        max_write_chunk_size: int = 200_000,
        max_write_partitions: int = 2048,
        repartition_num: Optional[int] = None,
        **kwargs,
    ):
        """
        初始化方法。
        column_name: 输入文本所在的列名#输入文本所在的列名
        index_column: 用于标识文本的索引列名#用于标识文本的索引列名
        threshold: 相似度阈值#相似度阈值，大于等于该阈值的文本会被认为重复
        ngram_size: 窗口大小#生成 n-gram 的窗口大小
        min_length: 文本的最小长度#文本的最小长度，低于该长度的文本将被过滤
        num_perm: 哈希置换次数#MinHash 的哈希置换次数
        bands: 分桶数量#LSH 分桶的 band 数量，若为 None 则自动计算
        rows_per_band: band行数#每个 band 的行数，若为 None 则自动计算
        checkpoint_dir: 中间结果的检查点存储路径#中间结果的检查点存储路径
        output_dir: 输出结果保存路径#输出结果保存路径
        debug_assignment: 是否输出调试信息#是否输出调试信息
        max_write_chunk_size: 单次写出最大数据条数#单次写出最大数据条数
        max_write_partitions: 输出文件的最大分区数#输出文件的最大分区数
        repartition_num: 重新分区数量#重新分区数量，None（不强制 repartition）
        """
        super().__init__(**kwargs)
        self.column_name = column_name
        self.index_column = index_column
        self.threshold = threshold
        self.ngram_size = ngram_size
        self.min_length = min_length
        self.num_perm = num_perm
        self.bands = bands
        self.rows_per_band = rows_per_band
        self.checkpoint_dir = self.get_default_dir(checkpoint_dir)
        self.output_dir = output_dir
        self.debug_assignment = debug_assignment
        self.max_write_chunk_size = max_write_chunk_size
        self.max_write_partitions = max_write_partitions
        self.repartition_num = repartition_num
        self.prefer_mlh = False

    def run(self, df, spark=None):
        if spark is None:
            from data_engine.core.factory import ExecutorFactory

            executor = ExecutorFactory.create_executor("spark")
            spark = executor.spark
        spark.sparkContext.setCheckpointDir(self.checkpoint_dir)

        col = self.column_name
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame")

        # optionally use ML MinHashLSH (降级/替代)
        if self.prefer_mlh and _HAS_MLHASH:
            try:
                return self._process_with_mlhash(df, spark)
            except Exception:
                # 如果 ML 路径失败，回退到经典实现并记录（用户可添加日志）
                pass

        # 计算 b,r
        B, R = self.bands, self.rows_per_band
        if B is None or R is None:
            try:
                B, R = _heuristic_optimal_param(self.threshold, self.num_perm)
            except Exception:
                B, R = (self.num_perm, 1)

        HASH_RANGES = [(i * R, (i + 1) * R) for i in range(B)]
        perm_a = RNG.randint(1, MOD_PRIME, size=(self.num_perm,), dtype=np.uint64)
        perm_b = RNG.randint(0, MOD_PRIME, size=(self.num_perm,), dtype=np.uint64)

        sc = spark.sparkContext
        bc_hashranges = sc.broadcast(HASH_RANGES)
        bc_permutations = sc.broadcast((perm_a, perm_b))

        # 用 Spark SQL 过滤短文本（避免 Python UDF）
        tokens_size_col = F.size(
            F.split(F.regexp_replace(F.lower(F.col(col)), r"\W+", " "), r"\s+")
        )
        working = df.filter(tokens_size_col >= F.lit(self.min_length))
        use_internal_id = self.index_column is None
        index_col = self.index_column or "__id__"
        if use_internal_id:
            working = working.withColumn(
                index_col, F.monotonically_increasing_id().cast(LongType())
            )

        working = working.persist(StorageLevel.DISK_ONLY)
        total_before = working.count()

        # mapPartitions 版本，executor 端计算 hash 值
        def _part_map_rows(part_iter):
            # restore broadcasted
            hr = bc_hashranges.value
            a, b = bc_permutations.value
            for row in part_iter:
                try:
                    idx = row[index_col]
                    text = row[col]
                except Exception:
                    # defensive: row might be Row object
                    idx = getattr(row, index_col)
                    text = getattr(row, col)
                vals = _generate_hash_values(
                    content=text,
                    idx=idx,
                    num_perm=self.num_perm,
                    ngram_size=self.ngram_size,
                    min_length=self.min_length,
                    hashranges=hr,
                    permutations=(a, b),
                )
                for v in vals:
                    yield ((v[0], v[1]), v[2])

        triplet_pair_rdd = working.select(index_col, col).rdd.mapPartitions(
            _part_map_rows
        )

        # 使用 combineByKey 避免 groupByKey 的潜在 OOM（对每个 key 聚合索引列表）
        def create_combiner(x):
            return [x]

        def merge_value(acc, x):
            acc.append(x)
            return acc

        def merge_combiners(a, b):
            a.extend(b)
            return a

        grouped = triplet_pair_rdd.combineByKey(
            create_combiner, merge_value, merge_combiners
        )

        # 由每个 (band,hash) 的索引列表生成边（代表-最小id）
        edges_rdd = (
            grouped.flatMap(lambda kv: _generate_edges(kv[1]))
            .distinct()
            .persist(StorageLevel.DISK_ONLY)
        )

        if edges_rdd.isEmpty():
            if self.output_dir:
                _partitioned_save(
                    working,
                    self.max_write_chunk_size,
                    self.max_write_partitions,
                    self.output_dir,
                )
            result = working
            if use_internal_id:
                result = result.drop(index_col)
            working.unpersist(blocking=True)
            edges_rdd.unpersist(blocking=True)
            return result

        # DataFrame 构造 edges/vertices
        repart = self.repartition_num or min(4096, max(8, edges_rdd.getNumPartitions()))
        edges_df = (
            spark.createDataFrame(edges_rdd, schema=["src", "dst"])
            .select(F.col("src").cast(LongType()), F.col("dst").cast(LongType()))
            .repartition(repart)
            .persist(StorageLevel.DISK_ONLY)
        )

        vertices_df = (
            edges_df.select(F.col("src").alias("id"))
            .union(edges_df.select(F.col("dst").alias("id")))
            .distinct()
            .repartition(repart)
            .persist(StorageLevel.DISK_ONLY)
        )

        if not _HAS_GRAPHFRAMES:
            raise RuntimeError(
                "GraphFrames is not installed/available. Install graphframes or set up alternative CC solution."
            )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gf = GraphFrame(vertices_df, edges_df)
            assignment = gf.connectedComponents().persist(StorageLevel.DISK_ONLY)

        if self.debug_assignment and self.output_dir:
            assignment.write.parquet(
                f"{self.output_dir}-assignment/assignment.parquet", mode="overwrite"
            )

        merged = working.join(
            assignment.select(
                F.col("id").alias(index_col), F.col("component").alias("__component__")
            ),
            on=index_col,
            how="left",
        ).persist(StorageLevel.DISK_ONLY)

        deduped = (
            merged.filter(
                F.col("__component__").isNull()
                | (F.col("__component__") == F.col(index_col))
            )
            .drop("__component__")
            .persist(StorageLevel.DISK_ONLY)
        )

        if self.output_dir:
            _partitioned_save(
                deduped,
                self.max_write_chunk_size,
                self.max_write_partitions,
                self.output_dir,
            )

        # 清理
        merged.unpersist(blocking=True)
        working.unpersist(blocking=True)
        edges_rdd.unpersist(blocking=True)
        assignment.unpersist(blocking=True)
        vertices_df.unpersist(blocking=True)
        edges_df.unpersist(blocking=True)

        if use_internal_id:
            deduped = deduped.drop(index_col)
        return deduped

    def _process_with_mlhash(self, df, spark):
        """
        可选：将文本 token 化、用 HashingTF 生成稀疏向量，再用 MinHashLSH 做近似近邻/相似度连接。
        适用于：当你更倾向使用 Spark ML 的分布式实现时（通常性能更好、可伸缩）。
        注意：需要为每条文档构建 token 列（list<string>），以及设置适当 numFeatures。
        返回与主流程兼容的去重 DataFrame（基于 connected components 或基于 pairwise keep-first 策略）。
        """
        if not _HAS_MLHASH:
            raise RuntimeError("MinHash LSH (pyspark.ml) not available.")
        # 简化流程：tokenize (非字母分隔)
        from pyspark.sql.functions import udf
        from pyspark.sql.types import ArrayType, StringType

        tokenize_udf = udf(
            lambda s: [t for t in NON_ALPHA.split(s.lower()) if t],
            ArrayType(StringType()),
        )
        working = df.withColumn(
            "__tokens__", tokenize_udf(F.col(self.column_name))
        ).filter(F.size(F.col("__tokens__")) >= self.min_length)
        # hashingTF
        num_features = 1 << 18  # 262k features, 可以根据数据量调整
        hashingTF = HashingTF(
            inputCol="__tokens__", outputCol="features", numFeatures=num_features
        )
        featurized = hashingTF.transform(working)
        mh = MinHashLSH(
            inputCol="features",
            outputCol="hashes",
            numHashTables=min(4, max(1, self.num_perm // 64)),
        )
        model = mh.fit(featurized)
        # approxSimilarityJoin: 将自己与自己 join（会产生 pair），使用 threshold 评估（Jaccard距离）
        joined = model.approxSimilarityJoin(
            featurized, featurized, 1.0 - self.threshold, distCol="dist"
        ).select(F.col("datasetA.*"), F.col("datasetB.*"), F.col("dist"))
        # 筛选 self-pairs; 保留只保留 idA < idB 的 pair 作为边
        id_col = self.index_column or "__id__"
        if self.index_column is None:
            featurized = featurized.withColumn(
                id_col, F.monotonically_increasing_id().cast(LongType())
            )
            joined = joined.withColumnRenamed("__id__", id_col)
        edges = (
            joined.filter(F.col(f"datasetA.{id_col}") < F.col(f"datasetB.{id_col}"))
            .select(
                F.col(f"datasetA.{id_col}").alias("src"),
                F.col(f"datasetB.{id_col}").alias("dst"),
            )
            .distinct()
        )
        # 接下来可以与 GraphFrames 一样求 connectedComponents 并选代表
        if not _HAS_GRAPHFRAMES:
            # 如果没有 GraphFrames，简单返回按 id 保留最小 id 行（不完美）
            # keep records with minimal id per component approximation: unsupported here
            raise RuntimeError("GraphFrames needed for CC after MLMinHash path.")
        edges_df = edges.select(
            F.col("src").cast(LongType()), F.col("dst").cast(LongType())
        ).persist(StorageLevel.DISK_ONLY)
        vertices_df = (
            edges_df.select(F.col("src").alias("id"))
            .union(edges_df.select(F.col("dst").alias("id")))
            .distinct()
            .persist(StorageLevel.DISK_ONLY)
        )
        gf = GraphFrame(vertices_df, edges_df)
        assignment = gf.connectedComponents().persist(StorageLevel.DISK_ONLY)
        merged = featurized.join(
            assignment.select(
                F.col("id").alias(id_col), F.col("component").alias("__component__")
            ),
            on=id_col,
            how="left",
        )
        deduped = merged.filter(
            F.col("__component__").isNull() | (F.col("__component__") == F.col(id_col))
        ).drop("__component__")
        return deduped


def main():
    from pyspark.sql import SparkSession
    from pyspark.sql import Row

    spark = SparkSession.builder.master("yarn").appName("near-dedup-test").getOrCreate()

    data = [
        Row(id=1, content="The quick brown fox jumps over the lazy dog"),
        Row(id=2, content="Quick brown fox jumps over lazy dog!"),
        Row(id=3, content="Completely unrelated sentence here."),
        Row(
            id=4, content="the quick brown fox jumps over the lazy dog."
        ),  # duplicate-ish
        Row(id=5, content="Completely unrelated sentence here!!"),
    ]

    df = spark.createDataFrame(data)
    tool = NlpFilterNearDedup(
        column_name="content",
        index_column="id",
        threshold=0.8,
        num_perm=128,
        ngram_size=3,
        min_length=3,
        debug_assignment=False,
    )
    res = tool.run(df, spark=spark)
    aa = res.take(10000)
    spark.stop()
