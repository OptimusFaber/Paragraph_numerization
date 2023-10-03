def fb(dct, file_path):
    feedback_list = []

    keys = list(dct.keys())
    for i in range(1, len(keys)):
        if dct[keys[i]]['status'] == 'MISSING':
            feedback_list.append((dct[keys[i]]['name'], dct[keys[i]]['sign'], dct[keys[i]]['pos']))

    t = open(file_path).readlines()
    t = ' ' + ''.join(t)

    buf = 0
    for k in list(feedback_list):
        if '.' in k[0]:
            text = k[0] + ' ' + 'Missng'
        else:
            if len(k[1]) == 1:
                text = k[0] + k[1] + ' ' + 'Missing'
            else:
                text = '(' + k[0] + ')' + ' ' + 'Missing'
        t = t[:k[2]+buf+1] + '\n' + text + '\n' + t[k[2]+1+buf:]
        buf+=len(text)+2
    t=t[1:]
    new_path = file_path.split('/')
    new_path[-1] = "new_" + new_path[-1]
    new_path = '/'.join(new_path)
    print('New file {} was saved'.format(new_path))
    f = open(new_path, "a")
    f.write(t)
    f.close()
    
    return feedback_list



