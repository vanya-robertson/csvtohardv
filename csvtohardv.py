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

#from sys import argv
from itertools import permutations
import csv
import tempfile, subprocess
from re import findall, sub, split, search, DOTALL

#input_card = """NEXT	2023-09-14 19:05:49 +0100
#PREV	2023-09-12 19:05:49 +0100
#Q	Describe the C syntax structure coded "union NAME {
#    ELEMENTS;
#} [VARIABLE_NAME];".
#A	creates a custom data type where only one instance can exist
#STRUCTURE	union
#%%this is the first comment
#%%this is the second comment
#%%
#
#"""
#
#input_untabbed = """Describe the C syntax structure coded "union NAME {
#    ELEMENTS;
#} [VARIABLE_NAME];"."""
#
#input_tabbed = """Describe the C syntax structure coded "union NAME {
#	    ELEMENTS;
#	} [VARIABLE_NAME];"."""

# Prepend tab to any line n > 1 in a string
def add_tabs(instring):
    returnlist = []
    count = 0
    for line in instring.split("\n"):
        if count == 0:
            returnlist.append(line)
        else:
            returnlist.append("\t" + line)
        count += 1
    return "\n".join(returnlist)

def column_combinatorics(array, explanation=None):
    array_only_lists = False
    for item in array:
        if type(item) is list:
            array_only_lists = True
    if array_only_lists == True:
        if len(array) != 2:
            raise ValueError("The array should contain exactly two sub_perm_lists")
        primary_perms = permutations(array, len(array))

        # Use case only for arrays comprised of only subarrays
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
                final_perm_string += str(" ".join(final_perm_list)) + " format_string='\"%s\"' outfile=\"\"" + "\n"
    else:
        # Use case only for arrays comprised of no subarrays
        perms = permutations(array, 2)
        final_perm_string = ""
        for permutation in list(perms):
            final_perm_list = []
            for sub_perm_list in permutation:
                final_perm_list.append(sub_perm_list)
            if explanation is not None:
                final_perm_list.append(explanation)
            final_perm_string += str(" ".join(final_perm_list)) + " format_string='\"%s\"' outfile=\"\"" + "\n"

    # Output to nvim buffer
    with tempfile.NamedTemporaryFile(suffix='csvtohardv') as temp:
        text = open(temp.name, 'w')
        text.write(str(final_perm_string))
        text.close()
        subprocess.call(['nvim', temp.name])
        text = open(temp.name, 'r')
        buffer_output = text.read()
        temp.close()
    return(buffer_output)


# Return a list of dictionaries embodying a card
def csv_to_dict(infile, selected_column_names, format_string='"%s"', mod=None):

    input_card_list = []

    with open(infile, newline='') as csvfile:
        # Wipe output file
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
            card_dict = {'MOD': mod,
                        'question_field': add_tabs(row[all_column_names.index(selected_column_names[0])]),
                        'format_string': format_string,
                        'A': row[all_column_names.index(selected_column_names[1])]}
            for column_name in selected_column_names[2:]:
                card_dict[column_name.upper()] = row[all_column_names.index(column_name)]
            input_card_list.append(card_dict)
    csvfile.close()
    return input_card_list


def hardv_card_to_dict(input_str):

    line_list = []
    card = {}

    count = 0
    for line in input_str.split("\n"):
        if count == 0:
            line_list.append(line + "\n")
        else:
            if bool(search("^[A-Z]+\t|^%%", line)):
                line_list.append(line + "\n")
            else:
                line_list[-1] = line_list[-1] + line + "\n"
        count += 1

    commentno=1
    for field in line_list:
#        print(field)
        if bool(search("^[A-Z]+\t", field)):
            key = findall("^[A-Z]+", field)[0]
            value = findall("(?<=[A-Z]\t).*", field, DOTALL)[0]
# If newline is causing issues, look at lines below
            if value[-1] == "\n":
                value = value[:-1]
#                print(value)
            if key == "Q":
                if bool(search("\".*\"", field, DOTALL)):
                    question_field_var = findall("(?<=\").*(?=\")", field, DOTALL)[0]
                    card["question_field"] = question_field_var
                    # Split string and insert %s
                    fmt_str_list = value.split(question_field_var)
                    fmt_str_list.insert(1,"%s")
                    card["format_string"] = "".join(fmt_str_list)
                else:
                    card["question_field"] = value
                    card["format_string"] = "%s"
            else:
                card[key] = value
        elif bool(search("^%%\n", field)):
            card["terminator"] = field
        elif bool(search("^%%", field)):
            card["comment" + str(commentno)] = field.rstrip()
            commentno+=1
        else:
            raise ValueError

    return card

def hardv_file_to_list(input_file):

    with open(input_file, newline='') as infile:
        file_content = infile.read()
        card_list = split("%%\n\n", file_content)
        counter = 0
        for card in card_list[:-1]:
            # Add support for %%\n
            card_list[counter] = card + "%%\n"
            counter += 1
        card_list.remove('')
    return card_list

#buffer_output = column_combinatorics(["structure", "code", "desc"]) # desired behaviour
buffer_output='code desc format_string=\'Describe the C syntax structure coded "%s"\' outfile="/home/jcrtf/csvtohardv/code-to-structure.fc"'
lineiterator = buffer_output.splitlines()
for line in lineiterator:

    # Read arguments from buffer_output
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
        format_string_full_arg = [ match for match in keywords if "format_string=" in match ][0]
        format_string_quoted_arg = split("=", format_string_full_arg, 1)[1]
        format_string_arg = str(format_string_quoted_arg.replace("\'", "", 1).replace("\'", "", len(format_string_quoted_arg)))
    except IndexError:
        format_string_arg='%s'

    generated_list = csv_to_dict("/home/jcrtf/projects/csvtohardv/c-syntax-structures.csv", non_keywords, format_string=format_string_arg, mod=mod_arg)
#    Generate the list of existing cards
    existing_list = []
    for card in hardv_file_to_list(outfile_arg):
        existing_list.append(hardv_card_to_dict(card))

    combined_list = []
    question_field_list = [existing_card['question_field'] for existing_card in existing_list]

#    print(generated_list)
#    print(existing_list)

    for card in generated_list:
        if card['question_field'] in question_field_list:
            card_no = question_field_list.index(card['question_field'])
            combined_list.append(existing_list[card_no] | card)
#            print(existing_list[card_no])
#            print(card)
        else:
            combined_list.append(card)
#            pass

    # Wipe output file
    open(outfile_arg, 'w').close()
    text = open("/dev/stdout", "a")
    for item in combined_list:
#        print(item.keys())
        if item['MOD'] != '':
            text.write("MOD\t" + item['MOD'] + "\n")
        if 'NEXT' in item.keys():
            text.write("NEXT\t" + item['NEXT'] + "\n")
        if 'PREV' in item.keys():
            text.write("PREV\t" + item['PREV'] + "\n")
        text.write("Q\t" + item['format_string'] % item['question_field'] + "\n")
        text.write("A\t" + item['A'] + "\n")
        # Insert all other allcaps values
        for x in item.keys():
            if bool(search("^[A-Z]+", x)) and x != 'MOD' and x != 'A' and x != 'NEXT' and x != 'PREV':
                text.write(x + "\t" + item[x] + "\n")
        # Insert all comments
        for x in item.keys():
            if bool(search("^comment.+", x)):
                text.write(item[x] + "\n")
        text.write('%%\n\n')
