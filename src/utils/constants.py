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
from multiprocessing import Process,Manager
from multiprocessing.managers import BaseManager,DictProxy
# folder names of the datasets

class MyManager(BaseManager):
    pass

MyManager.register('defaultdict',defaultdict,DictProxy)
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

# manager=Manager()
# dataDic=manager.dict()
# # dataComments={filepath:Comment}
# dataComments=manager.dict()

# # metric={dataset:{path:{comment:[AVGIDF]}}}
# metric=manager.dict()

dataDic={}
dataComments={}
metric={}
stopwords=set(stopwords.words('english'))

