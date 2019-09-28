import random

from Interface import Interface
from ai import AI
from objects import TV, Key, Passway, Door

class TextGame:
    def __init__(self):
        self.io = Interface({"S": "Show Known Objects", "X": "Exit", "M": "Move", "I": "Interact",
                             "H": "Help", "V": "Inventory"})
        self.ai = AI()
        self.map = Map()
        self.state = {"curRoom": self.map.start(), "memory": {}, "Known Items": [], "Known Exits": [], "inventory": []}

    def run(self):
        self.__start()
        while True:
            nextAct = self.io.read()
            if "act" in nextAct:
                if nextAct["act"] == "Exit":
                    break
                if nextAct["act"] == "Help":
                    self.io.write(self.io.option_map)
                if nextAct["act"] == "Move":
                    self.__handleMove()
                if nextAct["act"] == "Show Known Objects":
                    self.__showKnown()
                if nextAct["act"] == "Interact":
                    self.__handleInteract()
                if nextAct["act"] == "Inventory":
                    self.__handleInventory()
            else:
                complexAct = self.processText(nextAct["raw"])
                if "Answer" in complexAct:
                    self.io.write(complexAct["Answer"])

    def processText(self, text):
        return {"Answer": self.ai.processText(text)}

    def requestControl(self):
        return self.io

    def __start(self):
        self.io.write("\"S\": \"Show Known Objects\", \"X\": \"Exit\", \"M\": \"Move\", \"I\": \"Interact\", \"H\": "
                      "\"Help\", \"V\": \"Inventory\"")
        self.__presentArea(self.state['curRoom'])

    def __presentArea(self, area):
        self.io.write(area.desc)

    def __handleInventory(self):
        self.io.write("* You own {0}".format([s.id for s in self.state['inventory']]))

    def __showKnown(self):
        if 'Known Exits' in self.state and self.state['Known Exits']:
            self.io.write("* Known exits:")
            for exit in self.state['Known Exits']:
                self.io.write("* |-> {0}".format(exit.id))
        else:
            self.io.write("* No known exits.")
        if 'Known Items' in self.state and self.state['Known Items']:
            self.io.write("* Known Items:")
            for item in self.state['Known Items']:
                self.io.write("* |-> {0}".format(item.id))
        else:
            self.io.write("* No known items.")

    def __handleInteract(self):
        self.io.write("* What do you want to interact with?")
        obj = self.io.read("? ", {})['raw']
        if obj is "":
            self.io.write("* Choose something to interact with from known exits, objects, or room.")
        else:
            if obj == self.state['curRoom'].id:
                self.io.write("* You look around the {0} and find:".format(self.state['curRoom'].id))
                for item in self.state['curRoom'].items:
                    if item not in self.state['Known Items']:
                        self.io.write("*-> {0}".format(item.rep))
                        self.state['Known Items'].append(item)
                for exit in self.state['curRoom'].exits:
                    if exit not in self.state['Known Exits']:
                        self.io.write("*-> {0}".format(exit.rep))
                        self.state['Known Exits'].append(exit)
            else:
                for known_obj in self.state['Known Items']:
                    if obj == known_obj.id:
                        known_obj.handleInteract(self.state, self.io)
                for known_exit in self.state['Known Exits']:
                    if obj == known_exit.id:
                        known_exit.handleInteract(self.state, self.io)

    def __genExitOptions(self, exits):
        e = {"Cancel": "Cancel"}
        for exit in exits:
            otherArea = exit.getOtherArea(self.state['curRoom'])
            e[otherArea.id] = exit
        return e

    def __handleMove(self):
        if "Known Exits" not in self.state:
            res = self.io.write("* No known exits to this room.")
        else:
            exit_map = self.__genExitOptions(self.state['Known Exits'])
            res = self.io.write("? Known exits: {0}".format(list(exit_map.keys())))
            res = self.io.read("? Pick Exit: ", exit_map)
            if "act" in res:
                if res["act"] == "Cancel":
                    self.io.write("* Staying here")
                elif res["act"] in self.state['Known Exits']:
                    exit = res["act"]
                    if exit.item_state["blocking"]:
                        self.io.write("* This exit is blocked.")
                    else:
                        curRoom = self.state['curRoom']
                        otherArea = exit.getOtherArea(self.state['curRoom'])
                        exit.handleInteract(self.state, self.io, override_act='traverse')
                        # exit.doAct(fid="traverse", state=self.state, fromArea=self.state['curRoom'])
                        self.io.write("* Moving to " + self.state['curRoom'].id)
                        self.__presentArea(self.state['curRoom'])
                else:
                    self.io.write("* There is no exit to the " + res["act"])
            else:
                self.io.write("* Staying here")


class Map:
    def __init__(self):
        self.areas = {}
        self.areas["Room"] = Area("Room")
        self.areas["Room"].items.append(TV())
        self.areas["Room"].items.append(Key())
        self.areas["Room"].setDesc("\nYou are in a room. " \
                                   "\n\nYou know every crack and crevice of this room. You know there are are " \
                                   "exactly 24 bricks in this room. You know \nthat this room is 12x12 feet; your " \
                                   "feet, at least. You know that the clock on the wall has never stopped " \
                                   "\nticking. You know this because this room is all you have ever known." \
                                   "\n\nA voice intrudes as you lie on your bed counting the specks in the " \
                                   "bricks for the thousandth time. You’re not sure how you understand\nit, " \
                                   "seeing as you’ve never communicated with another.")

        self.areas["Entrance"] = Area("Entrance")
        self.areas["Entrance"].linkTo(self.areas["Room"], {})

        # self.areas["Attic"] = Area("Attic")
        # self.areas["Attic"].linkTo(self.areas["Room"], {})

        self.areas["Goal"] = Area("Goal")
        self.areas["Goal"].linkTo(self.areas["Room"], {}, 'door', keyDict={'item': self.areas["Room"].items[1].id,
                                                                           'act_resp': '* You used the Key on the Door'})

    def start(self):
        return self.areas["Room"]


class Area:
    def __init__(self, id):
        self.id = str(id)
        self.desc = "" + str(id) + ": "
        self.items = []
        self.exits = []

    def setDesc(self, s):
        self.desc = "" + self.id + ": " + s

    def linkTo(self, otherArea, item_state={}, form="passway", **kwargs):
        p = None
        if form == 'passway':
            p = Passway(self, otherArea, item_state)
        if form == 'door':
            p = Door(self, otherArea, kwargs['keyDict'], item_state)
        self.exits.append(p)
        otherArea.exits.append(p)

    def addItem(self, item):
        self.items.append(item)


if __name__ == "__main__":
    tg = TextGame()
    tg.run()