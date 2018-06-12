import numpy as np

def func_NeuralNetwork(self, data, model_para):
    # read parameters
    file = open("model_parameter_LK_UCTE.txt", "r")
    json_str = file.read()
    # model_para = json.loads(json_str)

    # ===== NEURAL NETWORK CONSTANTS =====

    # - Input 1
    x1_step1 = model_para['x1_step1']
    # - Layer 1
    b1 = np.array(model_para['b1'])
    b1 = b1[np.newaxis, :]
    b1 = np.transpose(b1)
    IW1_1 = np.array(model_para['IW1_1'])
    # - Layer 2
    b2 = np.array(model_para['b2'])
    LW2_1 = np.array(model_para['LW2_1'])
    # - Output 1
    y1_step1 = model_para['y1_step1']

    # ===== SIMULATION ========

    # Dimensions
    Q = x1.shape[0]

    # Input 1
    x1 = np.transpose(x1)
    xp1 = mapminmax_apply(x1, x1_step1)

    # Layer 1
    a1 = tansig_apply(np.tile(b1, (1, Q)) + np.matmul(IW1_1, xp1))

    # Layer 2
    a2 = np.tile(b2, (1, Q)) + np.matmul(LW2_1, a1)

    # Output 1
    y1 = mapminmax_reverse(a2, y1_step1)

    return y1


def mapminmax_apply(self, a, x1_step1):
    atilde = np.transpose(a.values)
    y = np.add(atilde, -np.array(x1_step1['xoffset']))
    y = y * np.array(x1_step1['gain'])
    y = y + np.array(x1_step1['ymin'])
    y = np.transpose(y)

    return y


def tansig_apply(self, n):
    a = 2 / (1 + np.exp(-2 * n)) - 1

    return a


def mapminmax_reverse(self, a, y1_step1):
    x = a - np.array(y1_step1['ymin'])
    x = x / np.array(y1_step1['gain'])
    x = x + np.array(y1_step1['xoffset'])

    return x

