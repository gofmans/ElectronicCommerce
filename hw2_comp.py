import pandas as pd
import numpy as np

class Student:
    free_students = set()

    def __init__(self, sid, pref_list: list, math_grade, cs_grade, utils):
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


def make_compromise_pair(sid, merged_students, projects, students_without_projects, free_projects):
    first_free_project = free_projects[0]
    free_projects.remove(first_free_project)
    projects[first_free_project].main_student = sid
    grade_type = projects[first_free_project].grade_type
    compromise_grade = get_relevant_grade(sid, merged_students, grade_type)
    projects[first_free_project].best_current_score = compromise_grade
    students_without_projects.remove(sid) #nomore projectless
    merged_students[sid].project = first_free_project


def find_best_contender(relevant_students, merged_students, grade_type):
    if len(relevant_students) == 1: #only one contendor
        relevant_grade = get_relevant_grade(relevant_students[0],merged_students,grade_type)
        return relevant_students[0], relevant_grade
    else:
        score_list = []
        for sid in relevant_students:
            relevant_grade = get_relevant_grade(sid, merged_students, grade_type)
            score_list.append([sid, relevant_grade])
        result = sorted(score_list, key=lambda x: x[1], reverse = True)[0]
        return result[0], result[1]


def find_best_contender_utils(relevant_students):
    if len(relevant_students) == 1:  # only one contendor
        relevant_util = relevant_students[0][1]
        return relevant_students[0][0], relevant_util
    else:
        score_list = []
        for sid in relevant_students:
            relevant_util = sid[1]
            score_list.append([sid[0], relevant_util])
        result = sorted(score_list, key=lambda x: x[1], reverse=True)[0]
        return result[0], result[1]



def make_pairs(pid, merged_students, projects, students_without_projects,free_projects):
    # get all students who is actually interested in the project
    relevant_students = [p[0] for p in projects[pid].proposals if p[1] != -1]
    if relevant_students: # somebody is interested
        contender, contender_score = find_best_contender(relevant_students,merged_students,projects[pid].grade_type)
        if contender_score > projects[pid].best_current_score: #new best fit found
            if pid in free_projects:
                free_projects.remove(pid)
            if projects[pid].main_student: # project is taken
                defeated_student = projects[pid].main_student
                students_without_projects.append(defeated_student) #throw him to projectless
                merged_students[defeated_student].project = None
            projects[pid].main_student = contender
            projects[pid].best_current_score = contender_score
            students_without_projects.remove(contender) #no more projectless
            projects[pid].proposals = [] #reset proposals after iteration
            merged_students[contender].project = pid
    else:#nobody wants the project
        pass


def make_pairs_utils(pid, merged_students, projects, students_without_projects,free_projects):
    # get all students who is actually interested in the project
    relevant_students = [p for p in projects[pid].proposals if p[1] != -1]
    if relevant_students: # somebody is interested
        contender, contender_util = find_best_contender_utils(relevant_students)
        if contender_util > projects[pid].best_current_score: #new best fit found
            if pid in free_projects:
                free_projects.remove(pid)
            if projects[pid].main_student: # project is taken
                defeated_student = projects[pid].main_student
                students_without_projects.append(defeated_student) #throw him to projectless
                merged_students[defeated_student].project = None
            projects[pid].main_student = contender
            projects[pid].best_current_score = contender_util
            students_without_projects.remove(contender) #no more projectless
            projects[pid].proposals = [] #reset proposals after iteration
            merged_students[contender].project = pid
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
    pairs_data = pd.read_csv('data/' + 'pairs_comp_' + str(n) + '.csv')
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


def merge_lists(first_list, second_list):
    # pref list in form of:[[pid, utility_score],...] >> [['5', 4], ['4', 3], ['1', 2], ['2', 1]]
    merged_list = []

    combined_score = None
    for i in first_list: # i in form of pair: [pid, utility_score]
        for j in second_list: # j in form of pair: [pid, utility_score]
            if i[0] == j[0]:
                combined_score = i[1] + j[1] # same project in both lists, sum scores
                second_list.remove(j) # remove item from second list
                break
        if combined_score:
            merged_list.append([i[0], combined_score])
        else:
            merged_list.append(i)
    if second_list: # add remaining elements from second list
        merged_list += second_list
    merged_list = sorted(merged_list, key=lambda x: x[1], reverse=True)
    return merged_list



def build_merged_students(grades_data, preferences_data, projects, n):
    pairs_data = pd.read_csv('data/' + 'pairs_comp_' + str(n) + '.csv')
    # build normal students dictionary and preferences list
    students = {}
    for index, row in grades_data.iterrows():
        temp_student = Student(row['student_id'], [], row['math_grades'], row['cs_grades'], None)
        temp_student.pair = find_partner(pairs_data, temp_student.sid)
        students[temp_student.sid] = temp_student
    get_preferences_lists(preferences_data, students, projects)

    # iterate over all students and combine partners into one
    merged_students = {} # Student : (sid, pref_list, math_grade, cs_grade, utils)
    for sid in students.keys():
        if not np.isnan(students[sid].pair):
            merged_sid = str(int(students[sid].sid)) + '.' + str(int(students[sid].pair)) # get new identifier
            merged_math_grade = (students[sid].math_grade + students[students[sid].pair].math_grade) / 2
            merged_cs_grade = (students[sid].cs_grade + students[students[sid].pair].cs_grade) / 2
            if not students[sid].pref_list or not students[students[sid].pair].pref_list:
                continue #we already counted that pair
            merged_pref_list = merge_lists(students[sid].pref_list, students[students[sid].pair].pref_list)
            merged_students[merged_sid] = Student(merged_sid, merged_pref_list, merged_math_grade, merged_cs_grade, None)
        else: #the student does not have a pair
            merged_students[sid] = students[sid]
    return students, merged_students


def reassign_projects(students, merged_students): # complete assigment of students
    for merged_sid, merged_data in merged_students.items(): # iterate over all merged students and assign projects accordingly
        original_sids = str(merged_sid).split('.')
        temp_pid = merged_students[merged_sid].project
        sid_1, sid_2 = int(original_sids[0]), int(original_sids[1])
        students[sid_1].project = temp_pid
        if sid_2 != 0:
            sid_2 = int(original_sids[1])
            students[sid_2].project = temp_pid


def run_deferred_acceptance_for_pairs_comp(n) -> dict:
    # load data from files
    grades_data = pd.read_csv('data/' + 'grades_comp_' + str(n) + '.csv')
    preferences_data = pd.read_csv('data/' + 'preferences_comp_' + str(n) + '.csv')

    # build useful dictionaries
    projects = {p: Project(p) for p in preferences_data.columns[1::]}
    students, merged_students = build_merged_students(grades_data, preferences_data, projects, n)

    # define helpful lists
    students_without_projects = list(merged_students.keys())
    free_projects = [pid for pid in projects.keys()]

    # assign projects for merged students
    while students_without_projects:
        for s in students_without_projects:
            most_desired_project = merged_students[s].pref_list.pop(0)  # get first pref: [pid, utility_score] >> ['5', 4]
            projects[most_desired_project[0]].proposals.append([s, most_desired_project[1]])
            if most_desired_project[1] == -1:  # the student run out of options
                make_compromise_pair(s, merged_students, projects, students_without_projects, free_projects)
        for pid in projects.keys():
            if n == 1:
                make_pairs(pid, merged_students, projects, students_without_projects, free_projects)
            else:
                make_pairs_utils(pid, merged_students, projects, students_without_projects, free_projects)

    # translate assigment of students to projects
    reassign_projects(students, merged_students)
    matching = {sid: students[sid].project for sid in students.keys()}
    return matching


def count_blocking_pairs_comp(matching_file, n) -> int:
    # load data from files
    matching_data = pd.read_csv(matching_file)
    grades_data = pd.read_csv('data/' + 'grades_comp_' + str(n) + '.csv')
    grades_data = grades_data.set_index('student_id')
    util_data = pd.read_csv('data/' + 'preferences_comp_' + str(n) + '.csv')
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


def calc_total_welfare_comp(matching_file, n) -> int:
    # load data from files
    matching_data = pd.read_csv(matching_file)
    util_data = pd.read_csv('data/' + 'preferences_comp_' + str(n) + '.csv')
    util_data = util_data.set_index('student_id')

    total_welfare = 0
    for index, row in matching_data.iterrows():
        sid = row['sid']
        pid = str(int(row['pid']))
        total_welfare += util_data.loc[sid, pid]
    return total_welfare


