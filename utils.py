import sys

def logger(message, log_file="todo"): # TODO
    print(message)
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(log_file, 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(message)
        sys.stdout = original_stdout # Reset the standard output to its original value


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