import vk_api.vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll

from Constantes import Constantes as cst


class Session:
    vk = vk_api.VkApi(token=cst.token)
    long_poll = VkBotLongPoll(vk, group_id=cst.group_id)
    vk_api = vk.get_api()
    upload = VkUpload(vk)



