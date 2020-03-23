# SE-Project
Predicting Query quality for Source Code Dataset
Papers refered are linked in the repository.

**Need to create a hidden folder called ".intermediate if you want to store the intermediate files in extract_dataset.py**

**Latest Commit has file "Val"(32Mb) which has dump of metric dictionary after running specificity (12 pre-retrieval metrics).
# Requirements so far
1.  **nltk and corpus-data**
So far this is used to remove stop-words from the queries.
2.  **tqdm**
Used to show progress (based on iterations completed)
3.  **comment-parser**
Used to extract comments from source-code files

# Datasets used
1.  **CodeBlocks Source code**
http://sourceforge.net/projects/codeblocks/files/Sources/17.12/codeblocks-17.12-1.el7.centos.src.rpm
2.  **7-zip Source Code**
https://www.7-zip.org/a/7z1900-src.7z

# Description of code so far

## GLOBAL VARIABLES
1. **dataset_directory_list** - contains folder names of the datasets
2. **file_extension_list** - contains list of file extensions
3. **stops_words** - set of english stopwords
4. **FILE_LIST** - list of path of files
5.  **ERROR_LIST** - subset of FILE_LIST that cause error when read().
6.  **dataDic** - datadic = {datasetName:[list of path of valid files from that dataset]}
datasetName = folder name of the dataset from dataset_directory_list
path = path of the file from FILE_LIST
7. **dataComments** - dataComments = {filepath:Comments}
filepath = file_path from FILE_LIST
Comment = list of comments
8. **metrics** - metrics={dataset:{path:{comment:[AVGIDF]}}}
dataset = name of the dataset folder
path = path of the source code file
comment = comment in the source code file
The list stores values in the follwing order [AvgIdf,MaxIdf,DevIDF,AvgIctf,MaxIctf,DevIctf,AvgEntropy,MedEntropy,MaxEntropy,DevEntropy]

## Function description
1.  