#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, argparse, re
from urllib.parse import urljoin

def brklnk(url:str, depth:int, visited:set = set()) -> int:
    try:
        if depth >= 0:
            #Check the website status
            response = requests.get(url)
            if 200 <= response.status_code < 400 and depth > 0 :
                content = BeautifulSoup(response.content, 'html.parser')
                for a in content.find_all('a'):
                    link = a.get("href")
                    # Check http or https
                    if re.match("http", link) == None:
                        link = urljoin(url, link)
                    if link not in visited:
                        visited.add(link)
                        brklnk(link, depth - 1, visited)   
            elif 400 <= response.status_code < 600:
                print("-------BROKEN LINK ------->", url)
            return len(visited)
    except Exception as error:
        print(error)

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
