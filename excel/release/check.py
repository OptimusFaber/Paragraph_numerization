from parser_part import *
from tree import *
from feedback import *
from modification.abb import *
import os
import json
from modification.sentence_compare import *

def check_file(excel_path=None, json_path=None, output_path=None, text=False, test=False, visualize=False):    
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
    if excel_path:
        F = open(excel_path, encoding='utf-8')
        t = json.load(F)
    else:
        return 
    content = None
    if paragraph_check:
        dcts = []
        data = parse(t, excel_path)
        for lst in data.values():
            tree = Make_tree()
            dcts.extend(tree.walk(lst, excel_path))
            dcts
            if text:
                print(lst)
            if visualize:
                tree.show()
    else:
       dcts = {} 
    if test:
        return dcts
    else:
        feedback2 = abb_finder(json_text=t, abbs=abb_check, dicts=dict_check,  add_info=add_info, content_strings=content, excel_path=excel_path)
        feedback = fb(text=t, dictonaries=dcts)
        feedback += feedback2
        feedback = dict(zip([feedback[i][2] for i in range(len(feedback))], [feedback[i][:2] for i in range(len(feedback))]))

        if paragraph_check:
            F = open(excel_path, encoding='utf-8')
            t = json.load(F)
            for sheet in t['Worksheets']:
                text = []
                for st in sheet['Rows']:
                    for cl in st['Cells']:
                        if cl['Address'] in feedback.keys():
                            cl['Error'] = feedback[cl['Address']][1]
                            cl['Feedback'] = feedback[cl['Address']][0]
                        if cl['Entities']:
                            ok = compare_single_text(cl['Entities'][0]["document_text"], cl['Entities'][0]["catalog_title"])
                            if ok != True:
                                cl['Error'] = "Incorrect entities"
                                cl['Feedback'] = ok

            save_path = "out.json"
            if output_path:
                out = re.sub("[/\\]\w*[.]json", "", output_path)
                if os.path.exists(out):
                    save_path = output_path

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(t, f, ensure_ascii=False, indent=4)
            
            return save_path

