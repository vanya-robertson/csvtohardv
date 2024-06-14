#!/usr/bin/env python3
# Script to test separation of kwargs from args from buffer

import csv
from re import match, split

def output_to_hardv(infile, args, formatstring='"%s"', mod=None, outfile="/dev/stdout"):
    with open(infile, newline='') as csvfile:
        text = open(outfile, "a")
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
                text.write("MOD\t%s\n" % mod)
            if formatstring != "":
                text.write("Q\t" + formatstring % row[0] + "\n")
            else:
                text.write("Q\t%s\n" % row[0])
            text.write("A\t%s\n" % row[1])
            for filtered_column_name in args[2:]:
                text.write(filtered_column_name.upper() + "\t" + row[column_names[0].index(filtered_column_name) + "\n"])
            text.write("%%\n\n")
        text.close()
    csvfile.close()

buffer_output='structure code formatstring=\'"%s"\' mod="modscript" outfile="outputfile"'

output_list = buffer_output.split()

outfile_arg = list(filter(lambda v: match('^outfile=.*$', v), output_list))
outfile_unsanitised = split("=", outfile_arg[0], 1)[1]
proto_outfile = outfile_unsanitised.replace("\"", "", 1).replace("\"", "", len(outfile_unsanitised))
output_list.remove(outfile_arg[0])

mod_arg = list(filter(lambda v: match('^mod=.*$', v), output_list))
mod_unsanitised = split("=", mod_arg[0], 1)[1]
proto_mod = mod_unsanitised.replace("\"", "", 1).replace("\"", "", len(mod_unsanitised))
output_list.remove(mod_arg[0])

formatstring_arg = list(filter(lambda v: match('^formatstring=.*$', v), output_list))
formatstring_unsanitised = split("=", formatstring_arg[0], 1)[1]
proto_formatstring = formatstring_unsanitised.replace("\'", "", 1).replace("\'", "", len(formatstring_unsanitised))
output_list.remove(formatstring_arg[0])

print("Output file is: " + proto_outfile)
print("MOD script is: " + proto_mod)
print("Format string is: " + proto_formatstring)
print("Remaining arguments are: " + str(output_list))

output_to_hardv("/home/jcrtf/archives/flashcards/c-syntax-structures.csv", output_list, formatstring=proto_formatstring, mod=proto_mod)
