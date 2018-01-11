from model import *
import json

def read(file_name):
    with open(file_name,'r') as f:
        course_dict = json.load(f)
    return course_from_dict(course_dict)

def save(gb, file_name):
    data = json.dumps(course_to_dict(gb), indent=2, sort_keys=True)
    with open(file_name, mode='w', encoding='utf-8') as f:
        f.write(data)

# transfer all data in the course object hierarchy to a dictionary
def course_to_dict(gb):
    course = {'name': gb.name, 'term': gb.term, 'schema_version': gb.schema_version, 'gradeables':[], 'scores':[]}
    course['categories'] = [{'id':i, 'name': c.name, 'pct_of_grade': c.pct_of_grade, \
            'drop_low_n': c.drop_low_n, 'obj': c} for i, c in enumerate(gb.categories)]
    course['students'] = [{'id':i, 'first': s.first, 'last': s.last, \
            'email': s.email, 'is_active': s.is_active, 'obj': s} for i, s in enumerate(gb.students)]
    cat_dict = {item['obj']: item for item in course['categories']}
    for i, g in enumerate(gb.gradeables):
        gd = {'id':i, 'cid': cat_dict[g.category]['id'], 'name': g.name, 'total_pts': g.total_pts, \
                'sub_pct': g.sub_pct, 'added_pts': g.added_pct, 'added_pct': g.added_pct, 'questions': []}
        for j, q in enumerate(g.questions):
            gd['questions'].append( {'id':j, 'gid': i, 'points': q.points} )
            for sd in course['students']:
                course['scores'].append( {'sid': sd['id'], 'gid': gd['id'], 'qid': j, \
                        'value': gb.get_score(sd['obj'],g,q).value } )
        course['gradeables'].append(gd)       
    for s in course['students']: del s['obj']
    for c in course['categories']: del c['obj']
    return course

# construct the course object hierarchy from a dictionary
def course_from_dict(course_dict):
    global schema_version
    while not 'schema_version' in course_dict or course_dict['schema_version'] < schema_version:
        upgrade(course_dict)

    # id-keyed dicts for reconstructing scores
    category_dict = {item['id'] : item for item in course_dict['categories']}
    gradeable_dict = {item['id'] : item for item in course_dict['gradeables']}
    student_dict = {item['id'] : item for item in course_dict['students']}
    question_dict = {(q['gid'],q['id']) : q for g in course_dict['gradeables'] \
            for q in g['questions'] }

    course_obj = Course(course_dict['name'], course_dict['term'])
    for cd in course_dict['categories']:
        category = Category(course_obj, cd['name'], cd['pct_of_grade'], cd['drop_low_n'])
        category_dict[cd['id']]['obj'] = category
        course_obj.categories.append(category)
    for sd in course_dict['students']:
        student = Student(course_obj, sd['first'], sd['last'], sd['email'], sd['is_active'])
        student_dict[sd['id']]['obj'] = student
        course_obj.students.append(student)
    for gd in course_dict['gradeables']:
        gradeable = Gradeable(course_obj, gd['name'], category_dict[gd['cid']]['obj'], \
                gd['total_pts'], gd['sub_pct'], gd['added_pts'], gd['added_pct'])
        gradeable_dict[gd['id']]['obj'] = gradeable
        course_obj.gradeables.append(gradeable)
        for qd in gd['questions']:
            question = Question(gradeable, qd['points'])
            question_dict[(qd['gid'],qd['id'])]['obj'] = question
            gradeable.questions.append(question)

    for sd in course_dict['scores']:
        student = student_dict[sd['sid']]['obj']
        gradeable = gradeable_dict[sd['gid']]['obj']
        question = question_dict[(sd['gid'],sd['qid'])]['obj']
        score = Score(student, gradeable, question, sd['value'])
        course_obj.scores[(student, gradeable, question)] = score
    return course_obj

def upgrade(course_dict):
    if not 'schema_version' in course_dict:
        course_dict['schema_version'] = 1
        print("upgraded schema to version 1")
    elif course_dict['schema_version'] == 1:
        # upgrade from version 1 to version 2
        pass

