from parser_part import *
from tree import *
from feedback import *
from modification.abb import *
import os
import json
import codecs
from modification.sentence_compare import *
from modification.report import *

def check_file(txt_path=None, json_path=None, report_output=None, output_path=None, text=False, test=False, visualize=False):    
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
        t = json.load(F)
        F.close()
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
        feedback = fb(dictonaries=dcts)
        feedback2 = abb_finder(text=t, abbs=abb_check, dicts=dict_check,  add_info=add_info, content_strings=content, txt_path=txt_path)
        feedback.extend(feedback2)
        dictionary =  {}
        for i in range(len(feedback)):
            if not dictionary.get(feedback[i][2]):
                dictionary[feedback[i][2]] = [{"ErrorType": feedback[i][0],"Description": feedback[i][1], "Element": feedback[i][3]}]
            else:
                dictionary[feedback[i][2]].append({"ErrorType": feedback[i][0],"Description": feedback[i][1], "Element": feedback[i][3]})


        F = codecs.open(txt_path, "r", "utf_8_sig")
        t = json.load(F)
        report = []
        for elem in t.keys():
            if elem == 'Paragraphs':
                for e in range(len(t[elem])):
                    if t[elem][e]['Index'] in dictionary.keys():
                        t[elem][e]['Errors'] = dictionary[t[elem][e]['Index']]
                        report.append({"Error": dictionary[t[elem][e]['Index']][0]["Description"],
                                               "Feedback": dictionary[t[elem][e]['Index']][0]["ErrorType"]})
                    else:
                        t[elem][e]['Errors'] = None

                    if t[elem][e]['Entities']:
                        for j in range(len(t[elem][e]['Entities'])):
                            mistake = compare_single_text(t[elem][e]['Entities'][j])
                            if mistake:
                                if t[elem][e]['Errors']:
                                    t[elem][e]['Errors'].append(mistake)
                                else:
                                    t[elem][e]['Errors'] = [mistake]
                                report.append({"Error": "Неверные сущности",
                                               "Feedback": t[elem][e]['Entities'][j]})
                        
            elif elem == 'Tables':
                for e in range(len(t[elem])):
                    for cell in range(len(t[elem][e]['Rows'])):
                        for c in range(len(t[elem][e]['Rows'][cell]['Cells'])):
                            if t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Index'] in dictionary.keys():
                                t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Errors'] = dictionary[t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Index']]
                                report.append({"Error": dictionary[t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Index']][0]["Description"],
                                               "Feedback": dictionary[t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Index']][0]["ErrorType"]})
                            else:
                                t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Errors'] = None
                            
                            if t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Entities']:
                                for j in range(len(t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Entities'])):
                                    mistake = compare_single_text(t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Entities'][j])
                                    if mistake:
                                        if t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Errors']:
                                            t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0].append(mistake)
                                        else:
                                            t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0] = [mistake]
                                        report.append({"Error": "Неверные сущности",
                                                       "Feedback": t[elem][e]['Rows'][cell]['Cells'][c]["Paragraphs"][0]['Entities'][j]})
                        
        generate(dict_list=report, output_pdf=report_output)

        json_object = json.dumps(t, indent=4, ensure_ascii=False)

        save_path = "feedback.json"
        if output_path:
            out = re.sub("[/\\]\w*[.]json", "", output_path)
            if os.path.exists(out):
                save_path = output_path

        with codecs.open(save_path, "w", encoding='utf-8') as outfile:
            outfile.write(json_object)
        outfile.close()