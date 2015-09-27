# -*- coding: utf-8 -*-

import pexpect
import time
import os
import socket
import picam
import unicodedata
import subprocess
from sendmail import sendmail
import threading
import Queue
import glob

# Functions

def toAscii(cad):
    '''
    Convert cad from Unicode to ASCII    
    '''
    
    if isinstance(cad, unicode):
        return unicodedata.normalize('NFKD', cad).encode('ascii','ignore')
    else:
        return cad
        

def sendUserAndConsole(telegram, cad):
    ''' 
    This function send cad to the user and also prints it in the console for debug purposes
    '''

    telegram.sendline(comando_mensaje + cad)
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
        
        time.sleep(5*60)
    
    
    
## Functions


#Constants

PATH_2_IMG = r"/home/pi/Documents/Proyecto_vAlfred2/imagenes_picam/picam.jpg"
PATH_2_TELEGRAM = r"/home/pi/Documents/Proyecto_vAlfred2/tg/bin/telegram-cli" 
PATH_2_TG_PARAM = r"/home/pi/Documents/Proyecto_vAlfred2/tg/tg-server.pub"
PATH_2_EMAIL_CREDENTIALS = r"/home/pi/Documents/Proyecto_vAlfred2/vAlfred/credentials.txt"
PATH_2_3RD_NOTIFICATIONS = r"/home/pi/Documents/Proyecto_vAlfred2/vAlfred/3rd_notifications/*.txt"

SLEEP_COMMAND = "sleepBestiaParda"
BESTIA_PARDA_ADDRESS = "192.168.1.2"
PORT = 55412

smtp_server_address = 'smtp.gmail.com:587' #This is not secret, don't need to be in a separated file
tag = '+vAlfred' #Using this tag allows me to apply specific rules in gmail

#Messages and/or commands
comando_mensaje = "msg Amo_Ricardo "
comando_foto = "send_photo Amo_Ricardo " + PATH_2_IMG

cmd_cierre = "Alfred, retirate"
cmd_apagar = "Alfred, apaga la Bestia Parda"
cmd_encender = "Alfred, enciende la Bestia Parda"
cmd_foto = "Alfred, muestrame lo que ves"
cmd_ayuda = "Alfred, ayuda"
cmd_ip = "Alfred, dime tu ip"
cmd_test = "Alfred, prueba el nuevo comando"

cmd_list = [cmd_cierre, cmd_apagar, cmd_encender, cmd_foto, cmd_ayuda, cmd_ip, cmd_test]


resp_saludo = ur"Hola, amo Ricardo"
resp_despedida = ur"Como usted desee, señor."
resp_no_soportado1 = ur"El comando "
resp_no_soportado2 = ur"Aún no esta soportado."
resp_ejecutado_apagar = ur"Señor, la orden de apagar se ha ejecutado correctamente."
resp_ejecutado_encender = ur"La Bestia Parda se está levantando, señor."
resp_ejecutado_foto = ur"Enseguida, señor. Deme unos segundos."
resp_ayuda = ur"A continuación le mostraré los comandos que tengo disponibles: "
resp_ip = u"Mi IP pública es %s"
resp_notificacion = u"Amo, una aplicación externa ha solicitado enviarle una notificación. La reproduzco a continuación: "

resp_list = [resp_saludo, resp_despedida, resp_no_soportado1, resp_no_soportado2, resp_ejecutado_apagar,
             resp_ejecutado_encender, resp_ejecutado_foto, resp_ayuda, resp_ip, resp_notificacion]

## Constants


                
                
                
def runnable():
    
    ''' SETUP '''
    '''-------'''
    
    flag_cerrar = False
    msj_recibido = u"";
    
    telegram = pexpect.spawn(PATH_2_TELEGRAM + ' -k ' + PATH_2_TG_PARAM)
    sendUserAndConsole(telegram, resp_saludo)
    
    #Reading credentials for email capabilities
    credentials = {'server_address' : smtp_server_address}
    
    with open(PATH_2_EMAIL_CREDENTIALS, 'r') as f:
        credentials['email'] = f.readline()[:-1]  #readline return '\n' character in all but the last line in the file
        credentials['password'] = f.readline()
    
    username, domain = credentials['email'].split('@')
    receiver = username + tag + '@' + domain
    
    #Initializing the module for 3rd process notifications
    notifQueue = Queue.Queue()
    stopNotificationsEvent = threading.Event()
    notificationsThread = threading.Thread(target = process3rdNotifications, args = (notifQueue, stopNotificationsEvent))
    notificationsThread.start()
                
    #TODO Check that a 3rd person cannot send commands. Restrict by user.
    
    ''' LOOP '''
    '''------'''
    
    while not flag_cerrar:
        telegram.expect(["> ", pexpect.TIMEOUT, pexpect.EOF])
        
        telegram.expect(['0m', pexpect.TIMEOUT, pexpect.EOF])
        msj_recibido = telegram.before[0:-2] #el final contiene dos caracteres no imprimibles (basura)
        msj_recibido = toAscii(msj_recibido).lower()
        
        if msj_recibido.startswith("alfred"):
        
        
            if msj_recibido == toAscii(cmd_apagar).lower():
    	
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                except socket.error, msg:
                    resp_error =  'No se ha podido crear el socket. Error' + msg[0] + ' ' + msg[1]
        
                if s is None:
                    sendUserAndConsole(telegram, resp_error)
                else:
                    s.sendto(SLEEP_COMMAND, (BESTIA_PARDA_ADDRESS, PORT))
                    s.close()
                    sendUserAndConsole(telegram, resp_ejecutado_apagar)
                    time.sleep(0.5)
    			
       
            elif msj_recibido == toAscii(cmd_encender).lower():
                os.system("wakeonlan E0:CB:4E:83:91:AB")
                sendUserAndConsole(telegram, resp_ejecutado_encender)
                time.sleep(0.5)
    
    
            elif msj_recibido == toAscii(cmd_foto).lower():
                sendUserAndConsole(telegram, resp_ejecutado_foto)
                
                picture = picam.takePhotoWithDetails(640, 480, 85)
                picture.save(PATH_2_IMG)                   
                
                telegram.sendline(comando_foto)
                telegram.expect(['100', pexpect.TIMEOUT, pexpect.EOF], timeout = 1200)
                telegram.expect(['photo', pexpect.TIMEOUT, pexpect.EOF])
                telegram.expect(['0m', pexpect.TIMEOUT, pexpect.EOF])
                
                
            elif msj_recibido == toAscii(cmd_cierre).lower():
                flag_cerrar = True
            
            
            elif msj_recibido == toAscii(cmd_ayuda).lower():
                
                sendUserAndConsole(telegram, resp_ayuda)
                
                for command in cmd_list:
                    sendUserAndConsole(telegram, command)
                    
    
            elif msj_recibido == toAscii(cmd_ip).lower():
                sendUserAndConsole(telegram, resp_ejecutado_foto) #it seems wrong, but is for reutilization purposes, its ok
                public_ip = subprocess.Popen('curl ifconfig.me', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                #public_ip = subprocess.Popen(['curl', 'ifconfig.me'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                sendUserAndConsole(telegram, resp_ip % public_ip)
                
                
            #This command is just for testing new functionality before being completely integrated 
            #This time the command just send an email
            elif msj_recibido == toAscii(cmd_test).lower():
                sendUserAndConsole(telegram, resp_despedida) #it seems wrong, but is for reutilization purposes, its ok

                subj = 'Amo Ricardo, tengo que comunicarle algo'    
                msg = 'Mensaje enviado desde Alfred'  
                
                res = sendmail(credentials, receiver, subj, msg)
                sendUserAndConsole(telegram, 'Respuesta del motor de correo: ')
                sendUserAndConsole(telegram, '>>> ' + res)
                
            else:
                sendUserAndConsole(telegram, resp_no_soportado1)
                sendUserAndConsole(telegram, msj_recibido)
                sendUserAndConsole(telegram, resp_no_soportado2)
                time.sleep(0.3)
                
        #Let's check if we have any notification to send
        check = True
        
        while check:
            try:
                notif = notifQueue.get_nowait()
                
                sendUserAndConsole(telegram, resp_notificacion)
                sendUserAndConsole(telegram, '>>> ' + notif)
                    
                notifQueue.task_done()
            except:
                check = False
            
                    
                    
    
    ''' END '''
    '''-----'''
    sendUserAndConsole(telegram, resp_despedida)
    telegram.sendline('quit')
    stopNotificationsEvent.set()  
    #The main program automatically waits till all non-daemon threads have finished. Don't need join()


if __name__ == "__main__":
    runnable()