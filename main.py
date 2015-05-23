# -*- coding: utf-8 -*-

import pexpect
import time
from os import system
import socket
import picam
import unicodedata
import subprocess

# Funciones
'''Convert cad from unicode to ascii'''
def toAscii(cad):
    if isinstance(cad, unicode):
        return unicodedata.normalize('NFKD', cad).encode('ascii','ignore')
    else:
        return cad
        
''' This function send cad to the user and also prints it in the console for debug purpose'''
def sendUserAndConsole(cad):
    telegram.sendline(comando_mensaje + cad)
    print toAscii(cad)
## Funciones


#Constantes

PATH_2_IMG = u"/home/pi/Documents/Proyecto_vAlfred2/imagenes_picam/picam.jpg"
PATH_2_TELEGRAM = u"/home/pi/Documents/Proyecto_vAlfred2/tg/bin/telegram-cli" 
PATH_2_TG_PARAM = u"/home/pi/Documents/Proyecto_vAlfred2/tg/tg-server.pub"

SLEEP_COMMAND = "sleepBestiaParda"
BESTIA_PARDA_ADDRESS = "192.168.1.2"
PORT = 55412


#mensajes y/o comandos
comando_mensaje = "msg Amo_Ricardo "
comando_foto = "send_photo Amo_Ricardo " + PATH_2_IMG

cmd_cierre = "Alfred, retirate"
cmd_apagar = "Alfred, apaga la Bestia Parda"
cmd_encender = "Alfred, enciende la Bestia Parda"
cmd_foto = "Alfred, muestrame lo que ves"
cmd_ayuda = "Alfred, ayuda"
cmd_ip = "Alfred, dime tu ip"

resp_saludo = ur"Hola, amo Ricardo"
resp_despedida = ur"Como usted desee, señor."
resp_no_soportado1 = ur"El comando "
resp_no_soportado2 = ur" Aún no esta soportado."
resp_ejecutado_apagar = ur"Señor, la orden de apagar se ha ejecutado correctamente."
resp_ejecutado_encender = ur"La Bestia Parda se está levantando, señor."
resp_ejecutado_foto = ur"Enseguida, señor. Deme unos segundos."
resp_ayuda = ur"A continuación le mostraré los comandos que tengo disponibles: "
resp_ip = u"Mi IP pública es %s"

## Constantes


def runnable():
    flag_cerrar = False
    msj_recibido = u"";
    
    telegram = pexpect.spawn(PATH_2_TELEGRAM + ' -k ' + PATH_2_TG_PARAM)
    sendUserAndConsole(resp_saludo)
    
    #TODO Cuidao que alguien de fuera puede enviar los comandos aunque no tenga permiso. Hay que restringirlo por usuario
    
    while not flag_cerrar:
        telegram.expect(["> ", pexpect.TIMEOUT])
        
        telegram.expect(['0m', pexpect.TIMEOUT])
        msj_recibido = telegram.before[0:-2] #el final contiene dos caracteres no imprimibles (basura)
        msj_recibido = toAscii(msj_recibido).lower()
        
        if msj_recibido.startswith("alfred"):
        
            if msj_recibido == toAscii(cmd_apagar).lower():
    	
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                except socket.error, msg:
                    resp_error =  'No se ha podido crear el socket. Error' + msg[0] + ' ' + msg[1]
        
                if s is None:
                    sendUserAndConsole(resp_error)
                else:
                    s.sendto(SLEEP_COMMAND, (BESTIA_PARDA_ADDRESS, PORT))
                    s.close()
                    sendUserAndConsole(resp_ejecutado_apagar)
                    time.sleep(0.5)
    			
            elif msj_recibido == toAscii(cmd_encender).lower():
                system("wakeonlan E0:CB:4E:83:91:AB")
                sendUserAndConsole(resp_ejecutado_encender)
                time.sleep(0.5)
    
            elif msj_recibido == toAscii(cmd_foto).lower():
                sendUserAndConsole(resp_ejecutado_foto)
                
                picture = picam.takePhotoWithDetails(640, 480, 85)
                picture.save(PATH_2_IMG)                   
                
                telegram.sendline(comando_foto)
                telegram.expect(['100', pexpect.TIMEOUT], timeout = 1200)
                telegram.expect(['photo', pexpect.TIMEOUT])
                telegram.expect(['0m', pexpect.TIMEOUT])
                
            elif msj_recibido == toAscii(cmd_cierre).lower():
                flag_cerrar = True
            
            elif msj_recibido == toAscii(cmd_ayuda).lower():
                sendUserAndConsole(resp_ayuda)
                sendUserAndConsole(cmd_cierre)
                sendUserAndConsole(cmd_apagar)
                sendUserAndConsole(cmd_encender)
                sendUserAndConsole(cmd_foto)
                sendUserAndConsole(cmd_ayuda)
                sendUserAndConsole(cmd_ip)
    
            elif msj_recibido == toAscii(cmd_ip).lower():
                sendUserAndConsole(resp_ejecutado_foto) #it seems wrong, but is for reutilizing purpose, its ok
                public_ip = subprocess.Popen('curl ifconfig.me', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                #public_ip = subprocess.Popen(['curl', 'ifconfig.me'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                sendUserAndConsole(resp_ip % public_ip)
                
            else:
                sendUserAndConsole(resp_no_soportado1)
                sendUserAndConsole(msj_recibido)
                sendUserAndConsole(resp_no_soportado2)
                print msj_recibido
                time.sleep(0.3)
    
    sendUserAndConsole(resp_despedida)
    telegram.sendline('quit')


if __name__ == "__main__":
    runnable()