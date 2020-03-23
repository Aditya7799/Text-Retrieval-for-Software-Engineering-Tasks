import math
import statistics
from collections import defaultdict
from tqdm import tqdm
from utils.constants import *

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




    def term_relatedness(self):
        for dataset,files in self.dataDic.items():
            print("Looping files in Dataset:",dataset,end=" ")
            for file in tqdm(files):
                try:
                    comments=self.dataComments[file]
                    print("Looping",len(comments)," comments in file :",files.index(file),file)
                    for comment in  comments:
                        pmi_val=[]


                        terms=set(comment.split(" "))
                        terms=list(terms-stopwords-set([" ",""]))
                        
                        if(len(terms)==0): #case for comment made up completely of stopwords
                            continue

                        n=len(terms)
                        if(n==1):
                            #handle case for query with one term only
                            pmi_val.append(1)
                        
                        for i in range(n):
                            for j in range(i+1,n):
                                pmi_val.append(self.PMI(dataset,terms[i],terms[j]))
                        
                        AvgPMI=statistics.mean(pmi_val)
                        MaxPMI=max(pmi_val)

                        print(AvgPMI,MaxPMI)
                        print("******************************************")
                        
                        self.metric[dataset][file][comment].append(AvgPMI)
                        self.metric[dataset][file][comment].append(MaxPMI)
                        
                except KeyError: #path has no comment
                    continue

