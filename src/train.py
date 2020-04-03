import json
import csv
import numpy as np
import cvxopt
from collections import Counter

from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier


from sklearn.model_selection import train_test_split
from sklearn.metrics import *
from imblearn.over_sampling import SMOTE,BorderlineSMOTE,ADASYN
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

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
                

    # w=csv.writer(f)
    # w.writerows(c)
    X,Y=[],[]
    for i in c:
        if(len(i)==0 or len(i)!=22):
            continue

        X.append(i[0:21])
        Y.append(i[21])
        
    return X,Y


def main():
    oversample=ADASYN()
    undersample=RandomUnderSampler(sampling_strategy=0.5)
    steps=[('o',oversample),('u',undersample)]
    pipeline=Pipeline(steps=steps)
    X,Y=createCSV()
    X_train,X_test,Y_train,Y_test=train_test_split(X,Y,shuffle=True)
    print(Counter(Y_train)) 
    # X_train,Y_train=oversample.fit_resample(X_train,Y_train)
    print(Counter(Y_train))
    print(Counter(Y_test))
    # SVM classifier
    svm_clf=svm.SVC(kernel="rbf",gamma=1)
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
    dt_clf=DecisionTreeClassifier(criterion="entropy",max_depth=10)
    dt_clf.fit(X_train,Y_train)
    Y_pred=dt_clf.predict(X_test)
    print("DT CLASSIFIER")
    print(classification_report(Y_test,Y_pred))
    print("********************")
    # GBT classfier
    gbt_clf=GradientBoostingClassifier(max_depth=5)
    gbt_clf.fit(X_train,Y_train)
    Y_pred=gbt_clf.predict(X_test)
    print("GBT CLASSIFIER")
    print(classification_report(Y_test,Y_pred))
    print("********************")
    #MLP classifier
    mlp_clf=MLPClassifier()
    mlp_clf.fit(X_train,Y_train)
    Y_pred=mlp_clf.predict(X_test)
    print("MLP Output")
    print(classification_report(Y_test,Y_pred))
    print("*******************************************")
    #Random Forest Classifier
    rf_clf=RandomForestClassifier()
    rf_clf.fit(X_train,Y_train)
    Y_pred=rf_clf.predict(X_test)
    print("Random Forest Classifier")
    print(confusion_matrix(Y_test,Y_pred))
    print(classification_report(Y_test,Y_pred))
    print("******************************")







main()