# -*- coding: utf-8 -*-
"""
Created on Thu Oct 08 20:51:29 2015

@author: Ricardo
"""

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup
from sys import exit

import json
import os
import subprocess
import time

'''
STEPS
ask user instalation directory
ask user telegram paths and store them in a file in the instalation path
 - telegram-cli
 - tg-server.pub
ask for email login
call setup with the new instalation path
check dependencies and ask for instalation
ask for add watchdog to crontab
'''


#Constants
##########
TELEGRAM_FILE = "telegram-cli"
TG_PARAM_FILE = "tg-server.pub"
CMD_FIND_TELEGRAM = 'find / -name "%s" 2>/dev/null' % TELEGRAM_FILE
CMD_FIND_TG_PARAM = 'find / -name "%s" 2>/dev/null' % TG_PARAM_FILE
PATH2_TELEGRAM_CONFIG = "%s/telegram_config.ini"
PATH_2_EMAIL_CREDENTIALS = "%s/email_credentials.ini"

#Ask user instalation directory
#####################

userhome = os.path.expanduser('~') #Example userhome: /home/pi
default_install_path = userhome + '/programs/vAlfred'
install_path = None

valid_path = False

while not valid_path:
    
    try:
        install_path = raw_input('\nWhere do you want to install Alfred?\nPress <Enter> for default path (' + default_install_path + '): ')
    except EOFError:
        exit()
    
    
    if not len(install_path):
        install_path = default_install_path
    elif install_path.endswith('/'):
        install_path = install_path[:-1]
        
        
    #It is considered valid?
    if not install_path.startswith('/'):
        print ('This is not a valid path. It must be an absolute path (and start with "/")')
    else:
        #Exist? Can be created?
        if os.path.isdir(install_path):
            valid_path = True
        else:
            try:
                os.makedirs(install_path)
                valid_path = True
            except OSError:
                print "Can't access to this path. Please, provide a new one."


print('Chosen path: ' + install_path)




#Get telegram paths and store them in the installation folder
#################################

valid_character = False

while not valid_character:
    
    try:
        answer = raw_input('\nHave you installed Telegram messenger CLI? [Y/N]: ')
    except EOFError:
        exit()
    
    answer = answer.lower()
    
    if answer not in ['yes', 'y', 'no', 'n']:
        print("Please type Y or N")
    elif answer in ['no', 'n']:
        print('Please, first install Telegram messenger CLI and then you can continue this installation\n'
        'You can find more info about this in https://github.com/ricgu8086/vAlfred-2.0#instalation')
        exit()
    else:
        valid_character = True
        

valid_tg_path = False


print("vAlfred will automatically locate all Telegram messenger CLI's relevant files.\nPlease wait...\n")
telegram_available_paths = subprocess.Popen(CMD_FIND_TELEGRAM, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
tg_param_available_paths = subprocess.Popen(CMD_FIND_TG_PARAM, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]        
telegram_available_paths = telegram_available_paths.split('\n')[:-1]
tg_param_available_paths = tg_param_available_paths.split('\n')[:-1]

if not len(telegram_available_paths) or not len(tg_param_available_paths):
    print("Sorry, we were unable to find Telegram messenger CLI's relevant files.\n"
    "Have you properly installed it?\nHave you created the public key (%s)?\n" % (TG_PARAM_FILE))
    exit()

#Binary file
print("We have found Telegram messenger CLI's binary in the following locations: \n" )

for number, line in enumerate(telegram_available_paths, start=1):
    print("%d) %s" % (number, line))
#print("\n%d) Manually specify the location to file '%s'\n" % (len(telegram_available_paths)+1, TELEGRAM_FILE))

valid_option = False

while not valid_option: 

    try:
        option = raw_input ("\nPlease choose one option (in case of doubt, take into account that %s's path usually contains '/tg/bin/'): " % (TELEGRAM_FILE))
    except EOFError:
        exit()    
    option = int(option)-1
    
    if option in range(0,len(telegram_available_paths)):
        valid_option = True
    else:
        print("Sorry, that was not a valid option. Please, try again: ")

#if manual location
if option is len(tg_param_available_paths)+1:
    None #TODO
else:
    path_2_telegram = telegram_available_paths[int(option)]
    
print('Chosen path: ' + path_2_telegram + '\n')

time.sleep(1)

#Public keys
print("We have found your public keys for Telegram messenger CLI in the following locations: \n" )

for number, line in enumerate(tg_param_available_paths, start=1):
    print("%d) %s" % (number, line))
#print("\n%d) Manually specify the location to file '%s'\n" % (len(tg_param_available_paths)+1, TG_PARAM_FILE))
        
valid_option = False
        
while not valid_option: 
    
    try:
        option = raw_input ("\nPlease choose one option (in case of doubt, take into account that %s's path usually contains '/tg/'): " % (TG_PARAM_FILE))
    except EOFError:
        exit()        
    option = int(option)-1
    
    if option in range(0,len(tg_param_available_paths)):
        valid_option = True
    else:
        print("Sorry, that was not a valid option. Please, try again: ")

#if manual location
if option is len(tg_param_available_paths)+1:
    None #TODO
else:
    path_2_tg_param = tg_param_available_paths[int(option)]

print('Chosen path: ' + path_2_tg_param + '\n')

telegram_config = {'path_2_telegram' : path_2_telegram, 'path_2_tg_param' : path_2_tg_param}
PATH2_TELEGRAM_CONFIG = PATH2_TELEGRAM_CONFIG % install_path

try:
    
    with open(PATH2_TELEGRAM_CONFIG, 'w') as f:
        json.dump(telegram_config, f)
        
except:
    
    print('There was an unexpected I/O ERROR. Please check that you have write permissions in %s\n' % (PATH2_TELEGRAM_CONFIG))
        
        

#Ask for email login
#################

'''
try:
    
    with open(PATH_2_EMAIL_CREDENTIALS, 'r') as f:
        credentials['email'] = f.readline()[:-1]  #readline return '\n' character in all but the last line in the file
        credentials['password'] = f.readline()
    
    username, domain = credentials['email'].split('@')
    receiver = username + tag + '@' + domain
    email_capabilities = True
    
except:
    
    email_capabilities = False
'''    
try:
    
    with open(PATH_2_EMAIL_CREDENTIALS, 'w') as f:
        json.dump(telegram_config, f)
        
except:
    
    print('There was an unexpected I/O ERROR. Please check that you have write permissions in %s\n' % (PATH2_TELEGRAM_CONFIG))
        

        
#Project external dependencies

dependencies = {
'picam': 'https://github.com/ashtons/picam.git',
 'pexpect': None #This module can be found on Pypi hence does not need a link
}

'''
setup(
    name='vAlfred-2.0',
    version='2.2.0',
    description='My virtual butler. And soon yours!!',
    long_description='This is a virtual butler that will help you making your house more awesome.',
    keywords='home automation virtual butler raspberry pi iot internet of things',
    author='Ricardo Guerrero Gómez-Olmedo',
    author_email='ricgu8086@gmail.com',
    url='http://ricgu8086.github.io/vAlfred-2.0/',
    license='LGPLv3',
    platforms='Linux',
    py_modules='',  #TODO
    packages=['', ''], #TODO
    package_dir={'mypkg': 'src/mypkg'}, #TODO
    package_data={'mypkg': ['data/*.dat']}, #TODO
    data_files=[('pepito', 'Logs/2015-5-23.txt'),
                ('3rd_notifications', ['3rd_notifications/example_tickets.txt', '3rd_notifications/#example_tickets.txt'])]
    install_requires=dependencies.keys(),
    dependency_links = dependencies.values()
)
'''
#TODO: ¿cogera pepito o cogera Logs?



#Check dependencies and ask for instalation
    
    ## añadir a una lista los comandos que no se pueden importar y luego mostrarlos todos con su url
    ## en plan: ha habido 3 dependencias que no se han podido resolver y son:
'''
for dependency in list_dependencies:
    
    available = False
    
    try:
        importlib.importmodule(dependency)
        available = True
    except ImportError:
        print("Paquete %s no disponible" % dependency)
        
    if not available:
        ask user
 

'''