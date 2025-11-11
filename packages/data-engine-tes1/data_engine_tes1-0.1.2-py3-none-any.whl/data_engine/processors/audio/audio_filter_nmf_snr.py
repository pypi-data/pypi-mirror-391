#!/usr/bin/env python3
# nmf_snr_filter.py

import librosa
import numpy as np
from librosa.decompose import decompose
from loguru import logger
from data_engine.core.base import BaseFilter


def separate_signal_noise(
    audio: np.ndarray, n_components: int = 2, nmf_iter: int = 500
):
    """用 NMF 把音频分成 signal 和 noise"""
    S = np.abs(librosa.stft(audio))
    W, H = decompose(
        S, n_components=n_components, init="random", random_state=0, max_iter=nmf_iter
    )
    signal = np.dot(W[:, :1], H[:1, :])
    noise = np.dot(W[:, 1:2], H[1:2, :])
    sig_time = librosa.istft(signal * np.exp(1j * np.angle(S)))
    noi_time = librosa.istft(noise * np.exp(1j * np.angle(S)))
    return sig_time, noi_time


def compute_nmf_snr(audio: np.ndarray, nmf_iter: int = 500) -> float:
    """计算音频的 NMF SNR（dB）"""
    sig, noi = separate_signal_noise(audio, nmf_iter=nmf_iter)
    p_sig = np.mean(sig**2)
    p_noi = np.mean(noi**2)
    if p_noi == 0:
        return np.finfo(np.float64).max
    return 10 * np.log10(p_sig / p_noi)


class AudioFilterNmfSnr(BaseFilter):
    """
    音频 NMF SNR 过滤
    计算音频的 NMF SNR 分数
    """

    def __init__(
        self,
        min_snr: float = 0.0,
        max_snr: float = None,
        nmf_iter: int = 500,
        file_path: str = "path",
        **kwargs,
    ):
        """
        初始化方法。
        min_snr: 最小 SNR # 最小 SNR 数值
        max_snr: 最大 SNR # 最大 SNR 数值
        nmf_iter: NMF 迭代次数 # NMF 迭代次数大小
        file_path: 音频文件字段名称#用于加载音频文件
        """
        super().__init__(**kwargs)
        self.min_snr = min_snr
        self.max_snr = max_snr or float("inf")
        self.nmf_iter = nmf_iter
        self.file_path = file_path

    def process(self, row: dict) -> dict:
        audio_path = row[self.file_path]
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        snr = compute_nmf_snr(audio, nmf_iter=self.nmf_iter)
        row["nmf_snr"] = float(snr)
        if self.do_filter and not (self.min_snr <= snr <= self.max_snr):
            return {}
        return row
