import json


class Joshua:
    def __init__(self, path):
        self.path = path

    def read_data(self):
        with open(self.path, "r", encoding="UTF-8") as f:
            return json.load(f)
        
    def save_data(self, new_data):
        with open(self.path, "w", encoding="UTF-8") as f:
            json.dump(new_data, f, indent=2)




class Jackson:
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, "r", encoding="UTF-8") as f:
            return f.read()
        
    def write(self, text):
        with open(self.path, "a") as f:
            f.write(text)