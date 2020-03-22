import math
import statistics
from collections import defaultdict
from tqdm import tqdm
from utils.constants import *

class Coherency():
    def __init__(self,dataDic,dataComments,metric):
        self.dataDic=dataDic
        self.dataComments=dataComments
        self.metric=metric

        #memoization dictionaries
        self.D_t=defaultdict(list)
        
        self.t_f={}
        for dataset in dataDic.keys():
            self.t_f[dataset]={}

    def Dt(self,dataset,term):
        #returns a list of paths of documents of dataset containing the term
        if(len(self.D_t[term])!=0):
            return self.D_t[term]
        
        for f in self.dataDic[dataset]:
            try:
                file=open(f,"r")
                string=file.read()
                if(term in string):
                    self.D_t[term].append(f)
            except IsADirectoryError:
                continue
        return self.D_t[term]

    def idf(self,dataset,term):
        documents_path=self.dataDic[dataset]
        no_of_documents_corpus=len(documents_path)
        doc_containing_term=len(self.Dt(dataset,term))
        return abs(math.log(doc_containing_term/no_of_documents_corpus))

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

    def w(self,dataset,term,document):
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        temp=1+math.log(self.tf(dataset,term,False,document))
        # print("Temp",temp)
        return (temp*self.idf(dataset,term)/no_of_documents_corpus)

    def w_bar(self,dataset,term):
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        dt=self.Dt(dataset,term)
        
        sum=0
        for doc in dt:
            sum=sum+self.w(dataset,term,doc)
        
        return sum/len(dt)

    def VAR(self,dataset,term):
        document_path=self.dataDic[dataset]
        no_of_documents_path=len(document_path)
        dt=self.Dt(dataset,term)
        wbar=self.w_bar(dataset,term)
        num=0
        for doc in dt:
            x=self.w(dataset,term,doc)
            num=num+(x - wbar)**2
        return math.sqrt(num/len(dt))

    def coherency(self):
        for dataset,files in self.dataDic.items():
            print("Looping files in Dataset:",dataset,end=" ")
            for file in tqdm(files):
                try:
                    comments=self.dataComments[file]
                    print("Looping comments in file:",files.index(file))
                    for comment in tqdm(comments):
                        print(comment)
                        var_val=[]
                        
                        terms=set(comment.split(" "))
                        terms=list(terms-stopwords-set([" ",""]))
                        
                        if(len(terms)==0): #case for comment made up completely of stopwords
                            continue
                        
                        for term in terms:
                            var_val.append(self.VAR(dataset,term))
                
                        # print(entropy_val)
                        AvgVAR=abs(statistics.mean(var_val))
                        MaxVAR=abs(max(var_val))
                        SumVAR=sum(var_val)


                        print(AvgVAR,MaxVAR,SumVAR)
                        print("******************************************")
                        
                        self.metric[dataset][file][comment].append(AvgVAR)
                        self.metric[dataset][file][comment].append(MaxVAR)
                        self.metric[dataset][file][comment].append(SumVAR)


                except KeyError: #path has no comment
                    continue
        return self.metric