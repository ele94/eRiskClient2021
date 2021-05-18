from datetime import datetime
import subprocess
import os
import pickle
import yaml
import sys
import csv

def logger(message, log_file="log.txt"):
    txt = "[{}] {}".format(datetime.now(), message)
    print(txt[:500])
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(log_file, 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(txt[:500])
        sys.stdout = original_stdout # Reset the standard output to its original value


########### parameters ##################

def load_parameters(params_file):
    with open(params_file) as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    return params

def load_all_parameters(params_file):
    with open(params_file) as f:
        docs = yaml.load_all(f, Loader=yaml.FullLoader)
        params = list(docs)
    return params

def update_parameters(params_file, params):
    with open(params_file, 'w') as f:
        yaml.safe_dump(params, f, default_flow_style=False)
    return params


########## process decisions to send to server ##############################


def process_decisions(users, decisions, scores):
    user_decisions = prepare_data(users, decisions)
    #user_scores = prepare_data(users, scores)

    return process_decisions_f2(user_decisions)

# gets in dictionary: user - list of decisions
def process_decisions_f2(user_decisions):
    decision_list = []
    for user, decisions in user_decisions.items():
        formatted_string = {"nick": user, "decision": decisions[-1], "score": decisions[-1]}
        decision_list.append(formatted_string)

    return decision_list

def process_decision_seq(users, all_decisions, scores):
    user_decisions = prepare_data_v2(users, all_decisions)

    return process_decisions_w2(user_decisions, user_decisions)


def process_decisions_w2(user_decisions, user_scores, max_strategy=1):
    decision_list = []
    new_user_decisions = {}
    new_user_sequence = {}

    for user, decisions in user_decisions.items():
        new_user_decisions[user] = []
        new_user_sequence[user] = []

    # politica de decisiones: decidimos que un usuario es positivo a partir del 5 mensaje positivo consecutivo
    # a partir de ahi, todas las decisiones deben ser positivas, y la secuencia mantenerse estable
    for user, decisions in user_decisions.items():
        count = 0
        for i in range(0, len(decisions)):
            count = count+1
            if decisions[i] == 0 and count <= max_strategy:
                count = 0
                new_user_decisions[user].append(0)
                new_user_sequence[user].append(i)
            elif decisions[i] == 1 and count <= max_strategy:
                new_user_decisions[user].append(1)
                new_user_sequence[user].append(i)
            else:
                new_user_decisions[user].append(1)
                new_user_sequence[user].append(new_user_sequence[user][i - 1])

    # lo montamos en el formato que acepta el evaluador
    for user, decisions in new_user_decisions.items():
        decision_list.append(
            {"nick": user, "decision": new_user_decisions[user][-1], "score":
                user_scores[user][-1], "sequence": new_user_sequence[user][-1]})

    return decision_list


def prepare_data(users, resul_array):

    resul_array = resul_array.tolist()
    test_users = users

    user_tuples = list(zip(test_users, resul_array))
    user_dict = array_to_dict(user_tuples)

    return user_dict


def prepare_data_v2(users, resul_array):

    user_dict = {}
    for index, user in enumerate(users):
        user_dict[user] = [resul_list[index] for resul_list in resul_array]

    return user_dict


def array_to_dict(l):
    d = dict()
    [d[t[0]].append(t[1]) if t[0] in list(d.keys())
     else d.update({t[0]: [t[1]]}) for t in l]
    return d



######### pickles ########################

def save_pickle(filepath, filename, data):
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    file = os.path.join(filepath, filename)
    with open(file, 'wb') as data_file:
        pickle.dump(data, data_file)


def load_pickle(filepath, filename):
    file = os.path.join(filepath, filename)
    with open(file, 'rb') as data_file:
        data = pickle.load(data_file)
    return data


def remove_pickle(filepath, filename):
    file = os.path.join(filepath, filename)
    if os.path.exists(file):
        os.remove(file)

def check_pickle(filepath, filename):
    if os.path.exists(filepath):
        file = os.path.join(filepath, filename)
        return os.path.isfile(file)
    else:
        return False


########## evaluation #################

def penalty(delay):
    import numpy as np
    p = 0.0078
    pen = -1.0 + 2.0 / (1 + np.exp(-p * (delay - 1)))
    return (pen)



def eval_performance(run_results, qrels):
    import numpy as np

    total_pos = n_pos(qrels)

    true_pos = 0
    true_neg = 0
    false_pos = 0
    false_neg = 0
    erdes5 = np.zeros(len(run_results))
    erdes50 = np.zeros(len(run_results))
    ierdes = 0
    latency_tps = list()
    penalty_tps = list()

    for r in run_results:
        try:
            # print(qrels[ r['nick']   ], r['decision'], r['nick'], qrels[ r['nick']   ] ==  r['decision'] )
            if (qrels[r['nick']] == r['decision']):
                if (r['decision'] == 1):
                    # print('dec = 1')
                    true_pos += 1
                    erdes5[ierdes] = 1.0 - (1.0 / (1.0 + np.exp((r['sequence'] + 1) - 5.0)))
                    erdes50[ierdes] = 1.0 - (1.0 / (1.0 + np.exp((r['sequence'] + 1) - 50.0)))
                    latency_tps.append(r['sequence'] + 1)
                    penalty_tps.append(penalty(r['sequence'] + 1))
                else:
                    # print('dec = 0')
                    true_neg += 1
                    erdes5[ierdes] = 0
                    erdes50[ierdes] = 0
            else:
                if (r['decision'] == 1):
                    # print('++')
                    false_pos += 1
                    erdes5[ierdes] = float(total_pos) / float(len(qrels))
                    erdes50[ierdes] = float(total_pos) / float(len(qrels))
                else:
                    # print('****')
                    false_neg += 1
                    erdes5[ierdes] = 1
                    erdes50[ierdes] = 1

        except KeyError:
            print("User does not appear in the qrels:" + r['nick'])

        ierdes += 1

    if (true_pos == 0):
        precision = 0
        recall = 0
        F1 = 0
    else:
        precision = float(true_pos) / float(true_pos + false_pos)
        recall = float(true_pos) / float(total_pos)
        F1 = 2 * (precision * recall) / (precision + recall)

    speed = 1 - np.median(np.array(penalty_tps))

    eval_results = {}
    eval_results['precision'] = precision
    eval_results['recall'] = recall
    eval_results['F1'] = F1
    eval_results['ERDE_5'] = np.mean(erdes5)
    eval_results['ERDE_50'] = np.mean(erdes50)
    eval_results['median_latency_tps'] = np.median(np.array(latency_tps))
    eval_results['median_penalty_tps'] = np.median(np.array(penalty_tps))
    eval_results['speed'] = speed
    eval_results['latency_weighted_f1'] = F1 * speed

    return eval_results


def n_pos(qrels):
    total_pos = 0
    for key in qrels:
        total_pos += qrels[key]
    return (total_pos)


################## CSV ###############

def write_csv(eval_resuls, run=None):
    if not run:
        run = 0

    data = {"run": run, "commit hash": subprocess.check_output(["git", "describe", "--always"]).strip().decode()}

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    data["timestamp"] = dt_string

    data.update(eval_resuls)

    erisk_eval_file = os.path.join("post_task_eval.csv")
    csv_file = erisk_eval_file

    csv_columns = data.keys()
    dict_data = [data]

    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            if os.path.getsize(csv_file) == 0:
                writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")