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

from transfer_annotation import toyaml,from_yaml

index_map = {}

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

def get_spans(spans,base_id):
    spans_res = []
    start,end = spans
    spans_res.append({"base":base_id,"start":start,"end":end})
    return spans_res

def main():
    global index_map
    prev_end = 0
    chapter_layer_path = "P000047/P000047.opf/layers/v001/Chapter.yml"
    base_text = Path("P000047/P000047.opf/base/v001.txt").read_text()
    root_base_text = ""
    chapter_layer = from_yaml(Path(chapter_layer_path))
    annotations = chapter_layer["annotations"]
    annotation_keys = list(annotations.keys())
    for index,id in enumerate(annotation_keys):
        cur_span = annotations[id]["span"]
        if index == 0 and cur_span["start"] != 0:
            next_span = annotations[annotation_keys[index+1]]["span"]
            root_base_text+=base_text[:cur_span["start"]-1]
            prev_end = len(root_base_text)
            cur_root = base_text[cur_span["end"]:next_span["start"]-1]
            root_base_text+= cur_root
            cur_toc = base_text[cur_span["start"]:next_span["end"]]
            index_map.update({cur_toc:(prev_end,prev_end+len(cur_root))})
            prev_end += len(cur_root)
        elif index == len(annotation_keys)-1:
            cur_root = base_text[cur_span["end"]:]
            root_base_text += cur_root
            cur_toc = base_text[cur_span["start"]:cur_span["end"]]
            index_map.update({cur_toc:(prev_end,prev_end+len(cur_root))})
        else:
            next_span = annotations[annotation_keys[index+1]]["span"]
            cur_root = base_text[cur_span["end"]:next_span["start"]-1]
            root_base_text+=cur_root
            cur_toc = base_text[cur_span["start"]:cur_span["end"]]
            index_map.update({cur_toc:(prev_end,prev_end+len(cur_root))})
            prev_end += len(cur_root)

    #create_opf(root_base_text)
    base_text = annote_text(root_base_text)
    Path("./base_text.txt").write_text(base_text)
    
def annote_text(text):
    base_text = ""
    for index,title in enumerate(index_map):
        tittle_annotation = "{"+title+"}"
        start,end = index_map[title]
        if index == 0 and start !=0:
            base_text+=text[:start]
        tittle_annotation = "{"+title+"}"
        start,end = index_map[title]
        base_text+=f"{tittle_annotation}\n{text[start:end]}"

    base_text+=f"\n{text[end:]}"    
    return base_text    
if __name__ == "__main__":
    main()