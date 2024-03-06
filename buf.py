s = set()
for l1 in range(-900,900):
    for l2 in range(l1+1,901):
        A = range(l1, l2 + 1)
        counter = 0 
        lst = []
        flag = False
        for x in range(-100,100):
            for y in range(-100,100):
                f = (not (x in A) or (x**2 <= 81)) and (not(y**2 <= 36) or (y in A)) 
                if f:
                    counter += 1 
                else:
                    flag = True
                    break
            if flag:
                break
        if counter == 200*200:
            s.add(abs(l2-l1))
print(max(s))