from parser_part import *
from tree import *
from feedback import *
from modification.abb import *
import os
import json
import codecs

def check_file(txt_path=None, json_path=None, output_path=None, text=False, test=False, visualize=False):    
    if json_path:
        F = open(json_path, encoding='utf-8')
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
        F = codecs.open(txt_path, "r", "utf_8_sig")
        t = ' ' + ''.join(F)
    else:
        return 
    content = None
    if paragraph_check:
        txt = parse(t, txt_path)
        tree = Make_tree()
        dcts = tree.walk(txt, txt_path)
        if text:
            print(txt)
        if visualize:
            tree.show()
        content = tree.content_set
    else:
       dcts = {} 
    if test:
        return dcts
    else:
        feedback = fb(text=t, dictonaries=dcts)
        feedback2 = abb_finder(text=t, abbs=abb_check, dicts=dict_check,  add_info=add_info, content_strings=content, txt_path=txt_path)
        dictionary = []
        if paragraph_check:
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
                                        "NextLine": feedback2[i][5],
                                        "Element": feedback2[i][6]})
        dictionary = sorted(dictionary, key=lambda x: x["LineNumber"])
        json_object = json.dumps(dictionary, indent=4, ensure_ascii=False)

        save_path = "feedback.json"
        if output_path:
            out = re.sub("[/\\]\w*[.]json", "", output_path)
            if os.path.exists(out):
                save_path = output_path

        with codecs.open(save_path, "w", encoding='utf-8') as outfile:
            outfile.write(json_object)
        outfile.close()