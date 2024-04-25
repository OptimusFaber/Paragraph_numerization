from check import check_file
import cProfile

# check_file(json_path="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/4026.json",
#                config_path="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/Config.json",
#                report_output="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/report.pdf",
#                json_output="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/feedback.json",
#                global_log_path="/home/titan/Desktop/Work/EasyData/Paragraph_numerization/result.log",
#                visualize=True)

res = cProfile.run("check_file(json_path='/home/titan/Desktop/Work/EasyData/Paragraph_numerization/3862.json',config_path='/home/titan/Desktop/Work/EasyData/Paragraph_numerization/Config.json', report_output='/home/titan/Desktop/Work/EasyData/Paragraph_numerization/report.pdf', json_output='/home/titan/Desktop/Work/EasyData/Paragraph_numerization/feedback.json', global_log_path='/home/titan/Desktop/Work/EasyData/Paragraph_numerization/result.log')")