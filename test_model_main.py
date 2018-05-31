from core.test_agent import TestAgent
from Models.Math.Add.V1.model import Model

t = TestAgent()

add = Model(1,"Adder")
add.agent = t

t.set_model(add)

t.set_input("in1", 1)
t.set_input("in2", 2)

t.start()
print(t.model_outputs)

t.set_input("in3", 10)
t.start()
print(t.model_outputs)

t.remove_input("in3")
t.start()
print(t.model_outputs)

t.set_input("in2", 3)
t.start()
print(t.model_outputs)

t.remove_input("in2")
t.start()
print(t.model_outputs)

t.remove_input("in1")
t.start()
print(t.model_outputs)