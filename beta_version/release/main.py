from check import check_file

file_txt = "text_docx_libreoffice2.txt"
# file_txt = "text/118.txt"
# file_txt = "tests/test1.txt"
# file_txt = "error.txt"
config_json = "472.json"
check_file(txt_path=file_txt, json_path=config_json, visualize=True)
