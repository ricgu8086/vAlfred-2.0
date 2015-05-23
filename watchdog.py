# -*- coding: utf-8 -*-
"""
Created on Sat May 23 10:09:58 2015

@author: Ricardo
"""


'''
This code, combined with crontab, will help us to monitor and debug the state of our service
It will be ran twice a week. If it finds our service down, it will check the log folder to 
send any founded file to an email address, or if there was no file, it will just notify there
was a crash but it din't produce any log (which will reveal another bug). After that, it will
turn on the service again
'''


import os
import glob
import logging
import datetime



# Constants
PROCESS2MONITOR = 'loggedLaunch.py' #This is the name we will look for
COMMAND = 'ps -ef | grep python' #This system command will show all processes that uses the python interpreter
EXEC_PROCESS = 'python loggedLaunch.py  > /dev/null 2>&1' #This is how we re-invoke that process
EMAIL = '' #We will send notifications to this address
PATH2LOGS = './Logs/*.txt'
PATH2LOG = './Logs/'

# Functions
        
def processIsDown(processName):
    
    ret = os.popen(COMMAND, 'r')
    cad = " ".join(ret.readlines())
    
    if cad.find(processName) != -1:
        print "Process is UP"
        return False
    else:
        print "Process is DOWN"
        return True
        
def findLogs(path):
    '''
    Just some syntactic sugar for non critical function
    '''
    return glob.glob(path)
    
#TODO testear si se quedan bloqueados los ficheros por la funcion logger
def cleanFolder(paths):
    print "Removing old logs"
    [os.remove(path) for path in paths]
    
    
def wakeUpProcess(command):
    print "Process is UP again (watchdog powered)" #I prefer to put this line after the system call
                                                   #but it redirects the standard output so..
    os.system(command)
    
    
#TODO implement
def sendEmail(logs):
    None
    
# Main block

if __name__ == '__main__':
    
    if processIsDown(PROCESS2MONITOR):
        
        now = datetime.datetime.now()
        filename = '%s-%s-%s.txt' % (now.year, now.month, now.day)
        logging.basicConfig(filename = PATH2LOG + filename, format = '%(asctime)s %(message)s', level = logging.INFO)
        logging.info("The watchdog has found the process closed. Now it's turning it on\n")
    
        logs = findLogs(PATH2LOGS)
        sendEmail(logs)
        
        #if len(logs) != 0:
            #cleanFolder(logs)
            
        wakeUpProcess(EXEC_PROCESS)
     