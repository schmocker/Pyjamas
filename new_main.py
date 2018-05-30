from core.controller import Controller
import time

def main():

    c = Controller()

    c.add_agent(1,"smith")
    c.add_agent(2,"anderson")

    boxes = []
    links = []

    boxes.append(("Math.Constant.V1.model","constant number"))
    boxes.append(("Math.Incrementer.V1.model","Incrementer"))
    boxes.append(("Math.Add.V1.model","Adder"))
    boxes.append(("InOutput.ConsolePrint.V1.model","Printer"))
    boxes.append(("Control.Sleep.V1.model","Sleeper"))
    boxes.append(("Control.Storage.V1.model","Storage"))
    boxes.append(("Scheduler.Regular.V1.model","cron_job"))

    links.append(("constant number", "const", "Adder", "in1"))
    links.append(("Incrementer", "num", "Adder", "in2"))
    links.append(("Storage", "stored", "Adder", "in3"))
    links.append(("Adder", "sum", "Sleeper", "input"))
    links.append(("Sleeper", "output", "Printer", "to_print"))
    links.append(("Adder", "sum", "Storage", "to_store"))

    mods = {}
    mods2 = {}

    for i, box in enumerate(boxes):
        uuid1 = c.add_model(1,box[0],i,box[1])
        uuid2 = c.add_model(2,box[0],i,box[1])
        mods[box[1]] = uuid1
        mods2[box[1]] = uuid2

    for link in links:
        c.link_models(1,mods[link[0]],link[1],mods[link[2]],link[3])
        c.link_models(2,mods2[link[0]],link[1],mods2[link[2]],link[3])

    print(c.get_agents())
    print(c.get_agents_running())

    time.sleep(3)

    c.start_agent(1)
    c.start_agent(2)

    print(c.get_agents())
    print(c.get_agents_running())

    time.sleep(2)
    c.set_property(1, mods["Sleeper"], "sleep_amount", 0)

    time.sleep(1)

    c.stop_agent(1)

    print(c.get_agents())
    print(c.get_agents_running())

    time.sleep(1)

    print(c.get_agents())
    print(c.get_agents_running())

    c.remove_agent(1)

    print(c.get_agents())
    print(c.get_agents_running())

    c.stop_agent(2)

    time.sleep(2)

    print(c.get_agents())
    print(c.get_agents_running())

    c.remove_agent(2)

    print(c.get_agents())
    print(c.get_agents_running())

if __name__ == "__main__":
    main()