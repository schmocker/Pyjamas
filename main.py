import importlib
import uuid
import multiprocessing
import json

def main():

    queue = multiprocessing.Queue()

    a = importlib.import_module("pyjama.core.agent").Agent("A", queue)
    b = importlib.import_module("pyjama.core.agent").Agent("B", queue)

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
    modsB = {}

    for box in boxes:
        i = uuid.uuid4()
        mods[box[1]] = importlib.import_module(f"pyjama.models.{box[0]}").Model(i,box[1])
        modsB[box[1]] = importlib.import_module(f"pyjama.models.{box[0]}").Model(i,box[1])

    for key, mod in mods.items():
        a.add_model(mod)

    for key, mod in modsB.items():
        b.add_model(mod)

    for link in links:
        a.link_models(mods[link[0]].id, link[1], mods[link[2]].id, link[3])
        b.link_models(modsB[link[0]].id, link[1], modsB[link[2]].id, link[3])

    a.remove_model(mods["Sleeper"].id)
    a.link_models(mods["Adder"].id, "sum", mods["Printer"].id, "to_print")

    a.set_property(mods["cron_job"].id,"number_of_exec",1)
    a.set_property(mods["cron_job"].id,"peri_interval",0)

    b.set_property(mods["Sleeper"].id,"sleep_amount",2)
    b.set_property(mods["cron_job"].id,"number_of_exec",10)

    a.start()
    # b.start()

    while True:
        inp = input("order: ")
        if not inp:
            break
        
        order = {}
        order["order"] = "end"
        order["model"] = ""
        order["text"] = ""

        if inp == "killa":
            order["agent"] = "A"
            queue.put(order)

        if inp == "killb":
            order["agent"] = "B"
            queue.put(order)

        

if __name__ == "__main__":
    main()