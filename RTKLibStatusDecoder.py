#!/usr/bin/env python3
"""
Module to extract data from RTKLib status files
LKB(c) 2019
"""
# import argparse
import sys
import glob
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib #so I can call next line
matplotlib.style.use('ggplot')

# TODO estimate residuals stats (RMS, STD per SV)

def parseRTKLibStatus(status_file,output_file="tmp.tmp"):
    '''
    extracts only Residuals from status file,ee pp 107 of manual

    $SAT,week,tow,sat,frq,az,el,resp,resc,vsat,snr,fix,slip,lock,outc,slipc,rejc
    week/tow : gps week no/time of week (s)
    sat/frq : satellite id/frequency (1:L1,2:L2,3:L5,...)
    az/el : azimuth/elevation angle (deg)
    resp : pseudorange residual (m)
    resc : carrier‐phase residual (m)
    vsat : valid data flag (0:invalid,1:valid)
    snr : signal strength (dbHz)
    fix : ambiguity flag (0:no data,1:float,2:fixed,3:hold)
    slip : cycle‐slip flag (bit1:slip,bit2:parity unknown)
    lock : carrier‐lock count
    outc : data outage count
    slipc : cycle‐slip count
    rejc : data reject (outlier) count

    $SAT,1557,432000.000,3,1,253.2,64.3,0.3219,-0.0006,1,48,1,1,1,0,1,0
    '''
    f_output = open(output_file,'w')
    #read line by line and filter
    with open(status_file, 'r') as statusFile:
      for line in statusFile:
        #find end of header
        if line.strip().split(",")[0] == "$SAT": #find end of header
            try:
                output_string = ",".join(line.strip().split(",")[1:])
                f_output.write(output_string+"\n")
            except:
                print("Reading error, possibly corrupted message")

    if f_output is not sys.stdout: f_output.close()
    return 0

def ReadRTKLibStatus(RTKLibProcessedFile):
    '''
    reading RTKLib status file processed by parseRTKLibStatus()
    week,tow,sat,frq,az,el,resp,resc,vsat,snr,fix,slip,lock,outc,slipc,rejc
    '''

    dataFrame = pd.read_csv(RTKLibProcessedFile, delimiter = ",",error_bad_lines=False,header=-1,
                 skipinitialspace=True,
                 encoding = 'utf-8-sig',na_values = ["NULL",""],engine ='c')
    columns = ["GPSweek","sow","SV","frq","az","el","resp","resc","vsat","snr","fix","slip","lock","outc","slipc","rejc"]
    dataFrame.columns = columns

    dataFrame['time']=dataFrame.apply(lambda row: timeFromGPS(row['GPSweek'],row['sow']), axis = 1)
    dataFrame=dataFrame.drop(['GPSweek','sow'],axis=1)
    dataFrame=dataFrame.set_index('time')

    return dataFrame

def timeFromGPS(GPSWeek,sow):
    '''
    get time from GPSWeek and seconds of the week
    '''
    import datetime as dt

    GPS0 = dt.datetime(1980, 1, 6) #GPS starting time

    epoch = GPS0  + dt.timedelta(weeks=GPSWeek, seconds=sow)
    return epoch

def plotResiduals(dataFrame,datasetDescription):
    '''
    plot data read by ReadRTKLibStatus()
    '''
    SV_el = dataFrame.pivot_table(columns='SV',values='el',index='time')
    SV_az = dataFrame.pivot_table(columns='SV',values='az',index='time')
    res_PR = dataFrame.pivot_table(columns='SV',values='resp',index='time')
    res_PR =  res_PR.dropna(axis=1, how='all')

    # plt_fig, axs = plt.subplots(3, 1, gridspec_kw={'height_ratios': [1,1, 1]},
    #                 figsize=(9, 9))
    plt_fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2,1]},
                    figsize=(9, 9))


    res_PR.plot(kind='box',ax=axs[0])
    axs[0].set_ylabel('Residuals [m]')
    axs[0].set_xlabel('SV')
    axs[0].set_title('PR residuals for {}'.format(datasetDescription))
    axs[0].set_xticklabels(axs[0].get_xticklabels(),rotation=45)
    axs[0].set_ylim([-1,1])

    #NOTE there is bug in py3.4, use py3.6 instead
    axs[1].scatter(SV_el,res_PR,alpha=0.1)
    axs[1].set_ylabel("PR residuals[m]")
    axs[1].set_xlabel('SV elevation (deg)')
    axs[1].set_ylim([-2,2])
    axs[1].set_xlim([0,90]) #el angle

    #create stats per SV
    cols = res_PR.columns
    std = res_PR[cols].apply(lambda x: np.nanstd(x), axis=0)
    std = np.insert(std.values,0,std.values[0]) #repeating first value twice, HACK
    mean = res_PR[cols].apply(lambda x: np.nanmean(x), axis=0)
    mean = np.insert(mean.values,0,mean.values[0])

    axs[0].plot(mean+std,'b',alpha=0.5) 
    axs[0].plot(mean-std,'b',alpha=0.5)

    #create overall stats for residuals
    allSV_stats = [dataFrame.resp.mean(),dataFrame.resp.std()]

    axs[0].axhline(allSV_stats[0]+allSV_stats[1],color='m',alpha=0.5)
    axs[0].axhline(allSV_stats[0]-allSV_stats[1],color='m',alpha=0.5)



    axs[1].axhline(allSV_stats[0]+allSV_stats[1],color='m',alpha=0.5)
    axs[1].axhline(allSV_stats[0]-allSV_stats[1],color='m',alpha=0.5)
    #describe RMS for all SV on top of magenta line
    text="STDE: {:.2f} m".format(allSV_stats[1])
    axs[1].annotate(text,(0,allSV_stats[0]+allSV_stats[1]),
        xycoords = 'data',fontweight='bold')

    # TODO: add option to plot ICP residuals
    # res_c = dataFrame.pivot_table(columns='SV',values='resc',index='time')
    # res_c =  res_c.dropna(axis=1, how='all')

    # res_c.plot(kind='box',ax=axs[2])
    # axs[2].set_ylabel('Residuals [m]')
    # axs[2].set_xlabel('SV')
    # axs[2].set_title('ICP residuals for {}'.format(datasetDescription))
    # axs[2].set_xticklabels(axs[0].get_xticklabels(),rotation=45)
    # axs[2].set_ylim([-0.02,0.02])

    # allSV_stats = [dataFrame.resc.mean(),dataFrame.resc.std()]
    # axs[2].axhline(allSV_stats[0]+allSV_stats[1],color='m',alpha=0.5)
    # axs[2].axhline(allSV_stats[0]-allSV_stats[1],color='m',alpha=0.5)


    plt.savefig("{}.png".format(datasetDescription), bbox_inches="tight", dpi=200);
    plt.close()

# class GPSDate(dt.date):
#     """
#     Class with useful GPS related date representations
#     modified after HdL
#     """
#
#     GPS0 = dt.date(1980, 1, 6) #GPS starting time
#
#     def __init__(self, *args):
#
#         self.gpsweek = '%i' % int((self - self.GPS0).days / 7)
#         self.day_of_week = self.strftime('%w')
#         self.day_of_year = self.strftime('%j')
#         self.yy = self.strftime('%y')
#         self.yyyy_mm_dd = self.strftime('%Y_%m_%d')
#         self.gps_sow = self - (self.GPS0 + dt.timedelta(weeks=int(self.gpsweek)))


if __name__ == "__main__":

    allFiles = glob.glob('*.stat') #read all files
    for ReadRTKLibStatusFile in allFiles:
        print("Reading {}...".format(ReadRTKLibStatusFile))

        parseRTKLibStatus(ReadRTKLibStatusFile,"out.out")
        GPS=ReadRTKLibStatus("out.out")
        plotResiduals(GPS,ReadRTKLibStatusFile[:-9])
        print ("            ... plot completed")


    sys.exit(0)
