import sys, os, pickle, yaml
from datetime import datetime

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


def process_decisions_w2(user_decisions, user_scores, max_strategy=5):
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
            if decisions[i] == 0 and count < max_strategy:
                count = 0
                new_user_decisions[user].append(0)
                new_user_sequence[user].append(i)
            elif decisions[i] == 1 and count < max_strategy:
                count = count + 1
                new_user_decisions[user].append(0)
                new_user_sequence[user].append(i)
            elif count >= max_strategy:
                new_user_decisions[user].append(1)
                new_user_sequence[user].append(new_user_sequence[user][i - 1])

    # lo montamos en el formato que acepta el evaluador
    for user, decisions in new_user_decisions.items():
        decision_list.append(
            {"nick": user, "decision": new_user_decisions[user][-1], "score":
                user_scores[user][-1]})

    return decision_list


def prepare_data(users, resul_array):

    resul_array = resul_array.tolist()
    test_users = users

    user_tuples = list(zip(test_users, resul_array))
    user_dict = array_to_dict(user_tuples)

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