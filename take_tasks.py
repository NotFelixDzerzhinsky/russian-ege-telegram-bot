import random
from types import NoneType
import pandas as pd
import ranks
import numpy as np
import os, psycopg2
from config import DataBaseURL

connection = psycopg2.connect(
    DataBaseURL, sslmode='require'
)
connection.autocommit = True

class Task(object):
    def __init__(self, statement, solution, answer):
        self.statement = statement
        self.solution = solution
        self.answer = answer

user_ids = set()
current_task = dict()
tasks_list = dict()
global_tasks_list = []

def init():
    os.chdir('tasks')
    for task_number in range(1, 26):
        if os.path.exists(f'task{task_number}') == True:
            tasks_list[task_number] = pd.read_csv(f'task{task_number}/task{task_number}.csv')
            global_tasks_list.append(task_number)
        else:
            print(f'folder task{task_number} does not exists :(')
    os.chdir('..')
    return global_tasks_list

def change_element(userid, task_number, flag):
    if flag == 1:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT count_correct FROM leaderboard{task_number} WHERE user_id={userid};""")
            value = cursor.fetchone()[0] + 1
            cursor.execute(f"""UPDATE leaderboard{task_number}
            SET count_correct = {value}
            WHERE user_id = {userid};""")
    else:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT count_false FROM leaderboard{task_number} WHERE user_id={userid};""")
            value = cursor.fetchone()[0] + 1
            cursor.execute(f"""UPDATE leaderboard{task_number}
            SET count_false = {value}
            WHERE user_id = {userid};""")

def get_user_stats(userid, task_number):
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT * FROM leaderboard{task_number} WHERE user_id = {userid};""")
        return cursor.fetchone()

def check_user_in_database(userid):
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT * FROM users WHERE user_id = {userid};""")
        return cursor.fetchone()

def get_user_list():
    user_list = []
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT * FROM users;""")
        for user_information in cursor.fetchall():
            user_list.append(user_information[0])
    return user_list

def get_leaderboard(user, task_number : int):
    userid = user.id

    if type(check_user_in_database(userid)) == NoneType:
        with connection.cursor() as cursor:
            cursor.execute(f"""INSERT INTO users VALUES ({userid});""")

    dict_before_sort = dict()
    sort_list = []
    was_user = 1

    if task_number == 0:
        with connection.cursor() as cursor:
            for task in global_tasks_list:
                cursor.execute(f"""SELECT * FROM leaderboard{task};""")
                for user_information in cursor.fetchall():
                    if user_information[0] in dict_before_sort:
                        dict_before_sort[user_information[0]][2] += user_information[2]
                        dict_before_sort[user_information[0]][3] += user_information[3]
                    else:
                        dict_before_sort[user_information[0]] = list(user_information)
    else:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT * FROM leaderboard{task_number};""")
            for user_information in cursor.fetchall():
                if user_information[0] in dict_before_sort == True:
                    dict_before_sort[user_information[0]][2] += user_information[2]
                    dict_before_sort[user_information[0]][3] += user_information[3]
                else:
                    dict_before_sort[user_information[0]] = user_information
    
    for key, value in dict_before_sort.items():
        sort_list.append([value[2] - value[3], value[1], ranks.get_rank(value[2] - value[3]), value[0]])

    sort_list.sort()
    sort_list.reverse()

    return_leaderboard = ''

    for c in range(0, min(len(sort_list), 7)):
        return_leaderboard += str(c + 1)
        return_leaderboard += ") "
        return_leaderboard += sort_list[c][1]
        return_leaderboard += " | "
        return_leaderboard += str(sort_list[c][0])
        return_leaderboard += " | "
        return_leaderboard += sort_list[c][2]
        return_leaderboard += '\n'
        if sort_list[c][3] == userid:
            was_user = 0
    
    if return_leaderboard == '':
        return 'Эх, пока что никто не решал данное задание, но вы можете быть первым!'

    if was_user:
        return_leaderboard += '...\n'
        for c in range (len(sort_list)):
            if sort_list[c][3] == userid:
                return_leaderboard += str(c + 1)
                return_leaderboard += ") "
                return_leaderboard += sort_list[c][1]
                return_leaderboard += " | "
                return_leaderboard += str(sort_list[c][0])
                return_leaderboard += " | "
                return_leaderboard += sort_list[c][2]
                return_leaderboard += '\n'
                break

    return return_leaderboard

def get_task(user, task_number : int):
    print(len(tasks_list[task_number]))
    global current_task
    global user_ids
    userid = user.id
    user_full_name = user.full_name

    if type(check_user_in_database(userid)) == NoneType:
        with connection.cursor() as cursor:
            cursor.execute(f"""INSERT INTO users VALUES ({userid});""")

    if type(get_user_stats(userid, task_number)) == NoneType:
        with connection.cursor() as cursor:
            cursor.execute(f"""INSERT INTO leaderboard{task_number} VALUES ({userid}, '{user_full_name}', {0}, {0});""")
            print(f'user {user_full_name} added')

    if (userid in user_ids) == False:
        user_ids.add(userid)
        current_task[userid] = Task("","","")

    cur_task = ""
    rand_value = random.randint(0, len(tasks_list[task_number]) - 1)
    save_task = Task(tasks_list[task_number]['task'][rand_value], 
        tasks_list[task_number]['solution'][rand_value], 
        tasks_list[task_number]['answer'][rand_value]
    )
    cur_task += save_task.statement

    current_task[userid] = save_task
    return cur_task

def check_task(user, task_number : int, result : str):
    return_value = ""
    userid = user.id

    answers = current_task[userid].answer.lower().split('|')

    if result.lower() in answers:
        change_element(userid, task_number, 1)
        return_value = "True"
    else:
        get_solution = ""
        change_element(userid, task_number, 0)
        get_solution += current_task[userid].solution
        return_value = get_solution

    current_task[userid] = Task("", "", "")

    return return_value
