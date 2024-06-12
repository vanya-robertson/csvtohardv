#!/usr/bin/env python
# script to convert csvs into flashcards of all combinations

# also create json to hardv extension for steno

# make card class for manipulation

# 1. function takes in array (of column names from csv) and optionally column name for explanation, automatically generating permutations # done
# 2. output this to a neovim buffer for editing and add a format sequence to the end of each line
# https://stackoverflow.com/questions/10129214/opening-vi-from-python
# https://parezcoydigo.wordpress.com/2012/08/11/call-vim-from-inside-a-python-script/
# https://github.com/neovim/pynvim
# 3. save text from this neovim buffer, performing the function writing the hardv format 
# this function takes in csv file, output file, format string, args from column_combinatorics ([["1", "2"], ["3", "4"]] or [["1", "2"], "5"])
# for a given card, check whether a question is not output to a file if it is already present, unless the answer has been changed, in which case replace it
# if card in output, output to temp file with timestamps if present
# if card in input but not in output, output to temp file

from sys import argv
from itertools import permutations
import csv

def column_combinatorics(array, explanation=None):
    array_only_lists = False
    for item in array:
        if type(item) is list:
            array_only_lists = True
    if array_only_lists == True:
        if len(array) != 2:
            raise ValueError("The array should contain exactly two sublists")
        primary_perms = permutations(array, len(array))

        #use case only for arrays with only subarrays
        #returns list
        for primary_perm in list(primary_perms):
            secondary_perms = permutations(primary_perm[0], 1)
            for secondary_perm in list(secondary_perms):
                finallist = [secondary_perm[0]]
                for sublist in primary_perm[1:]:
                    for subsublist in sublist:
                        finallist.append(subsublist)
#                        if explanation is not None:
#                            finallist.append([explanation])
#                            print(explanation)
                print(finallist)
    else:
        #use case only for arrays with no subarrays
        #returns list
        perms = permutations(array, 2)
        for permutation in list(perms):
#            print(permutation)
            finallist = []
            for sublist in permutation:
                finallist.append(sublist)
            if explanation is not None:
                finallist.append(explanation)
#                        print(explanation)
            print(finallist)
#   output to nvim buffer

def check_whether_in_file():
    pass

def output_to_hardv(infile, outfile, formatstring, *args, mod=None):
    with open(infile, newline='') as csvfile:
        with open(outfile, "w"):
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            column_names = []
            for row in csvreader:
                column_names.append(row)
                break
            if "next" in args:
                raise ValueError("The column name may not be \"next\"")
            if "prev" in args:
                raise ValueError("The column name may not be \"prev\"")
            for row in csvreader:
                if mod is not None:
                    print("MOD\t%s" % mod)
                if formatstring != "":
                    print("Q\t" + formatstring % row[0])
                else:
                    print("Q\t%s" % row[0])
                print("A\t%s" % row[1])
                for filtered_column_name in args[2:]:
                    print(filtered_column_name.upper() + "\t" + row[column_names[0].index(filtered_column_name)])
                print("%%\n")
    csvfile.close()

def main():
#    kwargs={kw[0]:kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=')>0]}
#    args=[arg for arg in argv if arg.find('=')<0]
#    print(args)
#    print(kwargs)
#    output_to_hardv("/home/jcrtf/c-syntax-structures.csv", "Write the code for the C syntax structure \"%s\"", "structure", "code", "desc", mod="hello.sh")
#    column_combinatorics([["eng.txt", "eng.aud", "eng.vid"], ["rus.txt", "rus.aud", "rus.vid"], ["ara.txt", "ara.aud", "rus.vid"]]) # inhibit use case # done
#    column_combinatorics([["eng.txt", "eng.aud", "eng.vid"], ["rus.txt", "rus.aud", "rus.vid"]]) # desired behaviour
#    column_combinatorics([["eng.txt", "eng.aud"], ["rus.txt", "rus.aud"]]) # desired behaviour
#    column_combinatorics(["structure", "code", "desc"]) # desired behaviour
#    column_combinatorics(["structure", "code"]) # desired behaviour
#    column_combinatorics(["location", "pao"], explanation="explanation") # desired behaviour
#    column_combinatorics(["location", "pao"], "explanation") # desired behaviour
    check_whether_in_file()

main()