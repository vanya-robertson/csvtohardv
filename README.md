# csvtohardv

A program for high-throughput flashcard generation from csv files
Written in Python  
Work in progress

# Specifications

- Output to ![hardv](https://github.com/vanya-robertson/hardv) format

In chronological order:

## Combinatorics function (Major function)

- Takes in an array of column names from the csv file and an optional external argument, also a column name, but is appended unconditionally (as would be desirable with explanations)
    + Array in format "["title1", "title2", "title3"]" or "[["title1", "title2"], ["title3", "title4"]]", which will permute the outer list, and the first sublist, if present, combining array\[0]\[0] and array\[1]
- Former case:
    + Generates every possible pairiwise permutation of strings
    + so ["structure", "code", "description"] generates ${}_3 P_2 = 6$ permutations:
    + ["structure", "code"]
    + ["code", "structure"]
    + ["structure", "description"]
    + ["description", "structure"]
    + ["code", "description"]
    + ["description", "code"]
- Former case with external argument:
    + Generates every possible pairiwise permutation of strings
    + so '["location", "PAO"], "explanation"' generates ${}_2 P_{2} = 2$ lists:
    + ["location", "PAO", "explanation"]
    + ["PAO", "location", "explanation"]
- Latter case:
    + Generates every permutation of the lists and combines the lists, but individually including elements from the first list. 
    + so [["eng.text", "eng.audio"], ["fra.text", "fra.audio"]] generates $2 \text{(items in sublist)} * {}_2 P_{2} \text{(items in list)} = 4$ lists:
    + ["eng.text", "fra.text", "fra.audio"]
    + ["eng.audio", "fra.text", "fra.audio"]
    + ["fra.text", "eng.text", "eng.audio"]
    + ["fra.audio", "eng.text", "eng.audio"]

## Editing function (Major function)

- Writes the output of the combinatorics function to a new tempfile.  
- Opens $EDITOR to edit the tempfile, editing arguments and adding format strings, and output files.  

## Output function (Major function)

- Takes in input csv file, output text file, column names and optionally mod argument (for running specific script from hardv)
    + All these come from the edited text file above
- For each card in the output file
    + If it exists in the output file and input file and differs between them, add the card from the input file (which has no timestamp) to the tempfile
    + If it exists in the output file and input file and does not differ between them, add the card from the output file (which may have a timestamp)
    + If it exists in the output file and not the input file, append the card from the output file to the tempfile
    + If it exists in the input file and not in the output file, append the card to the tempfile
    + Once looped through all cards in both input and output files, write the tempfile to the output file

## Column name conversion (Minor function)

- Strips the prefixes from column names
- Benefit is that instead of auxiliary hardv fields being "FRA.AUDIO", they are "AUDIO" so csv columns can be differentiated without compromising reliability needed for MOD scripts

## Modules

sys.argv  
itertools.permutations  
csv  
