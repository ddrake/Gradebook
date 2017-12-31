
class Course:
    def __init__(self, name = '', term = ''):
        self.name = name
        self.term = term
        self.categories = []
        self.gradeables = []
        self.students = []
        self.actives = None
        self.scores = {}
        self.cur_student = None
        self.cur_gradeable = None
        self.cur_category = None
    
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

    def get_actives(self):
        if self.actives == None:
            self.actives = [s for s in self.students if s.is_active]
        return self.actives

    def remove_student(self, student):
        for k in [k for k in self.scores.keys()]: 
            if student is k[0]: self.scores.pop(k,None)
        self.students.remove(student)
        self.cur_student = None
        self.actives = None

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

    def categories_with_scores(self):
        return [c for c in self.categories \
                if any(k for k,v in self.scores.items() if k[1].category is c and v.value > 0.0)]

    def gradeables_with_scores(self):
        return [g for g in self.gradeables \
                if any(k for k,v in self.scores.items() if k[1] is g and v.value > 0.0)]

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
    def __init__(self, course, name='', pct_of_grade=0.0, drop_low_n=0):
        self.name = name
        self.pct_of_grade = pct_of_grade
        self.course = course
        self.drop_low_n = drop_low_n 
        # if drop_low_n > 0, all gradeables in category should have same pts

    def combined_score(self, student):
        gs = self.gradeables_with_scores()
        if any(g for g in gs if g.sub_pct !=0):
            return sum(g.adjusted_score(student) * \
                    (g.sub_pct/100.0 if g.sub_pct != 0.0 else 1.0) for g in gs)
        else:
            gscores = [g.adjusted_score(student) for g in gs]
            if self.drop_low_n > 0:
                st_idx = self.drop_low_n if len(gs) > self.drop_low_n  else 0
                return sum(sorted(gscores)[st_idx:])
            else:
                return sum(gscores)


    def combined_possible(self):
        gs = self.gradeables_with_scores()
        if any(g for g in gs if g.sub_pct !=0):
            return gs[0].total_pts
        else:
            if self.drop_low_n > 0:
                gct = len(gs)-self.drop_low_n
                gct = gct if gct > 0 else len(gs)
                return gs[0].total_pts * gct
            else:
                return sum([g.total_pts for g in gs])

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
        return (sum([self.course.get_score(student, self, q).value for q in self.questions]) \
                + self.added_pts)*(100.0+self.added_pct)/100.0
        
class Score:
    def __init__(self, student, gradeable, question, value = 0.0):
        self.student = student
        self.gradeable = gradeable
        self.question = question
        self.value = value

