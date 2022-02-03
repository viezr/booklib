'''
Repalce chars in string to ascii, clean special characters in text
'''


def chars_to_ascii(string):
    '''
    Replace chars in string to ascii.
    '''
    if not type(string):
        raise TypeError("Value must be string type")

    ss_ext = [("ч", "ch"), ("ш", "sh"), ("щ", "sh"), ("ё", "jo"), ("ж", "zh"),
        ("э", "e"), ("ю", "ju"), ("я", "ja"), ("ъ", ""), ("ь", "")]
    ss = "абвгдезийклмнопрстуфхцы"
    rs = "abvgdezijklmnoprstufhcy"
    for i, sign in enumerate(ss):
        string = string.replace(sign, rs[i])
        string = string.replace(sign.upper(), rs[i].upper())
    for pair in ss_ext:
        string = string.replace(pair[0], pair[1])
        if string.isupper():
            string = string.replace(pair[0].upper(), pair[1].upper())
        else:
            string = string.replace(pair[0].upper(), pair[1].capitalize())
    return string

def clean_with_underscore(string):
    '''
    Replace special charaters and spaces to underscores.
    '''
    for i in " %#@!?$%^&*`,[]():;=+\"\'\\":
        string = string.replace(i, "_")
    while "__" in string:
        string = string.replace("__", "_")
    string = string.strip("_ ")
    return string

def clean_with_space(string):
    '''
    Replace special charaters and underscores to spaces.
    '''
    for i in "_%#@!?$%^&*`,[]();=+\"\'\\":
        string = string.replace(i, " ")
    while "  " in string:
        string = string.replace("  ", " ")
    string = string.strip()
    return string
