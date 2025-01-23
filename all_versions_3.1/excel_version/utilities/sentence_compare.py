from difflib import SequenceMatcher
import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
global_path = __file__
global_path = "/".join(global_path.split("/")[:-1])
sys.path.append(global_path)
from utilities.logger import log_errors

@log_errors
def compare_single_text(json, threshold=0.6, error_path=None):
    doc, cat = json["Title"], json["CatalogTitle"]
    if doc and cat:
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
                return {"Type": "EntityTitle",
                        "Description": "Разные сущности",
                        "Element": json["Text"]}
            return False
        
    else:
        return False
