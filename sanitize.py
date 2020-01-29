def sanitize(string):
    new_string = ""
    for char in string:
        if char.isalnum() or char == " ":
            new_string += char

    return new_string.lower().strip('\n')

if __name__ == "__main__":
    print(sanitize("!%^^!#&#!^#&!^#&!#ur mom haha\n&$*# 7"))
    print(sanitize("$&@^@&^#&@^#^#@&#^&$^&@^&@^#&@#"))
    print(sanitize("WHerE Are U AT@#$*??\n\n\n\n\n\n\n\n\nwtf lol\nHAHAHA"))
    print(sanitize(""))
    print(sanitize("@@@@@@@@@@@@"))
