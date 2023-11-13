#!/home/arii/workspaces/unix/nosave/ux/bin/python

path = "./src/ciqual_data/"
#Convert the xls to csv
def convert():
    import pandas as pd
    import numpy as np

    excel_file = path + 'in.xls'

    df = pd.read_excel(excel_file).fillna(value="-")

    csv_file = 'out.csv'

    df.to_csv(path + csv_file, sep=";", index=False)

    print(f'{excel_file} has been converted to {csv_file}')

#import database into a list:
import csv

def init_list(path:str):

    # Initialize an empty list to store the data
    data_list = []

    # Open and read the CSV file
    with open(path, mode='r') as csv_file:
        # Create a CSV reader object
        csv_reader = csv.reader(csv_file)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            data_list.append(row)
    
    return data_list

def tri_list():
    all = init_list("out.csv")
    h = all[0]
    l = all[1:]


    
    #Récuperer l'index de la colonne Calcium
    for i in h[0]:
        if 'Calcium' in i:
            i_cal = h[0].index(i)
    
    r = []
    c = 0
    d = 0
    for i in l:
        if len(i) < 51:
            c += 1
            r.append(l.pop(l.index(i)))
        elif '-' == l[i_cal]:
            d += 1
            r.append(l.pop(l.index(i)))
    

    return r, l, c, d 
