import json
from time import sleep

import apiai as apiai
import vk_api.vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id

from bot.database.DataBases import UserBase
from bot.messages.user.Keyboard import StayHomeKeyboard
from bot.stuff.Config import Config as Config


class Vk:
    def __init__(self):
        self.VkSession = vk_api.VkApi(token=Config.TOKEN)
        self.VkApi = self.VkSession.get_api()
        self.LongPool = VkBotLongPoll(self.VkSession, group_id=Config.GROUP_ID)

    def MessageSend(self, send_id, message=None, attachment=None, keyboard=None):
        self.VkApi.messages.send(peer_id=send_id,
                                 message=message,
                                 random_id=get_random_id(),
                                 attachment=attachment,
                                 keyboard=keyboard)
        if send_id < 2000000000:
            UserBase().IncreaseParameters(send_id, messages_received=True)

    def CheckOnline(self, user_id):
        info = self.VkApi.users.get(user_ids=user_id, fields=['online'])
        return info

    def ConsoleMessage(self, message):
        self.MessageSend(Config.CONSOLE, message)

    def UploadAttachmentPhoto(self, photo):
        upload = VkUpload(self.VkSession)
        response = upload.photo_messages(photo)[0]
        return f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'

    def UserNameGet(self, user_id):
        info = self.VkApi.users.get(user_ids=user_id)[0]
        return info['first_name'], info['last_name']

    def SetActivity(self, peer_id):
        self.VkApi.messages.setActivity(type='typing',
                                        peer_id=peer_id,
                                        group_id=Config.GROUP_ID)

    def SetOnline(self):
        self.VkApi.groups.enableOnline(group_id=Config.GROUP_ID)

    def ManyMessagesSend(self, user_ids, message=None, attachment=None, keyboard=None):
        if len(user_ids) > 100:
            for i in range(len(user_ids) // 100 + 1):
                self.VkApi.messages.send(user_ids=user_ids[i * 100: 100 * (i + 1)],
                                         message=message,
                                         random_id=get_random_id(),
                                         attachment=attachment,
                                         keyboard=keyboard)
        else:
            self.VkApi.messages.send(user_ids=user_ids,
                                     message=message,
                                     random_id=get_random_id(),
                                     attachment=attachment,
                                     keyboard=keyboard)


class DialogFlow:
    def __init__(self):
        self.DialogFLow = apiai.ApiAI(Config.DIALOG_FLOW_TOKEN)

    def SendRequest(self, message):
        request = self.DialogFLow.text_request()
        request.lang = 'ru'
        request.session_id = 'SFTest'
        request.query = message
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']
        if response:
            return response
        else:
            return 'Я тебя не понимаю, прости'
