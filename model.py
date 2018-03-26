import numpy as np

schema_version = 4

class Course:
    def __init__(self, name = '', term = '', global_added_pct=0.0, letter_plus_minus_pct=1.0):
        global schema_version
        self.name = name
        self.term = term
        self.schema_version = schema_version
        self.categories = []
        self.gradeables = []
        self.students = []
        self.actives = None
        self.scores = {}
        self.cur_student = None
        self.cur_gradeable = None
        self.cur_category = None
        self.global_added_pct = global_added_pct
        self.letter_plus_minus_pct = letter_plus_minus_pct
 
    def get_score(self, student, gradeable, question):
        key = (student, gradeable, question)
        if key in self.scores.keys():
            return self.scores[key]
        else:
            s = Score(student, gradeable, question)
            self.scores[key] = s
        return s

    # Set the current student, gradeable, or category for a menu action
    def set_cur_student(self, student):
        self.cur_student = student

    def set_cur_gradeable(self, gradeable):
        self.cur_gradeable = gradeable

    def set_cur_category(self, category):
        self.cur_category = category

    def add_student(self, first, last, email):
        if not any(s for s in self.students 
                if (s.first == first and s.last == last) or s.email == email):
            self.students.append(Student(self, first, last, email))

    def remove_student(self, student):
        for k in [k for k in self.scores.keys()]: 
            if student is k[0]: self.scores.pop(k,None)
        self.students.remove(student)
        self.cur_student = None
        self.actives = None

    def get_actives(self):
        if self.actives == None:
            self.actives = [s for s in self.students if s.is_active]
        return self.actives

    def remove_gradeable(self, gradeable):
        for k in [k for k in self.scores.keys()]:
            if gradeable is k[1]: self.scores.pop(k,None)
        self.gradeables.remove(gradeable);
        self.cur_gradeable = None

    def remove_category(self, category):
        for k in [k for k in self.scores.keys()]: 
            if category is k[1].category: self.scores.pop(k,None)
        self.gradeables = [g for g in self.gradeables if not g.category is category]
        self.categories.remove(category)
        self.cur_category = None

    # Most items will have scores, so the 'any' should make these efficient
    def categories_with_scores(self):
        return [c for c in self.categories \
                if any(k for k,v in self.scores.items() if k[1].category is c and v.value > 0.0)]

    def gradeables_with_scores(self):
        return [g for g in self.gradeables \
                if any(k for k,v in self.scores.items() if k[1] is g and v.value > 0.0)]

    def students_with_scores(self):
        return [s for s in self.students \
                if any(k for k,v in self.scores.items() if k[0] is s and v.value > 0.0)]

    # The name of the associated JSON file for the course
    def file_name(self):
        return self.name.replace(' ','_') + "_" \
               + self.term.replace(' ','_') + ".json"

    def hope_factor(self):
        s = sum([(c.est_ct - c.actual_ct())/c.est_ct * c.pct_of_grade/100.0 \
                    for c in self.categories if c.est_ct - c.actual_ct() > 0])
        return 1/s if s > 0 else None

    def grade_mins(self):
        pm = self.letter_plus_minus_pct
        return [60.0, 60.0+pm, 70.0-pm, 70.0, 70.0+pm, 80.0-pm, 80.0, 80.0+pm, 90.0-pm, 90,   90.0+pm], \
               ['D-', 'D',    'D+',     'C-', 'C',     'C+',    'B-', 'B',     'B+',    'A-', 'A'    ]

    def letter_grade_for_pct(self, pct):
        mins, letters = self.grade_mins()
        for i in range(len(mins)-1,-1,-1):
            if pct >= mins[i]: 
                return letters[i]
        return 'F'

class Student:
    def __init__(self, course, first = '', last = '', email = '', \
            is_active=1, notes=''):
        self.course = course
        self.first = first
        self.last = last
        self.email = email
        self.is_active = is_active
        self.notes = notes

    def name(self):
        return self.first + (' {}.'.format(self.last[0]) if self.last else '')

    def fullname(self):
        return self.first + ' ' + self.last
        
    def lastfirst(self):
        return self.last + ', ' + self.first

    def has_scores(self):
        return self in self.course.students_with_scores()

    def grade(self):
        cats = self.course.categories_with_scores()
        if not cats: return None
        pcts = np.array([c.combined_pct(self) for c in cats])
        weights = np.array([cat.pct_of_grade for cat in cats])
        adj_weights = weights/sum(weights)
        return (pcts*adj_weights).sum() + self.course.global_added_pct
 
    def letter_grade(self):
        grade = self.grade()
        return None if grade == None else self.course.letter_grade_for_pct(grade)

    def partial_est_grade(self):
        cats = self.course.categories_with_scores()
        if not cats: return None
        pcts = np.array([c.combined_pct(self) for c in cats])
        weights = np.array([c.pct_of_grade for c in cats])
        act_cts = np.array([c.actual_ct() for c in cats])
        est_cts = np.array([c.est_ct for c in cats])
        return (pcts*weights/100.0*act_cts/est_cts).sum()

    def avg_score_needed_for_grade(self, grade):
        hf = self.course.hope_factor()
        if hf == None: return None
        return (grade - self.partial_est_grade()) * hf

class Question:
    def __init__(self, gradeable, points):
        self.gradeable = gradeable
        self.points = points

class Category:
    def __init__(self, course, name='', pct_of_grade=0.0, drop_low_n=0, est_ct=0):
        self.course = course
        self.name = name
        self.pct_of_grade = pct_of_grade
        self.drop_low_n = drop_low_n
        self.est_ct = est_ct  # the estimate number of gradeables in the category

    def actual_ct(self):
        gs = self.gradeables_with_scores()
        return 1 if any(g for g in gs if g.sub_pct !=0) else len(gs)

    def combined_pct(self, student):
        gs = self.gradeables_with_scores()
        if any(g for g in gs if g.sub_pct !=0):
            return sum(g.adjusted_score(student) * 100 / g.total_pts * \
                    (g.sub_pct/100.0 if g.sub_pct != 0.0 else 1.0) for g in gs)
        else:
            gpcts = [g.adjusted_score(student) * 100 / g.total_pts for g in gs]
            if self.drop_low_n > 0:
                st_idx = self.drop_low_n if len(gs) > self.drop_low_n  else 0
                return sum(sorted(gpcts)[st_idx:]) / (len(gpcts)-st_idx)
            else:
                return sum(gpcts) / len(gpcts)

    def gradeables_with_scores(self):
        return [g for g in self.course.gradeables_with_scores() if g.category is self]

class Gradeable:
    def __init__(self, course, name='', category = None, total_pts=0.0, \
            sub_pct = 0.0, added_pts = 0.0, added_pct = 0.0):
        self.course = course
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

    def adjusted_score(self, student):
        scoresum = sum([self.course.get_score(student, self, q).value for q in self.questions]) 
        return 0 if scoresum == 0 else scoresum + self.added_pts + self.added_pct*self.total_pts/100.0

    def adjusted_pct(self, student):
        return self.adjusted_score(student) / self.total_pts * 100.0 
        
    def has_scores(self):
        return self in self.course.gradeables_with_scores()

    def delete_scores(self):
        for k in [k for k in self.course.scores.keys()]:
            if self is k[1]: self.course.scores.pop(k,None)

class Score:
    def __init__(self, student, gradeable, question, value = 0.0):
        self.student = student
        self.gradeable = gradeable
        self.question = question
        self.value = value

