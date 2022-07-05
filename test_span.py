from pathlib import Path
from transfer_annotation import toyaml,from_yaml

def main_test():
    path = "O2FCA4A99/O2FCA4A99.opf/base/6ABB.txt"
    text = Path(path).read_text()
    print(text[23312:35855])

def test_sabche():
    sabche_path = "P000246/P000246.opf/layers/v001/Sabche.yml"
    base_text_path = "P000246/P000246.opf/base/v001.txt"
    toc = from_yaml(Path(sabche_path))
    base_text = Path(base_text_path).read_text()
    annotations = toc["annotations"]

    for seg_id in annotations:
        span = annotations[seg_id]["span"]
        start =span["start"]
        end = span["end"]
        print(base_text[start:end])
        print("****************")


if __name__ == "__main__":
    main_test()