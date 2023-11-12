#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, argparse, re

times = 0

def brklnk(url:str, depth:int):
    global times
    times += 1
    #Check the website status
    site_pattern = re.compile(r"https?://.*?\..*?\.\w+|https?://.*?\.\w")
    site = site_pattern.findall(url)
    #print(site)
    
    status = requests.head(url)
    if 200 <= status.status_code < 400 and depth > 0 :
        response = requests.get(url)
        content = BeautifulSoup(response.content, 'html.parser')
        all_a = list()
        for a in content.find_all('a'):
            link = a.get("href")
            if link != None:
                all_a.append(link)
        all_a = set(all_a)
        for link in all_a:
            if site_pattern.match(link) == None and re.search(r"\@", link) == None:
                if re.match("/", link) == None:
                    link = "/" + link
                new_link = site[0] + link
                brklnk(new_link, depth - 1)
            elif site_pattern.match(link) != None:
                brklnk(link, 0)
    elif 400 <= status.status_code < 600:
        print("-------BROKEN LINK ------->", url)

def main():
    # build an empty parser
    parser = argparse.ArgumentParser()

    # define arguments
    parser.add_argument("url", help="url to search the broken link")
    parser.add_argument("--depth", default=1, help="number of sub-website to be searched")


    # instruct parser to parse command line arguments
    args = parser.parse_args()

    brklnk(args.url, int(args.depth))

    print(f"{times} site(s) analyzed")

if __name__ == '__main__':
    main()
