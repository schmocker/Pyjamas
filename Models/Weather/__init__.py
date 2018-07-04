import os, json
import importlib


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

                if model == "Template_Model":
                    try:
                        mod = importlib.import_module(f"Models.{topic}.{model}.{version}.model").Model(1, '')
                    except Exception as e:
                        print(e)
                    input = mod.input
                    output = mod.output
                    docks = {'input': input, 'output': output}
                    ################ so bekommen wir die daten
                    docklist = list()
                    for direction, dock in docks.items():
                        for port_key, port in dock.items():
                            port['key'] = port_key
                        orientation = "bottom" if direction == "input" else "top"
                        ports = [port for key, port in dock.items()]
                        dock = {'direction': direction, 'orientation': orientation, 'ports': ports}
                        docklist.append(dock)
                    description = mod.description
                    info = {'docks': docklist, 'description': description}
                else:
                    info = get_info()
                model_dict[topic][model][version]['info'] = info
    return model_dict


def get_info():
    input = dict()
    input['naben_hoehe'] = {'name': 'Nabenhöhe', 'value': 150, 'dimensions': '', 'unit': 'm'}
    input['boden_rauhigkeit'] = {'name': 'Bodenrauhigkeit', 'value': 0.3, 'dimensions': '', 'unit': 'm'}

    output = dict()
    output['auslastung'] = {'name': 'Auslastung', 'value': 0.3, 'dimensions': '', 'unit': '-'}

    docks = {'input': input, 'output': output}
    ################ so bekommen wir die daten

    docklist = list()
    for direction, dock in docks.items():
        for port_key, port in dock.items():
            port['key'] = port_key

        orientation = "left" if direction == "input" else "right"
        ports = [port for key, port in dock.items()]
        dock = {'direction': direction, 'orientation': orientation, 'ports': ports}

        docklist.append(dock)

    description = 'Das Windturbien-Auslastunsmodel errechnet die aktuelle Auslastung aus Wetter und Nabenhöhe'

    info = {'docks': docklist, 'description': description}
    return info