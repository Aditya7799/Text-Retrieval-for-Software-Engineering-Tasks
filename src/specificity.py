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


    def ictf(self,dataset,term):
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        TF=self.tf(dataset,term)
        ICTF=math.log(no_of_documents_corpus/TF)
        return abs(ICTF)

    def entropy(self,dataset,term):
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        dt=self.Dt(dataset,term)
        sum=0
        # print("Term:",term,no_of_documents_corpus,len(dt))
        denominator=self.tf(dataset,term)
        for doc in dt:
            temp=self.tf(dataset,term,False,doc)/denominator
            sum+=temp+math.log(temp,no_of_documents_corpus)
        return abs(sum)

    def Query_Scope(self,dataset,terms):
        document_path=self.dataDic[dataset]
        no_of_documents_corpus=len(document_path)
        dic=defaultdict(int)
        for term in terms:
            for path in document_path:
                if(dic[path]==1):
                    continue
                # if(path in self.D_t[dataset][term]):
                #     dic[path]=1
                #     continue
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

    def specificity(self):
        for dataset,files in self.dataDic.items():
            print("Looping files in Dataset:",dataset,end=" ")
            for file in tqdm(files):
                try:
                    comments=self.dataComments[file]
                    print("Looping",len(comments)," comments in file :",files.index(file),file)
                    for comment in  comments:
                        idf_val=[]
                        ictf_val=[]
                        entropy_val=[]

                        terms=set(comment.split(" "))
                        terms=list(terms-stopwords-set([" ",""]))
                        
                        if(len(terms)==0): #case for comment made up completely of stopwords
                            continue
                        
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

                        print(AvgIdf,MaxIdf,DevIDF,AvgIctf,MaxIctf,DevIctf,AvgEntropy,MedEntropy,MaxEntropy,DevEntropy,QueryScope,SimClarityScore)
                        print("******************************************")
                        
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
                        
                except KeyError: #path has no comment
                    continue
        return self.metric