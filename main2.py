from tree import *
from parser_part import *
from feedback import *

txt = parse('/home/titan/Documents/example.txt')

t = Make_tree()
dct = t.walk(txt)

t.show()

res = fb(dct)
res = dict(sorted(list(res.items()), key=lambda x: x[0]))
print(res)
t = open('/home/titan/Documents/example.txt').readlines()
t = ' ' + ''.join(t)

buf = 0
for k in list(res.keys()):
    t = t[:k+buf+1] + '\n' + res[k] + '\n' + t[k+1+buf:]
    buf+=len(res[k])+1
t=t[1:]

f = open("/home/titan/Documents/new_example.txt", "a")
f.write(t)
f.close()