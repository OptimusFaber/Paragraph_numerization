from parser_part import *
from tree import *
from feedback import *
from modification.abb import *
import os
import json
import codecs

def check_file(path, test=False, visualize=False): 
    name = os.path.basename(path)        
    if path.endswith("json"):
        F = open(path)
        t = ' ' + json.load(F)["MAIN"]
    elif path.endswith("txt"):
        t = codecs.open(path, "r", "utf_8_sig")
        t = ' ' + ''.join(t)
    else:
        return 
    
    txt = parse(t)



    # print(txt)

    tree = Make_tree()
    dcts = tree.walk(txt)
    if visualize:
        tree.show()
    if test:
        return dcts
    else:
        new_path = path.replace(name, "fixed_{}".format(name))
        feedback = fb(dcts, t, new_path)
        feedback2 = abb_finder(t)
        # dictionary = dict(zip([i for i in range(len(feedback))], feedback))
        dictionary = {"MAIN":[], "TABLES":[]}
        for i in range(len(feedback)):
            if feedback[i][0] == "TextErrorNumber":
                dictionary["MAIN"].append({"TypeError": feedback[i][0],
                                           "ErrorLine": feedback[i][1],
                                           "LineNumber": feedback[i][2],
                                           "Description": feedback[i][3],
                                           "PrevLine": feedback[i][4],
                                           "NextLine": feedback[i][5]})
            else:
                dictionary["TABLES"].append({"TypeError": feedback2[i][0],
                                             "ErrorLine": feedback2[i][1],
                                             "LineNumber": feedback2[i][2],
                                             "Description": feedback2[i][3],
                                             "PrevLine": feedback2[i][4],
                                             "NextLine": feedback2[i][5]})
        for i in range(len(feedback2)):
            dictionary["MAIN"].append({"TypeError": feedback2[i][0],
                                        "ErrorLine": feedback2[i][1],
                                        "LineNumber": feedback2[i][2],
                                        "Description": feedback2[i][3],
                                        "PrevLine": feedback2[i][4],
                                        "NextLine": feedback2[i][5]})

        feedback = list(map(lambda x: "{}: {} || {} || {} || {} || {}".format(*x), feedback))
        feedback2 = list(map(lambda x: "{}: {} || {} || {} || {} || {}".format(*x), feedback2))
        feedback.extend(feedback2)

        json_object = json.dumps(dictionary, indent=4, ensure_ascii=False)
        with codecs.open("feedback.json", "w") as outfile:
            # json.dump(json_object, outfile, ensure_ascii=False)
            outfile.write(json_object)
        feedback = '\n'.join(feedback)
        f = open("feedback.txt", "w", encoding="utf-8")
        f.write(feedback)
        f.close()