#!/usr/bin/python
# coding=utf-8
__author__ = 'Vasily.A.Tsilko'
# Python 3 or higher
# 30.01.15

#*********************************************************************************************************
#*********************************************************************************************************
#**                                                                                                     **
#**                                                                                                     **
#** This script receives data from LD250 lightning detector device while this connected to any USB port.** 
#** Next, program calculate spatial coordinates of lightning discharge and stores it with RAW data      **
#** in PostgreSQL database.                                                                             **
#** At the same time, RAW data stores in plain.txt files                                                **
#**                                                                                                     **
#**                                                                                                     **
#*********************************************************************************************************
#*********************************************************************************************************
# Ver. 0.9

# Change Log
# 12.07.15
# 1. Config File format change ( COM port name without numbers)
# 2. Add Device finding method on the Detector.__init__ with automatic program ending if LD250 not 
#    found or not working.
# 3. Completely removed sockets supply.

# 08.04.17
# 1. Database support added.
# 2. In settings.ini file database parameters added.
#

# ToDo
# Need to add statistical counters from periodical Status Sentence


##########################################################################################################
# Initialization #########################################################################################
##########################################################################################################

import datetime         # Module for date and time.
import zlib             # Module for checksum.
import ConfigParser     # Module for ini-file.
import serial           # Module for com-port.
import threading        # Module for timer.
import time	            # module for time delay
import platform         # infrmation about OS and Platform
import os
import psycopg2         # Module for pstgresql
# import math             # Математика для sph
import sph              # module for Geospatial solver 


# -------------------------- Global variables (it's not true, but... ) ----------------------------------
km_in_mile = 1.60934 # Километров в миле

# ------------------------------------------------ Classes ----------------------------------------------

# Class allow work with ini-file settings.
# Required zlib library.
# Interface:
#           ClassIni(address) - constructor, address - address of file with settings.
#           ClassIni.check()  - calculate control sum of ini-file, if control sum is changed then 
#`              return true, else return false.
#           ClassIni.get(section, param) - get parameter from any section of ini-file.
class ClassIni:

    # Initialization. Set CheckSum of ini-file.
    def __init__(self, address):
        # Address of ini-file with settings.
        self.File = address
        # Control sum of ini-file.
        self.CheckSum = zlib.crc32( file(self.File).read() )
        #
        self.config = ConfigParser.ConfigParser()

    # Get checksum for ini-file. If old checksum not equal new return True.
    def check(self):
        if self.CheckSum == zlib.crc32( file(self.File).read() ):
            return False
        else:
            self.CheckSum = zlib.crc32( file(self.File).read() )
            return True

    # Get parameter from some section.
    def get(self, section, param):
        self.config.read(self.File)
        return self.config.get(section, param)

# Settings for detector light.
# Required class ini.
# Required serial library.
# Interface:
#           ClassDetector(ini)   - constructor, ini - file with settings, get settings 
#                                   from ini-file and set settings for detector.
#           ClassDetector.new()  - read settings, if they change then set new settings.
#           ClassDetector.data() - read data from Detector and if data string contains $WIMLI, 
#                                   so this is our data.
class ClassDetector:

    # Get settings from ini.
    def __init__(self, ini):
        # String for data from detector.
        self.Data = ''
        # Forgot ini-file.
        self.Ini = ini
        # Searching LD-250 device on available c0m ports:
        # ----------------------------------------------------------------------------------------------
        self.Com = False
        self.found = False
        if platform.system() == 'Linux':   # This method for Linux only
            for self.i in range(16) :      # first 16 COM ports checked
                try :
                    self.Com = self.Ini.get('Detector', 'Com')  # Read port adress from config file
                    self.Com = self.Com + str(self.i)   
                    self.Com = serial.Serial(self.Com,  timeout = 5)  # Open port with timeout 
                                # (if timeout not defined, program must be wait data from port
                                # unlimited time)
                    self.startTime = time.time()   # note the time
                    while (time.time() - self.startTime) < 5: # Waiting data from device with 5 seconds
                                                                # from each available port
                        try:
                            self.line = self.Com.readline()
                        except Exception:
                            pass
                        if self.line [0:4] == '$WIM': # If Data received then check it for "Our device"
                            self.found = True
                            break 
                    if not self.found:
                        self.Com.close() # If port mute we close it
                        self.Com = False
                except Exception :
                    pass
                if self.found:
                    break      
        # ----------------------------------------------------------------------------------------------
        if self.found:                      
            # Name of lighting detector.
            self.Name = self.Ini.get('Detector', 'Name')
            # Get settings for LD-250. Squelch.
            self.SQ = self.Ini.get('Detector', 'SQ')
            self.Com.write('SQ'+str(self.SQ)+'\n')
            # Get settings for LD-250. Close alarm distance.
            self.CA = self.Ini.get('Detector', 'CA')
            self.Com.write('CA'+str(self.CA)+'\n')
            # Get settings for LD-250. Severe alarm distance.
            self.SA = self.Ini.get('Detector', 'SA')
            self.Com.write('SA'+str(self.SA)+'\n')
            # Get settings for LD-250. Noise beep state.
            self.NB = self.Ini.get('Detector', 'NB')
            self.Com.write('NB'+str(self.NB)+'\n')
            # Get settings for LD-250. Minimum GPS speed.
            self.MS = self.Ini.get('Detector', 'MS')
            self.Com.write('MS'+str(self.MS)+'\n')
            #
            self.Work = self.Ini.get('Detector', 'Work')

    # Read new parameters from ini-file.
    def new(self):
        if self.SQ <> self.Ini.get('Detector','SQ'):
            self.SQ = self.Ini.get('Detector','SQ')
            self.Com.write('SQ'+str(self.SQ)+'\n')
        if self.CA <> self.Ini.get('Detector','CA'):
            self.CA = self.Ini.get('Detector','CA')
            self.Com.write('CA'+str(self.CA)+'\n')
        if self.SA <> self.Ini.get('Detector','SA'):
            self.SA = self.Ini.get('Detector','SA')
            self.Com.write('SA'+str(self.SA)+'\n')
        if self.NB <> self.Ini.get('Detector','NB'):
            self.NB = self.Ini.get('Detector','NB')
            self.Com.write('NB'+str(self.NB)+'\n')
        if self.MS <> self.Ini.get('Detector','MS'):
            self.MS = self.Ini.get('Detector','MS')
            self.Com.write('MS'+str(self.MS)+'\n')
        if self.Work <> self.Ini.get('Detector','Work'):
            self.Work = self.Ini.get('Detector','Work')

    # Get data from detector.
    # If data string contains '$WIMLI' then return string, else return false.
    def data(self):
        self.Data = self.Com.readline()
#        if self.Data[0:6] == '$WIMLI':
        return self.Data
#        else:
#            return False
    
    # Destructor. Need for close serial port
    def __del__(self):
        self.Com.close()

# Settings for saving result data.
# Required datetime library.
# Interface:
#           ClassResult(ini)     - constructor, ini - file with settings.
#           ClassResult.new()    - read settings, if they change then set new settings.
#           ClassResult.save()   - save data from detector to file.
#           ClassResult.reopen() - close and open file with result.
class ClassResult:

    # Get settings from ini-file.
    # Create filename for with data from detector.
    def __init__(self, ini):
        # Forgot ini-file.
        self.Ini = ini
        # Get folder for file with data from detector.
        self.Folder = self.Ini.get('Result','Folder')
        # Get current data for name of file with data from detector.
        self.Date = datetime.date.today().strftime('%Y-%m-%d')
        # Name of file with data from detector.
        self.Filename = self.Folder + self.Ini.get('Detector','Name') + '-' + self.Date
        # Descriptor of file with data from detector.
        self.File = open( self.Filename , 'a' )
        # Interval of time for reopen file with result (in second).
        self.Interval = int( self.Ini.get('Result','Interval') )
        #
        self.Work = self.Ini.get('Detector','Work')
        #
        self.SaveTimer = threading.Timer(self.Interval, self.reopen)
        self.SaveTimer.start()

    # Get new settings from ini.
    def new(self):
        #
        if self.Folder <> self.Ini.get('Result','Folder'):
            self.Folder = self.Ini.get('Result','Folder')
            self.File.close()
            self.Date = datetime.date.today().strftime('%Y-%m-%d')
            self.Filename = self.Folder + self.Ini.get('Detector','Name') + '-' + self.Date
            self.File = open( self.Filename , 'a' )
        #
        if self.Interval <> int( self.Ini.get('Result','Interval') ):
            self.Interval = int( self.Ini.get('Result','Interval') )
        #
        if self.Work <> self.Ini.get('Detector','Work'):
            self.Work = self.Ini.get('Detector','Work')

    # Save data from detector to file
    def save(self, data, Time):
        #
        self.File.write(Time.strftime('%H:%M:%S') + '.' + str(Time.microsecond) + ',
        ' + data.strip() + '\n')
        if self.Date != datetime.date.today().strftime('%Y-%m-%d'):
            self.Date = datetime.date.today().strftime('%Y-%m-%d')
            self.Filename = self.Folder + self.Ini.get('Detector','Name') + '-' + self.Date
        print (Time.strftime('%H:%M:%S')+'.'+str(Time.microsecond)+', '+ Detector.Data.strip())

    # Reopen file
    def reopen(self):
        self.SaveTimer.cancel()
        self.File.close()
        if self.Date != datetime.date.today().strftime('%Y-%m-%d'):
            self.Date = datetime.date.today().strftime('%Y-%m-%d')
            self.Filename = self.Folder + self.Ini.get('Detector','Name') + '-' + self.Date
        self.File = open(self.Filename, 'a')
        if self.Work == 'True':
            self.SaveTimer = threading.Timer(self.Interval, self.reopen)
            self.SaveTimer.start()

# Settings for saving result data to database PostgreSQL.
# Required psycopg2 library.
# Interface:
#           DataBase()               - constructor, ini - file with settings.
#           DataBase.connect(ini)    - Connecting to database server.
#           DataBase.table_create(name)          - Creating table if it not exists.
#           DataBase.table_print(table) - Read all data from table.
#           DataBase.insert(table, string)               - Inserting data to table.
#           DataBase.SQL(string)                    - SQL query executor.
class DataBase:

    def __init__(self):
        self.con = None

    def connect(self, ini): # Read parameters from .ini file
        self.Ini = ini
        self.dbname = self.Ini.get('Database', 'DBname')
        self.dbuser = self.Ini.get('Database', 'DBuser')
        self.dbpass = self.Ini.get('Database', 'DBpass')
        self.dbhost = self.Ini.get('Database', 'DBhost')
        self.connect_str = ("dbname='" + self.dbname + "' user='" + self.dbuser + "' host='"
        + self.dbhost + "' password='" + self.dbpass + "'")
        try:
            self.con = psycopg2.connect(self.connect_str)  # Connecting to database 
            self.cursor = self.con.cursor()  # Create psycopg2 cursor for queries
            return self.con
        except Exception:
            return self.con

    def table_create(self, name):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS " + name +
            "(time_date TIMESTAMP PRIMARY KEY NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL,"
            " distance_corr INT, distance INT, azimuth REAL)")
        self.con.commit()

    def table_print(self, table):
        self.cursor.execute("SELECT * from " + table)
        self.rows = self.cursor.fetchall()
        for self.row in self.rows:
            print(self.row)

    def insert(self, table, string):
        try:
            self.cursor.execute("INSERT INTO " + table + " VALUES " + string)
            self.con.commit()
        except Exception as e:
            return e

    def SQL(self, string):
        self.cursor.execute(string)
        return self.cursor.fetchall()

    def __del__(self):
        if self.con:
            self.con.close()

# ---------------------------------------------- Functions ----------------------------------------------

# ----------------------------------- Решение прямой геодезической задачи -------------------------------
def geo_direct(lat1, lon1, dist, azi):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    azi = math.radians(azi)
    dist = dist * km_in_mile / sph.a_e
    lat2, lon2 = sph.direct(lat1, lon1, dist, azi)
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2


#########################################################################################################
# Main Program ##########################################################################################
#########################################################################################################

# Initialization class for work with ini file.
cwd = os.getcwd()
Ini = ClassIni(cwd + '/settings.ini')
table_name = Ini.get('Detector','Name')
# Detector coordinates
Lat_ = Ini.get('Detector','Lat')
Lon_ = Ini.get('Detector','Lon')

# Database initialization
DB = DataBase()
DB.connect(Ini)
DB.table_create(table_name)

# Detector initialization
Detector = ClassDetector(Ini)
if not Detector.found:
    print ('Device not found or or does not work')
    time.sleep(5)
    exit(1)
print ('Device found on ',  Detector.Com)

Result = ClassResult(Ini)

print ('LD-250 started')
print (platform.system())

while Detector.Work == 'True':

    # Check ini-file for updates.
    if Ini.check():
        Detector.new()
        Result.new()

    # Read from detector.
    if Detector.data() [0:6] =='$WIMLI':
        time = datetime.datetime.today()
        timestr = time.strftime('%H:%M:%S')+'.'+str(time.microsecond)
        date = datetime.date.today().strftime('%Y-%m-%d')
        Result.save(Detector.Data, time)
        line = Detector.Data.split(",")
        tmp_line = line[3].split("*")
        line[3] = tmp_line[0]
        if (len(line)) > 3:
            date = datetime.date.today().strftime('%Y-%m-%d')
            lat2, lon2 = geo_direct(float(Lat_), float(Lon_), float(line[1]), float(line[3]))
            DB.insert(table_name + " (time_date, latitude, longitude, distance_corr, distance, azimuth)",
                        "('" + date + " " + timestr + "', " + str(lat2) + ", " + str(lon2) + ",
                        " + line[1] + ", " + line[2] + ", " + line[3] + ")")

print ('LD-250 is closed')
Result.SaveTimer.cancel()
