# csvtohardv

A program for high-throughput flashcard generation from csv files  
Written in Python  

# Specifications

## Command-line entry

From command-line, takes the input csv file and the names of its columns in either a space-separated list, a space separated list and separately in an explanatory column, or in two space-separated lists.  
- Array in formats `"col1 col2 col3"` (with a constituent number of 2 or more items), `"col1 col2" "col3"` or `"col1 col2" "col3 col4"`.  
1. `csvtohardv test/c-syntax-structures.csv "code description structure"`  
2. `csvtohardv test/c-syntax-structures.csv "code structure" "description"` or `csvtohardv test/c-syntax-structures.csv "code structure" description` (without the quotations)  
3. `csvtohardv test/french-verbs.csv "eng.text eng.audio" "fra.text fra.audio"`  
Note that column names may only include alphabetical characters and "." [see below](#column-name-conversion).  
Note that file names containing the `~` `$HOME` expansion do not work.

Case 1.  
  - Generates every possible pairwise permutation of strings  
  - so `"structure code description"` generates ${}_3 P_2 = 6$ permutations:  
  - ["structure", "code"]  
  - ["code", "structure"]  
  - ["structure", "description"]  
  - ["description", "structure"]  
  - ["code", "description"]  
  - ["description", "code"]  

Case 2.  
  - so `"location PAO" "explanation"` generates ${}_2 P_{2} = 2$ lists:  
  - Generates every possible pairwise permutation of strings  
  - ["location", "PAO", "explanation"]  
  - ["PAO", "location", "explanation"]  

Case 3.  
  - Generates every permutation of the lists and combines the lists, but individually including elements from the first list.  
  - so `"eng.text eng.audio" "fra.text fra.audio"` generates $2 \text{(items in each sublist)} * {}_2 P_{2} \text{(items in list)} = 4$ lists:  
  - ["eng.text", "fra.text", "fra.audio"]  
  - ["eng.audio", "fra.text", "fra.audio"]  
  - ["fra.text", "eng.text", "eng.audio"]  
  - ["fra.audio", "eng.text", "eng.audio"]  

## Buffer input

Permutations of columns are output to a neovim buffer for editing.  
For each permutation, the user adds the output file, and optionally a format string for the question, a mod script for the flashcard, or both.  
`structure code formatstring='Write the code for the C syntax structure "%s".' outfile="/home/user/flashcards/programing/c/structure-to-code.fc"`  

## Downstream processing

Output from the neovim buffer used to read csv file, creating representations of the flashcards in a list of dictionaries.  
Output files specified in the buffer are also read, creating an analogous list of dictionaries.  
These lists are compared, updating the format string, answer field, any supplementary field and the mod file from the original card, yet retaining any comments from the original. This means that a modification of a question field in the csv file will delete it from the output file, but a new one will be created without timestamps (desirable behaviour) and without comments (undesirable behaviour).
Updated cards are output in the specified files in the ![hardv](https://github.com/dongyx/hardv) format.  

## Column name conversion

Strips the prefixes from column names.  
`fra.text` as a column name renders as the field `TEXT` in the ![hardv](https://github.com/dongyx/hardv) output, so the csv columns `eng.text` and `fra.text` can be processed separately, but the same mod script can be applied to the ![hardv](https://github.com/dongyx/hardv) output.  

## Recommended preparation

Previously to reading a csv file, run `head -n 1 filepath.csv` to determine column names.  

## Modules

sys.argv  
so.path.isfile  
itertools.permutations  
csv  
tempfile  
subprocess  
re  
