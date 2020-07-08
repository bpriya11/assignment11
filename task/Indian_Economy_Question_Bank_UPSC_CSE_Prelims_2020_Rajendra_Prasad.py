import re
import json
f = open("13.txt", "r", encoding='utf-8')
data = f.read()
text=data.split('\n')
questions=[]
temp=''
state=0
for line in text:
    if re.match(r'\d{1,3}\.', line) or state:
        temp += line
        state = 1
    if line.startswith('Ans'):
         # temp += line
         questions.append(temp)
         temp = ""
         state = 0

def classify(textt,i):
        MCQ = {}
        question_start = re.search(r'\d\.', textt).end()
        question_end = textt.find('a)')

        MCQ['question'] = textt[question_start:question_end-1].strip(" ")

        options_1_start = textt.find('a)')
        options_1_end = textt.find('b)')

        MCQ['option1'] = textt[options_1_start+2:options_1_end].strip(" ")

        options_2_start = textt.find('b)')
        options_2_end = textt.find('c)')

        MCQ['option2'] = textt[options_2_start+2:options_2_end].strip(" ")

        options_3_start = textt.find('c)')
        options_3_end = textt.find('d)')

        MCQ['option3'] = textt[options_1_start+2:options_1_end].strip(" ")

        options_4_start = textt.find('d)')
        options_4_end = textt.find("Ans")
        MCQ['option4'] = textt[options_4_start+2:options_4_end].strip(" ")
        #answer_start = re.search(r'Ans ', textt).end()
        MCQ['solution'] = textt[-1]
        #MCQ['answer'] = ans[i]
        print(MCQ)
        return MCQ

with open('output13.json', 'w') as out:
        for i in range(len(questions)):
                json.dump(classify(questions[i],i), out, indent=4)
        out.close()
