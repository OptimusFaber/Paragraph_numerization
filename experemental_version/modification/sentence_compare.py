from difflib import SequenceMatcher
import logging

def compare_single_text(json, threshold=0.6, log_path="myapp.log", txt_path=None):
    logging.basicConfig(filename=log_path, level=logging.DEBUG, 
            format=f'%(asctime)s %(levelname)s module: %(name)s line num: %(lineno)s func:%(funcName)s %(message)s \nText path: {txt_path}\n')
    logger=logging.getLogger(__name__)
    try:
        doc_data, cat_data = json["Date"], json["CatalogDate"]
        doc_n, cat_n = json["Number"], json["CatalogNumber"]
        doc, cat = json["Title"], json["CatalogTitle"]
        if doc_data and cat_data:
            if json["Date"] != json["CatalogDate"]:
                # Даты разные
                return {"ErrorType": "EntityDate",
                        "Description": f"Разные даты {doc_data} и {cat_data}",
                        "Element": json["Text"]}
            return False
        elif doc_n and cat_n:
            if json["Number"] != json["CatalogNumber"]:
                # N не соответствует
                return {"ErrorType": "EntityNumber",
                        "Description": f"Разные номера {doc_n} и {cat_n}",
                        "Element": json["Text"]}
            return False
        elif doc and cat:
            if json["Title"]:
                #& ----------------
                if len(doc) > len(cat):
                    ratio_list = [SequenceMatcher(None, cat, doc[i:len(cat)+i]).ratio() for i in range(len(doc)-len(cat)+1)]  
                elif len(doc) < len(cat):
                    ratio_list = [SequenceMatcher(None, doc, cat[i:len(doc)+i]).ratio() for i in range(len(cat)-len(doc)+1)]
                else:
                    ratio_list = [SequenceMatcher(None, cat, doc).ratio()]

                if all(num < threshold for num in ratio_list):
                    # Предложения различаются по смыслу
                    return {"ErrorType": "EntityTitle",
                            "Description": "Разные сущности",
                            "Element": json["Text"]}
                return False
        else:
            # Предложения схожи по смыслу
            return False
    except Exception as err: logger.error(err)
