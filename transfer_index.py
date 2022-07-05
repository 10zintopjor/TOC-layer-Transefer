from pathlib import Path
from antx import transfer
from pyparsing import srange
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
    index = Layer(annotation_type=LayerEnum.index, annotations=get_index_annotations(base_text))      
    opf._meta = instance_meta
    opf._index = index
    opf.save_index()
    opf.save_meta()
    return base_id

def get_index_annotations(base_text):
    annotation = {}
    clean_text = ""
    tocs = list(re.finditer("\{.*\}",base_text))
    for index,toc in enumerate(tocs):
        _,toc_end = toc.span()
        if index == len(tocs)-1:
            spans,clean_text = get_spans(text,clean_text,toc_end)
        else:
            next_toc_start,_ = tocs[index+1].span()
            spans,clean_text = get_spans(text,clean_text,toc_end,next_toc_start)
        toc_title = re.match("\{(.*)\}",toc.group())    
        annotation.update({uuid4().hex:{"title":toc_title.group(1),"span":spans}})

    return annotation

def get_spans(text,clean_text,start,end=None):
    span = {}
    if end == None:
        span["start"] = len(clean_text)
        span["end"] = len(clean_text+text[start:])
        clean_text+=text[start:]
    elif clean_text == "":
        span["start"] = 0
        span["end"] = end-start
        clean_text+=text[start:end]
    else:
        span["start"] = len(clean_text)
        span["end"] = len(clean_text+text[start:end])
        clean_text+=text[start:end]

    return span,clean_text


def main():
    src = Path("base_text.txt").read_text(encoding="utf-8")
    trg = Path("O2FCA4A99/O2FCA4A99.opf/base/6ABB.txt").read_text(encoding="utf-8")
    annotations = [["toc","(\{.*\})"]]
    result = transfer(src, annotations, trg, output="txt")
    Path("annoted_txt.txt").write_text(result,encoding="utf-8")

if __name__ == "__main__":
    #main()
    text = Path("./annoted_txt.txt").read_text()
    create_opf(text)