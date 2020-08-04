import json
import re
import pdfplumber
from PyPDF2 import PdfFileReader, PdfFileWriter
textfilename = 'finaltexxxt.txt'
def convert_pdf_to_string(file_path):
    text_file = open(textfilename, 'w', encoding='utf-8')
    pdf = PdfFileReader(file_path)
    count = pdf.getNumPages()
    with pdfplumber.open(file_path) as pdf:
        for i in range(count):
            page_text = pdf.pages[i].extract_text()
            n = text_file.write(page_text)
    text_file.close()
convert_pdf_to_string("MAY-2020.pdf")
import re
import json
f = open('t1.txt', encoding="utf8")

# creating an instance s which holds all the content of the text file( sample.txt)
s = f.read()
li=[]
x=[]
list=['APRIL 2020','MARCH 2020','FEBRUARY 2020','JANUARY 2020']
r=1
for i in range(1):
    li=[]
    st = s.find(list[i])
    en = s.find(list[i+1])
    list.remove(list[i])
    string = s[st:en]
    temp = ''
    state = 0
    g = string.replace('.', '?')
    for i in range(r, 613):
        st = g.find(str(i) + ')')
        en = g.find(str(i + 1) + ')')
        aa = g[st:en]
        try:
            if '?' in aa:
                a, b = aa.split('?')
                li.append([a, b])
        except:
            print(i)
    x.append(li)
def classify(textt, i):
     MCQ = {}
     MCQ['question'] = textt[0]
     MCQ['answer'] = textt[1]
     return MCQ
with open('april2020.json', 'w') as out:
     for i in range(len(l)):
         json.dump(classify(l[i], i), out, indent=4)
     out.close()
