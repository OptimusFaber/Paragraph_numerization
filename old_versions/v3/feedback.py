import codecs

def fb(dcts, file_path):
    feedback_list = []

    for dct in dcts:
        keys = list(dct.keys())
        for i in range(1, len(keys)):
            if dct[keys[i]]['status'] == 'MISSING':
                feedback_list.append((dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['pos'], dct[keys[i]]['delimetr'], dct[keys[i]]['data_type']))

    t = codecs.open(file_path, "r", "utf_8_sig")
    t = ''.join(t)
    t = ' ' + t

    buf = 0
    for k in list(feedback_list):
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

    new_path = file_path.split('/')
    new_path[-1] = "new_" + new_path[-1]
    new_path = '/'.join(new_path)
    print('New file {} was saved'.format(new_path))
    f = open(new_path, "w", encoding="utf-8")
    f.write(t)
    f.close()
    
    return feedback_list