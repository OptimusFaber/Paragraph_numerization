from docxtpl import DocxTemplate
import os,sys
from datetime import datetime  
import time 
import codecs
import json
global_path = __file__
global_path = global_path.replace("report.py", "")
import logging


def generate(
        json_path=None, 
        output_pdf="./report.pdf",
        config_path=None,
        word_format = None, 
        save_doc=False, 
        libre_path=None, 
        status_path=global_path,
        log_path = None,
        new_format=0): 
    
    logging.basicConfig(filename=log_path, level=logging.DEBUG, 
    format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func:%(funcName)s %(message)s \nJson path: {json_path}\n')
    logger=logging.getLogger(__name__)

    if libre_path is None:
        print("No libre office parametr provided, using default libreoffice!!!")
        libre_path = 'libreoffice'

    if output_pdf is None:
        sys.exit("No output pdf directory was provided!")

    if not os.path.exists('/'.join(output_pdf.split('/')[:-1])):
        sys.exit("Wrong output pdf directory!")

    if json_path is None:
        sys.exit("No input json directory was provided!")
        
    if not os.path.exists(json_path):
        sys.exit("Wrong input json directory!")

    if config_path is not None:
        if not os.path.exists(config_path):
            sys.exit("Wrong config directory!")
        else:
            F = open(config_path, encoding='utf-8')
            j = json.load(F)
            if new_format:
                try:
                    NpaNta = j['Settings']['CheckNoNpaConnection']
                except:
                    sys.exit("Wrong config format, no ['Settings']['CheckNoNpaConnection'] object was found!")
            else:
                try:
                    NpaNta = j['Settings']['NotSelectNpaNta']
                except:
                    sys.exit("Wrong config format, no ['Settings']['NotSelectNpaNta'] object was found!")
    else:
        print('No configuration file was provided, setting NpaNta to True!!!')
        NpaNta = False

    #!-----------------------------------------------------------

    F = codecs.open(json_path, "r", "utf_8_sig")
    t = json.load(F)
    try:
        originalfilename = t["Name"]
    except:
        originalfilename = "отчет"
    mistakes = t['Errors']
    report = []
    for sheet in t['Worksheets']:
        for st in sheet['Rows']:
            for cl in st['Cells']:
                if cl['Errors']:
                    report.append({"Error": cl['Errors'][0]["Description"],
                                    "Feedback": cl['Errors'][0]["Type"]})
                else:
                    cl['Errors'] = None
                if cl['Entities']:
                    for j in range(len(cl['Entities'])):
                        if not cl['Entities'][j]["IsValid"]:
                            continue
                        if NpaNta and cl['Entities'][j]['Status'] == 'Actual':
                            continue 
                        if not cl['Entities'][j]["IsSkip"]:
                            report.append({"Error": "Неверные сущности",
                                            "Feedback": cl['Entities'][j]})

    if word_format is None:
        word_format = __file__
        word_format = word_format.replace("report.py", "standart_format.docx")
    #? Data
    basedir = os.path.dirname(sys.argv[0]).replace('release', 'modification')
    path = os.path.join(basedir, "", word_format)
    output_docx = output_pdf[:-3] + "docx"
    output_pdf = "/".join(output_pdf.split('/')[:-1])
    if len(output_docx.split('/'))==1:
        output_docx = os.path.join(basedir, "", output_docx)
    template = DocxTemplate(path)
    #?------------------------------------

    #? Manage outputdir for pdf
    if output_pdf is None or output_pdf == '.':
        output_pdf = "./report.pdf"    
    #?------------------------------
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    #* Containers and dictionaries
    value_dictionary = {
        "Unknown": ["CustomsUnionDecision", "RD", "RDS", "OST", "MGSN", "CustomsReglament", "SP", "MethodicalRecommendations", "GlobalNPA", "Unknown"],
        "FZ": ["FederalLaw", "PresidentDecree", "FSTEKDecree", "FSBDecree", "MinkomSvyazDecree", "SanDoctorDecree", "GovermentDecree", "DecreeMinTruda", "DecreeMinZdrav", "DecreeMinStroy", "DecreeMinEnergo", "DecreeMinRegion", "DecreeRosStandard", "DecreeFns", "DecreeMinistryOther"],
        "Moscow": ["MoscowLaw", "DecreeMoscow", "DecreeITMoscow"],
        "NpaSnip": ["SNiP"],
        "Gost": ["GOST"],
        "SanPin": ["SanPin"]
    }
    for j in range(len(report)):
        if report[j]["Error"] == 'Неверные сущности':
            for key in value_dictionary.keys():
                if report[j]["Feedback"]["DocumentType"] in value_dictionary[key]:
                    report[j]["Feedback"]["MainStatus"] = key
                    break
            else:
                report[j]["Feedback"]["MainStatus"] = "Unknown"
    var = {
        'Действует': 0,
        'Не действует': 0,
        'Не определен': 0
    }
    status = {
        'Actual': 'Действует',
        'Awaits': 'Действует',
        'Declined': 'Не действует',
        'NotApplicable': 'Не действует',
        'Changed': 'Не действует',
        'NotFound': 'Не определен',
        'Unknown': 'Не определен'
    }
    data = {
        "Unknown": var.copy(),
        "FZ": var,
        "Moscow": var.copy(),
        "Decree": var,
        "NpaSnip": var.copy(),
        "Gost": var.copy(),
        "SanPin": var.copy()
    }
    context = {
        'file_name': originalfilename,
        'date': date,
        'mistakes': [],
        'statistics': [],
        'tables': [
            {"full": 0, "name": "Федеральные НПА", "info": []},
            {"full": 0, "name": "НПА г. Москвы", "info": []},
            {"full": 0, "name": "ГОСТ", "info": []},
            {"full": 0, "name": "СанПиН", "info": []},
            {"full": 0, "name": "СНиП", "info": []},
            {"full": 0, "name": "Иные виды НПА и НТА", "info": []}
        ]
    }
    categories = {
        "Федеральные НПА": "FZ", #! add Decree
        "НПА г. Москвы": "Moscow", 
        "ГОСТ": "Gost",
        "СанПиН": "SanPin", 
        "СНиП": "NpaSnip", 
        "Иные виды НПА и НТА": "Unknown"}
    #*------------------------
    
    #! Mistakes statistics
    mistakes = [{'mistake': 'Сокращение не введено', 'amount': mistakes['Abbreviation']},
                {'mistake':'Подозрение на неоднозначное требование', 'amount': mistakes['Corruption']},
                {'mistake':'Нет связи с НПА (НТА)', 'amount': mistakes['NoNpaConnection']},
                {'mistake':'Некорректная формулировка', 'amount': mistakes['IncorrectStatement']},
                {'mistake':'Ошибка нумерации', 'amount': mistakes['Numeration']}
                ]
    
    context['mistakes']=mistakes
    #! -------------------

    #& Filling in data
    for elem in report:
        if elem['Error'] == 'Неверные сущности':
            data[elem["Feedback"]["MainStatus"]][status[elem["Feedback"]["Status"]]]+=1


    for elem in categories:
        stat = data[categories[elem]]
        active = stat['Действует'] if stat['Действует'] else "Нет"
        inactive = stat['Не действует'] if stat['Не действует'] else "Нет"
        unknown = stat['Не определен'] if stat['Не определен'] else "Нет"
        if active == inactive == unknown == "Нет":
            continue
        row = {"type":elem, "active":"{}".format(active), "inactive":"{}".format(inactive), "unknown":"{}".format(unknown)}
        context['statistics'].append(row)
    #&--------------------------------------------------------
        
    buf = {
        "Unknown": [context['tables'][5], 0],
        "FZ": [context['tables'][0], 0],
        "Moscow": [context['tables'][1], 0],
        "NpaSnip": [context['tables'][4], 0],
        "Gost": [context['tables'][2], 0],
        "SanPin": [context['tables'][3], 0]
    }
    tic = time.time()
    while os.path.isfile(f"{status_path}/libre_status.log"):
        time.sleep(0.5)
        if time.time()-tic>90:
            os.remove(f"{status_path}/libre_status.log")
    with open(f"{status_path}/libre_status.log", 'w') as fp:
        pass
    #! Create docx file
    res = list(map(lambda x: x['Feedback'],list(filter(lambda x: x['Error'] == 'Неверные сущности', report))))
    for i in range(len(res)): 
        tytle = buf[res[i]["MainStatus"]][0]['info']
        buf[res[i]["MainStatus"]][0]['full']+=1
        buf[res[i]["MainStatus"]][1] += 1
        fed_npa= {'num': buf[res[i]["MainStatus"]][1], 'doc': res[i]["Text"],'status': status[res[i]["Status"]],'link': "" if res[i]["CatalogLink"] is None else res[i]["CatalogLink"]}
        tytle.append(fed_npa)
    template.render(context)
    template.save(output_docx)
    #!--------------------------------------------------------
    #^ Save PDF
    res = True
    while res:
        res = os.system("{} \
                --convert-to {} \
                --outdir '{}' \
                '{}'".format(libre_path, 'pdf', output_pdf, output_docx))
        if res != 0:
            time.sleep(2)
    if not save_doc:
        os.remove(output_docx)
    os.remove(f"{status_path}/libre_status.log")
    #^------------------------

