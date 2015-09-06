# -*- coding: utf-8 -*-
"""
Created on Sat May 23 10:17:34 2015

@author: Ricardo
"""

'''
This program use the command pattern to take care of launch any code (function) between try-except 
clauses so we can get any error message and log it properly.
The module to be launched through this program must implement a 'runnable'-called function
'''


import logging
import sys
import datetime

from main import runnable


PATH2LOG = '/home/pi/Desktop/Alfred/vAlfred/Logs/'


try:
    runnable()
except:
    message = sys.exc_info()
    now = datetime.datetime.now()
    filename = '%s-%s-%s.txt' % (now.year, now.month, now.day)
    logging.basicConfig(filename = PATH2LOG + filename, format = '%(asctime)s %(message)s')
    logging.critical(message)
    print ("An unexpected error has been found and the program had to be closed.\n"
           "You can finde more information about it in %s" % (PATH2LOG + filename))
