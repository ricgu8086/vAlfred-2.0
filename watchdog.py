# -*- coding: utf-8 -*-
"""
Created on Sat May 23 10:09:58 2015

@author: Ricardo
"""


'''
This code, combined with crontab, will help us to monitor and debug the state of our service
It will be run twice a week. If it finds our service down, it will turn up, check the log folder
and if it found any file, it will send it to a specified mail, else, it will just notify there
was a crash but it doesn't produce any log (which will reveal another bug)
'''


import os

# Constants
PROCESS2MONITOR = '' #This is the name we will find in ls command
EXEC_PROCESS = '' #This is how we re-invoke that process
EMAIL = '' #We will send notifications to this address
PATH2LOGS = '' #This is the folder where logs will be stored


if isDown(PROCESS2MONITOR):
    logs = findLogs()
    sendEmail(logs)
    
    if logs != None:
        cleanFolder(PATH2LOGS)
        
        
        
def isDown(name):
    
    