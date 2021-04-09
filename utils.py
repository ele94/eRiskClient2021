import sys, os, pickle, yaml

def logger(message, log_file="todo"): # TODO
    print(message)
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(log_file, 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(message)
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

# gets in
def process_decisions(users, decisions, scores):
    pass # TODO (recuerda que tienes que guardar las decisiones anteriores si quieres usar la ventana)




def prepare_data(users, resul_array):

    resul_array = resul_array.tolist()
    test_users = users.tolist()

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