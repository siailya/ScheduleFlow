import vk_api.vk_api

from Base import write_base
from Console import Console
from Process import *
from User import User


class Inbox:
    def __init__(self, session, event, base, stat):
        self.base = base
        self.stat = stat
        self.vk = session
        self.upload = vk_api.VkUpload(self.vk)
        self.vk_api = self.vk.get_api()
        self.peer_id = event.obj.peer_id

        if self.peer_id == cst.console_id:
            Console(self.vk_api, event, self.base, self.stat)
        else:
            User(self.vk, event, self.base, self.stat)

        write_base(self.base, self.stat)

