# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:04:40 2015

@author: Ricardo Guerrero Gómez-Olmedo
"""

import smtplib

    
def sendmail(credentials, receiver, subject, message):
    '''
    This function abstract the task of sending an email using the SMTP protocol.
    It works perfect with gmail.

    Parameters
    ----------
    credentials : dict
        This dictionary contains the necessary parameters to log in the sender server, i.e.:
        email, password and server_address (ip:port).
    receiver : string
        The email address that will receive this email.
    subject: string
        The subject of the email.
    message: string
        The content (text) of the email.

    Returns
    -------
    _ : string
        Returns the result of the operation. If it was possible to send the email or not.
    '''

    # Email addresses
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
        return "Failed to send the email\n"
            
    
    
