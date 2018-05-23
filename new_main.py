from core.controller import Controller
import time

def main():

    c = Controller()

    # c.start()

    c.add_agent("smith")
    c.add_agent("anderson")

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

    for box in boxes:
        uuid1 = c.add_model("smith",box[0],box[1])
        uuid2 = c.add_model("anderson",box[0],box[1])
        mods[box[1]] = uuid1
        mods2[box[1]] = uuid2

    for link in links:
        c.link_models("smith",mods[link[0]],link[1],mods[link[2]],link[3])
        c.link_models("anderson",mods2[link[0]],link[1],mods2[link[2]],link[3])

    print(c.get_agents())
    print(c.get_agents_running())

    time.sleep(3)

    c.start_agent("smith")
    c.start_agent("anderson")

    print(c.get_agents())
    print(c.get_agents_running())

    time.sleep(2)
    c.set_property("smith", mods["Sleeper"], "sleep_amount", 0)

    time.sleep(.1)

    c.stop_agent("smith")

    print(c.get_agents())
    print(c.get_agents_running())

    time.sleep(1)

    print(c.get_agents())
    print(c.get_agents_running())

    c.remove_agent("smith")

    print(c.get_agents())
    print(c.get_agents_running())

    c.stop_agent("anderson")

    time.sleep(2)

    print(c.get_agents())
    print(c.get_agents_running())

    c.remove_agent("anderson")

    print(c.get_agents())
    print(c.get_agents_running())

    # c.stop()

if __name__ == "__main__":
    main()