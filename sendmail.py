# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:04:40 2015

@author: Ricardo Guerrero Gómez-Olmedo
"""

import smtplib

    
def sendmail(credentials, receiver, subject, message):
    
    #Email addresses
    fromAddr = credentials['email']
    toAddr = receiver
    
    email = '''\From: %s\nTo: %s\nSubject: %s\n\n%s'''% (fromAddr, toAddr, subject, message)
    
    try:
        server = smtplib.SMTP(credentials['server_address'])
        server.ehlo()
        server.starttls()
        server.login(credentials['email'], credentials['password'])
        server.sendmail(fromAddr, toAddr, email)
        server.close()  
        
        return "Email sent successfully\n"
        
    except:
        return  "Failed to send the email\n"
            
    
    
