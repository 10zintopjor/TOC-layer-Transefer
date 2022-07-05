from email.mime import base
from lib2to3.pytree import convert
from os import write
from requests import request
import requests
from openpecha.core.ids import get_base_id,get_initial_pecha_id
from datetime import datetime
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.pecha import OpenPechaFS 
from openpecha.core.metadata import InitialPechaMetadata,InitialCreationType
from bs4 import BeautifulSoup
from openpecha.core.annotation import AnnBase, Span
from uuid import uuid4
from pathlib import Path
from openpecha import github_utils,config
from zipfile import ZipFile
from pyewts import pyewts
import re
import logging
import csv
import yaml


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

def create_opf(base_text):
        pecha_id = get_initial_pecha_id()
        base_id = get_base_id()
        print(pecha_id)
        opf_path = f"{pecha_id}/{pecha_id}.opf"
        opf = OpenPechaFS(path =opf_path)
        bases = {f"{base_id}":base_text}
        opf.base = bases
        opf.save_base()
        instance_meta = InitialPechaMetadata(
            id=pecha_id,
            source = "P000246",
            initial_creation_type=InitialCreationType.input,
            source_metadata={
                "title":"༄༅། །བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པའི་ཟིན་བྲིས་མཚུངས་མེད་བླ་མའི་ཞལ་རྒྱུན་བཞུགས་སོ།",
                "language": "bo"
            })  
        index = Layer(annotation_type=LayerEnum.index, annotations=get_index_annotations(base_id))      
        opf._meta = instance_meta
        opf._index = index
        opf.save_index()
        opf.save_meta()
        return base_id

def get_index_annotations(base_id):
    annotation = []
    for chapter in index_map.keys():
        spans = get_spans(index_map[chapter],base_id)
        annotation.append({uuid4().hex:{"title":chapter.replace("\n",""),"span":spans}})
    annotations =  {uuid4().hex:{"parts":annotation}}
    return annotations

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

def get_spans(spans,base_id):
    spans_res = []
    for span in spans:
        start,end = span
        spans_res.append({"base":base_id,"start":start,"end":end})
    return spans_res

def update_index(cur_title,text):
    global index_map,prev_end
    if not index_map.keys():
        index_map[cur_title] = [(0,len(text))]
    elif cur_title not in index_map.keys():
        index_map[cur_title] = [(prev_end,prev_end+len(text))]
    elif cur_title in index_map.keys():
        index_map[cur_title].append((prev_end,prev_end+len(text)))

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
    base_text = text[start:end]
    base_text = remove_noise(base_text)
    return base_text

def remove_noise(text):
    nos = ["༡","༢","༣","༤","༥","༦","༧","༨","༩","༠"]
    for no in nos:
        text = text.replace(no,"")

    return text    

def main():
    TOC_layer = from_yaml(Path("P000246/P000246.opf/layers/v001/Sabche.yml"))
    root_layer = from_yaml(Path("P000246/P000246.opf/layers/v001/Tsawa.yml"))
    base_text = get_root_text(root_layer,TOC_layer)
    create_opf(base_text)


if __name__ == "__main__":
    main()