class Comment:
    def __init__(self, event):
        user_id = event.obj


class MessagesDeny:
    def __init__(self, event):
        user_id = event.obj


class MemberJoin:
    def __init__(self, event):
        user_id = event.obj


class MemberLeave:
    def __init__(self, event):
        user_id = event.obj

