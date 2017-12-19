import sys
sys.path.append('../')
from persist import read, save
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
    exam1 = Gradeable(gb, 'Exam1', mid1, 15)
    for i in range(3):
        quiz1.add_question(5)
        quiz2.add_question(5)
        exam1.add_question(5)
    gb.gradeables.append(quiz1)
    gb.gradeables.append(quiz2)
    gb.gradeables.append(exam1)

    for question in quiz1.questions:
        s = gb.get_score(joe, quiz1, question)
        s.value = 4
        s = gb.get_score(mary, quiz1, question)
        s.value = 5

    return gb

def test_save_and_load():
    gb = setup()
    save(gb,'test.json')
    gb2 = read('test.json')
    assert len(gb2.students) == 2
    assert len(gb2.categories) == 2
    assert len(gb2.gradeables) == 3

