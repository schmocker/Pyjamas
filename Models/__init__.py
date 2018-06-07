


'''

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


    info = {'docks': docklist,'description': description}
    return info
'''