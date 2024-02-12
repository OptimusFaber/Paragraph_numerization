from check import check_file
import os
from tqdm import tqdm

for file_txt in tqdm(os.listdir('text')):
    file_txt = 'text/' + file_txt
    config_json = "472.json"
    check_file(txt_path=file_txt, json_path=config_json)