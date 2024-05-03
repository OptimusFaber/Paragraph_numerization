import sys
global_path = __file__
global_path = global_path.replace("/check.py", "")
sys.path.append(global_path)
from parser_part import *
from tree import *
from feedback import *
from modification.abb import *
import os
import json
import codecs
from modification.sentence_compare import *
from modification.report import *
from copy import deepcopy

def check_file(json_path=None, config_path=None, report_output=None, json_output=None, global_log_path=None, libre_path='libreoffice', text=False, test=False, visualize=False):    
    print('VERSION 1.7')
    log_path = '/'.join(global_log_path.split('/')[:-1]) + '/myapp.log'
    if log_path=='myapp.log':
        log_path = global_path + '/' + log_path

    if os.path.exists(log_path):
        os.remove(log_path)
    else:
        out_error = '/'.join(log_path.split('/')[:-1])
        if not os.path.exists(out_error):
            log_path = global_path + '/myapp.log'

    if os.path.exists(global_log_path):
        os.remove(global_log_path)
    else:
        out_error = '/'.join(global_log_path.split('/')[:-1])
        if not os.path.exists(out_error):
            sys.exit("Error while creating log file")
    #? CHECKING INPUT CONFIGURATION DIRECTORY
    if config_path:
        try:
            F = open(config_path, encoding='utf-8')
            j = json.load(F)
            paragraph_check = j["Settings"]["CheckNumberList"]
            abb_check = j["Settings"]["CheckAbbreviations"]
            dict_check = j["Settings"]["DetectReference"]
            try:
                add_info = j["Dictionaries"]
            except:
                add_info = None
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: check.py\n%(message)s\nIncorrect Configuration file directory\nConfiguration path: {config_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Wrong config directory!")
    else:
        paragraph_check = abb_check = dict_check = True
    #* CHECKING INPUT-JSON DIRECTORY
    if json_path:
        try:
            F = codecs.open(json_path, "r", "utf_8_sig")
            t = json.load(F)
            F.close()
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: check.py\n%(message)s\nIncorrect text-json file directory\nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Wrong input-json directory!")
    else:
        logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
        format=f'%(asctime)s %(levelname)s module: check.py\nNo text-json file')
        logger=logging.getLogger(__name__)
        # logger.error(err)
        sys.exit("Missing a directory!") 
    content = None

    #! CHECKING OUTPUT-PDF DIRECTORY---------------------------------------------------------------------------------------------------------------
    if report_output:
        report_dir = '/'.join(report_output.split('/')[:-1])
        if not os.path.exists(report_dir):
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s module: check.py\n%(message)s\nOutput directory for pdf-report: {report_output}\n')
            logger=logging.getLogger(__name__)
            logger.error("Incorrect pdf-report file output directory")
            sys.exit("Wrong output-pdf directory!")
    else:
        logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
        format=f'%(asctime)s module: check.py\n(message)s\next path: {json_path}\n')
        logger=logging.getLogger(__name__)
        logger.error("Incorrect pdf-report file output directory")
        sys.exit("Missing a pdf-report directory!")
    #! CHECKING OUTPUT-JSON DIRECTORY--------------------------------------------------------------------------------------------------------------
    if json_output:
        report_dir = '/'.join(json_output.split('/')[:-1])
        if not os.path.exists(report_dir):
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s module: check.py\n%(message)s\nOutput directory for json-report: {json_output}\n')
            logger=logging.getLogger(__name__)
            logger.error("Incorrect pdf-report file output directory")
            sys.exit("Wrong output-json directory!")
    else:
        logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
        format=f'%(asctime)s module: check.py\n%(message)s\nText path: {json_path}\n')
        logger=logging.getLogger(__name__)
        logger.error("Incorrect pdf-report file output directory")
        sys.exit("Missing a pdf-report directory!")
    #!----------------------------------------------------------------------------------------------------------------------------------------------
    if paragraph_check:
        try:
            txt = parse(t, json_path, log_path)
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: parser.py \nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Error while parsimg data!")
        try:
            tree = Make_tree()
            dcts = tree.walk(txt, json_path, log_path)
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: tree.py \nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Error while working with paragraphs!")
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
        try:
            feedback = fb(dictonaries=dcts)
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: fedback.py \nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Error while printing result!")
        try:
            feedback2 = abb_finder(text=t, abbs=abb_check, dicts=dict_check,  add_info=add_info, content_strings=content, json_path=json_path, log_path=log_path)
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: abb.py \nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Error with abbriviations!")
        feedback.extend(feedback2)
        dictionary =  {}
        for i in range(len(feedback)):
            if not dictionary.get(feedback[i][2]):
                dictionary[feedback[i][2]] = [{"Type": feedback[i][0],"Description": feedback[i][1], "Element": feedback[i][4], "TextIndex": feedback[i][3]}]
            else:
                dictionary[feedback[i][2]].append({"Type": feedback[i][0],"Description": feedback[i][1], "Element": feedback[i][4], "TextIndex": feedback[i][3]})


        F = codecs.open(json_path, "r", "utf_8_sig")
        t = json.load(F)
        file_name = t["Name"]
        report = []
        for elem in t.keys():
            if elem == 'Paragraphs':
                for e in range(len(t[elem])):
                    if t[elem][e]['Index'] in dictionary.keys():
                        t[elem][e]['Errors'] = dictionary[t[elem][e]['Index']]
                        for p in range(len(dictionary[t[elem][e]['Index']])):
                            report.append({"Error": dictionary[t[elem][e]['Index']][p]["Description"],
                                           "Feedback": dictionary[t[elem][e]['Index']][p]["Type"]})
                    else:
                        t[elem][e]['Errors'] = None

                    if t[elem][e]['Entities']:
                        for j in range(len(t[elem][e]['Entities'])):
                            mistake = compare_single_text(json=t[elem][e]['Entities'][j], log_path=report_output, txt_path=json_path)
                            if mistake and mistake is not None:
                                if t[elem][e]['Entities'][j]['Errors']:
                                    t[elem][e]['Entities'][j]['Errors'].append(mistake)
                                else:
                                    t[elem][e]['Entities'][j]['Errors'] = [mistake]
                            if not t[elem][e]['Entities'][j]["IsValid"]:
                                continue
                            if not t[elem][e]['Entities'][j]["IsSkip"]:
                                report.append({"Error": "Неверные сущности",
                                               "Feedback": t[elem][e]['Entities'][j]})

        try:
            buf = deepcopy(report)
            generate(dict_list=buf, output_pdf=report_output, originalfilename=file_name, libre_path=libre_path, status_path='/'.join(global_log_path.split('/')[:-1]))
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: report.py\nError while generating the pdf-report\nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Error while generating the report!")

        try:
            json_object = json.dumps(t, indent=4, ensure_ascii=False)
            with codecs.open(json_output, "w", encoding='utf-8') as outfile: 
                outfile.write(json_object)
            outfile.close()
        except Exception as err:
            logging.basicConfig(filename=global_log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: report.py\nError while generating the json-report\nText path: {json_path}\n')
            logger=logging.getLogger(__name__)
            logger.error(err)
            sys.exit("Error while generating the report!")

        if os.path.getsize(log_path) == 0:
            os.remove(log_path)