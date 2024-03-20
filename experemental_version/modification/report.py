from docxtpl import DocxTemplate
import os,sys
import json
from datetime import datetime   


def generate(dict_list=None, output_pdf="./", inputFileName = "standart_format.docx", output_docx = "./report.docx", originalfilename = "отчёт", save_doc=False): 
    """
    json_path (string) -> path to .json file with statistics,
    output_pdf (string) -> folder where to place pdf file,
    inputFileName (string) -> path to doc standart form,
    output_docx (string) -> path where to save buf docx file with statistics,
    originalfilename (string) -> report name,
    save_doc (boolean) -> save docx with statistics if true
    """
    #? Data
    basedir = os.path.dirname(sys.argv[0]).replace('release', 'modification')
    path = os.path.join(basedir, "", inputFileName)
    if len(output_docx.split('/'))==1:
        output_docx = os.path.join(basedir, "", output_docx)
    template = DocxTemplate(path)
    #?------------------------------------

    #? Manage outputdir for pdf
    if output_pdf is None:
        output_pdf = "./"    
    #?------------------------------
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    #* Containers and dictionaries
    value_dictionary = {
        "Unknown": ["CustomsUnionDecision", "RD", "RDS", "OST", "MGSN", "CustomsReglament", "SP", "MethodicalRecommendations", "GlobalNPA"],
        "FZ": ["FederalLaw", "PresidentDecree", "FSTEKDecree", "FSBDecree", "MinkomSvyazDecree", "SanDoctorDecree", "GovermentDecree", "DecreeMinTruda", "DecreeMinZdrav", "DecreeMinStroy", "DecreeMinEnergo", "DecreeMinRegion", "DecreeRosStandard", "DecreeFns", "DecreeMinistryOther"],
        "Moscow": ["MoscowLaw", "DecreeMoscow", "DecreeITMoscow"],
        "NpaSnip": ["SNiP"],
        "Gost": ["GOST"],
        "SanPin": ["SanPin"]
    }
    for j in range(len(dict_list)):
        if dict_list[j]["Error"] == 'Неверные сущности':
            for key in value_dictionary.keys():
                if dict_list[j]["Feedback"]["DocumentType"] in value_dictionary[key]:
                    dict_list[j]["Feedback"]["MainStatus"] = key
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
    mistakes = {'Сокращение не введено': 0,
                'Подозрение на неоднозначное требование': 0,
                'Нет связи с НПА (НТА)': 0,
                'Некорректная формулировка': 0,
                'Ошибка нумерации': 0,}
    categories = {
        "Федеральные НПА": "FZ", #! add Decree
        "НПА г. Москвы": "Moscow", 
        "ГОСТ": "Gost",
        "СанПиН": "SanPin", 
        "СНиП": "NpaSnip", 
        "Иные виды НПА и НТА": "Unknown"}
    mstks_frmt = {'Abbreviation': 'Сокращение не введено',
                'Corruption': 'Подозрение на неоднозначное требование',
                'NoNPA': 'Нет связи с НПА (НТА)',
                'IncorrectForm': 'Некорректная формулировка',
                'Numbering': 'Ошибка нумерации',
                'DuplicateEntity': 'Ошибка нумерации'}
    #*------------------------
    
    #! Mistakes statistics
    for elem in dict_list:
        if elem['Error'] != 'Неверные сущности':
            mistakes[mstks_frmt[elem['Feedback']]]+=1
    for key in mistakes.keys():
        if mistakes[key] == 0:
            mistakes[key] = 'Нет'
    mistakes = list(mistakes.items())
    for i, (name, num) in enumerate(mistakes):
        mistakes[i] = {'mistake':name, 'amount':num}
    context['mistakes']=mistakes
    #! -------------------

    #& Filling in data
    for elem in dict_list:
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
    
    #! Create docx file
    res = list(map(lambda x: x['Feedback'],list(filter(lambda x: x['Error'] == 'Неверные сущности', dict_list))))
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
    os.system("libreoffice \
            --convert-to {} \
            --outdir {} \
            {}".format('pdf', output_pdf, output_docx))
    if not save_doc:
        os.remove(output_docx)
    #^------------------------