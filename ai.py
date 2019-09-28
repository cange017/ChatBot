from chatbot import Chatbot

class AI:
    def __init__(self):
        self.sentiment = "def"
        self.conversations = [
            {
                0: {
                    "lit": ["Fuck you."],
                    "resp": {"def": "Ok."},
                    "act": {"update": {"sentiment": "neg"}}
                },
                2: {
                    "lit": ["Who are you?", "What is your name?"],
                    "resp": {"def": "I am the AI"}
                },
                3: {
                    "lit": ["Where am I?", "What is this place?", "What is this room?"],
                    "resp": {"def": "Where you have always been"}
                }
            },
            {
                1: {
                    "lit": ["How do I leave?", "Where is the exit?"],
                    "resp": {"def": "The exit is before you", "neg": "Fuck you"}
                },
                4: {
                    "lit": ["I don't want to leave.", "I want to stay.", "I'm not leaving"],
                    "resp": {"def": "You cannot stay"}
                }
            },
            {
                1: {
                    "lit": ["How do I leave?", "Where is the exit?"],
                    "resp": {"def": "The door."}
                },
                4: {
                    "lit": ["I don't want to leave.", "I want to stay.", "I'm not leaving"],
                    "resp": {"def": "You must leave."}
                }
            }
        ]
        self.conversation = self.conversations[0]
        self.conversation.update(self.conversations[1])

        self.chatbot = Chatbot(self.conversation)

    def processText(self, text):
        resp, isDict = self.chatbot.processText(text)
        if isDict:
            return resp[self.sentiment]
        else:
            return resp