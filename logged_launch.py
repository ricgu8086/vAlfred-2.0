# -*- coding: utf-8 -*-
"""
Created on Sat May 23 10:17:34 2015

@author: Ricardo
"""

'''
This program will take care of launch any code between try-except clauses so we can
get any error message and log it properly
'''

import subprocess
import logging
import sys
import datetime

# Constants
EXEC_PROCESS = 'adsfasfa' #This is how we invoke our process
PATH2LOG = './Logs/'


#TODO pendiente de testear si funciona la linea subprocess!!!

try:
    subprocess.call(EXEC_PROCESS)
except:
    message = sys.exc_info()[0]
    
    now = datetime.datetime.now()
    filename = '%s-%s-%s.txt' % (now.year, now.month, now.day)
    logging.basicConfig(filename = PATH2LOG + filename, format = '%(asctime)s %(message)s')
    logging.critical(message)
    
        