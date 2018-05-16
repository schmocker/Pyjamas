import os, json

def _get_folders(path):
    dirs = os.listdir(path)
    dirs = filter(lambda x: os.path.isdir(path + '/' + x), dirs)
    dirs = filter(lambda x: x[0] != '_', dirs)
    return list(dirs)


def get_models():
    path = os.path.dirname(os.path.realpath(__file__))
    model_dict = dict()
    for topic in _get_folders(path):
        model_dict[topic] = dict()
        for model in _get_folders(path + '/' + topic):
            model_dict[topic][model] = dict()
            for version in _get_folders(path + '/' + topic + '/' + model):
                model_dict[topic][model][version] = dict()
                model_dict[topic][model][version]['info'] = get_info()
    return model_dict

def get_info():
    inputs = {'input_1': {'name': 'Input 1'},
              'input_2': {'name': 'Input 2'},
              'input_3': {'name': 'Input 3'}}
    outputs = {'output_1': {'name': 'Output 1'},
               'output_2': {'name': 'Output 2'}}
    info = {'inputs': inputs, 'outputs': outputs}

    return info