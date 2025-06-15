from datetime import datetime
from colorama import Fore, Style
def log(texte,mode="I"):
    if mode=="I":
        print(f"{str(datetime.now().time())[:-4]}-[INFO] : {texte}")
    elif mode=="W":
        print(Fore.YELLOW + f"{str(datetime.now().time())[:-4]}-[WARNING] : {texte}" + Style.RESET_ALL)
    elif mode=="E":
        print(Fore.RED + f"{str(datetime.now().time())[:-4]}-[ERROR] : {texte}" + Style.RESET_ALL)
