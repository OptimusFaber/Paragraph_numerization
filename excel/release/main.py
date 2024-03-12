from check import check_file

file_txt = "excel.json"
config_json = "Config.json"
out_json = check_file(excel_path=file_txt, json_path=config_json, visualize=True)
print(out_json)
