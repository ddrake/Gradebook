import numpy as np

schema_version = 7

class Course:
    def __init__(self, name = '', term = '', global_added_pct=0.0, \
            letter_plus_minus_pct=1.0, audible_warnings=1):
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
        self.audible_warnings = audible_warnings

 
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

    def remove_student_scores(self, student):
        for k in [k for k in self.scores.keys()]: 
            if student is k[0]: self.scores.pop(k,None)

    def remove_student(self, student):
        self.remove_student_scores(student)
        self.students.remove(student)
        self.cur_student = None
        self.actives = None

    def any_students_with_scores(self):
        return any(s for s in self.scores.values() if s.value != 0) 

    def remove_all_scores(self):
        self.scores = {}

    def delete_all_students(self):
        if self.any_students_with_scores(): return
        self.remove_all_scores()
        self.students = []
        self.actives = None

    def get_actives(self):
        if self.actives == None:
            self.actives = [s for s in self.students if s.is_active]
        return self.actives

    def remove_gradeable_scores(self, gradeable):
        for k in [k for k in self.scores.keys()]:
            if gradeable is k[1]: self.scores.pop(k,None)

    def remove_gradeable(self, gradeable):
        self.remove_gradeable_scores(gradeable)
        self.gradeables.remove(gradeable);
        self.cur_gradeable = None

    def remove_category(self, category):
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
        s = sum([c.hope_factor() for c in self.categories])
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

    def config_warnings(self):
        msgs = []
        if np.abs(sum([c.pct_of_grade for c in self.categories])-100.0) > 1.0e-6:
            msgs.append("The percentage weights of the categories do not sum to 100%")
        for c in self.categories:
            msgs += c.config_warnings()
        return msgs

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
        weights = np.array([c.pct_of_grade for c in cats])
        pcts = np.array([c.combined_pct(self) for c in cats])
        act_cts = np.array([c.actual_ct() for c in cats])
        est_cts = np.array([c.est_ct for c in cats])
        result = 0
        for i in range(len(cats)):
            if cats[i].gradeable_pcts:
                result += pcts[i]*weights[i]/100.0*(1 - sum(cats[i].gradeable_pcts[act_cts[i]:])/100.0)
            else:
                result += pcts[i]*weights[i]/100.0*act_cts[i]/est_cts[i]
        return result

    def avg_score_needed_for_grade(self, grade):
        hf = self.course.hope_factor()
        if hf == None: return None
        return (grade - self.partial_est_grade()) * hf

class Question:
    def __init__(self, gradeable, points):
        self.gradeable = gradeable
        self.points = points

class Category:
    def __init__(self, course, name='', pct_of_grade=0.0, drop_low_n=0,\
            est_ct=0, combine_pts=0, gradeable_pcts=[]):
        self.course = course
        self.name = name
        self.pct_of_grade = pct_of_grade
        self.drop_low_n = drop_low_n 
        # the estimated number of gradeables in the category (used to get avg score needed for grade)
        self.est_ct = est_ct 
        # combine gradeables by adding points instead of percents
        self.combine_pts = combine_pts 
        # better scores get weighted more heavily.  These should sum to pct_of_grade
        self.gradeable_pcts = sorted(gradeable_pcts)

    def actual_ct(self):
        gs = self.gradeables_with_scores()
        return 1 if any(g for g in gs if g.sub_pct !=0) else len(gs)

    def set_gradeable_pcts(self, pcts):
        self.gradeable_pcts = [] if pcts is None else sorted(pcts)

    def combined_pct(self, student):
        gs = self.gradeables_with_scores()
        if any(g for g in gs if g.sub_pct !=0):
            # retake option
            return sum(g.adjusted_score(student) * 100 / g.total_pts * \
                    (g.sub_pct/100.0 if g.sub_pct != 0.0 else 1.0) for g in gs)
        elif self.gradeable_pcts:
            # better scores get weighted more heavily
            # the user should set up all the gradeables in this category ahead of time
            # combine pts is not supported in this case
            # drop_low_n is not supported in this case
            spcts = sum(self.gradeable_pcts[:len(gs)])
            gpcts = [g.adjusted_score(student) * 100 / g.total_pts for g in gs]
            return sum([gp*p/spcts for gp,p in zip(self.gradeable_pcts, sorted(gpcts))])
        else:
            if self.combine_pts:
                # todo: figure out how to drop lowest in this case (maybe unnecessary)
                gpts = [g.adjusted_score(student) for g in gs]
                gtots = [g.total_pts for g in gs]
                return sum(gpts)/sum(gtots)*100
            else:
                gpcts = [g.adjusted_score(student) * 100 / g.total_pts for g in gs]
                if self.drop_low_n > 0:
                    st_idx = self.drop_low_n if len(gs) > self.drop_low_n  else 0
                    return sum(sorted(gpcts)[st_idx:]) / (len(gpcts)-st_idx)
                else:
                    return sum(gpcts) / len(gpcts)

    def hope_factor(self):
        if self.gradeable_pcts:
            return 0 if len(self.gradeable_pcts) <= self.actual_ct() \
                    else sum(self.gradeable_pcts[self.actual_ct():]) /100.0 
        return 0 if self.est_ct <= self.actual_ct() \
                else (self.est_ct - self.actual_ct())/self.est_ct * self.pct_of_grade/100.0 

    def config_warnings(self):
        msgs = []
        if any(g for g in self.course.gradeables if g.sub_pct !=0):
            if self.gradeable_pcts:
                msgs.append( ("Category '{}': Graded items weighted by score is not supported \n " + \
                        "when retake sub percent is set.").format(self.name))
            if self.combine_pts:
                msgs.append( ("Category '{}': Combine points instead of percents is not supported \n " + \
                        "when retake sub percent is set.").format(self.name))
        if self.combine_pts and self.gradeable_pcts:
            msgs.append( ("Category '{}': Combine points instead of percents is not supported \n " + \
                        "when Graded items weighted by score is set.").format(self.name))
        if self.drop_low_n and self.gradeable_pcts:
            msgs.append( ("Category '{}': Dropping the lowest n items is not supported \n " + \
                    "when Graded items weighted by score is set.").format(self.name))
        if self.drop_low_n and self.combine_pts:
            msgs.append( ("Category '{}': Dropping the lowest n items is not supported \n " + \
                    "when Combine points instead of percents is set.").format(self.name))
        if self.gradeable_pcts and self.est_ct != len(self.gradeable_pcts):
            msgs.append( ("Category '{}': The number of Estimated items should match \n " + \
                    "the number of percentages when " + \
                    "Graded items weighted by score is set.").format(self.name))
        return msgs

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

    def students_with_scores(self):
        return list({student for (student, gradeable, _) in self.course.scores.keys() if gradeable is self})

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

    def mean_score(self):
        students = self.students_with_scores()
        return sum([self.adjusted_score(s) for s in students]) / len(students)

class Score:
    def __init__(self, student, gradeable, question, value = 0.0):
        self.student = student
        self.gradeable = gradeable
        self.question = question
        self.value = value

