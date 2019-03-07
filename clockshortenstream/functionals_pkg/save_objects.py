import pickle

def save_obj(obj, path_name ):
    with open(path_name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(path_name):
    with open(path_name, 'rb') as f:
        return pickle.load(f)