import sys
log_file = "todo" #TODO

def logger(message, log_file=log_file):
    print(message)
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(log_file, 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(message)
        sys.stdout = original_stdout # Reset the standard output to its original value


def process_decisions(users, decisions, scores):
    pass