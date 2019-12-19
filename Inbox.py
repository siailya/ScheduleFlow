import vk_api.vk_api

from Console import Console
from Process import *
from User import User


class Inbox:
    def __init__(self, session, event, base):
        self.db = base
        self.vk = session
        self.upload = vk_api.VkUpload(self.vk)
        self.vk_api = self.vk.get_api()
        self.peer_id = event.obj.peer_id

        if self.peer_id == cst.console_id:
            Console(self.vk_api, event, self.db, self.vk)
        elif self.peer_id < 2000000000:
            self.vk_api.messages.markAsRead(peer_id=self.peer_id)
            User(self.vk, event, self.db)
        else:
            pass
