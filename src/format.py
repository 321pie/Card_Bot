from colorama import Fore, Back, Style

def error(message):
    return Fore.RED + "ERROR: " + Fore.RESET + message

def warning(message):
    return Fore.YELLOW + "WARNING: " + Fore.RESET + message