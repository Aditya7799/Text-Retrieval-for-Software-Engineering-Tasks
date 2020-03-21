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

GLOBAL_PATH = os.path.dirname(os.path.abspath(__file__))
        
    

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

stopwords=set(stopwords.words('english'))

# List containing the items stored in the respective files
FILE_LIST=[]
ERROR_LIST=[]

# datadic={datasetName:[list of path of valid files]}
dataDic=defaultdict(list)
# dataComments={filepath:Comment}
dataComments={}

# metrics={dataset:{path:{comment:[AVGIDF]}}}
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
                # PREPROCESS MULTI_LINE COMMENTS HERE
                comments=comment_parser.extract_comments_from_str(data)

                l=[c.text() for c in comments]
                dataComments[path]=l
            except (UnicodeDecodeError,comment_parser.UnsupportedError) as e:
                continue
            file.close()
   
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

def tf(dataset,term,all_documents=True,document_path=""):
    # all_documents=True is for tf(t,D)
    # all_documents=False is for tf(t,d)
    count=0
    if(all_documents):
        document_path=dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        for f in document_path:
            try:
                file=open(f,"r")
                string=file.read()
                count+=string.count(term)
            except IsADirectoryError:
                continue
    else: #counts tf only in single document (document_path)
        try:
            file=open(document_path,"r")
            string=file.read()
            count+=string.count(term)
        except IsADirectoryError:
            pass
    return count

def ictf(dataset,term):
    document_path=dataDic[dataset]
    no_of_documents_corpus=len(document_path)
    TF=tf(dataset,term)
    ICTF=math.log(no_of_documents_corpus/TF)
    return abs(ICTF)

def entropy(dataset,term):
    document_path=dataDic[dataset]
    no_of_documents_corpus=len(document_path)
    dt=[]
    for doc in document_path:
        try:
            file=open(doc,"r")
            string=file.read()
            if(term in string):
                dt.append(doc)
            file.close()
        except IsADirectoryError:
            continue
    sum=0
    # print("Term:",term,no_of_documents_corpus,len(dt))
    denominator=tf(dataset,term)
    for doc in dt:
        temp=tf(dataset,term,False,doc)/denominator
        sum+=temp+math.log(temp,no_of_documents_corpus)
    return abs(sum)

def Query_Scope(dataset,terms):
    document_path=dataDic[dataset]
    no_of_documents_corpus=len(document_path)
    dic=defaultdict(int)
    for term in terms:
        for path in document_path:
            if(dic[path]==1):
                continue
            file=open(path,"r")
            string=file.read()
            if(term in string):
                dic[path]=1
    return sum(dic.values())/no_of_documents_corpus

def SimClarity_Score(dataset,terms):
    #calculating denominator
    document_path=dataDic[dataset]
    no_of_documents_corpus=len(document_path)
    sum=0
    for term in terms:
        x=tf(dataset,term)/no_of_documents_corpus
        temp=p(term,terms)
        # print(temp,x)
        a=abs(math.log(abs(temp/x)))
        sum = sum +a
    return sum

def p(term,terms):
    count=1
    for t in term:
        if(t==term):
            count+=1
    return count/len(terms)

def specificity():
    global metric,dataDic,dataComments
    
    for dataset,files in dataDic.items():
        print("Looping files in Dataset:",dataset,end=" ")
        for file in tqdm(files):
            try:
                comments=dataComments[file]
                print("Looping comments in file:",files.index(file))
                for comment in tqdm(comments):
                    idf_val=[]
                    ictf_val=[]
                    entropy_val=[]

                    terms=set(comment.split(" "))
                    terms=list(terms-stopwords-set([" ",""]))
                    
                    if(len(terms)==0): #case for comment made up completely of stopwords
                        continue
                    
                    for term in terms:
                        idf_val.append(idf(dataset,term))
                        ictf_val.append(ictf(dataset,term))
                        entropy_val.append(entropy(dataset,term))
                    
                    # print(entropy_val)
                    AvgIdf=abs(statistics.mean(idf_val))
                    MaxIdf=abs(max(idf_val))
                    DevIDF=statistics.pstdev(idf_val)
                    
                    AvgIctf=abs(sum(ictf_val)/len(ictf_val))
                    MaxIctf=abs(max(ictf_val))
                    DevIctf=statistics.pstdev(ictf_val)

                    AvgEntropy=abs(statistics.mean(entropy_val))
                    MedEntropy=abs(statistics.median(entropy_val))
                    MaxEntropy=abs(max(entropy_val))
                    DevEntropy=abs(statistics.pstdev(entropy_val))

                    QueryScope=abs(Query_Scope(dataset,terms))
                    SimClarityScore=abs(SimClarity_Score(dataset,terms))

                    print(AvgIdf,MaxIdf,DevIDF,AvgIctf,MaxIctf,DevIctf,AvgEntropy,MedEntropy,MaxEntropy,DevEntropy,QueryScope,SimClarityScore)
                    print("******************************************")
                    
                    metric[dataset][file][comment].append(AvgIdf)
                    metric[dataset][file][comment].append(MaxIdf)
                    metric[dataset][file][comment].append(DevIDF)
                    metric[dataset][file][comment].append(AvgIctf)
                    metric[dataset][file][comment].append(MaxIctf)
                    metric[dataset][file][comment].append(DevIctf)
                    metric[dataset][file][comment].append(AvgEntropy)
                    metric[dataset][file][comment].append(MedEntropy)
                    metric[dataset][file][comment].append(MaxEntropy)
                    metric[dataset][file][comment].append(DevEntropy)
                    metric[dataset][file][comment].append(QueryScope)
                    metric[dataset][file][comment].append(SimClarityScore)

            except KeyError: #path has no comment
                continue
    
    temp=open("Final values","w")
    j=json.dumps(metric)
    temp.write(j)
    temp.close()


               
                    
                    


def main():
    # print(GLOBAL_PATH)
    extract()
    print(len(FILE_LIST))
    print(len(ERROR_LIST))
    print(len(dataDic))
    print(len(dataComments))
    specificity()



main()