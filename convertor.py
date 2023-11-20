import docx2txt
import glob

directory = glob.glob('C:\\Users\\titan\\Desktop\\Paragraph_numerization\\example2.docx')

for file_name in directory:
    with open(file_name, 'rb') as infile:
        with open(file_name[:-5]+'.txt', 'w', encoding='utf-8') as outfile:
            doc = docx2txt.process(infile)
            outfile.write(doc)

print("=========")
print("All done!")