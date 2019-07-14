#!/usr/bin/env python3
"""
Module to convert RTKLib to EMS format
LKB(c) 2019
"""
import sys

def convertRINEXB2EMS(RINEX_b_file,EMS_output):

    if EMS_output:
        f_output = open(EMS_output,'w')
    else:
        f_output =  sys.stdout

    with open(RINEX_b_file, 'r') as RINEX_b:
      for line in RINEX_b:
        #find end of header
        if line.strip() == "END OF HEADER": #find end of header
            break
      while True:
        #read blocks of 3
        message=RINEX_b.readline().split()
        if not message: break #EOF
        try:
            if message[10]=='SBA': #SBAS message
                for idx in list(range(2)):
                  message += RINEX_b.readline().split()
            else:
              for idx in list(range(2)): RINEX_b.readline() #skip next 2 lines

            #write output in EMS format  SV_ID DATE_TIME MESSAGE_ID MESSAGE
            #seconds format is xx.1, this converts it to EMS one - xx
            second = message[6].split(".")[0]
            head = " ".join(message[0:6]) + " " + second + " " + message[11] + " "
            EGNOSmessage = "".join(message[12:])
            f_output.write(head + EGNOSmessage +"\n")
        except:
            print("Reading error, possibly corrupted message")

    if f_output is  not sys.stdout: f_output.close()
    return 0
