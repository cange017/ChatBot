class Object():
    def __init__(self, id=None, rep=None, item_state={}, acts={}, updates={}):
        self.id = id
        self.rep = rep
        self.item_state = item_state
        self.acts = acts
        self.updates = updates

    def _handleInteract(self, act, state, io):
        pass

    def handleInteract(self, state, io, override_act=None):
        act = None
        if override_act is None:
            io.write("* You can {0}.".format(list(self.acts.keys())))
            act = io.read("? ", self.acts)
            if 'act' in act:
                act = act['act']
            else:
                io.write("* Not an option")
        else:
            act = override_act
        self._handleInteract(act, state, io)

    def update(self, state):
        for update in updates:
            if update['type'] == 'global':
                self.item_state[updade['updateTo']] = update['update'][state[update['updateWith']]]


class TV(Object):
    def __init__(self):
        super().__init__(
            id='TV',
            rep='An old TV set.',
            item_state={'curChannel': 'OFF',
                        'channels': ['OFF', '0', '1'],
                        'contents': {'OFF': 'The TV is OFF', '0': 'Nothing', '1': 'Nothing'}})

        self.acts = {'Change channel': 'changeChannel', 'Inspect': 'inspectScreen'}
        self.updates = {'changeContents':
                            {'type': 'global',
                             'updateWith': 'aiSentiment',
                             'updateTo': 'contents',
                             'update':
                                 {
                                     "Pos":
                                         {
                                             "OFF": "The TV is OFF.",
                                             "0": "Nothing",
                                             "1": "Nothing"
                                         },
                                     "Neu":
                                         {
                                             "OFF": "The TV is OFF.",
                                             "0": "Nothing",
                                             "1": "Nothing"
                                         },
                                     "Neg":
                                         {
                                             "OFF": "The TV is OFF.",
                                             "0": "An ominous sound comes off the speaker.",
                                             "1": "Nothing"
                                         }
                                 }
                             }
                        }

    def _handleInteract(self, act, state, io):
        if act == 'changeChannel':
            channel = io.read("? Change to channel: ", {})['raw']
            if channel in self.item_state['channels']:
                self.item_state['curChannel'] = channel
                io.write("* Changed channel to {0}".format(channel))
            else:
                io.write("* Channel not available.")
        elif act == 'inspectScreen':
            io.write("* " + self.item_state['contents'][self.item_state['curChannel']])


class Key(Object):
    def __init__(self):
        super().__init__(
            id='Key',
            rep='A small bronze key',
            item_state={})

        self.acts = {'Pick up': 'pick', 'Drop': 'drop'}
        self.update = {}

    def _handleInteract(self, act, state, io):
        if self in state['curRoom'].items and act == 'pick':
            io.write("* You picked up the {0}".format(self.id))
            state['inventory'].append(self)
            state['curRoom'].items.remove(self)
            state['Known Items'].remove(self)
        elif self in state['inventory'] and act == 'drop':
            io.write("* You dropped up the {0}".format(self.id))
            state['inventory'].remove(self)
            state['curRoom'].items.append(self)
            state['Known Items'].append(self)


class Path(Object):
    def __init__(self, fromArea, toArea, item_state={}, id=None, rep=None):
        # "{0} <-> {1}".format(fromArea.id, toArea.id)
        Object.__init__(self,
                        id=id,
                        rep=rep,
                        item_state=item_state)
        self.item_state["blocking"] = True
        self.item_state["area1"] = fromArea
        self.item_state["area2"] = toArea
        self.acts = {'traverse': 'traverse'}

    def _handleInnerInteract(self, act, state, io):
        pass

    def _handleInteract(self, act, state, io):
        if act == 'traverse':
            if not self.item_state["blocking"]:
                fromArea = state['curRoom']
                toArea = None
                if fromArea == self.item_state["area1"]:
                    toArea = self.item_state["area2"]
                elif fromArea == self.item_state["area2"]:
                    toArea = self.item_state["area1"]
                if fromArea.id not in state['memory']:
                    state['memory'][fromArea.id] = {}
                state['memory'][fromArea.id]['Known Items'] = state['Known Items']
                state['memory'][fromArea.id]['Known Exits'] = state['Known Exits']

                if toArea.id in state['memory']:
                    state['Known Items'] = state['memory'][toArea.id]['Known Items']
                    state['Known Exits'] = state['memory'][toArea.id]['Known Exits']
                else:
                    state['Known Exits'] = [self]
                    state['Known Items'] = []
                state['curRoom'] = toArea
                print(toArea.id)
            else:
                io.write('* This path is blocked.')
        else:
            self._handleInnerInteract(act, state, io)

    def getOtherArea(self, thisArea):
        if thisArea == self.item_state["area1"]:
            return self.item_state["area2"]
        elif thisArea == self.item_state["area2"]:
            return self.item_state["area1"]


class Passway(Path):
    def __init__(self, fromArea, toArea, item_state={}):
        Path.__init__(self, fromArea, toArea, item_state=item_state,
                      id="Passway between {0} and {1}".format(fromArea.id, toArea.id), rep="An open passway.")
        self.item_state["blocking"] = False


class Door(Path):
    def __init__(self, fromArea, toArea, keyDict, item_state={}):
        Path.__init__(self, fromArea, toArea, item_state=item_state,
                      id="Door between {0} and {1}".format(fromArea.id, toArea.id), rep="A Door.")
        self.item_state["blocking"] = True
        self.acts.update({'use': 'use'})
        self.keyDict = keyDict

    def _handleInnerInteract(self, act, state, io):
        if act == 'use':
            if not state['inventory']:
                io.write("* Your inventory is empty. Nothing can be used")
            else:
                io.write("* You can use {0}".format([s.id for s in state['inventory']]))
                inDict = {}
                for item in state['inventory']:
                    if item.id == self.keyDict['item']:
                        inDict[item.id] = 'valid'
                    else:
                        inDict[item.id] = 'invalid'
                res = io.read("> ", inDict)
                if res['act'] == 'valid':
                    io.write(self.keyDict['act_resp'])
                    self.item_state["blocking"] = False
                else:
                    io.write("Nothing happened")


