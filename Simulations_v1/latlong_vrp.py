from geopy.distance import geodesic 
import pandas as pd
from csv import writer
import os
import sys
import matplotlib.pyplot as plt
import math

def update_file(file):
    open(''.join([file,'\\site_latlong.csv']), 'w').close()
    open(''.join([file,'\\site_time.csv']), 'w').close()
    open(''.join([file,'\\result.txt']), 'w').close()

def update_fixed(file):
    
    open(''.join([file,'\\fixed_latlong.csv']), 'w').close()
    open(''.join([file,'\\fixed_time.csv']), 'w').close()


def plotgraph(latlongs):
        for s in latlongs:
            p = latlongs[s]
            plt.plot(p[0],p[1],'o')
            plt.text(p[0]+.01,p[1],s,horizontalalignment='left',verticalalignment='center')
            plt.show()
        plt.gca().axis('off') 

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)



def makefile(latlongs,file):

    for i in latlongs :
        results = []
        time = []
        time.append(i)
        results.append(i)
        for j in latlongs :
            site1 = latlongs[i]
            site2 = latlongs[j]
            value = (geodesic(site1,site2).km)
            results.append((value*1000))
            time.append(math.ceil(value*5))
        append_list_as_row(''.join([file,'\\site_latlong.csv']), results)
        append_list_as_row(''.join([file,'\\site_time.csv']), time)
        append_list_as_row(''.join([file,'\\fixed_latlong.csv']), results)
        append_list_as_row(''.join([file,'\\fixed_time.csv']), time)


