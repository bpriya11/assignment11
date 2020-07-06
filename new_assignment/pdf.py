from PyPDF2 import PdfFileReader, PdfFileWriter
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import json

def convert_pdf_to_string(file_path):

 	output_string = StringIO()
 	with open(file_path, 'rb') as in_file:
 	    parser = PDFParser(in_file)
 	    doc = PDFDocument(parser)
 	    rsrcmgr = PDFResourceManager()
 	    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
 	    interpreter = PDFPageInterpreter(rsrcmgr, device)
 	    for page in PDFPage.create_pages(doc):
 	        interpreter.process_page(page)
 	return(output_string.getvalue())

data=[]
path='C:/Users/DELL/Downloads//General Science For UPSC MC Graw Hill.pdf'
c=0
list=[59,113,112,128,191,219,218,223,385,445,444,450,536,598,597,602,768,861,860,868,1028,1108,1108,1113]


for i in range(len(list)):
    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(path)
    c=c+1
    print('######################################################################')
    print(list)
    st=list[0]
    end=list[1]
    for page in range(st,end):
              pdf_writer.addPage(pdf_reader.getPage(page))
    output_filename = '{}.pdf'.format(c)
    with open(output_filename, 'wb') as out:
                  pdf_writer.write(out)
    print('Created: {}'.format(output_filename))
    print('######################################################################')
    text = convert_pdf_to_string(output_filename)
    questions = []
    TextList = text.split('\n')
    temp = ""
    state = 0
    import re
    x=0
    for line in TextList:
        if line.startswith('1. '):
            g = TextList.index(line)
            TextList = TextList[g:]
            break
    for line in TextList:
         if re.match(r'\d{1,3}\.', line) or state or re.match(r'\*\d{1,3}\.', line) or re.search(r"\x0c\d{1,3}\.", line) or re.search(r"\x0c\*\d{1,3}\.", line):
             temp += line
             state = 1

         if re.match(r"\(d\)", line) or re.match(r"\x0c\(d\)", line):
             #temp += line
             questions.append(temp)
             temp = ""
             state = 0
    for i in TextList:
         if i.startswith('1. ('):
             g=TextList.index(i)
             s=TextList[g:]
    p='\n'.join(s)
    p=p.split(')')
    ans=[]
    for i in p:
          if re.search(r'\d{1,3}\.', i):
              ans.append(i[-1])
    a=[]
    if (len(ans)>len(questions)):
        for i in range(len(questions)):
             a.append(ans[i])
    else:
        a=ans


    def classify(textt,i):
        MCQ = {}
        question_start = re.search(r'\d\.', questions[2]).end() or re.search(r'\*\d\.', questions[2]).end()
        question_end = re.search(r"\(a\)", textt).start() or re.search(r"\x0c\(a\)", textt).start()

        MCQ['question'] = textt[question_start:question_end].strip(" ")

        options_1_start = re.search(r"\(a\)", textt).end() or re.search(r"\x0c\(a\)", textt).end()
        options_1_end = re.search(r"\(b\)", textt).start() or re.search(r"\x0c\(b\)", textt).start()

        MCQ['option1'] = textt[options_1_start:options_1_end].strip(" ")

        options_2_start = re.search(r"\(b\)", textt).end() or re.search(r"\x0c\(b\)", textt).end()
        options_2_end = re.search(r"\(c\)", textt).start() or re.search(r"\x0c\(c\)", textt).start()

        MCQ['option2'] = textt[options_2_start:options_2_end].strip(" ")

        options_3_start = re.search(r"\(c\)", textt).end() or (re.search(r"\x0c\(d\)", textt).start())
        options_3_end = (re.search(r"\(d\)", textt).start()) or (re.search(r"\x0c\(d\)", textt).start())

        MCQ['option3'] = textt[options_3_start:options_3_end].strip(" ")

        options_4_start = (re.search(r"\(d\)", textt).end()) or (re.search(r"\x0c\(d\)", textt).end())
        MCQ['option4'] = textt[options_4_start:].strip(" ")
        MCQ['answer'] = a[i]
        print(MCQ)
        return MCQ


    for i in range(len(questions)):
            try:
                data.append(classify(questions[i],i))
            except:
                a=a[:i]+['']+a[i:]
                continue
    list = list[2:]
    if len(list)==0:
        break
with open('output.json', 'w') as out:
        for i in range(len(data)):
                json.dump((data[i]), out, indent=4)
        out.close()
