from parser_part import *
from tree import *
from feedback import *
from modification.abb import *
import os
import json
import codecs

def check_file(txt_path=None, json_path=None, text=False, test=False, visualize=False):    
    if json_path:
        F = open(json_path)
        j = json.load(F)
        paragraph_check = j["Settings"]["CheckNumberList"]
        abb_check = j["Settings"]["CheckAbbreviations"]
        dict_check = j["Settings"]["DetectReference"]
        try:
            add_info = j["Dictionaries"]
        except:
            add_info = None
    else:
        paragraph_check = abb_check = dict_check = True
    if txt_path:
        # name = os.txt_path.basename(txt_path)
        F = codecs.open(txt_path, "r", "utf_8_sig")
        t = ' ' + ''.join(F)
    else:
        return 
    
    if paragraph_check:
        txt = parse(t)
        tree = Make_tree()
        dcts = tree.walk(txt)
        if text:
            print(txt)
        if visualize:
            tree.show()
    else:
       dcts = {} 
    if test:
        return dcts
    else:
        feedback = fb(text=t, dictonaries=dcts)
        feedback2 = abb_finder(text=t, abbs=abb_check, dicts=dict_check,  add_info=add_info)
        dictionary = []
        for i in range(len(feedback)):
            dictionary.append({"TypeError": feedback[i][0],
                                        "ErrorLine": feedback[i][1],
                                        "LineNumber": feedback[i][2],
                                        "Description": feedback[i][3],
                                        "PrevLine": feedback[i][4],
                                        "NextLine": feedback[i][5]})
        for i in range(len(feedback2)):
            dictionary.append({"TypeError": feedback2[i][0],
                                        "ErrorLine": feedback2[i][1],
                                        "LineNumber": feedback2[i][2],
                                        "Description": feedback2[i][3],
                                        "PrevLine": feedback2[i][4],
                                        "NextLine": feedback2[i][5]})
        dictionary = sorted(dictionary, key=lambda x: x["LineNumber"])
        json_object = json.dumps(dictionary, indent=4, ensure_ascii=False)
        with codecs.open("feedback.json", "w") as outfile:
            outfile.write(json_object)
        outfile.close()