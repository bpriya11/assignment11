import re
import json
f = open("3.txt", "r", encoding='utf-8')
data = f.read()
text=data.split('\n')
questions=[]
temp=''
state=0
for line in text:
    if re.match(r'\d{1,3}\.', line) or state:
        temp += line
        state = 1

    if re.match(r"\(d\)", line):
         # temp += line
         questions.append(temp)
         temp = ""
         state = 0

for i in text:
    if i.startswith('1.      ('):
            g = text.index(i)
            s = text[g:]

p = '\n'.join(s)
p = p.split(')')
ans = []
for i in p:
    if re.search(r'\d{1,3}\.', i):
        ans.append(i[-1])
def classify(textt,i):
        MCQ = {}
        question_start = re.search(r'\d\.', textt).end()
        question_end = re.search(r"\(a\)", textt).start()

        MCQ['question'] = textt[question_start:question_end].strip(" ")

        options_1_start = re.search(r"\(a\)", textt).end()
        options_1_end = re.search(r"\(b\)", textt).start()

        MCQ['option1'] = textt[options_1_start:options_1_end].strip(" ")

        options_2_start = re.search(r"\(b\)", textt).end()
        options_2_end = re.search(r"\(c\)", textt).start()

        MCQ['option2'] = textt[options_2_start:options_2_end].strip(" ")

        options_3_start = re.search(r"\(c\)", textt).end()
        options_3_end = (re.search(r"\(d\)", textt).start())

        MCQ['option3'] = textt[options_3_start:options_3_end].strip(" ")

        options_4_start = (re.search(r"\(d\)", textt).end())
        MCQ['option4'] = textt[options_4_start:].strip(" ")
        MCQ['answer'] = ans[i]
        print(MCQ)
        return MCQ

with open('output3.json', 'w') as out:
        for i in range(len(questions)):
                json.dump(classify(questions[i],i), out, indent=4)
        out.close()
