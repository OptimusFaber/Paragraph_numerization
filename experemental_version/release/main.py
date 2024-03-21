from check import check_file

file_txt = "49.json"
config_json = "Config.json"
check_file(json_path=file_txt, config_path=config_json, report_output="./report.pdf", visualize=True)
