# -*- coding: utf-8 -*-

"""


@author: Ricardo Guerrero Gómez-Olmedo
"""

import glob
import os
import picam
import Queue
import socket
import subprocess
import time
import threading
import unicodedata

from AdapterTelegram2Channel import AdapterTelegram2Channel
from sendmail import sendmail


# Current Working Directory
CWD = os.path.dirname(os.path.abspath(__file__)) + '/'

# Constants
##########

PATH_2_IMG = CWD + "Picam/img_picam.jpg"
PATH_2_EMAIL_CREDENTIALS = CWD + "Credentials/email_credentials.ini"
PATH_2_BOT_CREDENTIALS = CWD + "Credentials/bot_credentials.ini"
PATH_2_3RD_NOTIFICATIONS = CWD + "3rd_notifications/*.txt"

BESTIA_PARDA_ADDRESS = "192.168.1.2"
PORT = 55412

smtp_server_address = 'smtp.gmail.com:587'  # This is not secret, don't need to be in a separated file
tag = '+vAlfred'  # Using this tag allows me to apply specific rules in gmail

PERIOD_CHECK_NOTIF = 5 * 60

# Messages and/or commands
cmd_message = "msg Amo_Ricardo "
cmd_pic = "send_photo Amo_Ricardo " + PATH_2_IMG
cmd_finish = "quit"
cmd_on = "wakeonlan E0:CB:4E:83:91:AB"
cmd_pc_off = "sleepBestiaParda"

usr_cmd_finish = "Alfred, retirate"
usr_cmd_pc_off = "Alfred, apaga la Bestia Parda"
usr_cmd_pc_on = "Alfred, enciende la Bestia Parda"
usr_cmd_pic = "Alfred, muestrame lo que ves"
usr_cmd_help = "Alfred, ayuda"
usr_cmd_ip = "Alfred, dime tu ip"
usr_cmd_test = "Alfred, prueba el nuevo comando"

usr_cmd_list = [usr_cmd_finish, usr_cmd_pc_off, usr_cmd_pc_on, usr_cmd_pic, usr_cmd_help, usr_cmd_ip, usr_cmd_test]

usr_resp_welcome = ur"Hola, amo Ricardo"
usr_resp_bye = ur"Como usted desee, señor."
usr_resp_unsupported1 = ur"El comando "
usr_resp_unsupported2 = ur"aún no esta soportado. Le sugiero probar con: " + usr_cmd_help
usr_resp_pc_off = ur"Señor, la orden de apagar se ha ejecutado correctamente."
usr_resp_pc_on = ur"La Bestia Parda se está levantando, señor."
usr_resp_pic = ur"Enseguida, señor. Deme unos segundos."
usr_resp_help = ur"A continuación le mostraré los comandos que tengo disponibles: "
usr_resp_ip = u"Mi IP pública es %s"
usr_resp_notif = u"Amo, una aplicación externa ha solicitado enviarle una notificación. La reproduzco a continuación: "
usr_resp_sock_error = "No se ha podido crear el socket. Error %s %s"
usr_resp_email_error = "El fichero de credenciales no se ha podido leer correctamente en la ruta: %s . Por favor, revisela" % PATH_2_EMAIL_CREDENTIALS
usr_resp_unknown_user = "Ang aking unang bot" # Means "My first bot" in Tagalo language, to disorient people

usr_resp_list = [usr_resp_welcome, usr_resp_bye, usr_resp_unsupported1, usr_resp_unsupported2, usr_resp_pc_off,
                 usr_resp_pc_on, usr_resp_pic, usr_resp_help, usr_resp_ip, usr_resp_notif, usr_resp_sock_error,
                 usr_resp_email_error, usr_resp_unknown_user]


## Constants


# Functions
###########

def to_ascii(msg):
    '''
    Convert msg from Unicode to ASCII
    '''

    if isinstance(msg, unicode):
        return unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore')
    else:
        return msg


def sendUserAndConsole(channel, msg):
    ''' 
    This function send msg to the user and also prints it in the console for debug purposes
    '''

    channel.send_text(msg)
    print to_ascii(msg)


def process3rdNotifications(notifQueue, stopNotificationsEvent):
    '''
    3rd party programs or other independent modules can use Alfred to send notifications to 
    its human lord, just by placing a txt file in PATH_2_3RD_NOTIFICATIONS with their
    correspondent message. This function will be read the directory every 5 minutes.
    
    As we can get race conditions if we try to read files that are in use, we will use the 
    following mechanism: the 3rd party programs need to create an empty file with the same
    name as the intended but starting with '#' which we will call  the lock. Then it will
    create the normal file, and after writing the message and close the file, it will 
    delete the lock. As file creation is an atomic operation we will use this as a signal to
    decide whether consume or not a notification. It's the same procedure LibreOffice uses.
    
    Using files to communicate process seems not the most elegant way, but it allows the 
    easiest bash scripts, matlab's, etc to use Alfred. I'm considering in a future doing some
    experiments with netcat to move on sockets if possible.
    '''

    while not stopNotificationsEvent.is_set():

        files = glob.glob(PATH_2_3RD_NOTIFICATIONS)

        normal_files = [(os.path.basename(elem), elem) for elem in files if not os.path.basename(elem).startswith('#')]
        locked_files = [os.path.basename(elem)[1:] for elem in files if os.path.basename(elem).startswith('#')]
        ready_files = [elem[1] for elem in normal_files if elem[0] not in locked_files]

        for elem in ready_files:
            with open(elem, 'r') as f:
                cad = f.read()
                notifQueue.put(cad)

        [os.remove(elem) for elem in ready_files]

        time.sleep(PERIOD_CHECK_NOTIF)


## Functions


# Alfred
###########

def alfred_unsupported(channel, rec_message):
    sendUserAndConsole(channel, usr_resp_unsupported1)
    sendUserAndConsole(channel, ">>> " + rec_message)
    sendUserAndConsole(channel, usr_resp_unsupported2)
    time.sleep(0.3)


def alfred_test(email_credentials, email_capabilities, receiver, channel):
    '''
    This command is just for testing new functionality before being completely integrated
    This time the command just send an email
    '''

    if email_capabilities:
        sendUserAndConsole(channel, usr_resp_bye)  # it seems wrong, but is for reutilization purposes, its ok

        subject = 'Amo Ricardo, tengo que comunicarle algo'
        msg = 'Mensaje enviado desde Alfred'

        resp = sendmail(email_credentials, receiver, subject, msg)
        sendUserAndConsole(channel, 'Respuesta del motor de correo: ')
        sendUserAndConsole(channel, '>>> ' + resp)
    else:
        sendUserAndConsole(channel, usr_resp_email_error)


def alfred_ip(channel):
    sendUserAndConsole(channel, usr_resp_pic)  # it seems wrong, but is for reutilization purposes, its ok
    public_ip = \
        subprocess.Popen('curl ifconfig.co', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\
        .communicate()[0]
    sendUserAndConsole(channel, usr_resp_ip % public_ip)


def alfred_help(channel):
    sendUserAndConsole(channel, usr_resp_help)
    for command in usr_cmd_list:
        sendUserAndConsole(channel, command)


def alfred_pic(channel):
    sendUserAndConsole(channel, usr_resp_pic)

    picture = picam.takePhotoWithDetails(640, 480, 85)
    picture.save(PATH_2_IMG)

    channel.send_pic(PATH_2_IMG)


def alfred_pc_on(channel):
    os.system(cmd_on)
    sendUserAndConsole(channel, usr_resp_pc_on)
    time.sleep(0.5)


def alfred_pc_off(channel):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error, msg:
        usr_resp_error_aux = usr_resp_sock_error % (msg[0], msg[1])
    if s is None:
        sendUserAndConsole(channel, usr_resp_error_aux)
    else:
        s.sendto(cmd_pc_off, (BESTIA_PARDA_ADDRESS, PORT))
        s.close()
        sendUserAndConsole(channel, usr_resp_pc_off)
        time.sleep(0.5)


def alfred_finish(channel):
    pass

alfred_actions_list = [alfred_finish, alfred_pc_off, alfred_pc_on, alfred_pic, alfred_help, alfred_ip, alfred_test]

## Alfred

# Main thread
#############

def runnable():
    ''' SETUP '''
    '''-------'''

    flag_close = False
    rec_message = u""
    email_capabilities = False

    # Normalizing user available commands
    usr_cmd_list_norm = [to_ascii(cmd).lower() for cmd in usr_cmd_list]

    # Reading credentials for email capabilities
    email_credentials = {'server_address': smtp_server_address}

    try:

        with open(PATH_2_EMAIL_CREDENTIALS, 'r') as f:
            email_credentials['email'] = f.readline().strip()
            email_credentials['password'] = f.readline().strip()

        username, domain = email_credentials['email'].split('@')
        receiver = username + tag + '@' + domain
        email_capabilities = True

    except IOError:
        email_capabilities = False
        
    # Reading credentials for the Telegram's Bot API
    bot_credentials = {}
    
    with open(PATH_2_BOT_CREDENTIALS, 'r') as f:
        bot_credentials['token'] = f.readline().strip()
        bot_credentials['bot_id'] = f.readline().strip()
        bot_credentials['my_user'] = f.readline().strip()

    # Opening the communication channel
    channel = AdapterTelegram2Channel(**bot_credentials)
    channel.flush()
    sendUserAndConsole(channel, usr_resp_welcome)
    
    # Creating map between commands and functions
    actions = dict(zip(usr_cmd_list_norm, alfred_actions_list))

    # Initializing the module for 3rd process notifications
    notifQueue = Queue.Queue()
    stopNotificationsEvent = threading.Event()
    notificationsThread = threading.Thread(target=process3rdNotifications, args=(notifQueue, stopNotificationsEvent))
    notificationsThread.start()

    ''' LOOP '''
    '''------'''

    while not flag_close:
        rec_message, sender_id = channel.get_user_messages()

        if not rec_message:
            continue

        # Reject unknown users
        if not channel.allowed_user(sender_id):
            print(usr_resp_unknown_user)
            channel.send_text(usr_resp_unknown_user)
            # TODO log this
            continue

        rec_message = to_ascii(rec_message).lower()

        if rec_message.find("alfred") != -1:

            if rec_message in actions:
                actions[rec_message](channel)
            else:
                alfred_unsupported(channel, rec_message)

            # Special case
            if rec_message == to_ascii(usr_cmd_finish).lower():
                flag_close = True

        # Let's check if we have any notification to send
        check = True

        while check:
            try:
                notif = notifQueue.get_nowait()

                sendUserAndConsole(channel, usr_resp_notif)
                sendUserAndConsole(channel, '>>> ' + notif)

                notifQueue.task_done()
            except Queue.Empty:
                check = False

    ''' END '''
    '''-----'''
    sendUserAndConsole(channel, usr_resp_bye)
    channel.close()
    stopNotificationsEvent.set()
    # The main program automatically waits till all non-daemon threads have finished. Don't need join()


if __name__ == "__main__":
    runnable()
