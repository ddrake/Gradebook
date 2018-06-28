import sys
import pytest

sys.path.append('../')
from model import *

def setup():
    gb = Course('Math','Fall 2017')
    joe = Student(gb, 'Joe', 'Davis', 'joe@pdx.edu')
    mary = Student(gb, 'Mary', 'Wilcox', 'm2w@pdx.edu')
    gb.students.append(joe)
    gb.students.append(mary)
    quizzes = Category(gb, 'Quizzes', 25)
    mid1 = Category(gb, 'Midterm1', 15)
    gb.categories.append(quizzes)
    gb.categories.append(mid1)
    quiz1 = Gradeable(gb, 'Quiz1', quizzes, 15)
    quiz2 = Gradeable(gb, 'Quiz2', quizzes, 15)
    quiz3 = Gradeable(gb, 'Quiz3', quizzes, 15)
    exam1 = Gradeable(gb, 'Exam1', mid1, 15)
    exam1_retake = Gradeable(gb, 'Exam1 Retake', mid1, 15, sub_pct=50.0)
    for i in range(3):
        quiz1.add_question(5)
        quiz2.add_question(5)
        exam1.add_question(5)
        exam1_retake.add_question(5)
    gb.gradeables.append(quiz1)
    gb.gradeables.append(quiz2)
    gb.gradeables.append(quiz3)
    gb.gradeables.append(exam1)
    gb.gradeables.append(exam1_retake)

    for question in quiz1.questions:
        s = gb.get_score(joe, quiz1, question)
        s.value = 4
        s = gb.get_score(mary, quiz1, question)
        s.value = 5

    for question in quiz2.questions:
        s = gb.get_score(joe, quiz2, question)
        s.value = 4

    for question in exam1.questions:
        s = gb.get_score(joe, exam1, question)
        s.value = 3
        s = gb.get_score(mary, exam1, question)
        s.value = 4

    for question in exam1_retake.questions:
        s = gb.get_score(joe, exam1_retake, question)
        s.value = 2
        s = gb.get_score(mary, exam1_retake, question)
        s.value = 1

    return gb

def test_quiz_averages_correct():
    gb = setup()
    quizzes = gb.categories[0]
    joe = gb.students[0]
    mary = gb.students[1]
    assert quizzes.combined_pct(joe) == 24.0*100/30
    assert quizzes.combined_pct(mary) == 15*100/30
    quizzes.drop_low_n = 1
    assert quizzes.combined_pct(joe) == 12.0*100/15
    assert quizzes.combined_pct(mary) == 15.0*100/15

def test_midterm_retake_correct():
    gb = setup()
    mid1 = gb.categories[1]
    joe = gb.students[0]
    mary = gb.students[1]
    assert mid1.combined_pct(joe) == 12*100/15.
    assert mid1.combined_pct(mary) == 13.5*100/15.

def test_removing_a_student():
    gb = setup()
    quizzes = gb.categories[0]
    joe = gb.students[0]
    mary = gb.students[1]
    assert len(gb.gradeables_with_scores()) == 4
    assert quizzes.combined_pct(joe) == 24*100/30.
    assert quizzes.combined_pct(mary) == 15*100/30.
    assert len(gb.scores) == 24
    gb.remove_student(joe)
    assert len(gb.students) == 1
    assert quizzes.drop_low_n == 0
    assert len(gb.scores) == 12
    assert len(gb.gradeables_with_scores()) == 3
    assert quizzes.combined_pct(mary) == 15*100/15.

def test_gradeables_with_scores():
    gb = setup()
    assert len(gb.gradeables_with_scores()) == 4
    quiz2 = gb.gradeables[1]
    gb.remove_gradeable(quiz2)
    assert len(gb.gradeables_with_scores()) == 3

def setup_simple():
    gb = Course('Math','Fall 2017')
    joe = Student(gb, 'Joe', 'Davis', 'joe@pdx.edu')
    gb.students.append(joe)
    homework = Category(gb, 'Homework', 100, 0, 3)
    gb.categories.append(homework)
    hw1 = Gradeable(gb, 'HW1', homework, 15)
    hw1.add_question(15)
    gb.gradeables.append(hw1)

    s = gb.get_score(joe, hw1, hw1.questions[0])
    s.value = 1
    return gb

def test_rpt_avg_score_needed_for_grade():
    gb = setup_simple()
    joe = gb.students[0]
    assert abs(joe.avg_score_needed_for_grade(90) - (90*3-100/15)/2) < .00001

def test_rpt_avg_score_needed_for_grade2():
    gb = setup_simple()
    joe = gb.students[0]
    hw1 = gb.gradeables[0]
    s = gb.get_score(joe, hw1, hw1.questions[0])
    s.value = 15


def setup_simple2():
    gb = Course('Math','Fall 2017')
    joe = Student(gb, 'Joe', 'Davis', 'joe@pdx.edu')
    gb.students.append(joe)
    homework = Category(gb, 'Homework', 40, 0, 3)
    exam1 = Category(gb, 'Exam1', 20, 0, 1)
    final = Category(gb, 'Final', 30, 0, 1)
    gb.categories.append(homework)
    gb.categories.append(exam1)
    gb.categories.append(final)
    hw1 = Gradeable(gb, 'HW1', homework, 15)
    hw1.add_question(15)
    ex1 = Gradeable(gb, 'Exam1', exam1, 100)
    ex1.add_question(100)
    finl = Gradeable(gb, 'Final', final, 100)
    finl.add_question(100)

    gb.gradeables.append(hw1)
    gb.gradeables.append(ex1)
    gb.gradeables.append(finl)

    s = gb.get_score(joe, hw1, hw1.questions[0])
    s.value = 1
    s = gb.get_score(joe, ex1, ex1.questions[0])
    s.value = 25
    return gb

def test_rpt_avg_score_needed_for_grade3():
    gb = setup_simple2()
    hw, ex1, finl = gb.categories
    assert hw.actual_ct() == 1
    assert ex1.actual_ct() == 1
    assert finl.actual_ct() == 0
    hope_factor = 1/(0.40*(2/3) + 0.3)
    assert abs(gb.hope_factor() - hope_factor) < .00001
    joe = gb.students[0]
    cats = gb.categories_with_scores()
    assert len(cats) == 2
    partial_est = (.40*(1/3)*(1/15*100) + .20*(1/1)*25)
    assert abs(joe.partial_est_grade() - partial_est) < .00001
    expected = (90 - partial_est)*hope_factor
    assert abs(joe.avg_score_needed_for_grade(90) - (90 - partial_est)*hope_factor) < .00001

def test_category_with_gradeable_pcts():
    gb = Course('Math','Fall 2017')
    cat = Category(gb, name='Exams', pct_of_grade=100, est_ct = 3, gradeable_pcts=[40,35,25])
    gb.categories.append(cat)
    exam1 = Gradeable(gb,name='Exam 1', category=cat, total_pts=50)  
    exam1.add_question(50)
    gb.gradeables.append(exam1)
    exam2 = Gradeable(gb,name='Exam 2', category=cat, total_pts=50)  
    exam2.add_question(50)
    gb.gradeables.append(exam2)
    exam3 = Gradeable(gb,name='Exam 3', category=cat, total_pts=50)  
    exam3.add_question(50)
    gb.gradeables.append(exam3)
    joe = Student(gb,first='Joe',last='Crow',email='joe@pdx.edu')
    gb.students.append(joe)
    s = gb.get_score(joe, exam1, exam1.questions[0])
    s.value = 45
    gpcts = [g.adjusted_score(joe) * 100 / g.total_pts for g in cat.gradeables_with_scores()]
    assert(sorted(gpcts) == [90])
    assert(cat.gradeable_pcts[:1] == [25])
    assert(cat.combined_pct(joe) == 90)
    assert(joe.grade() == 90)
    assert(gb.hope_factor() == 1.0/0.75)
    assert(joe.avg_score_needed_for_grade(90) == 90)

    s = gb.get_score(joe, exam2, exam2.questions[0])
    s.value = 10
    gpcts = [g.adjusted_score(joe) * 100 / g.total_pts for g in cat.gradeables_with_scores()]
    assert(sorted(gpcts) == [20, 90])
    assert(cat.gradeable_pcts[:2] == [25,35])
    assert(cat.combined_pct(joe) == 3650/60)
    assert(joe.grade() == 3650/60)
    assert(gb.hope_factor() == 1.0/0.40)
    assert(joe.avg_score_needed_for_grade(80) == pytest.approx(108.75))
    
    s = gb.get_score(joe, exam3, exam3.questions[0])
    s.value = 40
    gpcts = [g.adjusted_score(joe) * 100 / g.total_pts for g in cat.gradeables_with_scores()]
    assert(sorted(gpcts) == [20,80,90])
    assert(cat.gradeable_pcts == [25,35,40])
    assert(cat.combined_pct(joe) == 69)
    assert(joe.grade() == 69)
    assert(gb.hope_factor() == None)
    assert(joe.avg_score_needed_for_grade(80) == None)
