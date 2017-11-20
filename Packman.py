import pickle


def pack_dict_to_request(dictionary):
    request = pickle.dumps(dictionary)
    return request


def unpack_request_to_dict(req):
    dictionary = pickle.loads(req)
    return dictionary
