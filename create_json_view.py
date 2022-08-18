from ctypes import alignment
from transfer_annotation import toyaml,from_yaml
from pathlib import Path
import json

def get_alignment():
    alignments = []
    toc_path = Path("O2FCA4A99/O2FCA4A99.opf/layers/6ABB/Toc.yml")
    chapter_path = Path("P000047/P000047.opf/layers/v001/Chapter.yml")
    toc = from_yaml(toc_path)
    chapter = from_yaml(chapter_path)
    toc_annotations = toc["annotations"]
    chapter_annotations = chapter["annotations"]

    for toc_ann_id,chapter_ann_id in zip(toc_annotations,chapter_annotations):
        alignment = {}
        toc_span = toc_annotations[toc_ann_id]["span"]
        chapter_span = chapter_annotations[chapter_ann_id]["span"]
        alignment["source_segment"] = chapter_span
        alignment["target_segment"] = toc_span
        alignments.append(alignment)
    return alignments



def main():
    alignment = get_alignment()
    json_view = {
        "id":"",
        "source":"P000047",
        "target":"O2FCA4A99",
        "type":"text",
        "alignmnet":alignment
    }

    json_view = json.dumps(json_view)
    Path("./view.json").write_text(json_view)

if __name__ == "__main__":
    main()