from bot.Api import Vk
from bot.database.DataBases import UserBase


class Comment:
    def __init__(self, event):
        Vk().ConsoleMessage(f'✏ Коммент от @id{event.obj["from_id"]}({" ".join(list(Vk().UserNameGet(event.obj["from_id"])))}):\n{event.obj["text"]}')


class MessagesDeny:
    def __init__(self, event):
        UserBase().DeleteUser(event.obj["user_id"])
        Vk().ConsoleMessage(f'⛔ @id{event.obj["user_id"]}({" ".join(list(Vk().UserNameGet(event.obj["user_id"])))}) запретил сообщения и был удален из базы!')


class MemberJoin:
    def __init__(self, event):
        user_id = event.obj['user_id']
        Vk().ConsoleMessage(f'🔔 Новый подписчик!\n@id{user_id}({" ".join(list(Vk().UserNameGet(user_id)))}) присоединился к нам!')


class MemberLeave:
    def __init__(self, event):
        user_id = event.obj['user_id']
        Vk().ConsoleMessage(f'🐔 Подписчик пропал...!\n@id{user_id}({" ".join(list(Vk().UserNameGet(user_id)))}) покинул нас...')


