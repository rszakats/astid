#!/usr/bin/env python
# coding: utf-8

from configparser import ConfigParser
import getpass
import os
import wget
import shutil
import gzip
from astropy.io import ascii
import sys
import re

def print_result(s):
    """
    Prints the result line(s) in a fancy way.

    Parameters
    ----------
    s : list
        The results.

    Prints a formatted output.
    """
    for line in s[1]:
        data2 = ascii.read(line, format='fixed_width_no_header',
               names=("MPC Desn", "H", "G", "Epoch", "M", "Peri.", "Node", "Incl.", "e", "n", "a", "U", "Reference", "#Obs", "#Opp", "Arc", "rms", "Perts", "Computer", "flag", "Designation", "Date"),
                col_starts=(0, 8, 14, 20, 26, 37, 48, 59, 70, 80, 92, 105, 107, 117, 123, 137, 142, 146, 150, 161, 166, 194),
                col_ends = (7, 13, 19, 25, 35, 46, 57, 68, 79, 91, 103, 106 ,116, 122, 126, 141, 145, 149, 160, 165, 193, 202),
                )
        # print(f"{'Results':=^80}")
        maxw = 0
        for i, _ in enumerate(data2.columns):
            if len(str(data2.columns[i-1][0])) > maxw:
                maxw = len(str(data2.columns[i-1][0])) + 10
        print(f"{'Results':=^{maxw+45}}")
        for i in range(len(data2.colnames)):
            if i%2:
                # text_width = len(str(data2.columns[i-1][0])) + 10
                text_width = 20
                #print(f"{text_width}")
                print(f"{str(data2.colnames[i-1]):10s}\t = {str(data2.columns[i-1][0]):{maxw}s}\t {data2.colnames[i]}\t = {data2.columns[i][0]}")

def print_help():
    """
    Returns the helpt text.
    """
    print("Usage:\nastinfo Ceres\nastinfo 1\nastinfo \"2007 OR10\"")

def nomatch(t):
    """
    Prints a message when there is no match for the input.

    Parameters
    ----------
    t : str
        The search string.

    Returns a no match string.
    """
    print(f"---------------------------\n"
          f"No match for {t}!\n"
          f"---------------------------\n")


def process_number(t, infile):
    """
    If input is an integer it will search for an asteroid number.

    Parameters
    ----------
    t : str
        Input string.
    infile : str
        Full path and name of the input index file.

    Returns
    -------
    str
        A fromatted output.

    """
    with open(infile, "r") as f:
        lines = []
        for line in f:
            if re.search(f"\({str(t)}\)", line):
                lines.append([str(line)])
        if len(lines) > 0:
            return [t, lines]
        else:
            return [0]

def process_name(t, infile):
    """
    If input is a string it will search for an asteroid name or designation.

    Parameters
    ----------
    t : str
        Input string.
    infile : str
        Full path and name of the input index file.

    Returns
    -------
    str
        A fromatted output.

    """
    with open(infile, "r") as f:
        lines = []
        for line in f:
            if str(t).lower() in line.lower():
                lines.append([str(line)])
            # if re.search(str(" "+str(t).lower()+" "), str(line)):
            #     lines.append(str(line))
        if len(lines) > 0:
            return [t, lines]
        else:
            return [0]
        

if __name__ == "__main__":
    user = getpass.getuser()
    # Reading config file
    config_object = ConfigParser()
    config_object.read("config.cfg")
    cfg = config_object["MAINCFG"]
    datadir = cfg['datadir']
    tmp = cfg['tmpdir']
    datafile = cfg['datafile']

    if os.path.exists(os.path.join("/home", user, datadir)) is False:
        os.mkdir(os.path.join("/home", user, datadir))

    if os.path.exists(os.path.join(tmp, user)) is False:
        os.mkdir(os.path.join(tmp, user))
    dfile = os.path.join("/home", user, datadir, datafile)
    if os.path.exists(dfile) is False:
        filename = wget.download("https://www.minorplanetcenter.net/iau/MPCORB/MPCORB.DAT.gz", out=os.path.join(tmp, user))
        with gzip.open(filename, 'rb') as f_in:
            with open(dfile, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    if len(sys.argv) == 1:
        print_help()
    # Printing help message.
    elif str(sys.argv[1]) == '--help':
        print_help()
    else:
        for i, targ in enumerate(sys.argv[1:]):
            # Check if the input is integer or string without a dot (float)
            if "." in targ:
                print(f"The {i+1}. argument ({targ}) is wrong! Plese see the "
                      f"usage below!")
                print_help()
                sys.exit()
            else:
                try:
                    targ = int(targ)
                    if isinstance(targ, int):
                        result = process_number(targ, dfile)
                        if result[0] == 0:
                            nomatch(targ)
                        else:
                            print_result(result)

                except ValueError:
                    if isinstance(targ, str):
                        result = process_name(targ, dfile)
                        if result[0] == 0:
                            nomatch(targ)
                        else:
                            print_result(result)
                            