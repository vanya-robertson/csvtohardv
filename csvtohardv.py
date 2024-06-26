#!/usr/bin/env python
# script to convert csvs into flashcards of all combinations

# also create json to hardv extension for steno

# make card class for manipulation

# 1. function takes in array (of column names from csv) and optionally column name for explanation, automatically generating permutations # done
# 2. output this to a neovim buffer for editing and add a format sequence to the end of each line
# 3. save text from this neovim buffer, performing the function writing the hardv format 
# this function takes in csv file, output file, format string, args from column_combinatorics ([["1", "2"], ["3", "4"]] or [["1", "2"], "5"])
# for a given card, check whether a question is not output to a file if it is already present, unless the answer has been changed, in which case replace it
# if card in output, output to temp file with timestamps if present
# if card in input but not in output, output to temp file

from sys import argv
from itertools import permutations
import csv
import tempfile, subprocess
from re import findall, sub, split

def column_combinatorics(array, explanation=None):
    array_only_lists = False
    for item in array:
        if type(item) is list:
            array_only_lists = True
    if array_only_lists == True:
        if len(array) != 2:
            raise ValueError("The array should contain exactly two sub_perm_lists")
        primary_perms = permutations(array, len(array))

        #use case only for arrays with only subarrays
        #returns list
        final_perm_string = ""
        for primary_perm in list(primary_perms):
            secondary_perms = permutations(primary_perm[0], 1)
            for secondary_perm in list(secondary_perms):
                final_perm_list = [secondary_perm[0]]
                for sub_perm_list in primary_perm[1:]:
                    for sub_sub_perm_list in sub_perm_list:
                        final_perm_list.append(sub_sub_perm_list)
#                        if explanation is not None:
#                            final_perm_list.append([explanation])
#                            print(explanation)
#                print(final_perm_list)
                final_perm_string += str(" ".join(final_perm_list)) + " formatstring='\"%s\"' outfile=\"\"" + "\n"
    else:
        #use case only for arrays with no subarrays
        #returns list
        perms = permutations(array, 2)
        final_perm_string = ""
        for permutation in list(perms):
#            print(permutation)
            final_perm_list = []
            for sub_perm_list in permutation:
                final_perm_list.append(sub_perm_list)
            if explanation is not None:
                final_perm_list.append(explanation)
#                        print(explanation)
#            print(final_perm_list)
            final_perm_string += str(" ".join(final_perm_list)) + " formatstring='\"%s\"' outfile=\"\"" + "\n"

#   output to nvim buffer
#    print(final_perm_string)

    with tempfile.NamedTemporaryFile(suffix='csvtohardv') as temp:
        text = open(temp.name, 'w')
        text.write(str(final_perm_string))
        text.close()
        subprocess.call(['nvim', temp.name])
        text = open(temp.name, 'r')
        buffer_output = text.read()
        temp.close()
    return(buffer_output)

def check_whether_in_file():
    pass

def output_to_hardv(infile, selected_column_names, formatstring='"%s"', mod=None, outfile="/dev/stdout"):
    with open(infile, newline='') as csvfile:
        # Wipe output file
        open(outfile, 'w').close()
        text = open(outfile, "a")
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        all_column_names = []
        for row in csvreader:
            for column_name in row:
                all_column_names.append(column_name)
            break
        if "next" in all_column_names:
            raise ValueError("A column name may not be \"next\"")
        if "prev" in all_column_names:
            raise ValueError("A column name may not be \"prev\"")
        for row in csvreader:
            if mod != '':
                text.write("MOD\t%s\n" % mod)
            text.write("Q\t" + formatstring % row[all_column_names.index(selected_column_names[0])] + "\n")
            text.write("A\t" + row[all_column_names.index(selected_column_names[1])] + "\n")
            for column_name in selected_column_names[2:]:
                text.write(column_name.upper() + "\t" + row[all_column_names.index(column_name)] + "\n")
            text.write("%%\n\n")
        text.close()
    csvfile.close()


def main():
#    output_to_hardv("/home/jcrtf/archives/flashcards/c-syntax-structures.csv", non_keywords, formatstring=formatstring_arg, mod=mod_arg, outfile=outfile_arg)
#    column_combinatorics([["eng.txt", "eng.aud", "eng.vid"], ["rus.txt", "rus.aud", "rus.vid"], ["ara.txt", "ara.aud", "rus.vid"]]) # inhibit use case # done
#    column_combinatorics([["eng.txt", "eng.aud", "eng.vid"], ["rus.txt", "rus.aud", "rus.vid"]]) # desired behaviour
#    column_combinatorics([["eng.txt", "eng.aud"], ["rus.txt", "rus.aud"]]) # desired behaviour
#    column_combinatorics(["structure", "code"]) # desired behaviour
#    column_combinatorics(["location", "pao"], explanation="explanation") # desired behaviour
#    column_combinatorics(["location", "pao"], "explanation") # desired behaviour
#    check_whether_in_file()
#    print(buffer_output)

#    buffer_output = column_combinatorics(["structure", "code", "desc"]) # desired behaviour
    buffer_output='code structure formatstring=\'Name the C syntax structure coded "%s"\' outfile="/dev/stdout"'

    lineiterator = buffer_output.splitlines()
    for line in lineiterator:
        keywords = findall("\\w+=\".+?\"|\\w+=\'.+?\'|\\w+=[\\S^\'\"]+", line)
        non_keywords = sub("\\w+=\".+?\"|\\w+=\'.+?\'|\\w+=[\\S^\'\"]+", '', line).split()

        try:
            outfile_full_arg = [ match for match in keywords if "outfile=" in match ][0]
            outfile_quoted_arg = split("=", outfile_full_arg, 1)[1]
            outfile_arg = str(outfile_quoted_arg.replace("\"", "", 1).replace("\"", "", len(outfile_quoted_arg)))
        except IndexError:
            outfile_arg='/dev/stdout'
    
        try:
            mod_full_arg = [ match for match in keywords if "mod=" in match ][0]
            mod_quoted_arg = split("=", mod_full_arg, 1)[1]
            mod_arg = str(mod_quoted_arg.replace("\"", "", 1).replace("\"", "", len(mod_quoted_arg)))
        except IndexError:
            mod_arg=''
    
        try:
            formatstring_full_arg = [ match for match in keywords if "formatstring=" in match ][0]
            formatstring_quoted_arg = split("=", formatstring_full_arg, 1)[1]
            formatstring_arg = str(formatstring_quoted_arg.replace("\'", "", 1).replace("\'", "", len(formatstring_quoted_arg)))
        except IndexError:
            formatstring_arg='%s'

#        print(non_keywords)
#        print(outfile_arg)
        output_to_hardv("/home/jcrtf/archives/flashcards/c-syntax-structures.csv", non_keywords, formatstring=formatstring_arg, mod=mod_arg, outfile=outfile_arg)
#        print(non_keywords)

#        print(keywords)
#        print(non_keywords)

#    print(non_keywords)

#
##    print(buffer_output)

main()
