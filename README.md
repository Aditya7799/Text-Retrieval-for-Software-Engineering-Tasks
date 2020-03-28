# SE-Project
Predicting Query quality for Source Code Dataset
Papers refered are linked in the repository.

**Need to create a hidden folder called ".intermediate if you want to store the intermediate files in extract_dataset.py**


Note that Coherence Score is still to be implemented.

# Latest Commit Changes
- Latest Commit has file "data.csv" which has dump of metric dictionary after running all 21 Pre-Retieval Metrics for both the datasets.
- SpamComments function implemented to remove spam comments like
"*********" , "----------------"  and empty Comments.

# Requirements so far
1.  **nltk and corpus-data**
So far this is used to remove stop-words from the queries.
2.  **tqdm**
Used to show progress (based on iterations completed)
3.  **comment-parser**
Used to extract comments from source-code files
4. **json** Used to dump and load dictionaries from files.
5. **statistics** used for mean() pstdev() functions.
6. **math** used for log() function.

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

## CLASS DESCRIPTION
1. **Memoization** - this class serves as the memory class to store calculated intermediate values that can be reused by other classes. The memoized values are:
   - D_t[dataset][term] : Dictionary that stores list of paths of all document in the dataset that contain term.
   - t_f[dataset][term] : Dictionary that stores the term-frequency of term in dataset.
   - IDF[dataset][term] : Dictionary that stores the InverseDocument-Frequency of term in dataset.
   - ICTF[dataset][term]: Dictionary that stores the Inverse Collection Term Frequency of term in dataset.
   - ENTPY[dataset][term] : Dictionary that stores the entropy values of term in dataset.
   - scq[dataset][term] : Dictionary that stores the scq similary value of term in dataset
   - W_BAR[dataset][term] : Dictionary that stores the w-average values of term in dataset.
   - Var[dataset][term]: Dictionary that stores the Var Coherency value of term in dataset.

## FUNCTION DESCRIPTION
1.  