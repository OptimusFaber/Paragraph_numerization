import re


def printRoman(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90,
           100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL",
           "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12

    while number:
        div = number // num[i]
        number %= num[i]

        while div:
            print(sym[i], end="")
            div -= 1
        i -= 1


t = ' ' + input()

f_elem = True

while t and f_elem:

    dot = re.search(r"(((\W[a-zA-Z])|(\d))[.])|((\d)+[.])+", t)
    bracket = re.search(r"((\W[a-zA-Z])|(\d))[)]", t)

    # t = re.sub('([a-zA-Z]|[\d])[.]([a-zA-Z]|[\d])+', '' ,t)

    if dot and bracket:
        f_elem = ')' if bracket.span()[0] < dot.span()[0] else '.'
        pos = min(bracket.span()[1]-1, dot.span()[1]-1)
    elif dot:
        f_elem = '.'
        pos = dot.span()[1]-2
    elif bracket:
        f_elem = ')'
        pos = bracket.span()[1]-2
    else:
        f_elem = None

    # f_elem это главная нумерация типа
    if f_elem:
        if not t[pos].isdigit():
            idx = pos
            paragraph = t[pos]
        else:
            idx = pos
            paragraph = t[pos]
            while t[pos - 1].isdigit():
                paragraph = t[pos - 1] + paragraph
                if pos == 0:
                    break
                pos -= 1
            pos = idx + 1
            if t[pos] == '.':
                paragraph += '.'
                while t[pos + 1].isdigit() or t[pos + 1] == '.':
                    paragraph += t[pos + 1]
                    pos += 1
                if t[pos + 1] == ')':       # Ситуация по типу: 2)Не забудь купить соли килограмма 3.3)...
                                            # или по типу: 2)Не помню какое напряжение было 1.2 или 2.1. 3)
                                            # Короче каждый раз нужна проверка. Ченить придумаем
                idx = pos

        t = t[idx+2:]
        print(t)
        print(paragraph, f_elem)
        print('--------------------')
