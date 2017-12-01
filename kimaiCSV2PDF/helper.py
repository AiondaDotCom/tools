#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# File:     helper.py
# Author:   arwk
# Github:   https://github.com/AiondaDotCom/tools
# Created:  25.10.17
# Modified: 25.10.17
##

import os
import datetime
import holidays


def roundToNearest(value, nearest):
    """
    Rounds the <value> to the next <nearest>
    """
    invNearest = 1./nearest
    return round(value * invNearest) / invNearest

def decimalToTimedelta(decTimeValue):
    """
    Wandelt HH:MM in <Stunden>.<Dezimalminuten> um
    """
    hours = int(decTimeValue)
    minutesDec = decTimeValue - hours
    minutes = minutesDec * 60
    return hoursMinutesToTimedelta(hours, minutes)

def timedeltaToDecimal(timedelta):
    """
    Wandelt Stunden und Minuten in Dezimaldarstellung um
    https://www.ontheclock.com/employee_punch_time_card_calculator.aspx
    """
    [hours, minutes] = timedeltaToHoursMinutes(timedelta)
    return hours + minutes/60.

def hoursMinutesToTimedelta(hours, minutes):
    """
    Wandelt Stunden und Minuten in ein timedelta-objekt um
    """
    return datetime.timedelta(hours=round(float(hours)), minutes=round(float(minutes)))

def timedeltaToHoursMinutes(td):
    """
    Wandelt Timedeltaobjekt in Stunden, Minuten um
    """
    return (td.seconds//3600, (td.seconds//60)%60)

def checkConfigFile(toplevelPath, configFilename):
    """
    Checks if a configfile is present inside the toplevel directory
    """
    configFile = '{}/{}'.format(toplevelPath, configFilename)
    if os.path.isfile(configFile):
        # Found config File
        return True
    else:
        # Config File not found
        return False


def isHoliday(myYear, myMonth, myDay):
    bw_holidays = holidays.DE(prov='BW')
    bw_holidays.append({"2017-10-31": "Reformationstag"})

    return  datetime.date(myYear, myMonth, myDay) in bw_holidays

def isWeekend(myYear, myMonth, myDay):
    datum = "{:02d}.{:02d}.{}".format(myDay, myMonth, myYear)
    dateObj = datetime.datetime.strptime(datum, '%d.%m.%Y')
    weekday = dateObj.weekday()
    return weekday >= 5
