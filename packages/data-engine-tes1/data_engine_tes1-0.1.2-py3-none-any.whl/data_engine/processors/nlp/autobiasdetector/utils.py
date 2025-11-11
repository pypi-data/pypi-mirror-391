import json


def read_jsonl(filename):
    with open(filename, encoding="utf8") as f:
        datas = f.readlines()
    datas_tmp = []
    for data in datas:
        data = json.loads(data)
        datas_tmp.append(data)
    return datas_tmp


def write_jsonl(file, train_datas):
    with open(file, "w", encoding="utf-8") as f:
        for data in train_datas:
            json.dump(data, f, ensure_ascii=False)
            f.write("\n")
