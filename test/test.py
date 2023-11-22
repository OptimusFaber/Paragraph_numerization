from release.check import check_file

def test1():
    result = check_file("test1.py", test=True)
    assert len(result) == 