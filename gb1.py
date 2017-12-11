#!/usr/bin/env python3

import sys, os
import subprocess
from menu import Menu
import pickle
from enum import Enum
import datetime

class Status(Enum):
    ACTIVE = 1
    DROPPED = 2
    AUDITING = 3

# simple class definitions
class Course:
    def __init__(self, name = '', quarter = ''):
        self.name = name
        self.quarter = quarter
        self.categories = []
        self.gradeables = []
        self.students = []
        self.scores = []
        self.cur_student = None
        self.cur_gradeable = None
        self.cur_category = None
    
    # Set the current student from a menu action
    def set_cur_student(self, student):
        self.cur_student = student

    # Set the current gradeable item from a menu action
    def set_cur_gradeable(self, gradeable):
        self.cur_gradeable = gradeable

    # Set the current category from a menu action
    def set_cur_category(self, category):
        self.cur_category = category

    def file_name(self):
        return self.name.replace(' ','_') + "_" \
               + self.quarter.replace(' ','_') + ".p"

# todo: consider adding an inactive status field, but keep is_active for simplicity in reporting.
class Student:
    def __init__(self, first = '', last = '', email = '', is_active=True):
        self.first = first
        self.last = last
        self.email = email
        self.is_active = is_active
       
    def name(self):
        return self.first + (' ' + self.last[0] if self.last else '')

    def fullname(self):
        return self.first + ' ' + self.last
    
# I think we don't need to assign an explicit number to questions, their order is just the order in which they were added
class Question:
    def __init__(self, gradeable, points):
        self.gradeable = gradeable
        self.points = points

# We should have a category for any kind of item that could combine multiple gradeables
# For example we might need to give a retake option for Midterm 1 so Midterm 1 should be a category
class Category:
    def __init__(self, name='', pct_of_grade=0.0):
        self.name = name
        self.pct_of_grade = pct_of_grade

# Total points doesn't include bonus problems.  Added pts and added pct can be applied globally to curve a gradeable
class Gradeable:
    def __init__(self, name='', category = None, total_pts=0.0, sub_pct = 0.0, added_pts = 0.0, added_pct = 0.0):
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
    def __init__(self, student, gradeable, question):
        self.student = student
        self.gradeable = gradeable
        self.question = question
        self.value = 0.0

# Try to find a score in the scores list that matches the student, gradeable and question number
# If the question number is ok, but there is no score for that combination, create it and add to scores
def get_score(student, gradeable, question):
    q = gradeable.get_question(question)
    for s in gb.scores:
        if s.student is student and s.gradeable is gradeable and s.question is question:
            return s
    s = Score(student, gradeable, question)
    gb.scores.append(s)
    return s

def read(file_name):
    with open(file_name,'rb') as f:
        return pickle.load(f)

def save(course, file_name):
    with open(file_name,'wb') as f:
        pickle.dump(course, f)

def save_and_exit():
    save(gb, gb.file_name())
    m_main.close()
   
def save_current():
    save(gb, gb.file_name())

def input_scores(gradeable):
    gb.set_cur_gradeable(gradeable)
    return input_score( 0, 0)

def input_student_scores(student):
    gb.set_cur_student(student)
    return input_student_score( 0 )

# sets the current gradeable and then opens a menu item
def set_gradeable_open_score_one_entry(gradeable):
    gb.set_cur_gradeable(gradeable)
    m_score_one_entry.open()

def set_gradeable_open_gradeable_edit_del(gradeable):
    gb.set_cur_gradeable(gradeable)
    m_gradeable_edit_del.open()

def set_and_open_category(category):
    gb.set_cur_category(category)
    m_category_edit_del.open()
  
def set_and_open_student(student):
    gb.set_cur_student(student)
    m_student_edit_del.open()
  
def get_string(title, default=None, prompt=" >> "):
    ftitle = title if default == None else title + " ({0:s})".format(default)
    print(ftitle)
    sval = input(prompt)
    return default if default != None and sval == '' else sval

def get_bool(title, default=None, prompt=" >> "):
    ftitle = title if default == None else title + " ({0:s})".format('Y' if default == True else 'N')
    while True:
        print(ftitle)
        sval = input(prompt).lower()
        if default != None and sval == '':
            return default
        if sval == 'y':
            return True
        elif sval == 'n':
            return False
        else:
            say("invalid")
            print("Value should be Y or N")

def bool_to_yn(flag):
    return "Y" if flag == True else "N"


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
    gb.categories.remove(gb.cur_category)
    gb.cur_category = None
    set_category_options()

def import_students():
    with open('students.txt','r') as f:
        text = f.read()
    lines = text.rstrip().split('\n')
    for line in lines:
        first, last, email = line.split()
        gb.students.append(Student(first, last, email))
    set_student_options()
    print('imported students')

def add_student():
    first = get_string("Enter First Name")
    last = get_string("Enter Last Name")
    email = get_string("Enter Email")
    is_active = get_bool("Is the Student Active? (y/n)", True)
    student = Student(first, last, email, is_active)
    gb.students.append(student)
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
    set_student_options()

def delete_student():
    gb.students.remove(gb.cur_student)
    gb.cur_student = None
    set_student_options()

def add_course():
    first = get_string("Enter Course Name (e.g. Math 251)")
    last = get_string("Enter Quarter (e.g. W18")
    gb.students.append(student)
    set_student_options()

def edit_course():
    name = get_string("Enter Course Name", gb.name)
    quarter = get_string("Enter Quarter", gb.quarter)
    gb.name = name
    gb.quarter = quarter

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
    gb.gradeables.remove(gb.cur_gradeable)
    gb.cur_gradeable = None
    set_gradeable_options()

# Given indices into the students and questions lists, validate the indices, then if possible
# Prompt the user for values for the specified student/question
# Also give the user the option to go back to the previous question or jump to the next or previous student.
# Also give the user the option to return to the previous menu
# If the indices are out of bounds, go to the first question last question for the last student.
def input_score(st_idx, q_idx):
    cg = gb.cur_gradeable
    if st_idx < 0 or st_idx >= len(gb.students):
        input_score( 0, 0)
    elif q_idx >= len(cg.questions):
        input_score(st_idx + 1, 0)
    elif q_idx < 0:
        input_score( st_idx - 1, -1)
    else:
        s = gb.students[st_idx]
        q = cg.questions[q_idx]
        score = get_score(s, cg, q)
        print("{0:s}: {1:s}, {2:d}. ({3:.1f})".format(cg.name, s.name(), q_idx+1, score.value))
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


# Given an index into the question list, validate the index, then if possible
# Prompt the user for values for the specified question
# Also give the user the option to go back to the previous question.
# Also give the user the option to return to the previous menu
# If the indices are out of bounds, go to the first question 
def input_student_score( q_idx):
    cg = gb.cur_gradeable
    s = gb.cur_student
    if q_idx >= len(cg.questions):
        input_student_score( 0)
    elif q_idx < 0:
        input_student_score( -1)
    else:
        q = cg.questions[q_idx]
        score = get_score(s, cg, q)
        print("{0:s}: {1:s}, {2:d}. ({3:.1f})".format(cg.name, s.name(), q_idx+1, score.value))
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

def say(phrase):
    #subprocess.call(['speech-dispatcher'])    #start speech dispatcher   
    subprocess.call(['spd-say', '-w', '"{0:s}"'.format(phrase)])

# Temporary test data.  Will be replaced by real pickled data.
def test_data():
    # Test data
    gb = Course('Math 251', 'W18')

    joe = Student('Joe', 'Smith')
    sue = Student('Sue', 'Jones')
    jeff = Student('Jeff', 'West')
    gb.students = [joe, sue, jeff]

    
    att = Category('Class Participation', 5.0)
    hw = Category('Homework', 5.0)
    quiz = Category('Quiz', 25.0)
    mid1 = Category('Midterm 1', 20.0)
    mid2 = Category('Midterm 2', 20.0)
    #final = Category('Final', 25.0)
    gb.categories = [att, hw, quiz, mid1, mid2]

    quiz1 = Gradeable('Quiz 1', quiz, 22)
    quiz1.add_question(5)
    quiz1.add_question(5)
    quiz1.add_question(5)
    quiz1.add_question(5)
    gb.gradeables.append(quiz1)

    quiz2 = Gradeable('Quiz 2', quiz, 20)
    quiz2.add_question(5)
    quiz2.add_question(5)
    quiz2.add_question(5)
    quiz2.add_question(5)
    gb.gradeables.append(quiz2)

    return gb


#------------------------
# setup category menu logic
#------------------------
def set_category_options():
    m_category.options = []
    m_category.add_option("Return to Gradebook", m_category.close)
    m_category.add_option("Add Category", add_category)
    for item in gb.categories:
        m_category.add_option("{0:s} ({1:.1f})".format(item.name, item.pct_of_grade), 
                                    lambda i=item: set_and_open_category(i))
        set_score_all_options()
        set_score_one_options()
        set_gradeable_options()

def set_category_edit_del_options():
    m_category_edit_del.options = []
    m_category_edit_del.add_option("Return to Manage Categories", m_category_edit_del.close)
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
        #m_student.add_option(item.name(), lambda i=item: set_and_open_student(i))
        set_score_one_entry_options()

def set_student_edit_del_options():
    m_student_edit_del.options = []
    m_student_edit_del.add_option("Return to Manage Students", m_student_edit_del.close)
    m_student_edit_del.add_option("Edit", edit_student)
    m_student_edit_del.add_option("Delete", delete_student)

def set_student_import_options():
    m_student_import.add_option("Return to Gradebook", m_student_import.close)
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

def set_gradeable_edit_del_options():
    m_gradeable_edit_del.options = []
    m_gradeable_edit_del.add_option("Return to Manage Graded Items", m_gradeable_edit_del.close)
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
        m_score_one.add_option(item.name, lambda i=item: set_gradeable_open_score_one_entry(i))

def set_score_one_entry_options():
    m_score_one_entry.options=[]
    m_score_one_entry.add_option("Return to Student Selection", m_score_one_entry.close)
    for item in gb.students:
        m_score_one_entry.add_option(item.name(), lambda i=item: input_student_scores(i))

#------------------------
# report menu logic
#------------------------
def set_reports_options():
    m_reports.options = []
    m_reports.add_option("Return to Gradebook", m_reports.close)

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

# Main Program
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        gb = read(sys.argv[1])
    else:
        today = datetime.date.today()
        m = today.month
        quarter = "Winter" if m >=11 or m < 2 else \
                  "Spring" if m >= 2 and m < 5 else \
                  "Summer" if m >=5 and m < 8 else "Fall" 
        gb = Course('New Course', quarter + " " + str(today.year + (1 if quarter == "Winter" else 0)))
        #gb = test_data()

    m_main = Menu(title = "Gradebook")
    m_course = Menu(title = "Edit Course")
    m_category = Menu(title = "Manage Categories")
    m_category_edit_del = Menu(title = "Edit / Delete Category")
    m_student = Menu(title = "Manage Students")
    m_student_edit_del = Menu(title = "Edit / Delete Student")
    m_student_import = Menu(title = "Import Students from Tab-Separated Textfile 'students.txt'")
    m_gradeable = Menu(title = "Manage Graded Items")
    m_gradeable_edit_del = Menu(title = "Edit / Delete Graded Item")
    m_score_all = Menu(title = "Enter Scores (All Students)")
    m_score_one = Menu(title = "Enter Scores (One Student)")
    m_score_one_entry = Menu(title = "Enter Scores for Student")
    m_reports = Menu(title = "Reports")

    initialize_menus()
    m_main.open()
