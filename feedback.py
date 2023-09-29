from roman_numeral import *

def fb(dct):

    feedback_list = {}

    keys = list(dct.keys())
    for i in range(len(keys)):
        root = keys[i].split('/')
        buf = []
        for j in range(i+1, len(keys)):
            alpha = keys[j].split('/')
            if '.' in alpha[-1]:
                alpha[-1] = alpha[-1].replace('.', '')
            if alpha[:-1] == root:
                buf.append(alpha[-1])
                if len(buf) == 1:
                    if buf[0].isdigit():
                        dif = abs(1-int(buf[0]))
                    elif dct[keys[j]]['data_type'] == 'sign':
                        st = None
                        if buf[0].isupper():
                            dif = abs(65-int(buf[0]))
                        else:
                            dif = abs(97-int(buf[0]))
                    elif dct[keys[j]]['data_type'] == 'roman':
                        dif = abs(1-Roman2Num(buf[0]))
                    else:       # for paragraphs 1.2.3.
                        pass
                    if dif != 0:
                            feedback_list[dct[keys[j]]['pos']-len(alpha)+1] = 'MISSING {} PARAGRAPHS'.format(dif)
                else:
                    if buf[-1].isdigit():
                        dif = abs(int(buf[-2])-int(buf[-1])) - 1
                    elif dct[keys[j]]['data_type'] == 'sign':
                        st = None
                        if buf[-1].isupper():
                            dif = abs(ord(buf[-2])-int(buf[-1])) - 1
                        else:
                            dif = abs(ord(buf[-2])-int(buf[-1])) - 1
                    elif dct[keys[j]]['data_type'] == 'roman':
                        dif = abs(Roman2Num(buf[-2])-Roman2Num(buf[-1])) - 1
                    else:       # for paragraphs 1.2.3.
                        pass
                    if dif != 0:
                            feedback_list[dct[keys[j]]['pos']-len(alpha)+1] = 'MISSING {} PARAGRAPHS'.format(dif)
    
    return feedback_list



