

class PrintHelper:

    def __init__(self, space_name):
        self.name = space_name
        self.msg_len =10

    def debug_if(self, enable=True,
              msg=''):
        if enable: self.debug(msg)

    def debug(self, msg):
        title = "DEBUG:"
        print(f"{title.ljust(self.msg_len, ' ')}{self.name} {msg}")

    def info_if(self, enable=True,
              msg=''):
        if enable: self.info(msg)

    def info(self, msg):
        title = "INFO:"
        print(f"{title.ljust(self.msg_len, ' ')}{self.name} {msg}")

    def wrn(self, msg):
        title = "WARNING:"
        print(f"{title.ljust(self.msg_len, ' ')}{self.name} {msg}")

    def alert(self, msg):
        title = "ALERT:"
        print(f"{title.ljust(self.msg_len, ' ')}{self.name} {msg}")

    def error(self, msg):
        title = "ERROR:"
        print(f"{title.ljust(self.msg_len, ' ')}{self.name} {msg}")
