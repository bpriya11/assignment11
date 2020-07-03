from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator


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

	return(output_string.getvalue())
text = convert_pdf_to_string('C:/Users/DELL/Downloads//The_Living_World.pdf')
text = text = text.replace('\nAakash  Educational  Services  Pvt.  Ltd.  -  Regd.  Office  :  Aakash  Tower,  8,  Pusa  Road,  New  Delhi-110005  Ph.011-47623456\n', '')
text = text.replace('\uf0ae', '->')
text = text.replace('\uf020\uf020\uf0af', '->')
text = text.replace('\uf020\uf020\uf020\uf020\uf020\uf020\uf020\uf020\uf020\uf020\uf020\uf020\uf020', '')
text = text.replace('\n\n\x0cSolutions  of Assignment  (Set-2)\n\nThe Living World\n','')
text = text.replace('\n\nSolutions  of Assignment  (Set-2)','')
text = text.replace('\uf0b7', '')
text = text.replace('\uf020', '')
text = text.replace('\uf0de', '=>')
text = text.replace('\uf0af', 'o')
text_file = open('finaltext.txt', 'w')
n = text_file.write(text)
text_file.close()



