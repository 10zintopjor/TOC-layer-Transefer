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


index_map = {}
prev_end = 0

def toyaml(dict):
    return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))


def get_root_text(root_layer,toc_layer):
    global prev_toc,cur_toc,next_toc
    annotations = root_layer["annotations"]
    toc = get_toc(toc_layer)
    toc_iter = neighborhood(toc)
    base_text = ""
    prev_toc,cur_toc,next_toc = next(toc_iter)
    for seg_id in annotations:
        seg_span = annotations[seg_id]["span"]
        seg_span = (seg_span["start"],seg_span["end"])
        text = get_text(seg_span)
        base_text+=text
        get_index_map(seg_span,toc_iter,text)

    return base_text

def neighborhood(iterable):
    iterator = iter(iterable)
    prev_item = None
    current_item = next(iterator)  # throws StopIteration if empty.
    for next_item in iterator:
        yield (prev_item, current_item, next_item)
        prev_item = current_item
        current_item = next_item
    yield (prev_item, current_item, None)

def get_index_map(seg_span,toc_iter,text):
    global prev_toc,cur_toc,next_toc
    cur_title,_,cur_toc_end = cur_toc
    _,next_toc_start,_ = next_toc
    seg_start,seg_end = seg_span
    if seg_start > cur_toc_end and seg_end < next_toc_start:
        update_index(cur_title,text)
    else:
        prev_toc,cur_toc,next_toc = next(toc_iter)
        get_index_map(seg_span,toc_iter,text)
        
    return

def update_index(cur_title,text):
    global index_map,prev_end
    if not index_map.keys():
        index_map.update({cur_title:(0,len(text))})
    elif cur_title not in index_map.keys():
        index_map.update({cur_title:(prev_end,prev_end+len(text))})
    else:
        prev_start,prev_end = index_map[cur_title]
        index_map.update({cur_title:(prev_start,prev_end+len(text))})
    prev_end +=len(text)     
    return       

def get_toc(Toc_layer):
    toc_layer = []
    annotations = Toc_layer["annotations"]
    for layer_id in annotations:
        span = annotations[layer_id]["span"]
        toc_title = get_text((span["start"],span["end"]))
        toc_layer.append((toc_title,span["start"],span["end"]))

    return toc_layer

def get_text(span):
    start,end = span
    base_path = "P000246/P000246.opf/base/v001.txt" 
    text = Path(base_path).read_text()
    return text[start:end]

def main():
    TOC_layer = from_yaml(Path("P000246/P000246.opf/layers/v001/Sabche.yml"))
    root_layer = from_yaml(Path("P000246/P000246.opf/layers/v001/Tsawa.yml"))
    base_text = get_root_text(root_layer,TOC_layer)
    Path("./base_text.txt").write_text(base_text)
    yml = toyaml(index_map)
    Path("./index.yml").write_text(yml)


if __name__ == "__main__":
    main()