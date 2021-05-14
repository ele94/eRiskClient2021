from data_client import DataClient, ServerClient, PickleClient
from utils import logger, load_pickle, check_pickle, save_pickle, load_all_parameters, load_parameters, write_csv
from runs import Run
from preprocessor import preprocess_data

runs_ids = [0, 1, 2, 3, 4]

def tests():

    client = ServerClient()

    data = client.get_writings()



def eval():

    params = load_parameters("params.yaml")
    client = PickleClient(params)
    run_params = load_all_parameters("run_params.yaml")

    logger("Starting post-task evaluation")

    # create runs 1, 2, 3, 4, 5
    logger("Creating run objects")
    run_objects = []
    for run_id in runs_ids:
        logger("Run {} with params {}".format(run_id, run_params[run_id]))
        new_run = Run(run_id, run_params[run_id])
        run_objects.append(new_run)

    clean_data = client.get_writings()
    current_sequence = clean_data[0]["number"]

    logger("Got data of length {}, sequence {}".format(len(clean_data), clean_data[0]["number"]))
    logger("Data: {}".format(clean_data))

    # initialize users list and users writing history
    users = [user["nick"] for user in clean_data]
    clean_user_writings_history = {user: [] for user in users}

    max = 470
    keep_going = True
    eval_resuls = {}
    positive_users = []
    while clean_data is not None and keep_going:

        if current_sequence >= max:
            keep_going = False
        clean_user_writings_history = update_writings_history(clean_data, clean_user_writings_history)

        # get decision for run and send decision for run
        for run_object in run_objects:
            logger("Getting decisions for run {} in sequence {}".format(run_object.run_identifier, current_sequence))
            decision = run_object.get_sequence_decisions(clean_user_writings_history, users)
            logger("Decision: {}".format(decision[-1]))
            logger("Sending decision for run {} in sequence {}".format(run_object.run_identifier, current_sequence))
            resuls = client.send_decision(decision, run_object.run_identifier)
            logger("Decision resuls: {}".format(resuls))
            eval_resuls[run_object.run_identifier] = resuls


        # get new batch of writings
        # he pasado esto para aqui abajo para que si data me da null ya salga del bucle
        logger("Getting new data batch")
        clean_data = client.get_writings()
        logger("Response: {}".format(clean_data))
        if clean_data is None:
            keep_going = False
            continue

        current_sequence = clean_data[0]["number"]

    for run_id in runs_id:
        logger("Eval resuls: {}".format(eval_resuls[run_id]))
        write_csv(eval_resuls[run_id], run_id)




def main():

    first_try = False

    client = ServerClient()

    params = load_parameters("params.yaml")
    run_params = load_all_parameters("run_params.yaml")

    logger("Starting experiment")

    # create runs 1, 2, 3, 4, 5
    logger("Creating run objects")
    run_objects = []
    for run_id in runs_ids:
        logger("Run {} with params {}".format(run_id, run_params[run_id]))
        new_run = Run(run_id, run_params[run_id])
        run_objects.append(new_run)

    current_sequence = 0

    # if its the first time were connecting to the server
    if first_try:
        logger("Getting first batch of data")
        # get first batch of writings
        data = client.get_writings()
        current_sequence = data[0]["number"]
        logger("Got data of length {}, sequence {}".format(len(data), data[0]["number"]))
        logger("Data: {}".format(data))

        # initialize users list and users writing history
        users = [user["nick"] for user in data]
        user_writings_history = {user: [] for user in users}
        clean_user_writings_history = {user: [] for user in users}

        # update writings history with first batch of writings
        #user_writings_history = update_writings_history(data, user_writings_history)

    else:
        logger("Continuing getting data batch")
        data = client.get_writings()
        current_sequence = data[0]["number"]
        logger("Got data of length {}, sequence {}".format(len(data), data[0]["number"]))
        logger("Data: {}".format(data))
        users = load_pickle(params["pickles_path"], params["users_name"])
        user_writings_history = load_pickle(params["pickles_path"], params["writings_name"])
        clean_user_writings_history = load_pickle(params["pickles_path"], params["clean_writings_name"])
        # load users and writing history from pickle


    keep_going = True
    max = params["range_max"]
    while data is not None and keep_going:
        logger("Preprocessing data for sequence {}".format(current_sequence))
        clean_data = preprocess_data(data)

        # update writings history with clean writings
        user_writings_history = update_writings_history(data, user_writings_history)
        clean_user_writings_history = update_writings_history(clean_data, clean_user_writings_history)

        #save user writings history to pickle
        save_pickle(params["pickles_path"], params["writings_name"], user_writings_history)
        save_pickle(params["pickles_path"], params["clean_writings_name"], clean_user_writings_history)

        # get decision for run and send decision for run
        for run_object in run_objects:
            logger("Getting decisions for run {} in sequence {}".format(run_object.run_identifier, current_sequence))
            if current_sequence <= max:
                decision = run_object.get_decisions(clean_user_writings_history, users)
                logger("Decision: {}".format(decision))
            else:
                logger("Reached max messages. Sending old decisions")
                keep_going = True
                decision = run_object.get_old_decisions()  # todo i dont know about this??
            logger("Sending decision for run {} in sequence {}".format(run_object.run_identifier, current_sequence))
            status_code, response = client.send_decision(decision, run_object.run_identifier) # todo add try catch here?
            logger("Response: {}, {}".format(status_code, response))

            if status_code != 200:
                logger("WARNING, RESPONSE: {}".format(response))
                keep_going = False
            # if error, keep_going = false and print something about the error

        # get new batch of writings
        # he pasado esto para aqui abajo para que si data me da null ya salga del bucle
        logger("Getting new data batch")
        data = client.get_writings()
        logger("Response: {}".format(data))
        if data is None:
            keep_going = False
            continue

        current_sequence = data[0]["number"]


########## helper methods ##############################################3

def update_writings_history(data, user_writings_history):
    user_writings = {writing["nick"]: writing for writing in data}
    user_writings_history = {user: (messages + [user_writings[user]] if user in user_writings.keys() else messages)
                             for (user, messages) in user_writings_history.items()}
    return user_writings_history

if __name__ == '__main__':
    eval()
