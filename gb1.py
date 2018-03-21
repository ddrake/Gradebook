#!/usr/bin/env python3

import sys, os
import datetime
import numpy as np
from model import *
import persist
import ui_helper as ui
import menus
import gmail
from report import SimpleReport, plot_hist

#--------------------
# Course Management
#--------------------
def edit_course(gb):
    name = ui.get_string("Enter Course Name", gb.name)
    term = ui.get_string("Enter Quarter", gb.term)
    gb.name = name
    gb.term = term
    menus.set_main_options(gb)

#--------------------
# Category Management
#--------------------
def add_category(gb):
    name = ui.get_string("Enter Category Name")
    pct_of_grade = ui.get_valid_float("Percent of Grade", 0, 100)
    drop_low_n = ui.get_valid_int("Drop Lowest n", 0, 3, 0)
    est_ct = ui.get_valid_int("Estimated Items", 0, 100, 0)
    cat = Category(gb, name, pct_of_grade, drop_low_n, est_ct)
    gb.categories.append(cat)
    menus.set_category_options(gb)

def edit_category(gb):
    name = ui.get_string("Enter Category Name", gb.cur_category.name)
    pct_of_grade = ui.get_valid_float("Percent of Grade", 0, 100, gb.cur_category.pct_of_grade)
    gb.cur_category.drop_low_n = ui.get_valid_int("Drop Lowest n", 0, 3, gb.cur_category.drop_low_n)
    est_ct = ui.get_valid_int("Estimated Items", 0, 100, gb.cur_category.est_ct)
    gb.cur_category.name = name or gb.cur_category.name
    gb.cur_category.pct_of_grade = pct_of_grade
    gb.cur_category.est_ct = est_ct
    menus.set_category_options(gb)

def delete_category(gb):
    gb.remove_category(gb.cur_category)
    menus.set_category_options(gb)
    menus.m_category_edit_del.close()

#-------------------
# Student Management
#-------------------
def add_student(gb):
    first = ui.get_string("Enter First Name")
    last = ui.get_string("Enter Last Name")
    email = ui.get_string("Enter Email")
    gb.add_student(first, last, email)
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    menus.set_student_options(gb)
    menus.set_student_last_first_options(gb)

def edit_student(gb):
    first = ui.get_string("Enter First Name", gb.cur_student.first)
    last = ui.get_string("Enter Last Name", gb.cur_student.last)
    email = ui.get_string("Enter Email", gb.cur_student.email)
    is_active = ui.get_bool("Is the Student Active? (y/n)", gb.cur_student.is_active)
    notes = ui.get_string("Append Notes", gb.cur_student.notes, is_append=True)
    gb.cur_student.first = first
    gb.cur_student.last = last
    gb.cur_student.email = email
    gb.cur_student.is_active = is_active
    if notes:
        if gb.cur_student.notes:
            gb.cur_student.notes += '  '
        gb.cur_student.notes += notes
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None 
    menus.set_student_options(gb)
    menus.set_student_last_first_options(gb)

def delete_student(gb):
    gb.remove_student(gb.cur_student)
    gb.students.sort(key=lambda s : s.name())
    gb.actives = None
    menus.set_student_options(gb)
    menus.set_student_last_first_options(gb)
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
        menus.set_student_last_first_options(gb)
    except:
        print("The file 'students.txt' could not be found or was incorrectly formatted")
    ui.pause()

def export_students(gb):
    try:
        with open('students.txt','w') as f:
            f.write("First Name\tLast Name\tEmail\tEst. Grade\tNotes\tActive?\tHas Scores\n")
            f.write("\n".join(["{}\t{}\t{}\t{}\t{}\t{}\t{}".format( \
                s.first, s.last, s.email, ui.num_na_str(s.estimated_grade()), s.notes, \
                "Y" if s.is_active else "N", \
                "Y" if s.has_scores() else "N") for s in gb.students]))
    except Exception as ex:
        print(ex)
    else:
        ui.open_in_calc('students.txt')
    ui.pause()

#---------------------
# Gradeable Management
#---------------------
def add_gradeable(gb):
    if not gb.categories:
        ui.pause("Can't create a graded item until there is at least one category.")
        return
    name = ui.get_string("Enter Graded Item Name")
    cat = ui.get_int_from_list("Select a numbered category", [c.name for c in gb.categories])
    category = gb.categories[cat-1]
    fpts = ui.get_space_separated_floats("Enter question point values separated by whitespace")
    total_pts = ui.get_valid_float("Total Points", sum(fpts)/2, sum(fpts), sum(fpts))
    gradeable = Gradeable(gb, name, category, total_pts)
    questions = [Question(gradeable, p) for p in fpts]
    gradeable.questions = questions
    gb.gradeables.append(gradeable)
    menus.set_gradeable_options(gb)

def edit_gradeable(gb):
    cg = gb.cur_gradeable
    name = ui.get_string("Enter Graded Item Name", cg.name)
    def_sel = gb.categories.index(cg.category) + 1
    cat = ui.get_int_from_list("Select a numbered category", [c.name for c in gb.categories], def_sel )
    category = gb.categories[cat-1]
    pts = [q.points for q in cg.questions]
    prev_tot = sum(pts)
    bonus = prev_tot - cg.total_pts
    if not cg.has_scores():
        fpts = ui.get_space_separated_floats("Enter question point values separated by whitespace", pts)
        total_pts = ui.get_valid_float("Total Points", sum(fpts)/2.0, sum(fpts), \
            cg.total_pts if prev_tot == sum(fpts) else sum(fpts) - bonus)
    else:
        print("Question points: ", pts)
        total_pts = ui.get_valid_float("Total Points", prev_tot/2, prev_tot, cg.total_pts)
    sub_pct = ui.get_valid_float("Retake Sub-percent", 0, 100, cg.sub_pct)
    added_pts = ui.get_valid_float("Added Points", 0, 10000, cg.added_pts)
    added_pct = ui.get_valid_float("Added Percent", 0, 100, cg.added_pct)
    cg.name = name or cg.name
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

# Looks for a online_scores.txt file with downloaded scores containing last-first names
# and overall assignment scores.  If not found, import fails.  
# Next looks for optional online_xref.txt file. If found, this file should contain 
# last-first names matching those in online_scores.txt and emails matching those in gradebook.
# In this case, students are matched by cross referencing.
# If no online_xref.txt file is found, students are matched by upcased last-first names.
def import_scores(gb):
    if gb.cur_gradeable.has_scores():
        if not ui.confirm("Delete existing scores?"): return
        gb.cur_gradeable.delete_scores()
    try:
        with open('online_scores.txt','r') as f:
            text = f.read()
        scores = []        
        lines = text.strip().split('\n')
        scores = [line.split('\t') for line in lines]
    except Exception as err:
        print("The file 'online_scores.txt' could not be found or was incorrectly formatted")
        print(err)
        ui.pause()
    try:
        with open('online_xref.txt','r') as f:
            xref_text = f.read()
    except:
        pass
    else:
        try:
            xref_list = [line.split('\t') for line in xref_text.strip().split('\n') ]
            xref = {name: email for name, email in xref_list}
        except Exception as err:
            print("The file 'online_xref.txt' was incorrectly formatted")
            print(err)
            ui.pause()

    update_scores(gb, scores, xref)

    menus.set_reports_gradeable_sel_options(gb)
    menus.set_reports_student_sel_options(gb)
    menus.set_gradeable_options(gb)
    ui.pause()

def update_scores(gb, scores, xref):
    for [name, q1_score] in scores:
        if name[0] == '"':
            name = name[1:-1] # remove quotes (if any)
        if xref:
            if name not in xref:
                print(name, " is not in the xref dict")
                continue
            matches = [s for s in gb.students if s.email == xref[name]]
        else:
            matches = [s for s in gb.students if s.lastfirst == name]
        if not matches:
            print("imported name '", name, "' doesn't match any student")
            continue
        if len(matches) > 1:
            print("imported name '", name, "' matches more than one student???")
            continue
        if not matches:
            print("")

        student = matches[0]
        score = gb.get_score(student, gb.cur_gradeable, gb.cur_gradeable.questions[0])
        score.value = float(q1_score)



#------------
# Score Entry
#------------
def input_scores(gb, cg):
    ss = gb.get_actives()
    qs = cg.questions
    s_idx, q_idx = 0, 0
    s_ct, q_ct = len(ss), len(qs)
    done = False
    while not done:
        s_idx, q_idx = handle_limits(s_idx, q_idx, s_ct, q_ct)
        s, q = ss[s_idx], qs[q_idx]
        score = gb.get_score(s, cg, q)
        done, s_idx, q_idx = get_input(score, s, cg, q, s_idx, q_idx)
    menus.set_reports_gradeable_sel_options(gb)

def input_student_scores(gb, s):
    cg = gb.cur_gradeable
    qs = cg.questions
    q_idx = 0
    q_ct = len(qs)
    done = False
    while not done:
        q_idx = handle_qlimit(q_idx, q_ct)
        q = qs[q_idx]
        score = gb.get_score(s, cg, q)
        done, q_idx = get_student_input(score, s, cg, q, q_idx)
    menus.set_reports_gradeable_sel_options(gb)  

def handle_limits(s_idx, q_idx, s_ct, q_ct):
    if s_idx <= 0 and q_idx < 0:
        ui.print_say("First One")
        return 0, 0
    elif s_idx >= s_ct - 1 and q_idx >= q_ct:
        ui.print_say("Last One")
        return s_ct - 1, q_ct - 1
    elif q_idx >= q_ct:  
        return s_idx + 1, 0
    elif q_idx < 0:
        return s_idx - 1, q_ct - 1
    else: 
        return s_idx, q_idx
 
def handle_qlimit(q_idx, q_ct):
    if q_idx < 0:
        ui.print_say("First One")
        return 0
    elif q_idx >= q_ct:
        ui.print_say("Last One")
        return q_ct-1
    else:
        return q_idx
 
def get_input(score, s, g, q, s_idx, q_idx):
        print("{0:s}: {1:s}, {2:d}. ({3:.1f})" \
                .format(g.name, s.name(), q_idx+1, score.value))
        value = ui.dinput()
        if value.upper() == 'Q':
            return True, s_idx, q_idx
        elif value.upper() == 'B':
            return False, s_idx, q_idx-1
        elif value == '':
            return False, s_idx, q_idx+1
        elif value.upper() == 'N':
            return False, s_idx+1, 0
        elif value.upper() == 'P':
            return False, s_idx-1, 0
        else:
            return False, s_idx, q_idx + try_set_score(score, q, value, q_idx)
        
def get_student_input(score, s, g, q, q_idx):
        print("{0:s}: {1:s}, {2:d}. ({3:.1f})" \
                .format(g.name, s.name(), q_idx+1, score.value))
        value = ui.dinput()
        if value.upper() == 'Q':
            return True, q_idx
        elif value.upper() == 'B':
            return False, q_idx-1
        elif value == '':
            return False, q_idx+1
        else:
            return False, q_idx + try_set_score(score, q, value, q_idx)

def try_set_score(score, q, value, q_idx):
    try:
        tval = float(value)
        if tval <= q.points and tval >= 0:
            score.value = tval
            return 1
        else:
            ui.print_say("Invalid score")
            return 0
    except ValueError:
        ui.print_say("What?")
        return 0

#--------
# Reports
#--------
def rpt_graded_item_details_by_student(gb):
    cg = gb.cur_gradeable
    names = np.array([s.name() for s in gb.get_actives()])
    ar = np.array([[gb.get_score(s,cg,q).value for q in cg.questions] \
            for s in gb.get_actives()])
    tots = ar.sum(1)+cg.added_pts
    pcts = tots/cg.total_pts*100.0 + cg.added_pct
    title="{} Details by Student".format(cg.name)
    m,n = ar.shape
    col_headings = ["#{0:d}".format(j+1) for j in range(n)]
    rpt = SimpleReport(title, name_col_width=16, data_col_width=6, total_col_width=8, \
            name_col_name='Student', row_headings=names, col_headings=col_headings, \
            data=ar, total_col=tots, total_col_name = "Total", \
            pct_col=pcts, has_average_row=True)
    print(rpt.render())
    ui.pause()

def rpt_graded_item_details(gb):
    cg = gb.cur_gradeable
    names = np.array([s.name() for s in gb.get_actives()])
    ar = np.array([[gb.get_score(s,cg,q).value for q in cg.questions] \
            for s in gb.get_actives()])
    tots = ar.sum(1)+cg.added_pts
    print(cg.added_pts)
    pcts = tots/cg.total_pts*100.0 + cg.added_pct
    title="{} Details".format(cg.name)
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
    ui.pause()

def rpt_class_detail(gb):
    gradeables = sorted(gb.gradeables_with_scores(), key=lambda g: g.name)
    if not gradeables:
        ui.pause(msg="No Graded Items with Scores.")
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
    ui.pause()

def rpt_class_summary(gb):
    cats = gb.categories_with_scores()
    if not cats:
        ui.pause(msg="No categories with Scores.")
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
    ui.pause()

def student_summary_line_body(student, grade, cats, pcts, send_email):
    name_col_width = 16
    if send_email:
        salutation = "Hi {},\n\n".format(student.first)
        salutation += "Here's your current estimated grade information: \n\n"
    else:
        salutation = "{}".format(student.name()).ljust(name_col_width)

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
        ui.pause("No categories with Scores.")
        return
    student = stud or gb.cur_student
    pcts = np.array([c.combined_pct(student) for c in cats])
    weights = np.array([cat.pct_of_grade for cat in cats])
    adj_weights = weights/sum(weights)
    grade = (pcts*adj_weights).sum()
    student_summary_line_body(student, grade, cats, pcts, send_email) 
    ui.pause()

def rpt_avg_score_needed_for_grade(gb):
    done = False
    while not done:
        print("Enter desired grade or 'Q' to quit")
        resp = ui.dinput()
        if resp.upper() == 'Q':
            done = True
        else:
            try:
                fval = float(resp)
                score = gb.cur_student.avg_score_needed_for_grade(fval)
                if score is None:
                    print("Unable to compute average score needed.\nEstimated counts must be set for categories.")
                else:
                    print("Average score needed is: {0:.1f}".format(score))
            except ValueError:
                pass

# Display or Email current grade status to all active students
def rpt_class_summary_line(gb, send_email=False):
    if send_email and not ui.confirm("Are you sure you want to email ALL students?"): 
        return
    cats = gb.categories_with_scores()
    if not cats:
        ui.pause(msg="No categories with Scores.")
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
    ui.pause()

def rpt_student_scores(gb, preview=False, send_email=False):
    students = gb.get_actives()
    for student in students:
        text = student_score_text(gb, student)
        if not send_email and not preview:
            print(student.name())
            print(text)
        else:
            salutation = "Hi {},\n\n".format(student.first)
            salutation += "Here are the scores I have recorded for you.  Please let me know if you find any errors: \n\n"
            body = salutation + text
            if preview:
                print(body)
            else:
                try:
                    g = gmail.Gmail("Recorded Scores", '')
                    signature = g.signature 
                    g.body = body + '\n\n' + signature
                    print(student.email)
                    print(g.body)
                    g.recipients = [student.email]
                    g.send()
                except:
                    print("failed to send the email.  ", \
                            "Perhaps there is something wrong with the signature file.")
    ui.pause()

def student_score_text(gb, student):
    out = ""
    for cat in gb.categories_with_scores():
        out += "  {}\n".format(cat.name)
        gs = sorted((g for g in gb.gradeables if g.category is cat), key=lambda g: g.name)
        for g in gs:
            out += "    {0} {1:.1f}\n".format(g.name,g.adjusted_score(student)/g.total_pts*100)
    return out

    gradeables = sorted(gb.gradeables_with_scores(), key=lambda g: g.name)
def save_and_exit(gb):
    persist.save(gb, gb.file_name())
    menus.m_main.close()
   
def save_current(gb):
    persist.save(gb, gb.file_name())

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
                str(today.year + (1 if term == "Winter" and m >= 11 else 0)))

    menus.initialize_menus(gb)
    menus.m_main.open()

