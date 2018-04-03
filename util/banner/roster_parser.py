#!/usr/bin/env python3
from html.parser import HTMLParser
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    if attr[1][:7] == 'mailto:':
                        #print(attr[1][7:])
                        self.student.append(attr[1][7:])
                        self.students.append(self.student)
                        self.student = []
                    else:
                        self.founda = True

    def handle_data(self, data):
        if self.founda:
            #print(data)
            self.student.append(data)
            self.founda = False

# This script assumes that the file 'classlist.html' exists in its directory.
# It parses that file (a table element from Banweb) and saves the results in roster.txt
parser = MyHTMLParser()
parser.founda = False
parser.students = []
parser.student = []

with open('classlist.html') as f:
    contents = f.read()

parser.feed(contents)

students = parser.students
studs = []
for name, email in students:
    namelst = name.split(', ')
    last, fullfirst = namelst
    start = fullfirst.find('(Pref:')
    end = fullfirst.find(')', start)
    if start >= 0:
        first = fullfirst[start+7:end]
    else:
        end = fullfirst.find(' ')
        first = fullfirst[:end] if end >= 0 else fullfirst
    stud = [first, last, email, fullfirst]
    studs.append(stud)

with open('roster.txt', 'w') as f:
    for s in studs:
        first, last, email = s[:3] 
        f.write("{}\t{}\t{}\n".format(first, last, email))


