# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:04:40 2015

@author: Ricardo
"""

import smtplib


    
def sendmail():
    
    #Sender credentials
    
    with open('./credentials.txt', 'r') as f:
        username = f.readline()[0:-1] #readline return '\n' character in all but the last line in the file
        password = f.readline() 
    
    #Email addresses
    fromAddr = username
    toAddr = 'soyelrichar+vAlfred@gmail.com'
    
    #Subject
    subj = 'Amo Ricardo, tengo que comunicarle algo'    
    
    #Message
    msg = 'Primer mensaje enviado desde Alfred'
    
    email = '''\From: %s\nTo: %s\nSubject: %s\n\n%s'''% (fromAddr, toAddr, subj, msg)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(fromAddr, toAddr, email)
        server.close()  
        
        print "Email sent successfully"
    except:
        print "Failed to send the email"
        import sys
        print sys.exc_info()
            

if __name__ == "__main__":
    sendmail()
    
    

    
    
