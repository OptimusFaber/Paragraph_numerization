from check import check_file

file_txt = "49.json"
config_json = "Config.json"
check_file(excel_path=f"/home/titan/Desktop/Work/EasyData/Paragraph_numerization/5070.json",
               config_path="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/Config.json",
               report_output="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/report.pdf",
               json_output="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/feedback.json",
               global_log_path="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/result.log",
               visualize=True)
