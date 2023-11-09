#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, argparse, re

def strextract(dir: str, suffix: str, path: bool, all: bool) -> None:    
    #Handle the path
    if path:
        path_prefix = os.path.abspath(dir) + "\t"
    else:
        path_prefix=""
    

    #pattern = re.compile(r"([\"\'])(.*?)(\1)")
    pattern = re.compile(r"\".*?\"|\'.*?\'")
    #Go through all the folder
    for root, _, filenames in os.walk(dir):
        #   Go through all the file in the folder
        for filename in filenames:
            # Handle --suffix option
            if suffix and not(filename.endswith(suffix)):
                continue
            # Handle --all option
            if not(all) and filename.startswith("."):
                continue
            with open(dir + "/" + filename,'r', encoding="UTF-8") as lines:
                for line in lines:
                    for item in pattern.findall(line):
                        print(item)

def main():
    # build an empty parser
    parser = argparse.ArgumentParser()

    # define arguments
    parser.add_argument("dir", help="directory path")
    parser.add_argument("-s", '--suffix', help="suffix of to be deleted files")
    parser.add_argument("--path", action="store_true", help="print the file path before each printed ligne")
    parser.add_argument("-a", "--all", action="store_true", help="shows the hidden folders and files")

    # instruct parser to parse command line arguments
    args = parser.parse_args()

    strextract(args.dir, args.suffix, args.path, args.all)

if __name__ == '__main__':
    main()
