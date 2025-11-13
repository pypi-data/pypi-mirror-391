class Greeter:
    def __init__(self, name: str):
        if not name:
            raise ValueError('Name cant be empty')
        self.name = name

    def greet(self):
        return f'chào {self.name}, bạn là ai ?'    