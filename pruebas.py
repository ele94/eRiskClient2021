from data_client import DataClient, ServerClient
from utils import logger, load_pickle, check_pickle, save_pickle, load_all_parameters, load_parameters
from runs import Run

runs_ids = [0, 1, 2, 3, 4]

def main():

    client = ServerClient()

    data = client.get_writings()



def experiment():

    first_try = True

    client = ServerClient()

    params = load_parameters("params.yaml")
    run_params = load_all_parameters("run_params.yaml")

    logger("Starting experiment")

    # create runs 1, 2, 3, 4, 5
    run_objects = []
    for run_id in runs_ids:
        new_run = Run(run_id, run_params[run_id])
        run_objects.append(new_run)

    # if its the first time were connecting to the server
    if first_try:
        # get first batch of writings
        data = client.get_writings()

        # initialize users list and users writing history
        users = [user["nick"] for user in data]
        user_writings_history = {user: [] for user in users}

        # update writings history with first batch of writings
        #user_writings_history = update_writings_history(data, user_writings_history)

    else:
        data = client.get_writings()
        users = load_pickle(params["pickles_path"], params["users_name"])
        user_writings_history = load_pickle(params["pickles_path"], params["writings_name"])
        # load users and writing history from pickle


    keep_going = True
    while data is not None and keep_going:

        # preprocess batch of writings
        # TODO

        # update writings history with clean writings
        user_writings_history = update_writings_history(data, user_writings_history)

        #save user writings history to pickle
        #maybe save it only if an error arises?
        save_pickle(params["pickles_path"], params["writings_name"], user_writings_history)

        # get decision for run and send decision for run
        for run_object in run_objects:
            decision = run_object.get_decisions(user_writings_history, users)
            client.send_decision(decision, run_object.run_identifier) # todo add try catch here?
            # if error, keep_going = false and print something about the error

        # get new batch of writings
        # he pasado esto para aqui abajo para que si data me da null ya salga del bucle
        data = client.get_writings()
        print(data)
        if data is None:
            keep_going = False
            continue



########## helper methods ##############################################3

def update_writings_history(data, user_writings_history):
    user_writings = {writing["nick"]: writing for writing in data}
    user_writings_history = {user: (messages + [user_writings[user]] if user in user_writings.keys() else messages)
                             for (user, messages) in user_writings_history.items()}
    return user_writings_history

if __name__ == '__main__':
    main()
