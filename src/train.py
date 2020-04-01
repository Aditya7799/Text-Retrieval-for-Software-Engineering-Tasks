import json
import csv
import numpy as np
import cvxopt

from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import *

def createCSV():
    metric=json.loads(open("Val","r").read())
    data=[]
    c=[]
    # f=open("data.csv","w")


    for dataset,files in metric.items():
        for file,comments in files.items():
            for comment,val in comments.items():
                # print(len(val))
                # data.append([dataset,file,comment]+val)
                c.append(val[0:22])
                
    c.remove([])
    # w=csv.writer(f)
    # w.writerows(c)
    X,Y=[],[]
    for i in c:
        # print(len(i))
        X.append(i[0:21])
        Y.append(i[21])
        
    return X,Y


def main():
    X,Y=createCSV()
    X_train,X_test,Y_train,Y_test=train_test_split(X,Y) 
    #SVM classifier
    svm_clf=svm.SVC()
    svm_clf.fit(X_train,Y_train)
    Y_pred=svm_clf.predict(X_test)
    print("SVM CLASSIFIER")
    print(classification_report(Y_test,Y_pred))
    print("*************************")
    #LR classifier
    lr_clf=LogisticRegression()
    lr_clf.fit(X_train,Y_train)
    Y_pred=lr_clf.predict(X_test)
    print("LR CLASSIFIER")
    print(classification_report(Y_test,Y_pred))
    print("*******************")
    #DT classfier
    dt_clf=DecisionTreeClassifier()
    dt_clf.fit(X_train,Y_train)
    Y_pred=dt_clf.predict(X_test)
    print("DT CLASSIFIER")
    print(classification_report(Y_test,Y_pred))
    print("********************")







main()