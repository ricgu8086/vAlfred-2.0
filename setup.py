# -*- coding: utf-8 -*-
"""
Created on Thu Oct 08 20:51:29 2015

@author: Ricardo
"""

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

'''
STEPS
ask user instalation directory
ask user telegram directory
 - try to find telegram-cli
 - try to find tg-server.pub
call setup with the new instalation path
store telegram paths in a file in the instalation path
check dependencies and ask for instalation
ask for add watchdog to crontab
'''

#Constants
##########


#ask user instalation directory
non_valid_path = True

while non_valid_path:
    try:
        install_path = raw_input('Where do you want to install Alfred? (example: /home/user/programs/alfred) <Enter> for default path')
    except EOFError:
        return
    
    if install_path taltal:
        non_valid_path = False
    else:
        print "This path was incorrect. Please, provide a new one."

¿existe la carpeta? ¿se puede crear?

#Project external dependencies
dependencies = 
[

]

setup(
    name='vAlfred-2.0',
    version='2.2.0',
    description='My virtual butler. And soon yours!!',
    long_description='', #TODO
    keywords='', #TODO
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
    install_requires=dependencies,
)

#TODO: ¿cogera pepito o cogera Logs?

# store telegram paths in a file in the instalation path
    
try:
    
    with open(PATH_2_EMAIL_CREDENTIALS, 'r') as f:
        credentials['email'] = f.readline()[:-1]  #readline return '\n' character in all but the last line in the file
        credentials['password'] = f.readline()
    
    username, domain = credentials['email'].split('@')
    receiver = username + tag + '@' + domain
    email_capabilities = True
    
except:
    
    email_capabilities = False
        
    
#check dependencies and ask for instalation
for dependency in list_dependencies:
    
    available = False
    
    try:
        importlib.importmodule(dependency)
        available = True
    except ImportError:
        print("Paquete %s no disponible" % dependency)
        
    if not available:
        ask user
 
