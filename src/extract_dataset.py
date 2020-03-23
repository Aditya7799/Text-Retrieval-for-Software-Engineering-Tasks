import glob
import os   
from comment_parser import comment_parser   #comment_parser()
from collections import defaultdict         #defaultdict()
import json                                 #dumps(),loads()
import math                                 #log()
import statistics                           #mean()
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm                      
from utils.PreRetrieval_Metrics import *
from utils.constants import *
GLOBAL_PATH = os.path.dirname(os.path.abspath(__file__))


def extract(use_intermediate_files=True,make_intermediate_files=False):
    global FILE_LIST,ERROR_LIST,dataComments,dataDic,metric

    if(use_intermediate_files):
        file_list=open(".intermediate/FILE_LIST","r")
        error_list=open(".intermediate/ERROR_LIST","r")
        datadic=open(".intermediate/dataDic","r")
        datacomments=open(".intermediate/dataComments","r")

        FILE_LIST=file_list.read().split("\n")
        ERROR_LIST=error_list.read().split("\n")
        data=datadic.read()
        dataDic=json.loads(data)
        data=datacomments.read()
        dataComments=json.loads(data)

        for d in dataset_directory_list:
            metric[d]={}
            for path in dataDic[d]:
                metric[d][path]=defaultdict()
                try:
                    for comment in dataComments[path]:
                        metric[d][path][comment]=[]
                except KeyError: #If the path file has no comments
                    continue
        return

    hashmap={}
    for dataset in dataset_directory_list:
        files=[]
        path=GLOBAL_PATH+"/Datasets/"+str(dataset)+"/**/*"
        files = [f for f in glob.glob(path, recursive=True)]
        hashmap[dataset]=files

    # extracting FILE_LIST
    for dataset,files in hashmap.items():
        for file in files:
            if(isValid(file) and not(os.path.isdir(file))):
                FILE_LIST.append(file)
    
    # extracting ERROR_LIST
    for file in FILE_LIST:
        temp=open(file,"r")
        try:
            data=temp.read()
        except UnicodeDecodeError:
            ERROR_LIST.append(file)

    # extracting dataDic
    for d in dataset_directory_list:
        for f in FILE_LIST:
            if(f not in ERROR_LIST):
                if(d in f.split("/")):
                    dataDic[d].append(f)
    
    # extracting dataComments
    for d,files in dataDic.items():
        for path in files:
            file=open(path,"r")
            try:
                # print(path)
                data=file.read()
                # PREPROCESS MULTI_LINE COMMENTS HERE
                comments=comment_parser.extract_comments_from_str(data)

                l=[c.text() for c in comments]
                dataComments[path]=l
            except (UnicodeDecodeError,comment_parser.UnsupportedError) as e:
                continue
            file.close()
   
    for d in dataset_directory_list:
        metric[d]={}
        for path in dataDic[d]:
            metric[d][path]=defaultdict()
            try:
                for comment in dataComments[path]:
                    metric[d][path][comment]=[]
            except KeyError: #If the path file has no comments
                continue
    # making files based on choice
    if(make_intermediate_files):
        file_list=open(".intermediate/FILE_LIST","w")
        error_list=open(".intermediate/ERROR_LIST","w")
        datadic=open(".intermediate/dataDic","w")
        datacomments=open(".intermediate/dataComments","w")

        for f in FILE_LIST:
            file_list.write(f+"\n")
        for f in ERROR_LIST:
            error_list.write(f+"\n")
        
        j=json.dumps(dataDic)
        datadic.write(j)
        j=json.dumps(dataComments)
        datacomments.write(j)

        file_list.close()
        error_list.close()
        datadic.close()
        datacomments.close()

def main():
    
    extract(True,False)
    # extract(False,True)
    mem=Memoization(dataDic,dataComments,metric)
    obj1=Specificity(dataDic,dataComments,metric,mem)
    obj2=Coherency(dataDic,dataComments,metric,mem)
    obj3=Similarity(dataDic,dataComments,metric,mem)
    obj4=Term_Relatedness(dataDic,dataComments,metric,mem)
    print(metric.keys())
    for dataset,files in dataDic.items():
        print("Looping files in Dataset:",dataset,end=" ")
        for file in tqdm(files):
            try:
                comments=dataComments[file]
                print("Looping",len(comments)," comments in file :",files.index(file),file)
                for comment in  comments:
                    try:
                        # print(repr(comment))
                        obj1.specificity(dataset,file,comment)
                        obj2.coherency(dataset,file,comment)
                        obj3.similarity(dataset,file,comment)
                        obj4.term_relatedness(dataset,file,comment)
                    except Exception:
                        continue
                    # break
            except KeyError: #path has no comment
                continue
        #     break
        # break
    
    
    print(metric["codeblocks-17.12svn11256"]["/home/aditya/Desktop/SE_Project/src/Datasets/codeblocks-17.12svn11256/src/tools/ConsoleRunner/main.cpp"]['\n * This file is part of the Code::Blocks IDE and licensed under the GNU General Public License, version 3\n * http://www.gnu.org/licenses/gpl-3.0.html\n *\n * $Revision$\n * $Id$\n * $HeadURL$\n '])

    # text=json.dumps(metric)
    # f=open("Val","w")
    # f.write(text)
    # f.close()




main()