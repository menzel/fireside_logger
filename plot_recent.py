#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import sys
import elitech
import seaborn
import os

#Sunrise/set
import datetime
from astral.sun import sun
from astral import LocationInfo
import matplotlib.patches as patches



device = elitech.Device("/dev/ttyUSB0")
body = device.get_data()



if len(sys.argv) > 1:
    cmd = sys.argv[1] 

if len(sys.argv) == 1 or cmd == "help":
    print("usage: [sudo] python3 plot_recent.py CMD")
    print("CMD: help, save, plot, reset")
    exit()

if cmd == "save" or cmd == "plot":
    dat = []

    for line in body:

        temp = float(line[2])
        date = str(line[1].date())
        time = str(line[1].time())

        dat.append((time, temp, date))

    if len(dat) == 0:
        print("No data available")



if cmd == "reset":
    devinfo = device.get_devinfo()
    param_put = devinfo.to_param_put()
    param_put_res = device.update(param_put)
    devinfo = device.get_devinfo()
    print(devinfo)



elif cmd == "save":
    # Write savefile

    desktop = os.path.expanduser("~/Desktop")

    with open(desktop + "/fireside_" + dat[0][0] + "_" + dat[0][2], "w") as sv:
        for line in dat:
            sv.write(str(line))

elif cmd == "plot":

    # Plot with colored lines
    v = [d[1] for d in dat] 
    low = np.ma.masked_greater_equal(v,0)
    high = np.ma.masked_greater_equal(v,25)

    plt.plot(v, linestyle='-', c='#ff3300')
    plt.plot(high, linestyle='-', c='#ffcc66')
    plt.plot(low, linestyle='-', c='#0099ff')

    # Labels and Ticks
    xlabc = 10

    maxval = max([x[1] for x in dat])
    minval = min([x[1] for x in dat]) 

    plt.xticks([x for x in range(0, len(dat),len(dat)//xlabc)],[dat[d][0][:-3] for d in range(0,len(dat),len(dat)//xlabc)], rotation='vertical') 
    plt.ylabel("Temp. (C)")
    plt.yticks(list(range(int(minval)-3,int(maxval)+3,1)))

    # Max/Min lines
    plt.axhline(maxval,0,0.01, c='#ccccff', linewidth=1, linestyle="--")
    plt.axhline(minval,0,0.01, c='#ccccff', linewidth=1, linestyle="--")


    # Title
    start = dat[0][2] + " (" + dat[0][0] + ")"
    end = dat[-1][2] + " (" + dat[-1][0] + ")" 
    plt.title("Temp. from " + start + " to " + end)


    # Sunrise/set

    def add_darkness(ax,dat, from_time, to_time, color='lightgray'):

        # location
        city = LocationInfo("London", "England", "Europe/London", 51.5, -0.116) 

        # find start
        date_start = datetime.datetime.strptime(dat[0][2], '%Y-%m-%d') 
        s = sun(city.observer, date=date_start) 

        for i,x in enumerate([d[0] for d in dat]): 
            if datetime.datetime.strptime(x, '%H:%M:%S').time() >= s[from_time].time():
                dusk = i
                break

        # find end
        date_end = datetime.datetime.strptime(dat[-1][2], '%Y-%m-%d')
        s = sun(city.observer, date=date_end) 

        for i,x in list(enumerate([d[0] for d in dat]))[::-1]: 
            if datetime.datetime.strptime(x, '%H:%M:%S').time() <= s[to_time].time():
                dawn = i 
                break 

        # add to plot
        darkness = patches.Rectangle((dusk,minval-3),dawn,abs(minval-3)+maxval+3,facecolor=color) 
        ax.add_patch(darkness)

    add_darkness(plt.gca(),dat, "sunset", "sunrise")
    add_darkness(plt.gca(),dat, "dusk", "dawn", "grey")

    # Lines
    [plt.axvline(x, c='silver',linestyle=':',linewidth=1) for x in range(0, len(dat),len(dat)//xlabc)]

    if minval < 0:
        plt.axhline(0, c='black', linewidth=1)





    # Adjust and show
    plt.subplots_adjust(bottom=0.2) 
    plt.show()


