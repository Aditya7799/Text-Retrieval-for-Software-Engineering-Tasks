import math
import statistics
from collections import defaultdict
from tqdm import tqdm
from utils.constants import *

class Specificity():
    def __init__(self,dataDic,dataComments,metric):
        self.dataDic=dataDic
        self.dataComments=dataComments
        self.metric=metric

        #memoization dictionaries for performance
        self.D_t={}
        self.t_f={}
        self.IDF={}
        self.ICTF={}
        self.ENTPY={}

        for dataset in dataDic.keys():
            self.IDF[dataset]={}
            self.ICTF[dataset]={}
            self.ENTPY[dataset]={}
            self.t_f[dataset]={}
            self.D_t[dataset]=defaultdict(list)     
    
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

    def ictf(self,dataset,term):
        if(term in self.ICTF[dataset]):
            return self.ICTF[dataset][term]
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        TF=self.tf(dataset,term)
        self.ICTF[dataset][term]=abs(math.log(no_of_documents_corpus/TF))
        return self.ICTF[dataset][term]

    def entropy(self,dataset,term):
        if(term in self.ENTPY[dataset]):
            return self.ENTPY[dataset][term]
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        dt=self.Dt(dataset,term)
        sum=0
        # print("Term:",term,no_of_documents_corpus,len(dt))
        denominator=self.tf(dataset,term)
        for doc in dt:
            temp=self.tf(dataset,term,False,doc)/denominator
            sum+=temp+math.log(temp,no_of_documents_corpus)
        self.ENTPY[dataset][term]=abs(sum)
        return self.ENTPY[dataset][term]

    def Query_Scope(self,dataset,terms):
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        dic=defaultdict(int)
        for term in terms:
            for path in document_path:
                if(dic[path]==1):
                    continue
                if(path in self.D_t[dataset][term]):
                    dic[path]=1
                    continue
                file=open(path,"r")
                string=file.read()
                if(term in string):
                    dic[path]=1
        return sum(dic.values())/no_of_documents_corpus

    def SimClarity_Score(self,dataset,terms):
        #calculating denominator
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        sum=0
        for term in terms:
            x=self.tf(dataset,term)/no_of_documents_corpus
            y=terms.count(term)/len(terms)
            a=y*abs(math.log(abs(y/x)))
            sum = sum +a
        return sum

    def specificity(self,dataset,file,comment):
        # print("Calculating Specificity")
        idf_val=[]
        ictf_val=[]
        entropy_val=[]

        terms=set(comment.split(" "))
        terms=list(terms-stopwords-set([" ",""]))
        
        if(len(terms)==0): #case for comment made up completely of stopwords
            raise Exception
        
        for term in terms:
            idf_val.append(self.idf(dataset,term))
            ictf_val.append(self.ictf(dataset,term))
            entropy_val.append(self.entropy(dataset,term))
        
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

        QueryScope=abs(self.Query_Scope(dataset,terms))
        SimClarityScore=abs(self.SimClarity_Score(dataset,terms))

        # print(repr(comment))
        # print(AvgIdf,MaxIdf,DevIDF,AvgIctf,MaxIctf,DevIctf,AvgEntropy,MedEntropy,MaxEntropy,DevEntropy,QueryScope,SimClarityScore)
        # print("******************************************")
        
        self.metric[dataset][file][comment].append(AvgIdf)
        self.metric[dataset][file][comment].append(MaxIdf)
        self.metric[dataset][file][comment].append(DevIDF)
        self.metric[dataset][file][comment].append(AvgIctf)
        self.metric[dataset][file][comment].append(MaxIctf)
        self.metric[dataset][file][comment].append(DevIctf)
        self.metric[dataset][file][comment].append(AvgEntropy)
        self.metric[dataset][file][comment].append(MedEntropy)
        self.metric[dataset][file][comment].append(MaxEntropy)
        self.metric[dataset][file][comment].append(DevEntropy)
        self.metric[dataset][file][comment].append(QueryScope)
        self.metric[dataset][file][comment].append(SimClarityScore)

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

    def similarity(self,dataset,file,comment):
        # print("Calculating Similarity")
        scq_val=[]
        
        terms=set(comment.split(    " "))
        terms=list(terms-stopwords-set([" ",""]))
        
        if(len(terms)==0): #case for comment made up completely of stopwords
            raise Exception
        
        for term in terms:
            scq_val.append(self.SCQ(dataset,term))
            

        # print(entropy_val)
        AvgSCQ=abs(statistics.mean(scq_val))
        MaxSCQ=abs(max(scq_val))
        SumSCQ=sum(scq_val)

        # print(AvgSCQ,MaxSCQ,SumSCQ)
        # print("******************************************")
        
        self.metric[dataset][file][comment].append(AvgSCQ)
        self.metric[dataset][file][comment].append(MaxSCQ)
        self.metric[dataset][file][comment].append(SumSCQ)

class Term_Relatedness():
    def __init__(self,dataDic,dataComments,metric):
        self.dataDic=dataDic
        self.dataComments=dataComments
        self.metric=metric

        #memoization dictionaries for performance
        self.D_t={}

        for dataset in dataDic.keys():
            self.D_t[dataset]=defaultdict(list)
     
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

    def PMI(self,dataset,term1,term2):
        d1=set(self.Dt(dataset,term1))
        d2=set(self.Dt(dataset,term2))
        num=len(d1.intersection(d2))/len(self.dataDic[dataset])
        den=(len(d1)/len(self.dataDic[dataset]))*(len(d2)/len(self.dataDic[dataset]))
        return math.log(num/den)
    
    def term_relatedness(self,dataset,file,comment):
        # print("Calculating Term-Relatedness")
        pmi_val=[]

        terms=set(comment.split(" "))
        terms=list(terms-stopwords-set([" ",""]))
        
        if(len(terms)==0): #case for comment made up completely of stopwords
            raise Exception

        n=len(terms)
        if(n==1):
            #handle case for query with one term only
            pmi_val.append(1)
        
        for i in range(n):
            for j in range(i+1,n):
                pmi_val.append(self.PMI(dataset,terms[i],terms[j]))
        
        AvgPMI=statistics.mean(pmi_val)
        MaxPMI=max(pmi_val)

        # print(AvgPMI,MaxPMI)
        # print("******************************************")
        
        self.metric[dataset][file][comment].append(AvgPMI)
        self.metric[dataset][file][comment].append(MaxPMI)

class Coherency():
    def __init__(self,dataDic,dataComments,metric):
        self.dataDic=dataDic
        self.dataComments=dataComments
        self.metric=metric

        #memoization dictionaries for performance
        self.D_t={}
        self.t_f={}
        self.IDF={}
        self.W_BAR={}
        self.Var={}


        for dataset in dataDic.keys():
            self.t_f[dataset]={}
            self.D_t[dataset]=defaultdict(list)
            self.IDF[dataset]={}
            self.W_BAR[dataset]={}
            self.Var[dataset]={}

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
        if(term in self.W_BAR[dataset]):
            return self.W_BAR[dataset][term]

        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        dt=self.Dt(dataset,term)
        
        temp=0
        for doc in dt:
            temp+=self.w(dataset,term,doc)
        
        self.W_BAR[dataset][term]=temp/len(dt)
        return self.W_BAR[dataset][term]

    def VAR(self,dataset,term):
        if(term in self.Var[dataset]):
            return self.Var[dataset][term]

        document_path=self.dataDic[dataset]
        no_of_documents_path=len(document_path)
        dt=self.Dt(dataset,term)
        wbar=self.w_bar(dataset,term)
        num=0
        for doc in dt:
            x=self.w(dataset,term,doc)
            num=num+(x - wbar)**2
        self.Var[dataset][term]=math.sqrt(num/len(dt))
        return self.Var[dataset][term]

    def simscore(self,doc1,doc2):
        #to be implemented

        return 1
    
    def Coh_Score(self,dataset,term):
        dt=self.Dt(dataset,term)
        n=len(dt)
        temp=0
        for i in range(n):
            for j in range(i+1,n):
                temp=temp+self.simscore(dt[i],dt[j])/(n*(n-1))
        return temp

    def coherency(self,dataset,file,comment):
        # print("Calculating Coherency")
        var_val=[]
        coh_score=[]
        
        terms=set(comment.split(    " "))
        terms=list(terms-stopwords-set([" ",""]))
        
        if(len(terms)==0): #case for comment made up completely of stopwords
            raise Exception
        
        for term in terms:
            var_val.append(self.VAR(dataset,term))
            coh_score.append(self.Coh_Score(dataset,term))

        # print(entropy_val)
        AvgVAR=abs(statistics.mean(var_val))
        MaxVAR=abs(max(var_val))
        SumVAR=sum(var_val)

        CS=abs(statistics.mean(coh_score))

        # print(AvgVAR,MaxVAR,SumVAR,CS)
        # print("******************************************")
        
        self.metric[dataset][file][comment].append(AvgVAR)
        self.metric[dataset][file][comment].append(MaxVAR)
        self.metric[dataset][file][comment].append(SumVAR)
        self.metric[dataset][file][comment].append(CS)

