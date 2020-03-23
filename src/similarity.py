import math
import statistics
from collections import defaultdict
from tqdm import tqdm
from utils.constants import *


class Similarity():
    def __init__(self,dataDic,dataComments,metric):
        self.dataDic=dataDic
        self.dataComments=dataComments
        self.metric=metric

        #memoization dictionaries for performance
        self.D_t={}
        self.t_f={}
        self.IDF={}
        self.ICTF={}
        self.scq={}    


        for dataset in dataDic.keys():
            self.t_f[dataset]={}
            self.D_t[dataset]=defaultdict(list)
            self.IDF[dataset]={}
            self.ICTF[dataset]={}
            self.scq[dataset]={}

    def Dt(self,dataset,term):
        #returns a list of paths of documents of dataset containing the term
        if(len(self.D_t[dataset][term])!=0):
            return self.D_t[dataset][term]
        
        for f in self.dataDic[dataset]:
            try:
                file=open(f,"r")
                string=file.read()
                if(term in string):
                    self.D_t[dataset][term].append(f)
            except IsADirectoryError:
                continue
        return self.D_t[dataset][term]

    def idf(self,dataset,term):
        if(term in self.IDF[dataset]):
            return self.IDF[dataset][term]

        documents_path=self.dataDic[dataset]
        no_of_documents_corpus=len(documents_path)
        doc_containing_term=len(self.Dt(dataset,term))
        self.IDF[dataset][term]=abs(math.log(doc_containing_term/no_of_documents_corpus))
        return self.IDF[dataset][term]
        
    def ictf(self,dataset,term):
        if(term in self.ICTF[dataset]):
            return self.ICTF[dataset][term]
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        TF=self.tf(dataset,term)
        self.ICTF[dataset][term]=abs(math.log(no_of_documents_corpus/TF))
        return abs(self.ICTF[dataset][term])

    def tf(self,dataset,term,all_documents=True,document_path=""):
        # all_documents=True is for tf(t,D)
        # all_documents=False is for tf(t,d)
        count=0
        if(all_documents):
            if(term in self.t_f[dataset]):
                return self.t_f[dataset][term]
            
            document_path=self.dataDic[dataset]
            no_of_documents_corpus=len(document_path)
            for f in document_path:
                try:
                    file=open(f,"r")
                    string=file.read()
                    count+=string.count(term)
                except IsADirectoryError:
                    continue
            self.t_f[dataset][term]=count
            return count
        else: #counts tf only in single document (document_path)
            try:
                file=open(document_path,"r")
                string=file.read()
                count+=string.count(term)
            except IsADirectoryError:
                pass
            return count

    def SCQ(self,dataset,term):
        if(term in self.scq[dataset]):
            return self.scq[dataset][term]
        
        self.scq[dataset][term]=1+math.log(self.ictf(dataset,term))*self.idf(dataset,term)
        return self.scq[dataset][term]



    def similarity(self):
        for dataset,files in self.dataDic.items():
            print("Looping files in Dataset:",dataset,end=" ")
            for file in tqdm(files):
                try:
                    comments=self.dataComments[file]
                    print("Looping ",len(comments)," comments in file:",files.index(file),file)
                    for comment in comments:
                        scq_val=[]
                        
                        terms=set(comment.split(    " "))
                        terms=list(terms-stopwords-set([" ",""]))
                        
                        if(len(terms)==0): #case for comment made up completely of stopwords
                            continue
                        
                        for term in terms:
                            scq_val.append(self.SCQ(dataset,term))
                            
                
                        # print(entropy_val)
                        AvgSCQ=abs(statistics.mean(scq_val))
                        MaxSCQ=abs(max(scq_val))
                        SumSCQ=sum(scq_val)

                        print(comment,AvgSCQ,MaxSCQ,SumSCQ)
                        print("******************************************")
                        
                        self.metric[dataset][file][comment].append(AvgSCQ)
                        self.metric[dataset][file][comment].append(MaxSCQ)
                        self.metric[dataset][file][comment].append(SumSCQ)
                except KeyError: #path has no comment
                    continue
        