# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 11:41:18 2015

These functions downloads and save the weather data from AEMET,METEOCAT
and WUNDERGROUND (not yet). The function needs 1 argument -> the type of
analysis required to be done: 'aemet', 'meteocat'

@author: daniel
"""


"""Libraries"""
import sys
import os
import io
import datetime
import urllib2
import urlparse
import shutil
from copy import deepcopy
from datetime import timedelta
import json

#reload(sys)
#sys.setdefaultencoding('utf-8')

""" Global variables """
global path_res, path_dat, path_data, type_r

""" Read the config file"""
with open('config.json') as data_file:    
    context = json.load(data_file)

print context

""" Type of analysis: first argument """
type_r = sys.argv[1]
print 'Analysis: %s' % type_r


def ws_time(s):
    try:
        time = datetime.datetime.strptime(s, '%d/%m/%Y %H:%M').strftime('%Y%m%d%H%M')
        return time
    except ValueError:
        time = datetime.datetime.strptime(s, '%d/%m/%Y %H:%M:%S').strftime('%Y%m%d%H%M%S')
        return time


def meteocat_time(s, time):
    # We only consider the first element of the given hour  (p.ex. 23:00 - 00:00) and the corrected format is without ':'
    s = s.split(' ')[0]
    hour = s.replace(':', '')
    time = time.strftime('%Y%m%d')
    time = time + hour
    return time


def download(url, fileName=None):
    def getFileName(url, openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(), ''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url, r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r, f)
    finally:
        r.close()

def readListaEstaciones(fileStations):
    # Reading and processing the data
    listLines = []
    fileName = path_dat + fileStations
    if os.path.isfile(fileName):
        f = open(fileName, 'r')
        for line in f:
            # Processing only the correct readed values (no comments: # neither no info)
            if line.find('#') == -1 and len(line) > 5:
                line = line.rstrip()
                values = line.split(',')
                listLines.append(values)
        f.close()

        return listLines
    else:
        sys.exit('readListaEstaciones: El archivo de entrada no puede ser leído')


def readListaEstacionesWeb():
    return


def downloadListaEstacionesAEMET(infoEstaciones):
    # Making data directory
    if os.path.exists(path_data) == False:
        os.makedirs(path_data)

    # Download html files
    for info in infoEstaciones:
        infoName = str(info[0])
        infoCode = str(info[1])
        url = 'http://www.aemet.es/es/eltiempo/observacion/ultimosdatos?k=arn&l='+infoCode+'&w=0&datos=det&x=h24&f=temperatura'
        print 'downloading %s' %infoName
        download(url, path_data+infoName)
    return


def downloadListaEstacionesMeteocat(infoEstaciones, day):
    # Making data directory
    if os.path.exists(path_data) == False:
        os.makedirs(path_data)

    # Download html files, only if the file does not already exist
    for info in infoEstaciones:
        infoName = str(info[0])
        infoCode = str(info[1])
        fileName = path_data + infoName
        if os.path.isfile(fileName) == False:
            url = 'http://www.meteo.cat/observacions/xema/dades?codi='+infoCode+'&dia='+day.strftime('%Y-%m-%d')
            download(url, fileName)
    return


def readEstacionAEMET(name):
    # Open the file
    filename = path_data + name
    print 'reading %s' %filename
    import urllib
    from bs4 import BeautifulSoup

    f = urllib.urlopen(filename)
    html = f.read()
    parsed_html = BeautifulSoup(html)
    if parsed_html.table != None:
        headers = parsed_html.table.thead.get_text()
        headers = headers.split('\n')
        headersList = []
        for header in headers:
            if header != '' and len(header) > 3:
                headersList.append(header)

        values = parsed_html.table.tbody.get_text()
        values = values.split('\n')
        valuesList = []
        for val in values:
            if val != '':
                valuesList.append(val)

        return [headersList, valuesList]
    else:
        return None


def readEstacionMeteocat(name):
    # Open the file
    filename = path_data + name
    #print 'reading %s' %filename
    import urllib
    from bs4 import BeautifulSoup

    f = urllib.urlopen(filename)
    html = f.read()
    parsed_html = BeautifulSoup(html)
    table = parsed_html.find("table", {"class" : "tblperiode"})
    if table != None:
        #Headers
        headers = table.tr.get_text()
        headers = headers.split('\n')
        headersList = []
        for header in headers:
            if header != '' and len(header) > 3:
                headersList.append(header)
        #Values
        valuesList = []
        for row in table.findAll("tr"):
            value_time = row.find("th").text.strip()
            values_val = row.findAll("td")
            if values_val != None and len(values_val) > 1:
                valuesList.append(value_time)
                for val in values_val:
                    valuesList.append(val.get_text())

        return [headersList, valuesList]
    else:
        return None

def windDirection(s):
    # llistes inicials
    listNames = ['Norte', 'Nordeste', 'Este', 'Sudeste', 'Sur', 'Sudoeste', 'Oeste', 'Noroeste']
    listValues = ['0.0', '45.0', '90.0', '135.0', '180.0', '225.0', '270.0', '315.0']
    # Checking the text and return the value
    for name in listNames:
        if name in s:
            position = listNames.index(name)
            return listValues[position]
    return 'NULL'
        

def writeEstacionAEMET(name, code, headersList, valuesList):
    # Making data directory
    if os.path.exists(path_res) == False:
        os.makedirs(path_res)

    # Reading the old file to obtain last written data
    fileName = path_res + name
    print 'writing %s' %fileName
    if os.path.isfile(fileName) and os.path.getsize(fileName) > 0:
        f = open(fileName, 'r')
        for line in f:
            pass
        lastData = line.split(',')[1]
        #lastData = ws_time(lastData) #Canvio el format
        f.close()
    else:
        lastData = 0

    # Creo la llista dels valors de les variables agrupada i ordenada
    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    newValuesList = lol(valuesList, len(headersList))
    newValuesList.reverse()

    # Creo el diccionari inicial de weatherdata
    orderedKeysWeatherDataToCheck = ['V. vien', 'Dir. viento', 'Racha', 'Dir. racha', 'Temp.', 'Humedad', 'Radiacio', 'Presi', 'Prec', 'Nubulositat']
    orderedKeysWeatherData = ['stationId', 'Fecha'] + orderedKeysWeatherDataToCheck
    weatherData = {}
    for keyWeatherData in orderedKeysWeatherData:
        weatherData[keyWeatherData] = ''

    # Per a cada llista de valors
    for values in newValuesList:
        tplc = deepcopy(weatherData)
        tplc['stationId'] = code

        # Trobo en quina posicio estan els valors i els guardo al diccionari (sempre que el valor no sigui null)
        for ele in tplc.keys():
            for header in headersList:
                if ele in header:
                    position = headersList.index(header)
                    if values[position] != u'\xa0':  # si valor no es null el guardo
                        if ele == orderedKeysWeatherData[1]:  # Canvio el format de data
                            tplc[ele] = ws_time(values[position])
                        elif ele == orderedKeysWeatherData[3] or ele == orderedKeysWeatherData[5]: # Canvio el format de direccio del vent
                            tplc[ele] = windDirection(values[position])
                        else:
                            tplc[ele] = values[position]

        # Escric la llista d'aquell ts
        with open(fileName, 'a+') as f:
            # cheking si existeix algun valor no null
            writeData = False
            for keyTC in orderedKeysWeatherDataToCheck:
                if tplc[keyTC] != '':
                    writeData = True
            # Nomes escriu si el temps a escriure es superior al darrer escrit i hi ha algun valor a no null
            currentData = tplc[orderedKeysWeatherData[1]]
            if lastData < currentData and writeData:
                for key in orderedKeysWeatherData:
                    #print  (key + ':' + str(tplc[key]) + ",")
                    f.write(str(tplc[key]) + ",")
                f.write("\n")

    f.close()
    return



def writeEstacionMeteocat(name, code, headersList, valuesList, day):
    # Making data directory
    if os.path.exists(path_res) == False:
        os.makedirs(path_res)

    # Opening the file
    fileName = path_res + name

    # Creo la llista dels valors de les variables agrupada i ordenada
    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    newValuesList = lol(valuesList, len(headersList))
    #newValuesList.reverse()

    # Creo el diccionari inicial de weatherdata
    orderedKeysWeatherDataToCheck = ['VVM', 'DVM', 'VVX', 'DVX', 'TM', 'HRM', 'RS', 'PM', 'PPT', 'Nubulositat']
    orderedKeysWeatherData = ['stationId', 'TU'] + orderedKeysWeatherDataToCheck
    weatherData = {}
    for keyWeatherData in orderedKeysWeatherData:
        weatherData[keyWeatherData] = ''

    # Per a cada llista de valors
    for values in newValuesList:
        tplc = deepcopy(weatherData)
        tplc['stationId'] = code

        # Trobo en quina posicio estan els valors i els guardo al diccionari (sempre que el valor no sigui null)
        for ele in tplc.keys():
            for header in headersList:
                if ele in header:
                    position = headersList.index(header)
                    if values[position] != u'\xa0':  # si valor no es null el guardo
                        if ele == orderedKeysWeatherData[1]:  # Canvio el format de data
                            tplc[ele] = meteocat_time(values[position], day)
                        else:
                            tplc[ele] = values[position]

        # Escric la llista d'aquell ts
        with open(fileName, 'a+') as f:
            # Nomes escriu si el temps a escriure es superior al darrer escrit i hi ha algun valor a no null
            for key in orderedKeysWeatherData:
                #print  (key + ':' + str(tplc[key]) + ",")
                f.write(str(tplc[key]) + ",")
            f.write("\n")

    return



"""
##############################
### Main Weather Data Code ###
##############################
"""


""" AEMET """
if type_r == 'aemet':
    # Paths
    path_res = context[type_r]['path_res']
    path_dat = context[type_r]['path_dat']
    path_data = context[type_r]['path_data']
    path_info = context[type_r]['path_info']
    # Weather stations file    
    fileStations = context[type_r]['file_stations']
    # Init date values
    today = datetime.datetime.now()
    todaydate_aemet = datetime.datetime.strptime(str(today), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
    # File where the information about this code execution is going to be written
    infoFile = path_info + 'aemet_info.txt'
    openFile = io.open(infoFile, 'a', newline = '')
    #openFile.write(unicode(' '+todaydate_aemet+'\n'))
    #openFile.write(unicode(' ------------------------------------------------\n'))
    # Reading estation list from estations.dat
    infoEstaciones = readListaEstaciones(fileStations)
    #openFile.write(unicode(' File Station readed\n'))
    readListaEstacionesWeb()
    #openFile.write(unicode(' Stations readed from AEMET web\n'))
    downloadListaEstacionesAEMET(infoEstaciones)
    #openFile.write(unicode(' Stations Downloaded\n'))
    for info in infoEstaciones:
        infoName = info[0]
        infoCode = info[1]
        #Read the table headers and the table values
        headers_values = readEstacionAEMET(infoName)
        if headers_values != None:
            headersList = headers_values[0]
            valuesList = headers_values[1]
            writeEstacionAEMET(infoName + '.met', infoCode, headersList, valuesList)
        #break
    #openFile.write(unicode(' All Stations successfully treated\n'))
    #openFile.write(unicode(' ------------------------------------------------\n'))
    openFile.close()

elif type_r == 'meteocat':
    # Paths
    path_res = context[type_r]['path_res']
    path_dat = context[type_r]['path_dat']
    
    # Weather stations file    
    fileStations = context[type_r]['file_stations']

    # Init date values
    today = datetime.datetime.now() - timedelta(days=1)
    numDays = today.timetuple().tm_yday
    dayList = [today - datetime.timedelta(days=x) for x in range(0, numDays)]
    dayList.reverse()

    #Open the info file
    todaydate = datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
    #infoFile = info_path + 'meteocat_info.txt'
    #openFile = io.open(infoFile, 'a', newline = '')
    #openFile.write(unicode(' '+ todaydate +'\n'))
    #openFile.write(unicode(' ------------------------------------------------\n'))

    # Reading estation list from estations.dat
    infoEstaciones = readListaEstaciones(fileStations)
    readListaEstacionesWeb()
    # Working (I only consider the current year, and the data one day before today)
    for day in dayList:
        #path_data = path_dat + 'prova/' + day.strftime('%Y%m%d') + '/'
        path_data = path_dat + day.strftime('%Y%m%d') + '/'
        print 'Processing %s' % day.strftime('%Y/%m/%d')
        downloadListaEstacionesMeteocat(infoEstaciones, day)
        for info in infoEstaciones:
            infoName = info[0]
            infoCode = info[1]
            #Read the table headers and the table values
            headers_values = readEstacionMeteocat(infoName)
            if headers_values != None:
                headersList = headers_values[0]
                valuesList = headers_values[1]
                writeEstacionMeteocat(infoName + '.met', infoCode, headersList, valuesList, day)
        #break
    #openFile.write(unicode(' All Stations successfully treated\n'))
    #openFile.write(unicode(' ------------------------------------------------\n'))
    #openFile.close()
else:
    print 'Analysis: %s not allowed' % type

