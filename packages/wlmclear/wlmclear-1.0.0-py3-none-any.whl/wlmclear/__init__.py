import platform, os
def clean():
    os.system("cls" if platform.system().lower().startswith("win") else "clear")
