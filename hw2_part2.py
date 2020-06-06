import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

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
        self.proposals = {}
        self.main_student = None
        self.partner_student = None
        self.price = 0

    def is_free(self):
        return bool(not self.main_student)


def build_student_dic(preferences_data, projects):
    students = {}
    for index, row in preferences_data.iterrows():
        temp_lis = []
        for p in projects.keys():
            temp_lis.append([p, row[str(p)]])
        sorted_list = sorted(temp_lis, key=lambda x: x[1], reverse=True)
        students[row['student_id']] = Student(row['student_id'], sorted_list, None, None, None)
    return students


def not_perfect_matching(G, students):
    students_ids = list(students.keys())
    matching_dic = nx.bipartite.maximum_matching(G, top_nodes=students_ids)
    if len(students_ids) == len(matching_dic.keys()) / 2:
        return False, matching_dic
    else:
        return True, matching_dic


def fix_prices_if_all_bigger_than_zero(projects):
    zero_exist = False
    for pid in projects.keys():
        if projects[pid].price == 0:
            zero_exist = True
            break
    if not zero_exist: #all prices bigger than zero, decrease all by 1
        for pid in projects.keys():
            projects[pid].price -= 1


def get_final_dictionaries(match_dic, projects): #build final dictionaries
    match_dic = {k: val for k, val in match_dic.items() if type(k) != str}
    prices_dict = {pid: projects[pid].price for pid in projects.keys()}
    return match_dic, prices_dict


def build_bipartite_graph(students, projects):
    edges = []
    for sid, sdata in students.items():
        utility_list = [[p[0], p[1] - projects[p[0]].price] for p in sdata.pref_list] #if p[1] != -1]
        top_wanted = [(sid, utls[0]) for utls in utility_list if utls[1] == max([u[1] for u in utility_list])]
        for e in top_wanted:
            edges.append(e)
    project_ids = [e[0] for e in edges]
    students_ids = list(students.keys())
    G = nx.Graph()
    G.add_nodes_from(students_ids, bipartite = 0)
    G.add_nodes_from(project_ids, bipartite = 1)
    G.add_edges_from(edges)
    return G


def get_conflicting_projects(G, match_dic, students):
    # conflicting_projects = []
    # for c in nx.connected_components(G):
    #     sub_g = G.subgraph(c)
    #     temp_match = nx.bipartite.maximum_matching(sub_g)
    #     students_in_sub_g = sum([1 for n in sub_g.nodes if type(n) != str])
    #     if students_in_sub_g != len(temp_match.keys()) / 2: #no matching
    #         projects_occurrences = []
    #         for e in sub_g.edges:
    #             projects_occurrences += [e[i] for i in [0,1] if type(e[i]) == str]
    #         conflicting_projects += [pid for pid in set(projects_occurrences) if projects_occurrences.count(pid) > 1]
    # return conflicting_projects
    conflicts = {}

    projectles_students = students.keys() - match_dic.keys()
    for projectles_student in projectles_students:
        conflicting_projects = []
        missed_projects = G.neighbors(projectles_student)
        thieves_students = []
        for missed_project in missed_projects:
            thieves_students.append(match_dic[missed_project])
        for thief in thieves_students:
            loot_projects = [pid for pid in G.neighbors(thief)]
            conflicting_projects += loot_projects
        return set(conflicting_projects)




def run_market_clearing(n):
    # load data
    preferences_data = pd.read_csv('data/' + 'preferences_' + str(n) + '.csv')
    projects = {p: Project(p) for p in preferences_data.columns[1::]}
    students = build_student_dic(preferences_data, projects)

    # check for existence of perfect matching
    G = build_bipartite_graph(students, projects)
    no_matching_found, match_dic = not_perfect_matching(G, students)
    if not no_matching_found:
        return get_final_dictionaries(match_dic, projects)

    while no_matching_found:
        conflicting_projects = get_conflicting_projects(G, match_dic, students)
        for pid in conflicting_projects: # increase price of conflicted projects
            projects[pid].price += 1
        fix_prices_if_all_bigger_than_zero(projects) # decrease projects prices if all bigger than zero
        G = build_bipartite_graph(students, projects) # update graph after prices update
        no_matching_found, match_dic = not_perfect_matching(G, students)

    return get_final_dictionaries(match_dic, projects)


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

