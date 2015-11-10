# -*- coding: utf-8 -*-

"""


@author: Ricardo Guerrero Gómez-Olmedo
"""

import glob
import os
import pexpect
import picam
import Queue
import socket
import subprocess
import time
import threading
import unicodedata

from sendmail import sendmail


# Current Working Directory
CWD = os.path.dirname(os.path.abspath(__file__)) + '/'

# Constants
##########

PATH_2_IMG = CWD + "../imagenes_picam/picam.jpg"
PATH_2_EMAIL_CREDENTIALS = CWD + "credentials.txt"
PATH_2_3RD_NOTIFICATIONS = CWD + "3rd_notifications/*.txt"
PATH_2_TELEGRAM = r"/home/pi/Documents/Proyecto_vAlfred2/tg/bin/telegram-cli"
PATH_2_TG_PARAM = r"/home/pi/Documents/Proyecto_vAlfred2/tg/tg-server.pub"

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
usr_resp_unsupported2 = ur"Aún no esta soportado."
usr_resp_pc_off = ur"Señor, la orden de apagar se ha ejecutado correctamente."
usr_resp_pc_on = ur"La Bestia Parda se está levantando, señor."
usr_resp_pic = ur"Enseguida, señor. Deme unos segundos."
usr_resp_help = ur"A continuación le mostraré los comandos que tengo disponibles: "
usr_resp_ip = u"Mi IP pública es %s"
usr_resp_notif = u"Amo, una aplicación externa ha solicitado enviarle una notificación. La reproduzco a continuación: "
usr_resp_sock_error = "No se ha podido crear el socket. Error %s %s"
usr_resp_email_error = "El fichero de credenciales no se ha podido leer correctamente en la ruta: %s . Por favor, revisela" % PATH_2_EMAIL_CREDENTIALS

usr_resp_list = [usr_resp_welcome, usr_resp_bye, usr_resp_unsupported1, usr_resp_unsupported2, usr_resp_pc_off,
                 usr_resp_pc_on, usr_resp_pic, usr_resp_help, usr_resp_ip, usr_resp_notif, usr_resp_sock_error]


## Constants


# Functions
###########

def toAscii(cad):
    '''
    Convert cad from Unicode to ASCII    
    '''

    if isinstance(cad, unicode):
        return unicodedata.normalize('NFKD', cad).encode('ascii', 'ignore')
    else:
        return cad


def sendUserAndConsole(telegram, cad):
    ''' 
    This function send cad to the user and also prints it in the console for debug purposes
    '''

    telegram.sendline(cmd_message + cad)
    print toAscii(cad)


def process3rdNotifications(notifQueue, stopNotificationsEvent):
    '''
    3rd party programs or other independent modules can use Alfred to send notifications to 
    its human lord, just by placing a txt file in PATH_2_3RD_NOTIFICATIONS with their
    correspondent message. This function will be read the directory every 5 minutes.
    
    As we can get race conditions if we try to read files that are in use, we will use the 
    following mechanism: the 3rd party programs need to create an empty file with the same
    name as the intended but starting with '#' which we will call it the lock. Then it will 
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

def alfred_unsupported(rec_message, telegram):
    sendUserAndConsole(telegram, usr_resp_unsupported1)
    sendUserAndConsole(telegram, rec_message)
    sendUserAndConsole(telegram, usr_resp_unsupported2)
    time.sleep(0.3)


def alfred_test(credentials, email_capabilities, receiver, telegram):
    if email_capabilities == True:
        sendUserAndConsole(telegram, usr_resp_bye)  # it seems wrong, but is for reutilization purposes, its ok

        subject = 'Amo Ricardo, tengo que comunicarle algo'
        msg = 'Mensaje enviado desde Alfred'

        resp = sendmail(credentials, receiver, subject, msg)
        sendUserAndConsole(telegram, 'Respuesta del motor de correo: ')
        sendUserAndConsole(telegram, '>>> ' + resp)
    else:
        sendUserAndConsole(telegram, usr_resp_email_error)


def alfred_ip(telegram):
    sendUserAndConsole(telegram, usr_resp_pic)  # it seems wrong, but is for reutilization purposes, its ok
    public_ip = \
        subprocess.Popen('curl ifconfig.me', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[
            0]
    sendUserAndConsole(telegram, usr_resp_ip % public_ip)


def alfred_help(telegram):
    sendUserAndConsole(telegram, usr_resp_help)
    for command in usr_cmd_list:
        sendUserAndConsole(telegram, command)


def alfred_pic(telegram):
    sendUserAndConsole(telegram, usr_resp_pic)
    picture = picam.takePhotoWithDetails(640, 480, 85)
    picture.save(PATH_2_IMG)
    telegram.sendline(cmd_pic)
    telegram.expect(['100', pexpect.TIMEOUT, pexpect.EOF], timeout=1200)
    telegram.expect(['photo', pexpect.TIMEOUT, pexpect.EOF])
    telegram.expect(['0m', pexpect.TIMEOUT, pexpect.EOF])


def alfred_pc_on(telegram):
    os.system(cmd_on)
    sendUserAndConsole(telegram, usr_resp_pc_on)
    time.sleep(0.5)


def alfred_pc_off(telegram):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error, msg:
        usr_resp_error_aux = usr_resp_sock_error % (msg[0], msg[1])
    if s is None:
        sendUserAndConsole(telegram, usr_resp_error_aux)
    else:
        s.sendto(cmd_pc_off, (BESTIA_PARDA_ADDRESS, PORT))
        s.close()
        sendUserAndConsole(telegram, usr_resp_pc_off)
        time.sleep(0.5)


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
    for cmd in usr_cmd_list:
        cmd = toAscii(cmd).lower()

    # Opening the communication channel
    telegram = pexpect.spawn(PATH_2_TELEGRAM + ' -k ' + PATH_2_TG_PARAM)
    sendUserAndConsole(telegram, usr_resp_welcome)

    # Reading credentials for email capabilities
    credentials = {'server_address': smtp_server_address}

    try:

        with open(PATH_2_EMAIL_CREDENTIALS, 'r') as f:
            credentials['email'] = f.readline()[:-1]  # readline return '\n' character in all but the last line in the file
            credentials['password'] = f.readline()

        username, domain = credentials['email'].split('@')
        receiver = username + tag + '@' + domain
        email_capabilities = True

    except IOError:
        email_capabilities = False

    # Create map between commands and functions
    # TODO


    # Initializing the module for 3rd process notifications
    notifQueue = Queue.Queue()
    stopNotificationsEvent = threading.Event()
    notificationsThread = threading.Thread(target=process3rdNotifications, args=(notifQueue, stopNotificationsEvent))
    notificationsThread.start()

    # TODO Check that a 3rd person cannot send commands. Restrict by user.

    ''' LOOP '''
    '''------'''

    while not flag_close:
        telegram.expect(["> ", pexpect.TIMEOUT, pexpect.EOF])

        telegram.expect(['0m', pexpect.TIMEOUT, pexpect.EOF])
        rec_message = telegram.before[0:-2]  # The last characters are non-printable ones (trash)
        rec_message = toAscii(rec_message).lower()

        if rec_message.startswith("alfred"):

            """
            if rec_message in actions:
                actions[rec_message]()
            else:
                alfred_unsupported(rec_message, telegram)
            """

            if rec_message == usr_cmd_pc_off:
                alfred_pc_off(telegram)


            elif rec_message == usr_cmd_pc_on:
                alfred_pc_on(telegram)


            elif rec_message == usr_cmd_pic:
                alfred_pic(telegram)


            elif rec_message == usr_cmd_finish:
                flag_close = True


            elif rec_message == usr_cmd_help:
                alfred_help(telegram)


            elif rec_message == usr_cmd_ip:
                alfred_ip(telegram)


            # This command is just for testing new functionality before being completely integrated
            # This time the command just send an email
            elif rec_message == usr_cmd_test:
                alfred_test(credentials, email_capabilities, receiver, telegram)

            else:
                alfred_unsupported(rec_message, telegram)

        # Let's check if we have any notification to send
        check = True

        while check:
            try:
                notif = notifQueue.get_nowait()

                sendUserAndConsole(telegram, usr_resp_notif)
                sendUserAndConsole(telegram, '>>> ' + notif)

                notifQueue.task_done()
            except Queue.Empty:
                check = False

    ''' END '''
    '''-----'''
    sendUserAndConsole(telegram, usr_resp_bye)
    telegram.sendline(cmd_finish)
    stopNotificationsEvent.set()
    # The main program automatically waits till all non-daemon threads have finished. Don't need join()


if __name__ == "__main__":
    runnable()
