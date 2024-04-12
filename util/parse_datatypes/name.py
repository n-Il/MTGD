from dataclasses import dataclass
@dataclass
class name_token:
    name: str

    def __init__(self,name):
        self.name = name

    def __str__(self):
        s = "name:{}".format(self.name)

    def eval(self,card):
        return self.name.lower() in card["name"]
        
