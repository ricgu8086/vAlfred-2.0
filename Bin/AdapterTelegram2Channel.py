# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:05:17 2016

@author: Ricardo
"""

import os
import time
from collections import deque

from twx.botapi import TelegramBot, InputFile, InputFileInfo

from AbstractChannel import AbstractChannel


class AdapterTelegram2Channel(AbstractChannel):

    def __init__(self, token, bot_id, my_user):
        self.token = token.strip()
        self.bot_id = int(bot_id)
        self.my_user = int(my_user)

        self.bot = TelegramBot(self.token)
        self.bot.update_bot_info().wait()

        self.queue = deque()
        self.offset = 0  # Needed for the bot.get_updates method to avoid getting duplicate updates

    def send_text(self, text):
        """
        Send a message to the user
        """
        # Removing the wait method will make sending multiple messages faster, of course, however in practice
        # it is too fast. It gives a better UX with the wait
        self.bot.send_message(self.my_user, text).wait()

    def get_user_messages(self):
        """
        Get updates sent to the bot
        """
        # Because many updates can happen in a short interval, we are going to store them in a queue
        # because to stick to the interface we need to return just one update by function call
        updates = self.bot.get_updates(offset=self.offset).wait()
        [self.queue.append(update) for update in updates if (update and update.message.sender.id != self.bot_id)]

        if len(updates):
            # Re-compute the offset
            self.offset = max([elem.update_id for elem in updates]) + 1

        if len(self.queue):
            # Get the oldest element in the queue
            first_update = self.queue.popleft()
            return first_update.message.text, first_update.message.sender.id
        else:
            return None, None

    def send_pic(self, path2pic):

        with open(path2pic, 'rb') as finput:
            file_info = InputFileInfo(os.path.basename(path2pic), finput, 'image/jpeg')
            input_file = InputFile('photo', file_info)
            self.bot.send_photo(self.my_user, input_file)
            time.sleep(0.5)

    def allowed_user(self, user_id):
        return user_id == self.my_user

    def close(self):
        pass

    def flush(self):
        """
        The purpose of this method is to clean the channel at the beginning of the execution.
        This is to fix a known issue with the usr_cmd_finish command that was left in the channel
        and causes the closing of Alfred every execution. This happens because at the beginning,
        self.offset it's initialized to 0 and many of the previous messages are recovered again
        """

        updates = self.bot.get_updates(offset=self.offset).wait()

        if len(updates):
            # Re-compute the offset
            self.offset = max([elem.update_id for elem in updates]) + 1