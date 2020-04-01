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

# folder names of the datasets
dataset_directory_list=[
    "codeblocks-17.12svn11256",
    "7z1900-src"
]
# Possible extensions of the files with source code
file_extension_list=[
    ".cpp",
    ".c",
    # ".h",
    # ".cppdata",
    # ".script"
]

# List containing the items stored in the respective files
FILE_LIST=[]
ERROR_LIST=[]


dataDic={}
dataComments={}
metric={}
stopwords=set(stopwords.words('english'))


spam_comments=['*',"-","=","/","_","*)"," "]

# GLOBAL_PATH points to src directory
GLOBAL_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))