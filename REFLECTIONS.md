# Technique

`csvtohardv.py` has given me experience planning a large, multi-step project.  
It has also been my first non-cursory use of the list and dictionary data structures.  

# Shortcomings compared to specification

At command-line argumentation, the program does not accept an explanatory column after two space-separated lists (not urgent, not important: limited use case).  

# Other shortcomings

`csvtohardv.py` only uses neovim to edit the buffer. Add support for `$EDITOR` (urgent, important) and modify to enable to work on Windows (not urgent, not important).  
File names with `~` to `$HOME` expansion do not work (not urgent, not important).  
Program does not check for existence of column names before creation of buffer (not urgent, not important).  

# Further development

Modify to read json to allow easy updating of ![plover](https://github.com/openstenoproject/plover) dictionaries. This will require an additional input file to show which words from the dictionary I would like to learn. Further thought about this one is how to handle multiple dictionaries, potentially with overlapping chords.  
