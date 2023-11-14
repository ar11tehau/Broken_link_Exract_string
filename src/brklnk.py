#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, argparse, re

def brklnk(url:str, depth:int, visited:int = 0) -> int:
    try:
        visited = 1
        site_pattern = re.compile(r"https?://.*?\..*?\.\w+|https?://.*?\.\w")

        #Check the website status
        status = requests.head(url)
        
        if 200 <= status.status_code < 400 and depth > 0 :
            response = requests.get(url)
            content = BeautifulSoup(response.content, 'html.parser')
            for a in content.find_all('a'):
                link = a.get("href")
                if link == None:
                    continue
                else:
                    if re.match("http", link) != None:
                        visited += brklnk(link, 0)
                    elif re.search(r"\@", link) == None:
                        if re.match("/", link) == None:
                            link = "/" + link
                        new_link = url + link
                        visited += brklnk(new_link, depth - 1)
        elif 400 <= status.status_code < 600:
            print("-------BROKEN LINK ------->", url)
        return visited
    except requests.exceptions.MissingSchema as error:
        print(error)
        return visited

def main():
    # build an empty parser
    parser = argparse.ArgumentParser()

    # define arguments
    parser.add_argument("url", help="url to search the broken link")
    parser.add_argument("--depth", default=1, help="number of sub-website to be searched")


    # instruct parser to parse command line arguments
    args = parser.parse_args()

    visited = brklnk(args.url, int(args.depth))

    print(f"{visited} site(s) analyzed")

if __name__ == '__main__':
    main()
