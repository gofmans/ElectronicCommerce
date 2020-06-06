import pandas as pd
import numpy as np

class Student:
    free_students = set()

    def __init__(self, sid: int, pref_list: list, math_grade, cs_grade, utils):
        self.sid = sid
        self.math_grade = math_grade
        self.cs_grade = cs_grade
        self.pref_list = pref_list
        self.project = None
        self.utils = utils
        self.pair = None

    def is_free(self):
        return bool(not self.project)


class Project:
    def __init__(self, pid):
        self.pid = pid
        self.grade_type = 'cs_grade' if int(pid) % 2 else 'math_grade'
        self.proposals = []
        self.main_student = None
        self.partner_student = None
        self.price = 0
        self.best_current_score = -1

    def is_free(self):
        return bool(not self.main_student)

def get_relevant_grade(sid,students,grade_type):
    result = students[sid].cs_grade if  grade_type == 'cs_grade' else students[sid].math_grade
    return result


def get_preferences_lists(preferences_data, students, projects):
    for index, row in preferences_data.iterrows():
        temp_lis = []
        for p in projects.keys():
            temp_lis.append([p, row[str(p)]])
        sorted_list = sorted(temp_lis, key=lambda x: x[1], reverse = True)
        students[row['student_id']].pref_list = sorted_list


def make_compromise_pair(sid, students, projects, students_without_projects, free_projects):
    first_free_project = free_projects[0]
    free_projects.remove(first_free_project)
    projects[first_free_project].main_student = sid
    grade_type = projects[first_free_project].grade_type
    compromise_grade = get_relevant_grade(sid,students,grade_type)
    projects[first_free_project].best_current_score = compromise_grade
    students_without_projects.remove(sid) #nomore projectless
    students[sid].project = first_free_project


def find_best_contender(relevant_students, students, grade_type):
    if len(relevant_students) == 1: #only one contendor
        relevant_grade = get_relevant_grade(relevant_students[0],students,grade_type)
        return relevant_students[0], relevant_grade
    else:
        score_list = []
        for sid in relevant_students:
            relevant_grade = get_relevant_grade(sid, students, grade_type)
            score_list.append([sid,relevant_grade])
        result = sorted(score_list,key=lambda x: x[1], reverse = True)[0]
        return result[0], result[1]


def make_pairs(pid, students, projects, students_without_projects,free_projects):
    # get all students who is actualy interested in the project
    relevant_students = [p[0] for p in projects[pid].proposals if p[1] != -1]
    if relevant_students: # somebody is interested
        contender, contender_score  = find_best_contender(relevant_students,students,projects[pid].grade_type)
        if contender_score > projects[pid].best_current_score: #new best fit found
            if pid in free_projects: free_projects.remove(pid)
            if projects[pid].main_student: #project is taken
                defeated_student = projects[pid].main_student
                students_without_projects.append(defeated_student) #throw him to projectless
                students[defeated_student].project = None
            projects[pid].main_student = contender
            projects[pid].best_current_score = contender_score
            students_without_projects.remove(contender) #no more projectless
            projects[pid].proposals = [] #reset proposals after iteration
            students[contender].project = pid
    else:#nobody wants the project
        pass


def is_conflicting_projects(sid_1, pid_1, sid_2, pid_2, util_data):
    original_utility_student_1 = util_data.loc[sid_1, pid_1]
    optional_utility_student_1 = util_data.loc[sid_1, pid_2]
    original_utility_student_2 = util_data.loc[sid_2, pid_2]
    optional_utility_student_2 = util_data.loc[sid_2, pid_1]

    con = original_utility_student_1 < optional_utility_student_1
    flict = original_utility_student_2 < optional_utility_student_2
    return True if con and flict else False


def is_conflicting_students(sid_1, pid_1, sid_2, pid_2, grades_data):
    grade_type_project_1 = 'cs_grades' if int(pid_1) % 2 else 'math_grades'
    grade_type_project_2 = 'cs_grades' if int(pid_2) % 2 else 'math_grades'
    original_grade_project_1 = grades_data.loc[sid_1, grade_type_project_1]
    optional_grade_project_1 = grades_data.loc[sid_2, grade_type_project_1]
    original_grade_project_2 = grades_data.loc[sid_2, grade_type_project_2]
    optional_grade_project_2 = grades_data.loc[sid_1, grade_type_project_2]

    con = original_grade_project_1 < optional_grade_project_1
    flict = original_grade_project_2 < optional_grade_project_2
    return True if con and flict else False


def get_dominant_students(grades_data, n):
    pairs_data = pd.read_csv('data/' + 'pairs_' + str(n) + '.csv')
    grades_data = grades_data.set_index('student_id')  # get grades with ease
    dominant_students = []  # these are the students which will determine the matching
    for index, row in pairs_data.iterrows():
        sid_1 = int(row['partner_1'])
        if pd.isnull(row['partner_2']):
            dominant_students.append(sid_1)
            continue
        else:
            sid_2 = int(row['partner_2'])
        sum_partner_1 = grades_data.loc[sid_1, 'cs_grades'] + grades_data.loc[sid_1, 'math_grades']
        sum_partner_2 = grades_data.loc[sid_2, 'cs_grades'] + grades_data.loc[sid_2, 'math_grades']
        if sum_partner_1 > sum_partner_2:
            dominant_students.append(sid_1)
        else:
            dominant_students.append(sid_2)
    return dominant_students


def find_partner(pairs_data, sid):
    for index, row in pairs_data.iterrows():
        if row['partner_1'] == sid:
            return row['partner_2']
        elif pd.isnull(row['partner_2']):
            return None
        elif row['partner_2'] == sid:
            return row['partner_1']


def build_students_dic(pairs, grades_data, preferences_data, projects,n):
    students = {}
    if pairs:
        pairs_data = pd.read_csv('data/' + 'pairs_' + str(n) + '.csv')
    for index, row in grades_data.iterrows():
        temp_student = Student(row['student_id'], [], row['math_grades'], row['cs_grades'], None)
        if pairs: # find partner if pairs exist
            temp_student.pair = find_partner(pairs_data, temp_student.sid)
        students[temp_student.sid] = temp_student
    get_preferences_lists(preferences_data, students, projects)
    return students


def reassign_partners(projects, students, dominant_students): # complete assigment of partners
    for d_sid in dominant_students: # iterate over all dominant students and assign projects to thier partners
        temp_pid = students[d_sid].project
        temp_partner_id = students[d_sid].pair
        if not np.isnan(temp_partner_id):
            students[temp_partner_id].project = temp_pid
            projects[temp_pid].partner_student = temp_partner_id


def run_deferred_acceptance(n) -> dict:
    # load data from files
    grades_data = pd.read_csv('data/' + 'grades_' + str(n) + '.csv')
    preferences_data = pd.read_csv('data/' + 'preferences_' + str(n) + '.csv')
    pairs = False

    # build useful dictionaries
    projects = {p: Project(p) for p in preferences_data.columns[1::]}
    students = build_students_dic(pairs, grades_data, preferences_data, projects, n)

    # define helpful lists
    students_without_projects = [int(sid) for sid in students.keys()]
    free_projects = [pid for pid in projects.keys()]

    # iterate over all students and find matching projects, student pref is [pid, score]
    while students_without_projects:
        for s in students_without_projects:
            most_desired_project = students[s].pref_list.pop(0)  # get first project&score per student
            projects[most_desired_project[0]].proposals.append([s, most_desired_project[1]])
            if most_desired_project[1] == -1:  # the student run out of options
                make_compromise_pair(s, students, projects, students_without_projects, free_projects)
        for pid in projects.keys():
            make_pairs(pid, students, projects, students_without_projects, free_projects)

    matching = {sid: students[sid].project for sid in students.keys()}
    return matching


def run_deferred_acceptance_for_pairs(n) -> dict:
    # load data from files
    grades_data = pd.read_csv('data/' + 'grades_' + str(n) + '.csv')
    preferences_data = pd.read_csv('data/' + 'preferences_' + str(n) + '.csv')
    pairs = True

    # build useful dictionaries
    projects = {p: Project(p) for p in preferences_data.columns[1::]}
    students = build_students_dic(pairs, grades_data, preferences_data, projects, n)

    # define helpful lists
    dominant_students = get_dominant_students(grades_data, n)
    students_without_projects = [*dominant_students]
    free_projects = [pid for pid in projects.keys()]

    # assign projects for dominant students
    while students_without_projects:
        for s in students_without_projects:
            most_desired_project = students[s].pref_list.pop(0)  # get first project&score per student
            projects[most_desired_project[0]].proposals.append([s, most_desired_project[1]])
            if most_desired_project[1] == -1:  # the student run out of options
                make_compromise_pair(s, students, projects, students_without_projects, free_projects)
        for pid in projects.keys():
            make_pairs(pid, students, projects, students_without_projects, free_projects)

    # complete assigment of partners to projects
    reassign_partners(projects, students, dominant_students)
    matching = {sid: students[sid].project for sid in students.keys()}
    return matching


def count_blocking_pairs(matching_file, n) -> int:
    # load data from files
    matching_data = pd.read_csv(matching_file)
    grades_data = pd.read_csv('data/' + 'grades_' + str(n) + '.csv')
    grades_data = grades_data.set_index('student_id')
    util_data = pd.read_csv('data/' + 'preferences_' + str(n) + '.csv')
    util_data = util_data.set_index('student_id')

    blocking_pairs = 0
    for outer_index, outer_row in matching_data.iterrows():
        outer_sid = outer_row['sid']
        outer_pid = str(int(outer_row['pid']))
        for inner_index, inner_row in matching_data.iterrows():
            inner_sid = inner_row['sid']
            inner_pid = str(int(inner_row['pid']))
            if [outer_sid, outer_pid] == [inner_sid, inner_pid]: # it's the same row
                continue
            conflicting_projects = is_conflicting_projects(outer_sid, outer_pid, inner_sid, inner_pid, util_data)
            conflicting_students = is_conflicting_students(outer_sid, outer_pid, inner_sid, inner_pid, grades_data)
            if conflicting_projects and conflicting_students:
                blocking_pairs += 1
    return blocking_pairs / 2 #note we counted every pair twice!


def calc_total_welfare(matching_file, n) -> int:
    # load data from files
    matching_data = pd.read_csv(matching_file)
    util_data = pd.read_csv('data/' + 'preferences_' + str(n) + '.csv')
    util_data = util_data.set_index('student_id')

    total_welfare = 0
    for index, row in matching_data.iterrows():
        sid = row['sid']
        pid = str(int(row['pid']))
        total_welfare += util_data.loc[sid, pid]
    return total_welfare


