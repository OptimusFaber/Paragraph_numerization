from check import check_file

lost = []
res = check_file("D:\\Work\\EasyData\\Paragraph_numerization\\test4.txt", test=True)
for dct in res:
        for key in list(dct.keys())[1:]:
            if dct[key]["status"] == "MISSING":
                lost.append(dct[key]["name"])
print(lost)