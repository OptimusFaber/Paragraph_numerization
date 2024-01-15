import pypandoc

print(pypandoc.convert_file("98.docx", "plain+simple_tables", format="docx", extra_args=(), encoding='utf-8', outputfile="98.txt"))