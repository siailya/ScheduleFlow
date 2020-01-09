from bot.database.DataBases import UserBase
from bot.stuff.Config import Config as Config
from bot.messages.user.User import User
from bot.messages.console.Console import Console
from bot.messages.сonference.Conference import Conference


class NewMessage:
    def __init__(self, event):
        peer_id = event.obj.message['peer_id']
        if peer_id == Config.CONSOLE:
            Console(event)
        elif peer_id < 2000000000:
            User(event)
            UserBase().IncreaseParameters(peer_id, messages_send=True)
        else:
            Conference(event)