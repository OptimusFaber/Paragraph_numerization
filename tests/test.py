import sys
sys.path.append("./release")
from check import check_file

def test1():
    lost = []
    dcts = check_file("test1.txt", test=True)
    for dct in dcts:
        for key in list(dct.keys())[1:]:
            if dct[key]["status"] == "MISSING":
                lost.append(dct[key]["name"])
    assert lost == ['2', '2', 'I', '4']

def test2():
    lost = []
    dcts = check_file("test2.txt", test=True)
    for dct in dcts:
        for key in list(dct.keys())[1:]:
            if dct[key]["status"] == "MISSING":
                lost.append(dct[key]["name"])
    assert lost == ['c', '2', '3', 'c', 'II', '2']

def test3():
    lost = []
    dcts = check_file("test3.txt", test=True)
    for dct in dcts:
        for key in list(dct.keys())[1:]:
            if dct[key]["status"] == "MISSING":
                lost.append(dct[key]["name"])
    assert lost == ['1.2', '1.3', '2.2.1', '3']
