import sys
sys.path.append('../')
from model import *

def setup():
    gb = Course('Math','Fall 2017')
    joe = Student('Joe', 'Davis', 'joe@pdx.edu')
    mary = Student('Mary', 'Wilcox', 'm2w@pdx.edu')
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
    assert quizzes.combined_score(joe) == 24
    assert quizzes.combined_score(mary) == 15
    assert quizzes.combined_possible() == 30
    quizzes.drop_low_n = 1
    assert quizzes.combined_score(joe) == 12
    assert quizzes.combined_score(mary) == 15
    assert quizzes.combined_possible() == 15

def test_midterm_retake_correct():
    gb = setup()
    mid1 = gb.categories[1]
    joe = gb.students[0]
    mary = gb.students[1]
    assert mid1.combined_score(joe) == 12
    assert mid1.combined_score(mary) == 13.5
    assert mid1.combined_possible() == 15

def test_removing_a_student():
    gb = setup()
    quizzes = gb.categories[0]
    joe = gb.students[0]
    mary = gb.students[1]
    assert quizzes.combined_score(joe) == 24
    assert quizzes.combined_score(mary) == 15
    assert quizzes.combined_possible() == 30
    assert len(gb.scores) == 24
    gb.remove_student(joe)
    assert len(gb.students) == 1
    assert quizzes.combined_score(mary) == 15
    assert len(gb.scores) == 12

def test_gradeables_with_scores():
    gb = setup()
    assert len(gb.gradeables_with_scores()) == 4
    quiz2 = gb.gradeables[1]
    gb.remove_gradeable(quiz2)
    assert len(gb.gradeables_with_scores()) == 3
