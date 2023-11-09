#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, argparse, re

def strextract(dir:str, suffix:str, path:bool, all:bool) -> str:

    #Create an object that contain the structute of the dir
    l = os.walk(dir)
    
    #Handle the path
    if path:
        path = os.path.abspath(dir) + "\t"
    else:
        path=""

    #Go through all the folder
    for folder in l:
        #   Go through all the file in the folder
        for fichier in folder[2]:
            # Handle --suffix option
            if suffix and not(fichier.endswith(suffix)):
                continue
            # Handle --all option
            if not(all) and fichier.startswith("."):
                continue
            with open(dir + "/" + fichier,'r', encoding="UTF-8") as f:
                content = f.read()
                match = re.findall(r"([\"\'])(.*?)(\1)", content)
                for line in match:
                    print(path + line[0] + line[1] + line[2])

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
