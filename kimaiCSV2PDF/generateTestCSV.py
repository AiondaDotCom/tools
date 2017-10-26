#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import datetime
import random
import helper as hlp


#Datum, von, bis, h'm, Zeit, Stundenlohn, Euro, Budget, Bestätigt, Status, Verrechenbar, Kunde, Projekt, Tätigkeit, Beschreibung, Kommentar, Ort, Auftragsnummer, Benutzer, abgerechnet


now = datetime.datetime.now()
myYear = now.year
myDay = now.day
myMonth = now.month

numDays = calendar.monthrange(myYear, myMonth)[1]
print "Datum, von, bis, h'm, Zeit"
for day in range(1, numDays + 1):
    datum = "{:02d}.{:02d}.".format(day, myMonth)
    startDec = hlp.roundToNearest(random.uniform(8,15), .1)
    endDec = hlp.roundToNearest(startDec + random.uniform(0,5), .1)
    duration = endDec - startDec

    #startH = random.randint(10,17)
    #endH = startH + random.randint(1,5)
    #startM = random.randint(0,59)
    #endM = random.randint(0,59)
    [startH, startM] = hlp.timedeltaToHoursMinutes( hlp.decimalToTimedelta(startDec) )
    [endH, endM]     = hlp.timedeltaToHoursMinutes( hlp.decimalToTimedelta(endDec) )
    [zeitH, zeitM]   = hlp.timedeltaToHoursMinutes( hlp.decimalToTimedelta(duration) )

    von = "{:02d}:{:02d}".format(startH, startM)
    bis = "{:02d}:{:02d}".format(endH, endM)
    hm = "{:02d}:{:02d}".format(zeitH, zeitM)

    print "{},{},{},{},{}".format(datum, von, bis, hm, duration)
