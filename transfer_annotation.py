from distutils.spawn import spawn
from pathlib import Path
import yaml
from logging import raiseExceptions
import os
from pathlib import Path
from uuid import uuid4
import shutil
import requests
import re
import json
from bs4 import BeautifulSoup
from openpecha.core.annotation import Page, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.metadata import InitialCreationType,InitialPechaMetadata
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml




def toyaml(dict):
    return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))


def form_root_text(root_layer,toc_layer):
    annotations = root_layer["annotations"]
    toc_iter = Toc_iter(toc_layer)
    for seg_id in annotations:
        print(next(toc_iter))
        span = annotations[seg_id]["span"]
        span = (span["start"],span["end"])
        get_text(span)

def Toc_iter(Toc_layer):
    annotations = Toc_layer["annotations"]
    for layer_id in annotations:
        span = annotations[layer_id]["span"]
        toc_title = get_text((span["start"],span["end"]))
        yield (toc_title,span["start"],span["end"])


def get_text(span):
    start,end = span
    base_path = "P000246/P000246.opf/base/v001.txt" 
    text = Path(base_path).read_text()
    return text[start:end]

def main():
    TOC_layer = from_yaml(Path("P000246/P000246.opf/layers/v001/Sabche.yml"))
    root_layer = from_yaml(Path("P000246/P000246.opf/layers/v001/Tsawa.yml"))
    form_root_text(root_layer,TOC_layer)


if __name__ == "__main__":
    main()