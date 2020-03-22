from nltk.corpus import stopwords
from collections import defaultdict


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

# List containing the items stored in the respective files
FILE_LIST=[]
ERROR_LIST=[]

# datadic={datasetName:[list of path of valid files]}
dataDic=defaultdict(list)
# dataComments={filepath:Comment}
dataComments={}

# metric={dataset:{path:{comment:[AVGIDF]}}}
metric={}

stopwords=set(stopwords.words('english'))

def isValid(f):
    return (f[f.rfind(".")+1:] in file_extension_list)