import colorama


def backColorStr(s, color):
    return f"{color}{s}{colorama.Back.RESET}"


def foreColorStr(s, color):
    return f"{color}{s}{colorama.Fore.RESET}"


def whiteBackStr(s):
    return foreColorStr(backColorStr(s, colorama.Back.WHITE), colorama.Fore.BLACK)


def yellowStr(s):
    return foreColorStr(s, colorama.Fore.YELLOW)


def blueBackStr(s):
    return backColorStr(s, colorama.Back.BLUE)


def greenBackStr(s):
    return backColorStr(s, colorama.Back.GREEN)


def redBackStr(s):
    return backColorStr(s, colorama.Back.RED)


def logError(s):
    print(redBackStr(s))


def lenInBytes(string):
    return len(string.encode("utf-8"))
