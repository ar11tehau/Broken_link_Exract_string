#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, argparse, re

def brklnk(url:str, depth:int) -> int:
    try:
        #Check the website status
        status = requests.head(url)
        visited_link = list()
        if 200 <= status.status_code < 400 and depth > 0 :
            response = requests.get(url)
            content = BeautifulSoup(response.content, 'html.parser')
            for a in content.find_all('a'):
                a_get = a.get("href")
                # Don't treat mails
                if re.search(r"\@", a_get) == None and a_get != None:
                    #Create the link to check
                    if re.match("http", a_get) != None:
                        link = a_get
                    elif re.match("/", a_get) == None:
                        link = url + "/" + a_get
                    else:
                         link = url + a_get
                    if link not in visited_link:
                        brklnk(link, depth - 1)
                        visited_link.append(link)
        elif 400 <= status.status_code < 600:
            print("-------BROKEN LINK ------->", url)
        return len(visited_link)
    except requests.exceptions.MissingSchema as error:
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
