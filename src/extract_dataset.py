import glob
import os
from comment_parser import comment_parser
from collections import defaultdict
import json
import math


GLOBAL_PATH="/home/aditya/Desktop/SE_Project/src"
# folder names of the datasets
dataset_directory_list=[
    "codeblocks-17.12svn11256",
    "7z1900-src"
]
# Possible extensions of the files with source code
file_extension_list=[
    "cpp",
    "c",
    "h",
    "cppdata",
    "script"

]

# List containing the items stored in the respective files
FILE_LIST=[]
ERROR_LIST=[]

# datadic={datasetName:[list of path of valid files]}
dataDic=defaultdict(list)
# dataComments={filepath:Commentobject}
dataComments={}

# metrics={dataset:{path:{comment:[AVGIDF]
# 
metric={}


def isValid(f):
    return (f[f.rfind(".")+1:] in file_extension_list)

def extract(use_intermediate_files=True,make_intermediate_files=False):
    global FILE_LIST,ERROR_LIST,dataComments,dataDic,metric
    if(use_intermediate_files):
        file_list=open("FILE_LIST","r")
        error_list=open("ERROR_LIST","r")
        datadic=open("dataDic","r")
        datacomments=open("dataComments","r")

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
        path=GLOBAL_PATH+"/DATASETS/"+str(dataset)+"/**/*"
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
                comments=comment_parser.extract_comments_from_str(data)

                l=[c.text() for c in comments]
                dataComments[path]=l
            except (UnicodeDecodeError,comment_parser.UnsupportedError) as e:
                continue
            file.close()


    
        # makes files FILE_LIST and ERROR_LIST based on paramenter 
    
    # making files based on choice
    if(make_intermediate_files):
        file_list=open("FILE_LIST","w")
        error_list=open("ERROR_LIST","w")
        datadic=open("dataDic","w")
        datacomments=open("dataComments","w")

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

# class quality_measures():
#     def __init__(self):
        
#         self.idf=None
#         self.AvgIDF=None 
#         self.MaxIDF=None
#     def getAvgIDF(self,query,document):

def idf(dataset,term):
    count=0
    documents_path=dataDic[dataset]
    no_of_documents_corpus=len(documents_path)
    for f in documents_path:
        try:
            file=open(f,"r")
            string=file.read()
            if(term in string):
                count+=1
        except IsADirectoryError:
            continue
    return abs(math.log(count/no_of_documents_corpus))

def IDF():
    global metric,dataDic,dataComments
    
    for dataset,files in dataDic.items():
        for file in files:
            try:
                comments=dataComments[file]
                for comment in comments:
                    idf_val=[]
                    for term in comment.split(" "):
                        idf_val.append(idf(dataset,term))
                    print(idf_val)
                    AvgIdf=abs(sum(idf_val)/len(idf_val))
                    Stand_dev=[l-AvgIdf for l in idf_val]
                    print(Stand_dev,sum(Stand_dev))
                    
                    MaxIdf=abs(max(idf_val))
                    # DevIDF=math.sqrt(sum([l-AvgIdf for l in idf_val])/len(idf_val))
                    # print(comment,":",AvgIdf,MaxIdf,DevIDF)
                    print("****************")
                    metric[dataset][file][comment].append(AvgIdf)
                    metric[dataset][file][comment].append(MaxIdf)
            except KeyError: #path has no comment
                continue


               
                    
                    


def main():
    extract()
    print(len(FILE_LIST))
    print(len(ERROR_LIST))
    print(len(dataDic))
    print(len(dataComments))
    IDF()



main()