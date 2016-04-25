# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 14:16:45 2016

@author: Ricardo
"""


from abc import ABCMeta, abstractmethod


class AbstractChannel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def send_text(self, text):
        pass

    @abstractmethod
    def get_user_messages(self):
        pass

    @abstractmethod
    def send_pic(self):
        pass

    @abstractmethod
    def allowed_user(self, user_id):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def flush(self):
        pass