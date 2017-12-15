#!/usr/bin/env python3

import sys, os
import subprocess
import datetime
import numpy as np
from matplotlib import pyplot as plt 
from model import *
import persist
from ui_helper import *
import menus
import gmail
#--------------------
# Category Management
#--------------------
def add_category(gb):
    name = get_string("Enter Category Name")
    pct_of_grade = get_valid_float("Percent of Grade", 0, 100)
    cat = Category(gb, name, pct_of_grade)
    gb.categories.append(cat)
    menus.set_category_options(gb)

def edit_category(gb):
    name = get_string("Enter Category Name", gb.cur_category.name)
    pct_of_grade = get_valid_float("Percent of Grade", 0, 100, gb.cur_category.pct_of_grade)
    gb.cur_category.name = name if name else gb.cur_category.name
    gb.cur_category.pct_of_grade = pct_of_grade
    menus.set_category_options(gb)

def delete_category(gb):
    gb.remove_category(gb.cur_category)
    menus.set_category_options(gb)
    menus.m_category_edit_del.close()

#-------------------
# Student Management
#-------------------
def import_students(gb):
    with open('students.txt','r') as f:
        text = f.read()
    lines = text.rstrip().split('\n')
    for line in lines:
        first, last, email = line.split('\t')
        gb.students.append(Student(first, last, email))
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    menus.set_student_options(gb)

def add_student(gb):
    first = get_string("Enter First Name")
    last = get_string("Enter Last Name")
    email = get_string("Enter Email")
    is_active = get_bool("Is the Student Active? (y/n)", 1)
    student = Student(first, last, email, is_active)
    gb.students.append(student)
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    menus.set_student_options(gb)

def edit_student(gb):
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
    menus.set_student_options(gb)

def delete_student(gb):
    gb.remove_student(gb.cur_student)
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    menus.set_student_options(gb)
    menus.m_student_edit_del.close()
#------------------
# Course Management
#------------------
def add_course(gb):
    first = get_string("Enter Course Name (e.g. Math 251)")
    last = get_string("Enter Quarter (e.g. W18")
    gb.students.append(student)
    menus.set_student_options(gb)

def edit_course(gb):
    name = get_string("Enter Course Name", gb.name)
    term = get_string("Enter Quarter", gb.term)
    gb.name = name
    gb.term = term

#---------------------
# Gradeable Management
#---------------------
def add_gradeable(gb):
    name = get_string("Enter Graded Item Name")
    cat = get_int_from_list("Select a numbered category", [c.name for c in gb.categories])
    category = gb.categories[cat-1]
    total_pts = get_valid_float("Total Points", 0, 10000)
    fpts = get_space_separated_floats("Enter question point values separated by whitespace", total_pts)
    sub_pct = get_valid_float("Retake Sub-percent", 0, 100, 0.0)
    added_pts = get_valid_float("Added Points", 0, 10000, 0.0)
    added_pct = get_valid_float("Added Percent", 0, 100, 0.0)
    gradeable = Gradeable(gb, name, category, total_pts, sub_pct, added_pts, added_pct)
    questions = [Question(gradeable, p) for p in fpts]
    gradeable.questions = questions
    gb.gradeables.append(gradeable)
    menus.set_gradeable_options(gb)

def edit_gradeable(gb):
    cg = gb.cur_gradeable
    has_scores = any(s for s in gb.scores if s.gradeable is cg)
    name = get_string("Enter Graded Item Name", cg.name)
    def_sel = gb.categories.index(cg.category) + 1
    cat = get_int_from_list("Select a numbered category", [c.name for c in gb.categories], def_sel )
    category = gb.categories[cat-1]
    total_pts = get_valid_float("Total Points", 0, 10000, cg.total_pts)
    if not has_scores:
        pts = [q.points for q in cg.questions]
        fpts = get_space_separated_floats("Enter question point values separated by whitespace", \
                total_pts, pts)
    sub_pct = get_valid_float("Retake Sub-percent", 0, 100, cg.sub_pct)
    added_pts = get_valid_float("Added Points", 0, 10000, cg.added_pts)
    added_pct = get_valid_float("Added Percent", 0, 100, cg.added_pct)
    cg.name = name if name else cg.name
    cg.category = category
    cg.total_pts = total_pts
    cg.sub_pct = sub_pct
    cg.added_pts = added_pts
    cg.added_pct = added_pct
    if not has_scores:
        cg.questions = [Question(cg, p) for p in fpts]
    menus.set_gradeable_options(gb)

def delete_gradeable(gb):
    gb.remove_gradeable(gb.cur_gradeable)
    menus.set_gradeable_options(gb)
    menus.m_gradeable_edit_del.close()
#------------
# Score Entry
#------------
# Helper for input_score - starts the recursion
def input_scores(gb,gradeable):
    gb.set_cur_gradeable(gradeable)
    input_score(gb, 0, 0)
    menus.set_reports_gradeable_sel_options(gb)
    menus.set_reports_student_sel_options(gb)

def input_score(gb, st_idx, q_idx):
    cg = gb.cur_gradeable
    q_ct = len(cg.questions)
    s_ct = len(gb.get_actives())
    if st_idx <= 0 and q_idx < 0:
        print("First One")
        say("first one")
        input_score(gb, 0, 0)
    elif st_idx >= s_ct - 1 and q_idx >= q_ct:
        print("Last One")
        say("last one")
        input_score(gb, s_ct-1, q_ct-1)
    elif q_idx >= q_ct:
        input_score(gb,st_idx + 1, 0)
    elif q_idx < 0:
        input_score(gb, st_idx - 1, -1)
    else:
        s = gb.students[st_idx]
        q = cg.questions[q_idx]
        score = gb.get_score(s, cg, q)

        print("{0:s}: {1:s}, {2:d}. ({3:.1f})".format(cg.name, \
                s.name(), q_idx+1, score.value))
        value = input(" >> ")
        if value.lower() == 'q':
            return False
        if value.lower() == 'b':
            input_score(gb, st_idx, q_idx-1)
        elif value == '':
            input_score(gb, st_idx, q_idx+1)
        elif value.lower() == 'n':
            input_score(gb, st_idx+1, 0)
        elif value.lower() == 'p':
            input_score(gb, st_idx-1, 0)
        else:
            try:
                tval = float(value)
                if tval <= q.points and tval >= 0:
                    score.value = tval
                    input_score(gb, st_idx, q_idx+1)
                else:
                    say("invalid")
                    print("Invalid score")
                    input_score(gb, st_idx, q_idx)
            except ValueError:
                say("What?")
                print("What?")
                input_score(gb, st_idx, q_idx)

# Helper for input_student_score -- starts the recursion
def input_student_scores(gb, student):
    gb.set_cur_student(student)
    input_student_score( gb,0 )
    menus.set_reports_gradeable_sel_options(gb)
    menus.set_reports_student_sel_options(gb)

def input_student_score(gb, q_idx):
    cg = gb.cur_gradeable
    s = gb.cur_student
    q_ct = len(cg.questions)

    if q_idx >= len(cg.questions):
        print("Last One")
        say("last one")
        input_student_score(gb, q_ct - 1)
    elif q_idx < 0:
        print("First One")
        say("first one")
        input_student_score(gb, 0 )
    else:
        q = cg.questions[q_idx]
        score = gb.get_score(s, cg, q)
        print("{0:s}: {1:s}, {2:d}. ({3:.1f})".format(cg.name, \
                s.name(), q_idx+1, score.value))
        value = input(" >> ")
        if value.lower() == 'q':
            return False
        if value.lower() == 'b':
            input_student_score(gb, q_idx-1)
        elif value == '':
            input_student_score(gb, q_idx+1)
        else:
            try:
                tval = float(value)
                if tval <= q.points and tval >= 0:
                    score.value = tval
                    input_student_score(gb, q_idx+1)
                else:
                    say("invalid")
                    print("Invalid score")
                    input_student_score(gb, q_idx)
            except ValueError:
                say("What?")
                print("What?")
                input_student_score(gb, q_idx)

#--------
# Reports
#--------

def plot_hist(pcts, title):
    h=np.histogram(pcts,bins=(0,60,70,80,90,100))
    barlist = plt.bar(range(5),h[0],width=0.85)
    colors = ['#ff0000', '#ff8000', '#ffff00', '#0080ff','#00ff00']
    for i in range(5):
        barlist[i].set_color(colors[i])
    xlab=['F', 'D', 'C', 'B', 'A']
    plt.xticks(np.arange(5),xlab)
    plt.title(title)
    plt.show()

def rpt_graded_item_details(gb):
    cg = gb.cur_gradeable
    names = np.array([s.name() for s in gb.get_actives()])
    ar = np.array([[gb.get_score(s,cg,q).value for q in cg.questions] \
            for s in gb.get_actives()])
    n,m = ar.shape
    tots = ar.sum(1)
    pcts = tots/cg.total_pts*100.0
    title="{0:s} Details".format(cg.name)
    plot_hist(pcts,title)
    totinds = tots.argsort()
    ar, names = ar[totinds,:], names[totinds]
    tots, pcts = tots[totinds], pcts[totinds]
    name_col_width, data_col_width, total_col_width = 16, 6, 8
    print(title)
    print("-"*len(title))
    print("Student".ljust(name_col_width), end='')
    for j in range(m):
        print("#{0:d}".format(j+1).rjust(data_col_width), end='')
    print("Total".rjust(total_col_width),end='')
    print("Pct.".rjust(total_col_width))
    print("-"*(name_col_width + m*data_col_width + 2*total_col_width))
    for i in range(n):
        print("{0:s}".format(names[i]).ljust(name_col_width), end='')
        for j in range(m):
            print("{0:.1f}".format(ar[i,j]).rjust(data_col_width), end='')
        print("{0:.1f}".format(tots[i]).rjust(total_col_width), end='')
        print("{0:.1f}".format(pcts[i]).rjust(total_col_width))

    print("-"*(name_col_width + m*data_col_width + 2*total_col_width))
    print("Average".ljust(name_col_width), end='')
    for j in range(m):
        print("{0:.1f}".format(ar[:,j].mean()).rjust(data_col_width), end='')
    print("{0:.1f}".format(tots.mean()).rjust(total_col_width), end='')
    print("{0:.1f}".format(pcts.mean()).rjust(total_col_width))
    print('')
    print('')
    input("Press <Enter>")


def rpt_class_detail(gb):
    gradeables = gb.gradeables_with_scores()
    if len(gradeables) == 0:
        input("No Graded Items with Scores - <Enter> to continue")
        return
    names = np.array([s.name() for s in gb.get_actives()])
    gnames = [g.name for g in gradeables]
    ar = np.array([[g.adjusted_score(s) for g in gradeables] for s in gb.get_actives()])
    n,m = ar.shape
    possibles = np.array([g.total_pts for g in gradeables])
    pcts = ar/possibles*100.0
    aves = pcts.mean(1)
    title="Class Details Report"
    plot_hist(aves,title)
    aveinds = aves.argsort()
    pcts, names, aves = pcts[aveinds,:], names[aveinds], aves[aveinds]
    name_col_width, data_col_width, total_col_width = 16, 8, 8
    print(title)
    print("-"*len(title))
    print("Student".ljust(name_col_width), end='')
    for gn in gnames:
        print("{0:s}".format(gn).rjust(data_col_width), end='')
    print("Avg.".rjust(total_col_width))
    print("-"*(name_col_width + m*data_col_width + total_col_width))
    for i in range(n):
        print("{0:s}".format(names[i]).ljust(name_col_width), end='')
        for j in range(m):
            print("{0:.1f}".format(pcts[i,j]).rjust(data_col_width), end='')
        print("{0:.1f}".format(aves[i]).rjust(total_col_width))
    print("-"*(name_col_width + m*data_col_width + total_col_width))
    print("Average".ljust(name_col_width), end='')
    for j in range(m):
        print("{0:.1f}".format(pcts[:,j].mean()).rjust(data_col_width), end='')
    print("{0:.1f}".format(aves.mean()).rjust(total_col_width))
    print('')
    print('')
    input("Press <Enter>")

def rpt_class_summary(gb):
    cats = gb.categories_with_scores()
    if len(cats) == 0:
        input("No categories with Scores - <Enter> to continue")
        return
    names = np.array([s.name() for s in gb.get_actives()])
    cnames = [c.name for c in cats]
    ar = np.array([[c.combined_score(s) for c in cats] for s in gb.get_actives()])
    n,m = ar.shape
    possibles = np.array([sum([g.total_pts for g in c.gradeables_with_scores()]) for c in cats])
    pcts = ar/possibles*100.0
    aves = pcts.mean(1)
    title="Class Summary Report"
    plot_hist(aves,title)
    aveinds = aves.argsort()
    pcts, names, aves = pcts[aveinds,:], names[aveinds], aves[aveinds]
    name_col_width, data_col_width, total_col_width = 16, 8, 8
    print(title)
    print("-"*len(title))
    print("Student".ljust(name_col_width), end='')
    for cn in cnames:
        print("{0:s}".format(cn).rjust(data_col_width), end='')
    print("Avg.".rjust(total_col_width))
    print("-"*(name_col_width + m*data_col_width + total_col_width))
    for i in range(n):
        print("{0:s}".format(names[i]).ljust(name_col_width), end='')
        for j in range(m):
            print("{0:.1f}".format(pcts[i,j]).rjust(data_col_width), end='')
        print("{0:.1f}".format(aves[i]).rjust(total_col_width))
    print("-"*(name_col_width + m*data_col_width + total_col_width))
    print("Average".ljust(name_col_width), end='')
    for j in range(m):
        print("{0:.1f}".format(pcts[:,j].mean()).rjust(data_col_width), end='')
    print("{0:.1f}".format(aves.mean()).rjust(total_col_width))
    print('')
    print('')
    input("Press <Enter>")

def student_summary_line_body(student, grade, cats, pcts, send_email):
    name_col_width = 16
    if send_email:
        salutation = "Hi {0:s},\n\n".format(student.first)
        salutation += "Here's your current estimated grade information: \n\n"
    else:
        salutation = "{0:s}".format(student.name()).ljust(name_col_width)

    grade_info = "Current Est. Grade: {0:.1f} based on: ".format(grade)
    m = len(cats)
    for j in range(m):
        cat = cats[j]
        punct = ', ' if j < m - 1 else '.'
        grade_info += "{0:s} (weighted {1:.0f}%): {2:.1f}%{3:s}" \
                .format(cat.name, cat.pct_of_grade, pcts[j], punct)
    if send_email:
        signature = "\n\nBest, Dow"
        g = gmail.Gmail("Current Est. Grade", salutation + grade_info + signature)
        print(student.email)
        print(salutation + grade_info + signature)
        g.recipients = [student.email]
        g.send()
    else:
        print(salutation, grade_info)

# Display or Email current grade status to a single student
def rpt_student_summary_line(gb, send_email=False, stud=None):
    cats = gb.categories_with_scores()
    if len(cats) == 0:
        input("No categories with Scores - <Enter> to continue")
        return
    student = stud if stud != None else gb.cur_student
    ar = np.array([c.combined_score(student) for c in cats])
    possibles = np.array([sum([g.total_pts for g in c.gradeables_with_scores()]) for c in cats])
    pcts = ar/possibles*100.0
    weights = np.array([cat.pct_of_grade for cat in cats])
    adj_weights = weights/sum(weights)
    grade = (pcts*adj_weights).sum()
    student_summary_line_body(student, grade, cats, pcts, send_email) 
    input("Press <Enter>")

# Display or Email current grade status to all students
def rpt_class_summary_line(gb, send_email=False):
    cats = gb.categories_with_scores()
    if len(cats) == 0:
        input("No categories with Scores - <Enter> to continue")
        return
    students = gb.get_actives()
    ar = np.array([[c.combined_score(s) for c in cats] for s in students])
    n,m = ar.shape
    possibles = np.array([sum([g.total_pts for g in c.gradeables_with_scores()]) for c in cats])
    pcts = ar/possibles*100.0
    weights = np.array([cat.pct_of_grade for cat in cats])
    adj_weights = weights/sum(weights)
    grades = (pcts*adj_weights).sum(1)
    for i in range(n):
        student = students[i]
        rpt_student_summary_line_body(student, grades[i], cats, pcts[i,:], send_email)
    input("Press <Enter>")

def save_and_exit(gb):
    persist.save(gb, gb.file_name())
    menus.m_main.close()
   
def save_current(gb):
    save(gb, gb.file_name())

#-------------
# Main Program
#-------------
if __name__ == "__main__":
    # Check the command line for a Course file.  
    # If none is found, start a new course with a default name
    if len(sys.argv) >= 2:
        gb = persist.read(sys.argv[1])
    else:
        today = datetime.date.today()
        m = today.month
        term = "Winter" if m >=11 or m < 2 else \
                  "Spring" if m >= 2 and m < 5 else \
                  "Summer" if m >=5 and m < 8 else "Fall" 
        gb = Course('New Course', term + " " + \
                str(today.year + (1 if term == "Winter" else 0)))

    menus.initialize_menus(gb)
    #subprocess.call(['speech-dispatcher'])    #start speech dispatcher   
    menus.m_main.open()

