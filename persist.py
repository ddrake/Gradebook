from model import *
import json

def read(file_name):
    with open(file_name,'r') as f:
        course_dict = json.load(f)
    return course_from_dict(course_dict)

def save(gb, file_name):
    data = json.dumps(course_to_dict(gb), indent=2)
    with open(file_name, mode='w', encoding='utf-8') as f:
        f.write(data)

def course_to_dict(gb):
    course = {'name': gb.name, 'term': gb.term}
    course['categories'] = [{'id':i, 'name': c.name, 'pct_of_grade': c.pct_of_grade, \
            'drop_low_n': c.drop_low_n, 'obj': c} \
            for i, c in enumerate(gb.categories)]
    # add the student object to the dict -- delete it once the scores list is finished
    course['students'] = [{'id':i, 'first': s.first, 'last': s.last, 'email': s.email, 'obj': s} \
            for i, s in enumerate(gb.students)]
    gradeables = []
    scores = []
    cat_dict = {item['obj']: item for item in course['categories']}
    for i, g in enumerate(gb.gradeables):
        questions = []
        gd = {'id':i, 'cid': cat_dict[g.category]['id'], 'name': g.name, 'total_pts': g.total_pts, \
                'sub_pct': g.sub_pct, 'added_pts': g.added_pct, 'added_pct': g.added_pct}
        for j, q in enumerate(g.questions):
            questions.append( {'id':j, 'gid': i, 'points': q.points} )
            for sd in course['students']:
                scores.append( {'sid': sd['id'], 'gid': gd['id'], 'qid': j, \
                        'value': gb.get_score(sd['obj'],g,q).value } )
        gd['questions'] = questions
        gradeables.append(gd)       
    
    course['gradeables'] = gradeables
    course['scores'] = scores
    for s in course['students']:
        del s['obj']
    for c in course['categories']:
        del c['obj']
    return course

def course_from_dict(course):
    category_dict = {item['id'] : item for item in course['categories']}
    gradeable_dict = {item['id'] : item for item in course['gradeables']}
    student_dict = {item['id'] : item for item in course['students']}
    question_dict = {(q['gid'],q['id']) : q for g in course['gradeables'] \
            for q in g['questions'] }
    course_obj = Course(course['name'], course['term'])
    categories = []
    gradeables = []
    students = []
    for cd in course['categories']:
        category = Category(course_obj, cd['name'], cd['pct_of_grade'], cd['drop_low_n'])
        category_dict[cd['id']]['obj'] = category
        categories.append(category)
    course_obj.categories = categories
    for sd in course['students']:
        student = Student(sd['first'], sd['last'], sd['email'])
        student_dict[sd['id']]['obj'] = student
        students.append(student)
    course_obj.students = students
    for gd in course['gradeables']:
        gradeable = Gradeable(course_obj, gd['name'], category_dict[gd['cid']]['obj'], \
                gd['total_pts'], gd['sub_pct'], gd['added_pts'], gd['added_pct'])
        gradeable_dict[gd['id']]['obj'] = gradeable
        gradeables.append(gradeable)
        for qd in gd['questions']:
            question = Question(gradeable, qd['points'])
            question_dict[(qd['gid'],qd['id'])]['obj'] = question
            gradeable.questions.append(question)
    course_obj.gradeables = gradeables
    for sd in course['scores']:
        student = student_dict[sd['sid']]['obj']
        gradeable = gradeable_dict[sd['gid']]['obj']
        question = question_dict[(sd['gid'],sd['qid'])]['obj']
        score = Score(student, gradeable, question, sd['value'])
        course_obj.scores[(student, gradeable, question)] = score
    return course_obj

