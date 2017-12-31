from model import *
from menu import Menu
import gb1 as app

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

#-------------
# Menu Helpers
#-------------
# These helpers set the current gradeable, student, etc... 
# then open a menu item
def set_gradeable_open_score_one_entry(gb, gradeable):
    gb.set_cur_gradeable(gradeable)
    m_score_one_entry.open()

def set_gradeable_open_gradeable_edit_del(gb, gradeable):
    gb.set_cur_gradeable(gradeable)
    m_gradeable_edit_del.open()

def set_and_open_category_edit_del(gb, category):
    gb.set_cur_category(category)
    m_category_edit_del.open()
  
def set_and_open_student(gb,student):
    gb.set_cur_student(student)
    m_student_edit_del.open()

def set_and_open_reports_gradeable(gb, gradeable):
    gb.set_cur_gradeable(gradeable)
    # currently only one report in this category so open it directly
    app.rpt_graded_item_details(gb)
    
def set_and_open_reports_student(gb, student):
    gb.set_cur_student(student)
    m_reports_student.open()

#------------------------
# setup category menu logic
#------------------------
def set_category_options(gb):
    m_category.options = []
    m_category.add_option("Return to Gradebook", m_category.close)
    m_category.add_option("Add Category", lambda : app.add_category(gb))
    for item in sorted(gb.categories, key=lambda i: i.name):
        m_category.add_option("{0:s} ({1:.1f})".format(item.name, item.pct_of_grade), 
                                    lambda i=item: set_and_open_category_edit_del(gb,i))
        set_score_all_options(gb)
        set_score_one_options(gb)
        set_gradeable_options(gb)

def set_category_edit_del_options(gb):
    m_category_edit_del.options = []
    m_category_edit_del.add_option("Return to Category List", \
            m_category_edit_del.close)
    m_category_edit_del.add_option("Edit", lambda : app.edit_category(gb))
    m_category_edit_del.add_option("Delete", lambda : app.delete_category(gb))

#------------------------
# setup student menu logic
#------------------------
def set_student_options(gb):
    m_student.options = []
    m_student.add_option("Return to Gradebook", m_student.close)
    m_student.add_option("Add Student", lambda : app.add_student(gb))
    for item in sorted(gb.students, key=lambda i: i.name()):
        m_student.add_option(item.name() + ('' if item.is_active else ' *'), 
                                    lambda i=item: set_and_open_student(gb,i))
        set_score_one_entry_options(gb)
        set_reports_student_sel_options(gb)

def set_student_edit_del_options(gb):
    m_student_edit_del.options = []
    m_student_edit_del.add_option("Return to Student List", \
            m_student_edit_del.close)
    m_student_edit_del.add_option("Edit", lambda : app.edit_student(gb))
    m_student_edit_del.add_option("Delete", lambda : app.delete_student(gb))

def set_student_import_options(gb):
    m_student_import.add_option("Return to Gradebook", \
            m_student_import.close)
    m_student_import.add_option("Import From File", lambda : app.import_students(gb))

#------------------------
# setup gradeables menu logic
#------------------------
def set_gradeable_options(gb):
    m_gradeable.options = []
    m_gradeable.add_option("Return to Gradebook", m_gradeable.close)
    m_gradeable.add_option("Add Graded Item", lambda : app.add_gradeable(gb))
    for item in sorted(gb.gradeables, key=lambda i: i.name):
        m_gradeable.add_option("{0:s}".format(item.name), 
                lambda i=item: set_gradeable_open_gradeable_edit_del(gb, i))
        set_score_all_options(gb)
        set_score_one_options(gb)
        set_reports_gradeable_sel_options(gb)

def set_gradeable_edit_del_options(gb):
    m_gradeable_edit_del.options = []
    m_gradeable_edit_del.add_option("Return to Graded Items List", \
            m_gradeable_edit_del.close)
    m_gradeable_edit_del.add_option("Edit", lambda : app.edit_gradeable(gb))
    m_gradeable_edit_del.add_option("Delete", lambda : app.delete_gradeable(gb))

#------------------------
# score entry menu logic
#------------------------
def set_score_all_options(gb):
    m_score_all.options=[]
    m_score_all.add_option("Return to Gradebook", m_score_all.close)
    for item in sorted(gb.gradeables, key=lambda i: i.name):
        m_score_all.add_option(item.name, lambda i=item: app.input_scores(gb,i))

def set_score_one_options(gb):
    m_score_one.options=[]
    m_score_one.add_option("Return to Gradebook", m_score_one.close)
    for item in sorted(gb.gradeables, key=lambda i: i.name):
        m_score_one.add_option(item.name, \
                lambda i=item: set_gradeable_open_score_one_entry(gb, i))

def set_score_one_entry_options(gb):
    m_score_one_entry.options=[]
    m_score_one_entry.add_option("Return to Student List", \
            m_score_one_entry.close)
    for item in sorted(gb.get_actives(), key=lambda i: i.name()):
        m_score_one_entry.add_option(item.name(), \
                lambda i=item: app.input_student_scores(gb,i))

#------------------------
# report menu logic
#------------------------
def set_reports_options(gb):
    m_reports.options = []
    m_reports.add_option("Return to Gradebook", m_reports.close)
    m_reports.add_option("Class Detail Report", lambda:app.rpt_class_detail(gb))
    m_reports.add_option("Class Summary Report", lambda:app.rpt_class_summary(gb))
    m_reports.add_option("Class Summary Lines", lambda:app.rpt_class_summary_line(gb))
    m_reports.add_option("Class Summary Email ALL Students", \
            lambda:app.rpt_class_summary_line(gb, send_email=True))
    m_reports.add_option("Student Reports", m_reports_student_sel.open)
    m_reports.add_option("Graded Item Reports", m_reports_gradeable_sel.open)
    set_reports_gradeable_sel_options(gb)
    set_reports_student_sel_options(gb)

def set_reports_gradeable_sel_options(gb):
    m_reports_gradeable_sel.options = []
    m_reports_gradeable_sel.add_option("Return to Report Menu", \
            m_reports_gradeable_sel.close)
    for item in sorted(gb.gradeables_with_scores(), key=lambda i: i.name):
        m_reports_gradeable_sel.add_option(item.name, \
                lambda i=item : set_and_open_reports_gradeable(gb,i))
    set_reports_gradeable_options(gb)

def set_reports_student_sel_options(gb):    
    m_reports_student_sel.options = []
    m_reports_student_sel.add_option("Return to Report Menu", \
            m_reports_student_sel.close)
    for item in sorted(gb.get_actives(), key=lambda i: i.name()):
        m_reports_student_sel.add_option(item.name(), \
                lambda i=item : set_and_open_reports_student(gb,i))
    set_reports_student_options(gb)

def set_reports_gradeable_options(gb):
    m_reports_gradeable.options = []
    m_reports_gradeable.add_option("Return to Graded Item List", \
            m_reports_gradeable.close)
    m_reports_gradeable.add_option("Graded Item Details", \
            app.rpt_graded_item_details)

def set_reports_student_options(gb):
    m_reports_student.options = []
    m_reports_student.add_option("Return to Student List", \
            m_reports_student.close)
    m_reports_student.add_option("Student Scores Preview", \
            lambda : app.rpt_student_summary_line(gb))
    m_reports_student.add_option("Student Scores Email", \
            lambda : app.rpt_student_summary_line(gb,send_email=True))

#------------------------
# main menu logic
#------------------------
def set_main_options(gb):
    m_main.options = []
    m_main.add_option("Quit", lambda : app.save_and_exit(gb))
    m_main.add_option("Save", lambda : app.save_current(gb))
    m_main.add_option("Enter Scores All Students", m_score_all.open)
    m_main.add_option("Enter Scores One Student", m_score_one.open)
    m_main.add_option("Reports", m_reports.open)
    m_main.add_option("Manage Graded Items", m_gradeable.open)
    m_main.add_option("Manage Categories", m_category.open)
    m_main.add_option("Manage Students", m_student.open)
    m_main.add_option("Import Students", m_student_import.open)
    m_main.add_option("Edit Course", lambda : app.edit_course(gb))

def initialize_menus(gb):
    set_gradeable_edit_del_options(gb)
    set_reports_options(gb)
    set_main_options(gb)

    # these will handle dependent options
    set_category_options(gb)
    set_category_edit_del_options(gb)
    set_student_options(gb)
    set_student_edit_del_options(gb)
    set_student_import_options(gb)

