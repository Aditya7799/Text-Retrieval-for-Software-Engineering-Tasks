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

class IREngine():
    def __init__(self,dataDic,n=5,createIndex=False):
        self.maxN=n
        self.mem={}

        for dataset in dataDic.keys():
            self.mem[dataset]={}
        
        if(createIndex==True):
            self.createIndex()


    def createIndex(self):
        global GLOBAL_PATH,dataset_directory_list
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


    def search(self,dataset,file,comment):
        if(comment in self.mem[dataset]):
            return self.mem[dataset][comment]

        ix=open_dir("indexdir/index_"+dataset)
        searcher=ix.searcher(weighting=scoring.BM25F)
        query=QueryParser("content",ix.schema).parse(comment)
        results=searcher.search(query)

        r=None
        if(len(results)>=self.maxN):
            r=[results[i]["title"] for i in range(self.maxN)]
        else:
            r=[results[i]["title"] for i in range(len(results))]
        # print(r)
        # print(file)
        if(file in r):
            self.mem[dataset][comment]=1
        else:
            self.mem[dataset][comment]=0
        return self.mem[dataset][comment]

