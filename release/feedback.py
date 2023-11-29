import codecs

def fb(dcts, file_path, new_file_path):
    feedback_list = []

    for dct in dcts:
        keys = list(dct.keys())
        for i in range(1, len(keys)):
            if dct[keys[i]]['status'] == 'MISSING':
                feedback_list.append([dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['pos'], dct[keys[i]]['delimetr'], dct[keys[i]]['data_type']])

    t = codecs.open(file_path, "r", "utf_8_sig")
    t = ''.join(t)
    t = ' ' + t

    buf = 0
    for k, i in zip(list(feedback_list), range(len(feedback_list))):
        if '.' in k[0]:
            text = k[0] + ' ' + 'Missing'
        else:
            if len(k[1]) == 1:
                text = k[0] + k[1] + ' ' + 'Missing'
            else:
                text = '(' + k[0] + ')' + ' ' + 'Missing'
        if k[4] == 'numbers':
            t = t[:k[2]+buf] + k[3] + text + t[k[2]+buf:]
        else:
            t = t[:k[2]+buf] + text + k[3] + t[k[2]+buf:]
        buf+=len(text)+len(k[3])

        n = t[:k[2]].count("\n")+1
        feedback_list[i][2] = n

    print('New file {} was saved'.format(new_file_path))
    f = open(new_file_path, "w", encoding="utf-8")
    f.write(t)
    f.close()
    
    return feedback_list