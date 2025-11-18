from RUDLeg.core_magic.CodeTemplateAndFunction import manager

def rudleg_create():
    filename = "manager.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(manager)
    print("\033[32mFile manager.py created.\033[0m")

def main():
    rudleg_create()


def hello():
    print("\033[33mHello RUDL!!!\033[0m")


def doc():
    pass


def codes():
    pass