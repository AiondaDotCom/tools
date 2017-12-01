#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# File:     kimai_csv2pdf.py
# config:   myConfig.json
# Author:   arwk
# Github:   https://github.com/AiondaDotCom/tools
# Created:  25.10.17
# Modified: 25.10.17
##

from pylatex import Document, LongTable, MultiColumn, Section, Command
from pylatex.utils import bold, NoEscape

import os, sys
import argparse
import calendar
import datetime
import csv
import json

import helper as hlp

# setUp argparse
parser = argparse.ArgumentParser(description='Kimai CSV to PDF')

parser.add_argument("-i", "--input",    dest='input',    help="Path to input file" )
parser.add_argument("-o", "--output",   dest='output',   help="Path to output file")
parser.add_argument("-e", "--employee", dest='employee', help="Name of employee")
parser.add_argument("-m", "--month",    dest='month',    help="Use MONTH instead of current month")
parser.add_argument("-y", "--year",     dest='year',     help="Use YEAR instead of current year")
parser.add_argument("-f", "--format",   dest='format',   help="Set time format ('normal', 'decimal', 'mixed')" )
parser.add_argument("-s", "--sign",     dest='signature',help="Path to image of scanned signature")
parser.add_argument("-w", "--weekend",  action='store_true', help="Mark weekends with WE")

args = parser.parse_args()

abbrv = ['WF', 'K', 'WA', 'U']

def generatePDF(obj):
    """
    Function that generates the rendered .pdf
    """
    geometry_options = {
        "margin": "2cm",
        "includeheadfoot": True
    }
    doc = Document(page_numbers=True, geometry_options=geometry_options)
    # Disable Page Numbering
    # https://jeltef.github.io/PyLaTeX/latest/examples/basic.html
    # https://tex.stackexchange.com/questions/7355/how-to-suppress-page-number#7357
    doc.preamble.append(Command('pagenumbering', 'gobble'))

    # Include Packages
    doc.preamble.append(Command('usepackage', 'url'))
    doc.preamble.append(Command('usepackage', 'fancyhdr'))
    doc.preamble.append(Command('usepackage', 'graphicx'))

    # Set Pagestyle (fancy is used for page header and footer)
    doc.preamble.append(Command('pagestyle', 'fancy'))

    # Header and Footer
    doc.preamble.append(Command('cfoot', NoEscape('Aionda Zeiterfassung - \\url{https://github.com/AiondaDotCom/tools}')))
    doc.preamble.append(Command('chead', (Command('Large', bold('Arbeitnehmer: Check-In-Time')))))

    #with doc.create(Section(NoEscape('Arbeitnehmer:\\\\Check-In-Time'), numbering=False)):

    # Create Table with informations about the employee
    with doc.create(LongTable("|l|l|l|")) as headerTable:
        headerTable.add_hline()
        headerTable.add_row([
            "Name: {}".format(obj["employee"]),
            "Monat: {:02d}".format(obj["month"]),
            "Jahr: {}".format(obj["year"])
            ])
        headerTable.add_hline()

    # Generate table for time tracking informations
    with doc.create(LongTable("|c|c|r|r|r|")) as data_table:
            data_table.add_hline()
            data_table.add_row([
                bold("Datum"),
                bold("von - bis"),
                bold("Pause"),
                bold("gesamte AZ"),
                bold(NoEscape("davon \\\"Uberstunden"))
                ])
            data_table.add_hline()
            data_table.end_table_header()
            data_table.add_hline()

            # Insert rows
            for row in obj["zeitAufzeichnungsTable"]:
                data_table.add_row(row)
                data_table.add_hline()

            data_table.add_hline()

            # Last row shows the total amount of hours
            arbeitszeitStr = "{}".format(obj["arbeitszeitKomplettRounded"])
            data_table.add_row(["Summe", '', '', arbeitszeitStr, ''])
            data_table.add_hline()

    # Generate table with remarks
    with doc.create(LongTable("lllll")) as signTable:
        signTable.add_row(['Bemerkungen:', 'Krankheitstage:',      'K',  'Schlechtwetter:', 'WA'])
        signTable.add_row(['',             'Wochenende/Feiertag:', 'WF', 'Urlaubstage:',    'U'])

    # Insert vertical space
    doc.append(Command('vspace', '1cm'))

    # place for signatures
    with doc.create(LongTable("ll")) as signTable:
        if obj['signatureFile']:
            signTable.add_row([Command('includegraphics', signatureFile, 'width=4cm'), Command('vspace', NoEscape('-.1cm'))])
        else:
            signTable.add_row(["", NoEscape("")])
        signTable.add_hline()
        signTable.add_row([NoEscape("Unterschrift Arbeitnehmer"), NoEscape("\hspace{4cm}Unterschrift Arbeitgeber")])

    # Finally the document is rendered
    doc.generate_pdf(obj['outputFilename'], clean_tex=False)


def generateZeitaufzeichnungsObj(csvFilename, employeeName, outputFilename, vonBisDarstellung, signatureFile):
    """
    Function that prepares the csv data

    """
    zeitAufzeichnungsObj = {}
    zeitAufzeichnung = {}
    zeitAufzeichnungsTable = []
    with open(csvFilename, 'rb') as csvfile:
        exportReader = csv.reader(csvfile, delimiter=',', quotechar='"')
        #Datum, von, bis, h'm, Zeit, Stundenlohn, Euro, Budget, Bestätigt, Status, Verrechenbar, Kunde, Projekt, Tätigkeit, Beschreibung, Kommentar, Ort, Auftragsnummer, Benutzer, abgerechnet

        i = 0

        arbeitszeitKomplett = 0
        arbeitszeitKomplettRounded = 0

        for row in exportReader:
            if i == 0:
                print "Skipping Header..."
            else:
                # Lese die Spalten der CSV-Zeile aus
                datum    = row[0]
                startHM  = row[1]
                endeHM   = row[2]
                dauerHM  = row[3]
                dauerDec = float(row[4])

                startObj = datetime.datetime.strptime("{}{} {}".format(datum, myYear, startHM), '%d.%m.%Y %H:%M')
                endObj   = datetime.datetime.strptime("{}{} {}".format(datum, myYear, endeHM), '%d.%m.%Y %H:%M')

                #print datum, start, startObj, ende, endObj, endObj-startObj

                # Summiere die Arbeitszeit mit voller Präzision auf
                arbeitszeitKomplett += dauerDec
                # Summiere die Arbeitszeit auf 15min gerundet auf
                #arbeitszeitKomplettRounded += hlp.roundToNearest(dauerDec, .25)

                # Überprüfe, ob das Datum bisher schon vorgekommen ist
                if datum not in zeitAufzeichnung:
                    # Noch kein Eintrag für diesen Tag
                    entry = {
                        'datum':    datum,
                        'startHM':  startHM,
                        'startObj': startObj,
                        'endeHM':   endeHM,
                        'endObj':   endObj,
                        'dauerDec': dauerDec
                        }
                    #row = [datum, "{}-{}".format(start, ende), '0.0', dauer, '']
                    zeitAufzeichnung[datum] = entry
                else:
                    # Bereits ein Eintrag für dieses Datum vorhanden
                    # -> Erweitern des bestehenden Eintrags
                    if startObj < zeitAufzeichnung[datum]['startObj']:
                        # der neue Eintrag ist früher als der bisherige
                        # -> setze das Startdatum auf das neue Datum
                        newStart = startObj
                        minStart = startHM
                    else:
                        # der Start des neuen Eintrags ist später als der bisherige
                        # -> behalte den alten Eintrag
                        newStart = zeitAufzeichnung[datum]['startObj']
                        minStart = zeitAufzeichnung[datum]['startHM']

                    if endObj > zeitAufzeichnung[datum]['endObj']:
                        newEnd = endObj
                        maxEnd = endHM
                    else:
                        newEnd = zeitAufzeichnung[datum]['endObj']
                        maxEnd = zeitAufzeichnung[datum]['endeHM']

                    entry = {
                        'datum':    datum,
                        'startObj': newStart,
                        'endObj':   newEnd,
                        'startHM':  minStart,
                        'endeHM':   maxEnd,
                        'dauerDec': zeitAufzeichnung[datum]['dauerDec'] + dauerDec
                        }

                zeitAufzeichnung[datum]=entry
            i+=1

        # Iteriere über alle Tage des Montas <myMonth>
        # Die Anzahl der Tage wird von der calendar Bibliothek bestimmt
        # https://stackoverflow.com/questions/42950/get-last-day-of-the-month-in-python#43663
        numDays = calendar.monthrange(myYear, myMonth)[1]
        arbeitszeitKomplettRounded = 0
        for i in range(1, numDays + 1):
        #for i in range(1, 31+1):
            #date = "{tag:02d}.{monat:02d}.{jahr}".format(tag=i, monat = now.month, jahr=now.year)
            date = "{tag:02d}.{monat:02d}.".format(tag=i, monat = myMonth)

            if date in zeitAufzeichnung:
                # Eintrag ist vorhanden

                startHM          = zeitAufzeichnung[date]['startHM']
                [startH, startM] = startHM.split(':')
                startDec         = hlp.timedeltaToDecimal(hlp.hoursMinutesToTimedelta(startH, startM))
                startDecRounded  = hlp.roundToNearest(startDec, .25)

                endHM            = zeitAufzeichnung[date]['endeHM']
                [endH, endM]     = endHM.split(':')
                endDec           = hlp.timedeltaToDecimal(hlp.hoursMinutesToTimedelta(endH, endM))
                endDecRounded    = hlp.roundToNearest(endDec, .25)

                # Rückumwandlung der gerundeten Zeit in Stunden, Minuten
                start = hlp.decimalToTimedelta(startDecRounded)
                [starth, startm] = hlp.timedeltaToHoursMinutes(start)

                end = hlp.decimalToTimedelta(endDecRounded)
                [endh, endm] = hlp.timedeltaToHoursMinutes(end)

                diffStartEnde = zeitAufzeichnung[date]['endObj'] - zeitAufzeichnung[date]['startObj']

                arbeitszeitKomplettRounded += hlp.roundToNearest(zeitAufzeichnung[date]['dauerDec'], 0.25)
                gesamteAZ = hlp.roundToNearest(zeitAufzeichnung[date]['dauerDec'], 0.25)
                gesamteAZStr = "{:.2f}".format(gesamteAZ)
                davonUeberstunden = ""

                # Pause: (ende-start) - realeArbeitszeit
                #pause = hlp.roundToNearest(
                #    hlp.timedeltaToDecimal(diffStartEnde -   hlp.decimalToTimedelta(zeitAufzeichnung[date]['dauerDec'])), .25)
                if endDecRounded >= startDecRounded:
                    pause = endDecRounded - startDecRounded - gesamteAZ

                    if pause < 0:
                        # Da alle Zeiten gerundet werden, kann es vorkommen, dass negative Pausen berechnet werden
                        # Um dies zu umgehen, werden die Start und Endzeiten angepasst
                        # Von der Startzeit wird die Hälfte der Pause abgezogen
                        # Von der Endzeit wird die Hälfte der Pause aufaddiert
                        print "Pause negativ (durch rundung) => korrigiere start & end-zeit"
                        print "Vorher: {}-{} ({}-{})".format(startDec, endDec, startDecRounded, endDecRounded)
                        startDec = startDec - abs(pause/2.)
                        endDec   = endDec   + abs(pause/2.)
                        # Runde Start und Endzeit neu
                        startDecRounded = hlp.roundToNearest(startDec, .25)
                        endDecRounded   = hlp.roundToNearest(endDec, .25)

                        start = hlp.decimalToTimedelta(startDecRounded)
                        [starth, startm] = hlp.timedeltaToHoursMinutes(start)

                        end = hlp.decimalToTimedelta(endDecRounded)
                        [endh, endm] = hlp.timedeltaToHoursMinutes(end)

                        print "Nachher: {}-{} ({}-{})".format(startDec, endDec, startDecRounded, endDecRounded)

                        # Berechne Pausendauer neu
                        pause = endDecRounded - startDecRounded - gesamteAZ

                    # Formatiere die Pausendauer auf zwei Nachkommastellen
                    pauseStr = "{:.2f}".format(pause)
                else:
                    # Gebe Warnung aus, wenn Startzeit nach Endzeit liegt
                    print "{}>{}".format(startDecRounded, endDecRounded)
                    raise ValueError('Endzeit kleiner als Startzeit (womöglich tagesübergreifend)')


                if vonBisDarstellung == 'decimal':
                    # Dezimal
                    vonBisStr = "{:05.2f} - {:05.2f}".format(startDecRounded, endDecRounded)

                elif vonBisDarstellung == 'mixed':
                    # mixed
                    vonBisStr = "{:02d}:{:02d} ({:05.2f}) - {:02d}:{:02d} ({:05.2f})".format(starth, startm, startDecRounded, endh, endm, endDecRounded)

                else:
                    # Normal (HH:MM)
                    vonBisStr = "{:02d}:{:02d} - {:02d}:{:02d}".format(starth, startm, endh, endm)


                row = [date, vonBisStr, pauseStr, gesamteAZStr, davonUeberstunden]
            elif args.weekend and (hlp.isHoliday(myYear, myMonth, i) or hlp.isWeekend(myYear, myMonth, i)):
                print "HOLIDAY/WE"
                row = [date, '(WF)', '(WF)', '(WF)', '']
            else:
                row = [date, NoEscape('---'), NoEscape('---'), NoEscape('---'), '']

            zeitAufzeichnungsTable.append(row)
            print row

    print "AZ komplett (exakt): {} = {}".format(arbeitszeitKomplett,        hlp.decimalToTimedelta(arbeitszeitKomplett))
    print "AZ komplett (~0.25): {} = {}".format(arbeitszeitKomplettRounded, hlp.decimalToTimedelta(arbeitszeitKomplettRounded))

    zeitAufzeichnungsObj = {
        'employee':                   employeeName,
        'year':                       myYear,
        'month':                      myMonth,
        'arbeitszeitKomplett':        arbeitszeitKomplett,
        'arbeitszeitKomplettRounded': arbeitszeitKomplettRounded,
        'zeitAufzeichnungsTable':     zeitAufzeichnungsTable,
        'outputFilename':             outputFilename,
        'signatureFile':              signatureFile
    }

    return zeitAufzeichnungsObj


if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))

    configFilename     = 'myConfig.json'
    configFilenameDemo = 'demoConfig.json'

    configFilePath = "{}/{}".format(path, configFilename)
    demopath = "{}/{}".format(path, configFilenameDemo)
    print configFilePath
    if hlp.checkConfigFile(path, configFilename):
        # Read configuration file
        with open(configFilePath) as json_data:
            config = json.load(json_data)
            #print(d)
    else:
        # Exit if no configfile is present
        print "There seems to be no config file '{cpath}' :(\nTo create one, you might want to copy the demo file.\n  cp {demopath} {cpath}\nExiting...".format(demopath=demopath, cpath=configFilePath)
        sys.exit()

    wdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

    now = datetime.datetime.now()
    myYear = now.year
    myDay = now.day

    employeeName       = args.employee            if args.employee             else config['defaultName']
    csvFilename        = args.input               if args.input                else config['defaultInput']
    outputFilename     = args.output              if args.output               else config['defaultOutput']
    myMonth            = int(args.month)          if args.month                else now.month
    myYear             = int(args.year)           if args.year                 else now.year
    vonBisDarstellung  = args.format              if args.format               else config['vonBisDarstellung']

    if config['sign'] or args.signature:
        signatureFile      = args.signature           if args.signature         else config['signature']
    else:
        signatureFile = False

    if signatureFile.upper() == 'DEMO':
        signatureFile = os.path.join(path, 'demoSignature.jpg')

    print """
Generating PDF:
    CSV:   {csv}
    PDF:   {outputFilename}
    Jahr:  {jahr}
    Monat: {monat}
    Name:  {name}
    Sign:  {signature}
    """.format(
        csv            = csvFilename,
        jahr           = myYear,
        monat          = myMonth,
        name           = employeeName,
        outputFilename = outputFilename,
        signature      = signatureFile
        )

    myObj = generateZeitaufzeichnungsObj(
        csvFilename       = csvFilename,
        employeeName      = employeeName,
        outputFilename    = outputFilename,
        vonBisDarstellung = vonBisDarstellung,
        signatureFile     = signatureFile
        )

    if signatureFile != False:
        ## Frage ob unterschrieben werden soll
        print """
!!! Please check the generated results and confirm that you want to sign your document !!!
!!! Signature File: {}
""".format(signatureFile)
        answer = raw_input('(y/n): ')
        if answer == 'y':
            print 'Generating PDF...'
            generatePDF(myObj)

        else:
            print 'Aborting... Goodbye!'
            sys.exit()
