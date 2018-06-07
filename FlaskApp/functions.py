import json
import random
'''
def get_agent():
    agent = dict()

    input_id = 0;
    output_id = 0;



    agent['models'] = list()
    for i in range(0, 5):
        orientations = ['left', 'right', 'top', 'bottom']

        model = dict()

        model['id'] = 'model_' + str(i)
        model['name'] = 'Model '+ str(i)
        model['x'] = 50 * i
        model['y'] = 100 * i
        model['width'] = 150
        model['height'] = 50
        model['settings'] = '{x: 1}'

        inputs = {'orientation': random.choice(orientations)}
        orientations.remove(inputs['orientation']);
        ports = list()
        for i in range(0, random.randint(0, 5)):
            ports.append({'name': 'Input '+ str(input_id), 'id': 'input_' + str(input_id)})
            input_id += 1
        inputs['ports'] = ports
        model['inputs'] = inputs

        outputs = {'orientation': random.choice(orientations)}
        ports = list()
        for i in range(0, random.randint(1, 5)):
            ports.append({'name': 'Output '+ str(output_id), 'id': 'output_' + str(output_id)})
            output_id += 1
        outputs['ports'] = ports
        model['outputs'] = outputs

        agent['models'].append(model)


    agent['connections'] = list()

    for i in range(0, 5):
        connection = dict()
        connection['id'] = "connection_" + str(i)
        connection['input'] = "input_" + str(random.randint(0, input_id - 1))
        connection['output'] = "output_" + str(random.randint(0, output_id - 1))
        agent['connections'].append(connection)




    return json.dumps(agent)

'''