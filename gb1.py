#!/usr/bin/env python3

from menu import Menu
import sys, os
import subprocess
import datetime
import json
import numpy as np
from matplotlib import pyplot as plt 
   


class Course:
    def __init__(self, name = '', term = ''):
        self.name = name
        self.term = term
        self.categories = []
        self.gradeables = []
        self.students = []
        self.actives = None
        self.scores = []
        self.cur_student = None
        self.cur_gradeable = None
        self.cur_category = None
    
    # Set the current student, gradeable, or category for a menu action
    def set_cur_student(self, student):
        self.cur_student = student

    def set_cur_gradeable(self, gradeable):
        self.cur_gradeable = gradeable

    def set_cur_category(self, category):
        self.cur_category = category

    def get_actives(self):
        if self.actives == None:
            self.actives = [s for s in self.students if s.is_active]
        return self.actives

    def remove_student(self, student):
        self.scores = [score for score in self.scores if score.student != student]
        self.students.remove(student)
        self.cur_student = None
        self.actives = None

    def remove_gradeable(self, gradeable):
        self.scores = [score for score in self.scores \
                if score.gradeable != gradeable]
        self.gradeables.remove(gradeable);
        self.cur_gradeable = None

    def remove_category(self, category):
        self.scores = [score for score in self.scores \
                if score.gradeable.category != category]
        self.gradeables = [gradeable for gradeable in self.gradeables \
                if gradeable.category != category]
        self.categories.remove(category)
        self.cur_category = None

    # The name of the associated JSON file for the course
    def file_name(self):
        return self.name.replace(' ','_') + "_" \
               + self.term.replace(' ','_') + ".json"

class Student:
    def __init__(self, first = '', last = '', email = '', is_active=1):
        self.first = first
        self.last = last
        self.email = email
        self.is_active = is_active
       
    def name(self):
        return self.first + (' {0:s}.'.format(self.last[0]) if self.last else '')

    def fullname(self):
        return self.first + ' ' + self.last
        
class Question:
    def __init__(self, gradeable, points):
        self.gradeable = gradeable
        self.points = points

class Category:
    def __init__(self, name='', pct_of_grade=0.0):
        self.name = name
        self.pct_of_grade = pct_of_grade

class Gradeable:
    def __init__(self, name='', category = None, total_pts=0.0, \
            sub_pct = 0.0, added_pts = 0.0, added_pct = 0.0):
        self.name = name
        self.category = category
        self.total_pts = total_pts
        self.sub_pct = sub_pct
        self.added_pts = added_pts
        self.added_pct = added_pct
        self.questions = []
    
    def add_question(self, points):
        q = Question(self, points)
        self.questions.append(q)

    def remove_question(self, question):
        self.questions.remove(question)

    def get_question(self, question):
        for q in self.questions:
            if q == question:
                return q
        return None

class Score:
    def __init__(self, student, gradeable, question, value = 0.0):
        self.student = student
        self.gradeable = gradeable
        self.question = question
        self.value = value

def get_score(student, gradeable, question):
    q = gradeable.get_question(question)
    for s in gb.scores:
        if s.student is student and s.gradeable is gradeable \
                and s.question is question:
            return s
    s = Score(student, gradeable, question)
    gb.scores.append(s)
    return s

def course_to_dict():
    course = {'name': gb.name, 'term': gb.term}
    course['categories'] = [{'id':i, 'name': c.name, 'pct_of_grade': c.pct_of_grade} \
            for i, c in enumerate(gb.categories)]
    # add the student object to the dict -- delete it once the scores list is finished
    course['students'] = [{'id':i, 'first': s.first, 'last': s.last, 'email': s.email, 'obj': s} \
            for i, s in enumerate(gb.students)]
    gradeables = []
    scores = []
    for cd in course['categories']:
        for i, g in enumerate(gb.gradeables):
            questions = []
            gd = {'id':i, 'cid': cd['id'], 'name': g.name, 'total_pts': g.total_pts, \
                    'sub_pct': g.sub_pct, 'added_pts': g.added_pct, 'added_pct': g.added_pct}
            for j, q in enumerate(g.questions):
                questions.append( {'id':j, 'gid': i, 'points': q.points} )
                for sd in course['students']:
                    scores.append( {'sid': sd['id'], 'gid': gd['id'], 'qid': j, \
                            'value': get_score(sd['obj'],g,q).value } )
            gd['questions'] = questions
            gradeables.append(gd)       
    course['gradeables'] = gradeables
    course['scores'] = scores
    for s in course['students']:
        del s['obj']
    return course

def course_from_dict(course):
    category_dict = {item['id'] : item for item in course['categories']}
    gradeable_dict = {item['id'] : item for item in course['gradeables']}
    student_dict = {item['id'] : item for item in course['students']}
    question_dict = {(q['gid'],q['id']) : q for g in course['gradeables'] \
            for q in g['questions'] }
    course_obj = Course(course['name'], course['term'])
    categories = []
    gradeables = []
    students = []
    scores = []
    for cd in course['categories']:
        category = Category(cd['name'], cd['pct_of_grade'])
        category_dict[cd['id']]['obj'] = category
        categories.append(category)
    course_obj.categories = categories
    for sd in course['students']:
        student = Student(sd['first'], sd['last'], sd['email'])
        student_dict[sd['id']]['obj'] = student
        students.append(student)
    course_obj.students = students
    for gd in course['gradeables']:
        gradeable = Gradeable(gd['name'], category_dict[gd['cid']]['obj'], \
                gd['total_pts'], gd['sub_pct'], gd['added_pts'], gd['added_pct'])
        gradeable_dict[gd['id']]['obj'] = gradeable
        gradeables.append(gradeable)
        for qd in gd['questions']:
            question = Question(gradeable, qd['points'])
            question_dict[(qd['gid'],qd['id'])]['obj'] = question
            gradeable.questions.append(question)
    course_obj.gradeables = gradeables
    for sd in course['scores']:
        score = Score(student_dict[sd['sid']]['obj'], gradeable_dict[sd['gid']]['obj'], \
                question_dict[(sd['gid'],sd['qid'])]['obj'], sd['value'])
        scores.append(score)
    course_obj.scores = scores
    return course_obj

def read(file_name):
    with open(file_name,'r') as f:
        course_dict = json.load(f)
    return course_from_dict(course_dict)

def save(course, file_name):
    data = json.dumps(course_to_dict(), indent=2)
    with open(file_name, mode='w', encoding='utf-8') as f:
        f.write(data)

def save_and_exit():
    save(gb, gb.file_name())
    m_main.close()
   
def save_current():
    save(gb, gb.file_name())



# --------------------------------------
# User input and type conversion helpers
# --------------------------------------
def get_string(title, default=None, prompt=" >> "):
    ftitle = title if default == None else title + " ({0:s})".format(default)
    print(ftitle)
    sval = input(prompt)
    return default if default != None and sval == '' else sval

def get_bool(title, default=None, prompt=" >> "):
    ftitle = title if default == None else title + \
            " ({0:s})".format('Y' if default == 1 else 'N')
    while True:
        print(ftitle)
        sval = input(prompt).lower()
        if default != None and sval == '':
            return default
        if sval == 'y':
            return 1
        elif sval == 'n':
            return 0
        else:
            say("invalid")
            print("Value should be Y or N")

def get_valid_float(title, minval, maxval, default=None, prompt=" >> ") :
    valid = False
    ftitle = title if default == None else title + " ({0:.1f})".format(default)

    while not valid:
        print(ftitle)
        sval = input(prompt)
        if default != None and sval == '':
            return default
        try:
            fval = float(sval)
            if fval >= minval and fval <= maxval:
                valid = True
            else:
                say("invalid")
                print("Value should be between {0:d} and {1:d}".format(minval, maxval))
        except ValueError:
            say("What?")
            print("What?")
    return fval

def get_int_from_list(title, slist, default=None, prompt = " >> "):
    valid = False
    ftitle = title if default == None else title + " ({0:d})".format(default)

    while not valid:
        print(ftitle)
        for i, item in enumerate(slist):
            print("{0:d}. {1:s}".format(i+1, item))
        sval = input(prompt)
        if default != None and sval == '':
            return default
        try:
            ival = int(sval)
            if ival >= 1 and ival <= len(slist):
                valid = True
            else:
                say("invalid")
                print("Select one of the numbered options")
        except ValueError:
            say("What?")
            print("What?")
    return ival

def get_space_separated_floats(title, valid_sum, default=None, prompt=" >> "):
    valid = False
    ftitle = title if default == None else title + " ({0:s})".format(' '.join(["{0:.1f}".format(p) for p in default]))
    while not valid: 
        print(ftitle)
        qs = input(prompt)
        if qs == '' and default != None:
            return default

        slst = qs.split()
        try:
            flst = [float(val) for val in slst]
            if sum(flst) >= valid_sum:
                valid = True
            else:
                say("invalid")
                print("The points should sum to at least {0:.1f}".format(valid_sum))
        except ValueError:
            say("What?")
            print("What?")
    return flst

# Give an audible warning
def say(phrase):
    subprocess.call(['spd-say', '-w', '"{0:s}"'.format(phrase)])

#--------------------
# Category Management
#--------------------
def add_category():
    name = get_string("Enter Category Name")
    pct_of_grade = get_valid_float("Percent of Grade", 0, 100)
    cat = Category(name, pct_of_grade)
    gb.categories.append(cat)
    set_category_options()

def edit_category():
    name = get_string("Enter Category Name", gb.cur_category.name)
    pct_of_grade = get_valid_float("Percent of Grade ({0:.1f})".format(gb.cur_category.pct_of_grade), 0, 100, gb.cur_category.pct_of_grade)
    gb.cur_category.name = name if name else gb.cur_category.name
    gb.cur_category.pct_of_grade = pct_of_grade
    set_category_options()

def delete_category():
    gb.remove_category(gb.cur_category)
    set_category_options()

#-------------------
# Student Management
#-------------------
def import_students():
    with open('students.txt','r') as f:
        text = f.read()
    lines = text.rstrip().split('\n')
    for line in lines:
        first, last, email = line.split()
        gb.students.append(Student(first, last, email))
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    set_student_options()

def add_student():
    first = get_string("Enter First Name")
    last = get_string("Enter Last Name")
    email = get_string("Enter Email")
    is_active = get_bool("Is the Student Active? (y/n)", 1)
    student = Student(first, last, email, is_active)
    gb.students.append(student)
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    set_student_options()

def edit_student():
    first = get_string("Enter First Name", gb.cur_student.first)
    last = get_string("Enter Last Name", gb.cur_student.last)
    email = get_string("Enter Email", gb.cur_student.email)
    is_active = get_bool("Is the Student Active? (y/n)", gb.cur_student.is_active)
    gb.cur_student.first = first
    gb.cur_student.last = last
    gb.cur_student.email = email
    gb.cur_student.is_active = is_active
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None 
    set_student_options()

def delete_student():
    gb.remove_student(gb.cur_student)
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    set_student_options()

#------------------
# Course Management
#------------------
def add_course():
    first = get_string("Enter Course Name (e.g. Math 251)")
    last = get_string("Enter Quarter (e.g. W18")
    gb.students.append(student)
    set_student_options()

def edit_course():
    name = get_string("Enter Course Name", gb.name)
    term = get_string("Enter Quarter", gb.term)
    gb.name = name
    gb.term = term

#---------------------
# Gradeable Management
#---------------------
def add_gradeable():
    name = get_string("Enter Graded Item Name")
    cat = get_int_from_list("Select a numbered category", [c.name for c in gb.categories])
    category = gb.categories[cat-1]
    total_pts = get_valid_float("Total Points", 0, 10000)
    fpts = get_space_separated_floats("Enter question point values separated by whitespace", total_pts)
    sub_pct = get_valid_float("Retake Sub-percent", 0, 100, 100.0)
    added_pts = get_valid_float("Added Points", 0, 10000, 0.0)
    added_pct = get_valid_float("Added Percent", 0, 100, 0.0)
    gradeable = Gradeable(name, category, total_pts, sub_pct, added_pts, added_pct)
    questions = [Question(gradeable, p) for p in fpts]
    gradeable.questions = questions
    gb.gradeables.append(gradeable)
    set_gradeable_options()

def edit_gradeable():
    cg = gb.cur_gradeable
    name = get_string("Enter Graded Item Name", cg.name)
    def_sel = gb.categories.index(cg.category) + 1
    cat = get_int_from_list("Select a numbered category", [c.name for c in gb.categories], def_sel )
    category = gb.categories[cat-1]
    total_pts = get_valid_float("Total Points", 0, 10000, cg.total_pts)
    pts = [q.points for q in cg.questions]
    fpts = get_space_separated_floats("Enter question point values separated by whitespace", total_pts, pts)
    sub_pct = get_valid_float("Retake Sub-percent", 0, 100, cg.sub_pct)
    added_pts = get_valid_float("Added Points", 0, 10000, cg.added_pts)
    added_pct = get_valid_float("Added Percent", 0, 100, cg.added_pct)
    cg.name = name if name else cg.name
    cg.category = category
    cg.total_pts = total_pts
    cg.sub_pct = sub_pct
    cg.added_pts = added_pts
    cg.added_pct = added_pct
    cg.questions = [Question(cg, p) for p in fpts]
    set_gradeable_options()

def delete_gradeable():
    gb.remove_gradeable(gb.cur_gradeable)
    set_gradeable_options()

#------------
# Score Entry
#------------
# Helper for input_score - starts the recursion
def input_scores(gradeable):
    gb.set_cur_gradeable(gradeable)
    return input_score( 0, 0)

def input_score(st_idx, q_idx):
    cg = gb.cur_gradeable
    q_ct = len(cg.questions)
    s_ct = len(gb.get_actives())
    if st_idx <= 0 and q_idx < 0:
        print("First One")
        say("first one")
        input_score( 0, 0)
    elif st_idx >= s_ct - 1 and q_idx >= q_ct:
        print("Last One")
        say("last one")
        input_score( s_ct-1, q_ct-1)
    elif q_idx >= q_ct:
        input_score(st_idx + 1, 0)
    elif q_idx < 0:
        input_score( st_idx - 1, -1)
    else:
        s = gb.students[st_idx]
        q = cg.questions[q_idx]
        score = get_score(s, cg, q)

        print("{0:s}: {1:s}, {2:d}. ({3:.1f})".format(cg.name, \
                s.name(), q_idx+1, score.value))
        value = input(" >> ")
        if value.lower() == 'q':
            return False
        if value.lower() == 'b':
            input_score( st_idx, q_idx-1)
        elif value == '':
            input_score( st_idx, q_idx+1)
        elif value.lower() == 'n':
            input_score( st_idx+1, 0)
        elif value.lower() == 'p':
            input_score( st_idx-1, 0)
        else:
            try:
                tval = float(value)
                if tval <= q.points and tval >= 0:
                    score.value = tval
                    input_score( st_idx, q_idx+1)
                else:
                    say("invalid")
                    print("Invalid score")
                    input_score( st_idx, q_idx)
            except ValueError:
                say("What?")
                print("What?")
                input_score( st_idx, q_idx)
    return


# Helper for input_student_score -- starts the recursion
def input_student_scores(student):
    gb.set_cur_student(student)
    return input_student_score( 0 )

def input_student_score( q_idx):
    cg = gb.cur_gradeable
    s = gb.cur_student
    q_ct = len(cg.questions)

    if q_idx >= len(cg.questions):
        print("Last One")
        say("last one")
        input_student_score( q_ct - 1)
    elif q_idx < 0:
        print("First One")
        say("first one")
        input_student_score( 0 )
    else:
        q = cg.questions[q_idx]
        score = get_score(s, cg, q)
        print("{0:s}: {1:s}, {2:d}. ({3:.1f})".format(cg.name, \
                s.name(), q_idx+1, score.value))
        value = input(" >> ")
        if value.lower() == 'q':
            return False
        if value.lower() == 'b':
            input_student_score( q_idx-1)
        elif value == '':
            input_student_score( q_idx+1)
        else:
            try:
                tval = float(value)
                if tval <= q.points and tval >= 0:
                    score.value = tval
                    input_student_score( q_idx+1)
                else:
                    say("invalid")
                    print("Invalid score")
                    input_student_score( q_idx)
            except ValueError:
                say("What?")
                print("What?")
                input_student_score( q_idx)
    return

def rpt_graded_item_stats():
    return None

def plot_hist(pcts):
    plt.hist(pcts, bins = [0,60,70,80,90,100]) 
    plt.title("histogram") 
    plt.show()

def rpt_graded_item_details():
    cg = gb.cur_gradeable
    names = np.array([s.name() for s in gb.get_actives()])
    ar = np.array([[get_score(s,cg,q).value for q in cg.questions] \
            for s in gb.get_actives()])
    n,m = ar.shape
    tots = ar.sum(1)
    pcts = tots/cg.total_pts*100.0
    plot_hist(pcts)
    totinds = tots.argsort()
    ar, names = ar[totinds,:], names[totinds]
    tots, pcts = tots[totinds], pcts[totinds]
 
    title="{0:s} Details".format(cg.name)
    print(title)
    print("-"*len(title))
    print("Student".ljust(20), end='')
    for j in range(m):
        print("#{0:d}".format(j+1).rjust(6), end='')
    print("Total".rjust(10), "%".rjust(5))
    for i in range(n):
        print("{0:s}".format(names[i]).ljust(20), end='')
        for j in range(m):
            print("{0:.1f}".format(ar[i,j]).rjust(6), end='')
        print("{0:.1f}".format(tots[i]).rjust(10), end='')
        print("{0:.1f}".format(pcts[i]).rjust(6))

    print("-"*(20 + 6*(m+1) + 10))
    print("Average".ljust(20), end='')
    for j in range(m):
        print("{0:.1f}".format(ar[:,j].mean()).rjust(6), end='')
    print("{0:.1f}".format(tots.mean()).rjust(10), end='')
    print("{0:.1f}".format(pcts.mean()).rjust(6))
    print('')
    print('')
    input("Press <Enter>")

def rpt_student_scores():
    return None

def rpt_course_summary():
    return None


#-------------
# Menu Helpers
#-------------
# These helpers set the current gradeable, student, etc... 
# then open a menu item
def set_gradeable_open_score_one_entry(gradeable):
    gb.set_cur_gradeable(gradeable)
    m_score_one_entry.open()

def set_gradeable_open_gradeable_edit_del(gradeable):
    gb.set_cur_gradeable(gradeable)
    m_gradeable_edit_del.open()

def set_and_open_category_edit_del(category):
    gb.set_cur_category(category)
    m_category_edit_del.open()
  
def set_and_open_student(student):
    gb.set_cur_student(student)
    m_student_edit_del.open()

def set_and_open_reports_gradeable(gradeable):
    gb.set_cur_gradeable(gradeable)
    m_reports_gradeable.open()

def set_and_open_reports_student(student):
    gb.set_cur_student(student)
    m_reports_student.open()

#------------------------
# setup category menu logic
#------------------------
def set_category_options():
    m_category.options = []
    m_category.add_option("Return to Gradebook", m_category.close)
    m_category.add_option("Add Category", add_category)
    for item in gb.categories:
        m_category.add_option("{0:s} ({1:.1f})".format(item.name, item.pct_of_grade), 
                                    lambda i=item: set_and_open_category_edit_del(i))
        set_score_all_options()
        set_score_one_options()
        set_gradeable_options()

def set_category_edit_del_options():
    m_category_edit_del.options = []
    m_category_edit_del.add_option("Return to Category List", \
            m_category_edit_del.close)
    m_category_edit_del.add_option("Edit", edit_category)
    m_category_edit_del.add_option("Delete", delete_category)

#------------------------
# setup student menu logic
#------------------------
def set_student_options():
    m_student.options = []
    m_student.add_option("Return to Gradebook", m_student.close)
    m_student.add_option("Add Student", add_student)
    for item in gb.students:
        m_student.add_option(item.name() + ('' if item.is_active else ' *'), 
                                    lambda i=item: set_and_open_student(i))
        set_score_one_entry_options()
        set_reports_student_sel_options()

def set_student_edit_del_options():
    m_student_edit_del.options = []
    m_student_edit_del.add_option("Return to Student List", \
            m_student_edit_del.close)
    m_student_edit_del.add_option("Edit", edit_student)
    m_student_edit_del.add_option("Delete", delete_student)

def set_student_import_options():
    m_student_import.add_option("Return to Gradebook", \
            m_student_import.close)
    m_student_import.add_option("Import From File", import_students)

#------------------------
# setup gradeables menu logic
#------------------------
def set_gradeable_options():
    m_gradeable.options = []
    m_gradeable.add_option("Return to Gradebook", m_gradeable.close)
    m_gradeable.add_option("Add Graded Item", add_gradeable)
    for item in gb.gradeables:
        m_gradeable.add_option("{0:s}".format(item.name), 
                lambda i=item: set_gradeable_open_gradeable_edit_del(i))
        set_score_all_options()
        set_score_one_options()
        set_reports_gradeable_sel_options()

def set_gradeable_edit_del_options():
    m_gradeable_edit_del.options = []
    m_gradeable_edit_del.add_option("Return to Graded Items List", \
            m_gradeable_edit_del.close)
    m_gradeable_edit_del.add_option("Edit", edit_gradeable)
    m_gradeable_edit_del.add_option("Delete", delete_gradeable)

#------------------------
# score entry menu logic
#------------------------
def set_score_all_options():
    m_score_all.options=[]
    m_score_all.add_option("Return to Gradebook", m_score_all.close)
    for item in gb.gradeables:
        m_score_all.add_option(item.name, lambda i=item: input_scores(i))

def set_score_one_options():
    m_score_one.options=[]
    m_score_one.add_option("Return to Gradebook", m_score_one.close)
    for item in gb.gradeables:
        m_score_one.add_option(item.name, \
                lambda i=item: set_gradeable_open_score_one_entry(i))

def set_score_one_entry_options():
    m_score_one_entry.options=[]
    m_score_one_entry.add_option("Return to Student List", \
            m_score_one_entry.close)
    for item in gb.students:
        m_score_one_entry.add_option(item.name(), \
                lambda i=item: input_student_scores(i))

#------------------------
# report menu logic
#------------------------
def set_reports_options():
    m_reports.options = []
    m_reports.add_option("Return to Gradebook", m_reports.close)
    m_reports.add_option("Course Summary Report", rpt_course_summary)
    m_reports.add_option("Student Reports", m_reports_student_sel.open)
    m_reports.add_option("Graded Item Reports", m_reports_gradeable_sel.open)
    set_reports_gradeable_sel_options()
    set_reports_student_sel_options()

def set_reports_gradeable_sel_options():
    m_reports_gradeable_sel.options = []
    m_reports_gradeable_sel.add_option("Return to Report Menu", \
            m_reports_gradeable_sel.close)
    for item in gb.gradeables:
        m_reports_gradeable_sel.add_option(item.name, \
                lambda i=item : set_and_open_reports_gradeable(i))
    set_reports_gradeable_options()

def set_reports_student_sel_options():    
    m_reports_student_sel.options = []
    m_reports_student_sel.add_option("Return to Report Menu", \
            m_reports_student_sel.close)
    for item in gb.get_actives():
        m_reports_student_sel.add_option(item.name(), \
                lambda i=item : set_and_open_reports_student(i))
    set_reports_student_options

def set_reports_gradeable_options():
    m_reports_gradeable.options = []
    m_reports_gradeable.add_option("Return to Graded Item List", \
            m_reports_gradeable.close)
    m_reports_gradeable.add_option("Graded Item Statistics", \
            rpt_graded_item_stats)
    m_reports_gradeable.add_option("Graded Item Details", \
            rpt_graded_item_details)

def set_reports_student_options():
    m_reports_student.options = []
    m_reports_student.add_option("Return to Student List", \
            m_reports_student.close)
    m_reports_student.add_option("Student Scores", rpt_student_scores)

#------------------------
# main menu logic
#------------------------
def set_main_options():
    m_main.options = []
    m_main.add_option("Quit", save_and_exit)
    m_main.add_option("Save", save_current)
    m_main.add_option("Enter Scores All Students", m_score_all.open)
    m_main.add_option("Enter Scores One Student", m_score_one.open)
    m_main.add_option("Import Students", m_student_import.open)
    m_main.add_option("Manage Students", m_student.open)
    m_main.add_option("Manage Categories", m_category.open)
    m_main.add_option("Manage Graded Items", m_gradeable.open)
    m_main.add_option("Reports", m_reports.open)
    m_main.add_option("Edit Course", edit_course)

def initialize_menus():
    set_gradeable_edit_del_options()
    set_reports_options()
    set_main_options()

    # these will handle dependent options
    set_category_options()
    set_category_edit_del_options()
    set_student_options()
    set_student_edit_del_options()
    set_student_import_options()

#-------------
# Main Program
#-------------
if __name__ == "__main__":
    # Check the command line for a Course file.  
    # If none is found, start a new course with a default name
    if len(sys.argv) >= 2:
        gb = read(sys.argv[1])
    else:
        today = datetime.date.today()
        m = today.month
        term = "Winter" if m >=11 or m < 2 else \
                  "Spring" if m >= 2 and m < 5 else \
                  "Summer" if m >=5 and m < 8 else "Fall" 
        gb = Course('New Course', term + " " + \
                str(today.year + (1 if term == "Winter" else 0)))

    m_main = Menu(title = "Gradebook")
    m_course = Menu(title = "Edit Course")
    m_category = Menu(title = "Manage Categories")
    m_category_edit_del = Menu(title = "Edit / Delete Category")
    m_student = Menu(title = "Manage Students")
    m_student_edit_del = Menu(title = "Edit / Delete Student")
    m_student_import = Menu(title = \
            "Import Students from Tab-Separated Textfile 'students.txt'")
    m_gradeable = Menu(title = "Manage Graded Items")
    m_gradeable_edit_del = Menu(title = "Edit / Delete Graded Item")
    m_score_all = Menu(title = "Enter Scores (All Students)")
    m_score_one = Menu(title = "Enter Scores (One Student)")
    m_score_one_entry = Menu(title = "Enter Scores for Student")
    m_reports = Menu(title = "Reports")
    m_reports_gradeable_sel = Menu(title = "Select Graded Item")
    m_reports_gradeable = Menu(title = "Reports on Specific Graded Items")
    m_reports_student_sel = Menu(title = "Select Student")
    m_reports_student = Menu(title = "Reports on Individual Students")
    initialize_menus()
    subprocess.call(['speech-dispatcher'])    #start speech dispatcher   
    m_main.open()

