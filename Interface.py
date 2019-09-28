class Interface:

    def __init__(self, option_map):
        self.option_map = option_map

    def write(self, str):
        print(str)

    def read(self, prompt="> ", option_map=None):
        if option_map is None:
            option_map = self.option_map;
        inp = input(prompt).strip()
        if inp in option_map:
            return {"act": option_map[inp]}
        else:
            return {"raw": inp}


if __name__ == "__main__":

    int = Interface({"A": "Open Menu"})
    while True:
        val = int.read()
        int.write(val)