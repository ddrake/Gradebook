#!/usr/bin/env python3

import sys, os
import subprocess
import datetime
import numpy as np
from model import *
import persist
from ui_helper import *
import menus
import gmail
from report import SimpleReport, plot_hist

#--------------------
# Course Management
#--------------------
def edit_course(gb):
    name = get_string("Enter Course Name", gb.name)
    term = get_string("Enter Quarter", gb.term)
    gb.name = name
    gb.term = term

#--------------------
# Category Management
#--------------------
def add_category(gb):
    name = get_string("Enter Category Name")
    pct_of_grade = get_valid_float("Percent of Grade", 0, 100)
    drop_low_n = get_valid_int("Drop Lowest n", 0, 3, 0)
    cat = Category(gb, name, pct_of_grade, drop_low_n)
    gb.categories.append(cat)
    menus.set_category_options(gb)

def edit_category(gb):
    name = get_string("Enter Category Name", gb.cur_category.name)
    pct_of_grade = get_valid_float("Percent of Grade", 0, 100, gb.cur_category.pct_of_grade)
    gb.cur_category.drop_low_n = get_valid_int("Drop Lowest n", 0, 3, gb.cur_category.drop_low_n)
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
def add_student(gb):
    first = get_string("Enter First Name")
    last = get_string("Enter Last Name")
    email = get_string("Enter Email")
    gb.add_student(first, last, email)
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

def import_students(gb):
    try:
        with open('students.txt','r') as f:
            text = f.read()
        lines = text.rstrip().split('\n')
        for line in lines:
            first, last, email = line.split('\t')
            gb.add_student(first, last, email)
        gb.students.sort(key=lambda s : s.name())
        gb.actives = None
        menus.set_student_options(gb)
    except:
        print("The file 'students.txt' could not be found or was incorrectly formatted")
    pause()
#---------------------
# Gradeable Management
#---------------------
def add_gradeable(gb):
    if not gb.categories:
        print("Can't create a graded item until there is at least one category.")
        pause()
        return
    name = get_string("Enter Graded Item Name")
    cat = get_int_from_list("Select a numbered category", [c.name for c in gb.categories])
    category = gb.categories[cat-1]
    fpts = get_space_separated_floats("Enter question point values separated by whitespace")
    total_pts = get_valid_float("Total Points", sum(fpts)/2, sum(fpts), sum(fpts))
    gradeable = Gradeable(gb, name, category, total_pts)
    questions = [Question(gradeable, p) for p in fpts]
    gradeable.questions = questions
    gb.gradeables.append(gradeable)
    menus.set_gradeable_options(gb)

def edit_gradeable(gb):
    cg = gb.cur_gradeable
    name = get_string("Enter Graded Item Name", cg.name)
    def_sel = gb.categories.index(cg.category) + 1
    cat = get_int_from_list("Select a numbered category", [c.name for c in gb.categories], def_sel )
    category = gb.categories[cat-1]
    pts = [q.points for q in cg.questions]
    prev_tot = sum(pts)
    bonus = prev_tot - cg.total_pts
    if not cg.has_scores():
        fpts = get_space_separated_floats("Enter question point values separated by whitespace", pts)
        total_pts = get_valid_float("Total Points", sum(fpts)/2.0, sum(fpts), \
            cg.total_pts if prev_tot == sum(fpts) else sum(fpts) - bonus)
    else:
        print("Question points: ", pts)
        total_pts = get_valid_float("Total Points", prev_tot/2, prev_tot, cg.total_pts)
    sub_pct = get_valid_float("Retake Sub-percent", 0, 100, cg.sub_pct)
    added_pts = get_valid_float("Added Points", 0, 10000, cg.added_pts)
    added_pct = get_valid_float("Added Percent", 0, 100, cg.added_pct)
    cg.name = name if name else cg.name
    cg.category = category
    cg.total_pts = total_pts
    cg.sub_pct = sub_pct
    cg.added_pts = added_pts
    cg.added_pct = added_pct
    if not cg.has_scores():
        cg.questions = [Question(cg, p) for p in fpts]
    menus.set_gradeable_options(gb)

def delete_gradeable(gb):
    gb.remove_gradeable(gb.cur_gradeable)
    menus.set_gradeable_options(gb)
    menus.m_gradeable_edit_del.close()

def import_scores(gb):
    if gb.cur_gradeable.has_scores():
        print("Delete existing scores? (Y/N)")
        resp = input(">>> ")
        if resp.upper() != 'Y':
            return
        gb.cur_gradeable.delete_scores()
    try:
        with open('scores.txt','r') as f:
            text = f.read()
        lines = text.strip().split('\n')
        for line in lines:
            email, q1_score = line.split('\t')
            matches = [s for s in gb.students if s.email == email]
            if not matches:
                print("imported email '", email, "' doesn't match any student")
                continue
            if len(matches) > 1:
                print("imported email '", email, "' matches more than one student???")
                continue
            student = matches[0]
            score = gb.get_score(student, gb.cur_gradeable, gb.cur_gradeable.questions[0])
            score.value = float(q1_score)
        menus.set_reports_gradeable_sel_options(gb)
        menus.set_reports_student_sel_options(gb)
    except Exception as err:
        print("The file 'scores.txt' could not be found or was incorrectly formatted")
        print(err)
    finally:
        pause()

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
def rpt_graded_item_details(gb):
    cg = gb.cur_gradeable
    names = np.array([s.name() for s in gb.get_actives()])
    ar = np.array([[gb.get_score(s,cg,q).value for q in cg.questions] \
            for s in gb.get_actives()])
    tots = ar.sum(1)
    pcts = tots/cg.total_pts*100.0
    title="{0:s} Details".format(cg.name)
    plot_hist(pcts,title)
    totinds = tots.argsort()
    ar, names = ar[totinds,:], names[totinds]
    m,n = ar.shape
    tots, pcts = tots[totinds], pcts[totinds]
    col_headings = ["#{0:d}".format(j+1) for j in range(n)]
    rpt = SimpleReport(title, name_col_width=16, data_col_width=6, total_col_width=8, \
            name_col_name='Student', row_headings=names, col_headings=col_headings, \
            data=ar, total_col=tots, total_col_name = "Total", \
            pct_col=pcts, has_average_row=True)
    print(rpt.render())
    pause()

def rpt_class_detail(gb):
    gradeables = sorted(gb.gradeables_with_scores(), key=lambda g: g.name)
    if not gradeables:
        pause(msg="No Graded Items with Scores.")
        return
    names = np.array([s.name() for s in gb.get_actives()])
    col_headings = [g.name for g in gradeables]
    ar = np.array([[g.adjusted_score(s) for g in gradeables] for s in gb.get_actives()])
    possibles = np.array([g.total_pts for g in gradeables])
    pcts = ar/possibles*100.0
    aves = pcts.mean(1)
    title="Class Details Report"
    plot_hist(aves,title)
    aveinds = aves.argsort()
    pcts, names, aves = pcts[aveinds,:], names[aveinds], aves[aveinds]
    rpt = SimpleReport(title, name_col_width=16, data_col_width=8, total_col_width=8, \
            name_col_name='Student', row_headings=names, col_headings=col_headings, \
            data=pcts, total_col=aves, total_col_name="Avg.", has_average_row=True)
    print(rpt.render())
    pause()

def rpt_class_summary(gb):
    cats = gb.categories_with_scores()
    if not cats:
        pause(msg="No categories with Scores.")
        return
    names = np.array([s.name() for s in gb.get_actives()])
    cnames = [c.name for c in cats]
    pcts = np.array([[c.combined_pct(s) for c in cats] for s in gb.get_actives()])
    aves = pcts.mean(1)
    title="Class Summary Report"
    plot_hist(aves,title)
    aveinds = aves.argsort()
    pcts, names, aves = pcts[aveinds,:], names[aveinds], aves[aveinds]
    name_col_width, data_col_width, total_col_width = 16, 8, 8
    rpt = SimpleReport(title, name_col_width=16, data_col_width=8, total_col_width=8, \
            name_col_name="Student", row_headings=names, col_headings=cnames, \
            data = pcts, total_col=aves, total_col_name="Avg.", has_average_row=True)
    print(rpt.render())
    pause()

def student_summary_line_body(student, grade, cats, pcts, send_email):
    name_col_width = 16
    if send_email:
        salutation = "Hi {0:s},\n\n".format(student.first)
        salutation += "Here's your current estimated grade information: \n\n"
    else:
        salutation = "{0:s}".format(student.name()).ljust(name_col_width)

    grade_info = "Current Est. Grade: {0:.1f} based on: ".format(grade)
    n = len(cats)
    for j in range(n):
        cat = cats[j]
        punct = ', ' if j < n - 1 else '.'
        grade_info += "{0:s} (weighted {1:.0f}%): {2:.1f}%{3:s}" \
                .format(cat.name, cat.pct_of_grade, pcts[j], punct)
    if send_email:
        try:
            g = gmail.Gmail("Current Est. Grade", '')
            signature = g.signature 
            g.body = salutation + grade_info + '\n\n' + signature
            print(student.email)
            print(g.body)
            g.recipients = [student.email]
            g.send()
        except:
            print("failed to send the email.  ", \
                    "Perhaps there is something wrong with the signature file.")
    else:
        print(salutation, grade_info)

# Display or Email current grade status to a single student
def rpt_student_summary_line(gb, send_email=False, stud=None):
    cats = gb.categories_with_scores()
    if not cats:
        pause("No categories with Scores.")
        return
    student = stud if stud != None else gb.cur_student
    pcts = np.array([c.combined_pct(student) for c in cats])
    weights = np.array([cat.pct_of_grade for cat in cats])
    adj_weights = weights/sum(weights)
    grade = (pcts*adj_weights).sum()
    student_summary_line_body(student, grade, cats, pcts, send_email) 
    pause()

# Display or Email current grade status to all active students
def rpt_class_summary_line(gb, send_email=False):
    if send_email:
        print("Are you sure you want to email ALL students? (Y/N)")
        resp = input(">>> ")
        if resp.upper() != 'Y':
            return
    cats = gb.categories_with_scores()
    if not cats:
        pause(msg="No categories with Scores.")
        return
    students = gb.get_actives()
    pcts = np.array([[c.combined_pct(s) for c in cats] for s in students])
    m,n = pcts.shape
    weights = np.array([cat.pct_of_grade for cat in cats])
    adj_weights = weights/sum(weights)
    grades = (pcts*adj_weights).sum(1)
    for i in range(m):
        student = students[i]
        student_summary_line_body(student, grades[i], cats, pcts[i,:], send_email)
    pause()

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

