import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh import scoring
from whoosh.index import open_dir
import sys
import csv
from whoosh.qparser import QueryParser
from tqdm import tqdm
import glob
from utils.constants import *
from extract_dataset import GLOBAL_PATH


def createIndex():
    global GLOBAL_PATH
    hashmap={}
    schema = Schema(title=TEXT(stored=True),path=ID(stored=True),content=TEXT,textdata=TEXT(stored=True))
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")


    for dataset in dataset_directory_list:
        path=GLOBAL_PATH+"/Datasets/"+str(dataset)+"/**/*"
        files = [f for f in glob.glob(path, recursive=True)]

        folder="indexdir/index_"+dataset
        if not os.path.exists(folder):
            os.mkdir(folder)
        ix=create_in(folder,schema)
        writer=ix.writer()
        for file in tqdm(files):
            if(os.path.isdir(file)):
                continue
            try:
                f=open(file,"r")
                text=f.read()
                f.close()
                writer.add_document(title=file.split("\\")[-1],path=file,content=text,textdata=text)
            except Exception as e:
                pass
        writer.commit()


def search(dataset,file,comment,maxN=3):
    ix=open_dir("indexdir/index_"+dataset)
    searcher=ix.searcher(weighting=scoring.BM25F)
    query=QueryParser("content",ix.schema).parse(comment)
    # print("Searching for comment", comment)
    results=searcher.search(query,limit=maxN)
    r=None
    try:
        r=[results[i]['title'] for i in range(maxN)]
    except:
        r=[results[i]['title'] for i in range(len(results))]
    # print(r)
    if(file in r and r.index(file)<maxN):
        return 1
    else:
        return 0


if __name__ == "__main__":
    search("codeblocks-17.12svn11256","/home/aditya/Desktop/SE_Project/src/Datasets/codeblocks-17.12svn11256/src/tools/ConsoleRunner/main.cpp",\
        " This will adapt the project's configuration file to your environment")
  