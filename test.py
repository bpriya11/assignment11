import json
import re
from io import StringIO
from PyPDF2 import PdfFileReader, PdfFileWriter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator
import sys
import fitz
import filetype
import PyPDF2
from PIL import Image

# result is output dict
result = {}


def convert_pdf_to_string(file_path):
    output_string = StringIO()
    laparams = LAParams()
    laparams.all_texts = True
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return (output_string.getvalue())


def ocrtotext():
    pass


def getBookName_and_author_name(file_name):
    path = file_name
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    result['author'] = info.author
    result['creator'] = info.creator
    result['producer'] = info.producer
    result['subject'] = info.subject
    result['title'] = info.title
    return result


def getBookLanguage(text):
    total = 0
    hindi = 0
    english = 0

    for i in text:
        if ord(i) in range(ord('\u0900'), ord('\u097F') + 1):
            hindi += 1
        else:
            english += 1
        total += 1

    print(hindi / total)
    print(english)
    print(total)
    if ((hindi / total) * 100) > 25:
        return "Hindi"
    return "English"


def isScanned(file_name):
    page_num = 0
    text_perc = 0.0

    doc = fitz.open(file_name)

    for page in doc:
        page_num = page_num + 1

        page_area = abs(page.rect)
        text_area = 0.0
        for b in page.getTextBlocks():
            r = fitz.Rect(b[:4])  # rectangle where block text appears
            text_area = text_area + abs(r)
        text_perc = text_perc + (text_area / page_area)

    text_perc = text_perc / page_num
    # If the percentage of text is very low, the document is most likely a scanned PDF
    if text_perc < 0.09:
        return True
    return False


def getQuestionStart(file_name):
    pass


def isAnswerKeySeparate(s):
    start_index_q1 = s.find('1.')
    end_index_q1 = s.find('(d)', start_index_q1)
    start_index_q2 = s.find('2.', end_index_q1)

    # ------------------finding Substring----------------------#
    st2 = s[end_index_q1:start_index_q2]

    # -------------------searcing Pattern----------------------#
    m = re.search(r"([a-d])", st2)

    if m is not None:
        return True
    else:
        return False


def getTopics(file_name):
    f = open(file_name, "r", encoding='utf-8')
    data = f.read()
    text = data.split('\n')
    temp = []
    list = ['Contents', 'Content', 'CONTENT', 'Index', 'index', 'Table of Contents', '\x0cTable of Contents ']

    for i in list:
        if i in text:
            st = text.index(i) + 2
            g = text[st:]
            break

    c = 0
    try:
        for i in g:
            if i.startswith('\x0c'):
                break
            for j in range(len(temp)):
                if (i != '' and i != ' ') and re.search(i, temp[j]):
                    if re.match(r'\d', i) or re.match('•', i):
                        continue
                    else:
                        # print(i)
                        c = 1
                        break
            if (c == 0):
                temp.append(i)
            else:
                break
    except:
        print('Questions regarding ', file_name)
    t = ('\n').join(temp)
    return t


def isExamYearMentioned(s):
    start_index = s.find('1.')
    end_index = s.find('2.')
    mylist = [s[start_index:end_index]]
    for l in mylist:
        match = re.match(r'.*([1-3][0-9]{3})', l)
        if match is not None:
            return True
            break
    else:
        return False


def getContentType(textfile):
    f = open(textfile, "r", encoding='utf-8')
    data = f.read()
    text = data.split('\n')
    questions = []
    temp = ''
    state = 0
    for line in text:
        if re.match(r'\d{1,3}\.', line) or state:
            temp += line
            state = 1

        if re.match(r"\(d\)", line):
            # temp += line
            questions.append(temp)
            temp = ""
            state = 0
    if (len(questions)==0):
        return 'other'
    else:
        return 'questions'



def areQuestionsImageBased(filename):
    input1 = PyPDF2.PdfFileReader(open(filename, "rb"))
    pdfFilePageCount = input1.numPages
    for i in range(2, pdfFilePageCount):
        page = input1.getPage(i)
        try:
            xObject = page['/Resources']['/XObject'].getObject()
        except:
            continue
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                return True
    return False


if __name__ == "__main__":
    # enter the name of the pdf without any extension
    file = input("Enter the name of the pdf: ")
    file_name = file + '.pdf'

    if not isScanned(file_name):
        text = convert_pdf_to_string(file_name)
        textfilename = 'finaltext.txt'
        text_file = open(textfilename, 'w', encoding='utf-8')
        n = text_file.write(text)
        text_file.close()

    try:
        getBookName_and_author_name(file_name)
    except:
        print('Error in Method -->  getBookName_and_author_name')

    try:
        result['Language'] = getBookLanguage(textfilename)
    except:
        print('Error in Method -->  getBookLanguage')

    try:
        result['Scanned'] = isScanned(file_name)
    except:
        print('Error in Method --> isScanned')

    try:
        result['Topics'] = getTopics(textfilename)
    except:
        print('Error in Method -->  getTopics')

    try:
        result['ContentType'] = getContentType(textfilename)
    except:
        print('Error in Method -->  getContentType')

    try:
        if not isScanned(file_name):
            if getContentType(textfilename) == 'questions':
                result['areQuestionsImageBased'] = areQuestionsImageBased(file_name)
    except:
        print('Error in Method -->  areQuestionsImageBased')

    try:
        result['Exam year mentioned'] = isExamYearMentioned(text)
    except:
        print('Error in Method -->  isExamYearMentioned')

    try:
        result['Ans with ques'] = isAnswerKeySeparate(textfilename)
    except:
        print('Error in Method -->   isAnswerKeySeparate ')

    # ---------------printing result----------------#
    for i in result:
        print(i, '-->', result[i])

# filename = "decrypted 1.pdf"
# filename = "ECONOMY 700 MCQs with Explanatory Note.pdf"
