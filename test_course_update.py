from usercustomize1 import *
import json

PATH_JSON_COURSE=get_path('project/project4/data/course.json')
PATH_JSON_COURSE_UPDATE=get_path('project/project4/data/course_update.json')

with open(PATH_JSON_COURSE, 'r', encoding='utf-8') as f1:
    course_data = json.load(f1)

with open(PATH_JSON_COURSE_UPDATE, 'r', encoding='utf-8') as f2:
    course_update_data = json.load(f2)

# Tạo một dict tra cứu status và score theo id từ course_data
update_map = {}
for session in course_data['sessions']:
    for ex in session['exercises']:
        update_map[ex['id']] = {
            'status': ex['status'],
            'score': ex['score']
        }

# Cập nhật lại vào course_update_data
for session in course_update_data['sessions']:
    for ex in session['exercises']:
        ex_id = ex['id']
        if ex_id in update_map:
            ex['status'] = update_map[ex_id]['status']
            ex['score'] = update_map[ex_id]['score']
            
with open(PATH_JSON_COURSE, 'w', encoding='utf-8') as f:
    json.dump(course_update_data, f, indent=2, ensure_ascii=False)
    


