#!/usr/bin/env python
"""
Run converter tool
Following metodology set by ROKUBUN
"""

import argparse
import sys

from RINEXb2EMS import convertRINEXB2EMS

if __name__ == "__main__":


    # Parse command line
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('input_log', metavar='<input RINEX b file>', type=str,
                        help="RINEX b 2.11 file")
    parser.add_argument('--output', '-o', metavar='<output EMS file>', type=str, default= "out.ems",
                        help="""
                        Output EMS file.
                        Default = out.ems.
                        To write to to the standard output use -o \"\"
                        """)


    ##running code
    args = parser.parse_args()
    RINEXfile = args.input_log

    print("writing{} to {}".format(RINEXfile,args.output))
    convertRINEXB2EMS(RINEXfile,args.output)



    sys.exit(0)
