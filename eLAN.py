import tkinter as tk

Items = []
Cables = []
Bridges = []
Cycles_limit = 20
change = False
lines = False
points = True
multiplier = 30
width, height = 1200, 800

save = False
load = True

save_name = "test1"
load_name = "test2"


class Win:

    def __init__(self, root):
        board = tk.Canvas(root, width=width, height=height - 100, bg="white")
        board.pack()
        buttons = tk.Frame(root, width=width, height=100)
        buttons.pack(side="left")
        self.Board = board
        self.create_board()
        self.create_buttons(buttons)
        self.item = ""
        self.cycles = 0
        self.cords1 = [-1, -1]
        self.cords2 = [-1, -1]
        if load:
            self.load_simulation(load_name)

    def create_board(self):
        if lines:
            for x in range(multiplier, 1200, multiplier):
                self.Board.create_line(x, 1, x, 800)

            for y in range(multiplier, 800, multiplier):
                self.Board.create_line(1, y, 1200, y)
        if points:
            for x in range(multiplier, 1200, multiplier):
                for y in range(multiplier, 800, multiplier):
                    self.Board.create_oval(x - 1, y - 1, x + 1, y + 1)

    @staticmethod
    def save_simulation(filename):
        global multiplier
        if ".txt" in filename:
            filename += ".txt"
        file = open(filename, "w", encoding="UTF-8")
        file.write("M {}\n".format(str(multiplier)))
        for bridge in Bridges:
            file.write("B {} {}\n".format(int(bridge.x), int(bridge.y)))
        for cable in Cables:
            file.write(
                "C {} {} {} {}\n".format(int(cable.start_x), int(cable.start_y), int(cable.end_x), int(cable.end_y)))

    def load_simulation(self, filename):
        global multiplier
        if ".txt" in filename:
            filename += ".txt"

        try:
            file = open(filename, "r", encoding="UTF-8")
        except FileNotFoundError:
            print("Couldn't locate that file, please check again.")
            return

        file_lines = file.read().split("\n")
        for line in file_lines:
            if line[0] == "M":
                multiplier = int(line.split()[1])
            if line[0] == "B":
                self.create_bridge(int(line.split()[1]), int(line.split()[2]))
            if line[0] == "C":
                cords = list(map(int, line.split()[1:]))
                self.create_cable(cords[0:2], cords[2:4])

    def create_buttons(self, buttons):
        button_color = "light blue"
        button_bridge = tk.Button(buttons, width=8, height=6, bg=button_color, text="BRIDGE", command=self.b_bridge)
        button_bridge.pack(side="left")
        button_cable = tk.Button(buttons, width=8, height=6, bg=button_color, text="CABLE", command=self.b_cable)
        button_cable.pack(side="left")

        button_start_simulation = tk.Button(buttons, width=8, height=6, bg="green", text="RUN",
                                            command=self.start_simulation)
        button_start_simulation.pack(side="right")

    def start_simulation(self):
        self.cycles = 0
        global change
        last_change = 0
        while self.cycles < Cycles_limit:
            change = False
            for cable in Cables:
                cable.messages = []
            for bridge in Bridges:
                bridge.send_messages()
            for bridge in Bridges:
                bridge.receive_messages()
            self.cycles += 1
            print("\nCycle:", self.cycles)
            if change:
                last_change = self.cycles
            if self.cycles - last_change >= 5:
                break

        if Cycles_limit == self.cycles:
            print("Could not find a stable configuration...\n")
        else:
            print("A stable configuration has been found!\n")

        for bridge in Bridges:
            print(bridge)
        if save:
            self.save_simulation(save_name)

    def b_cable(self):
        self.Board.bind("<Button-1>", self.get_mouse_cords)
        self.item = "cable"

    def b_bridge(self):
        self.Board.bind("<Button-1>", self.get_mouse_cords)
        self.item = "bridge"

    def get_mouse_cords(self, event):
        self.Board.unbind("<Button-1>")
        if self.item == "cable":
            if self.cords1 == [-1, - 1]:
                self.cords1 = [((abs(event.x - multiplier / 2)) // multiplier) + 1,
                               ((abs(event.y - multiplier / 2)) // multiplier) + 1]
                self.b_cable()
            elif self.cords2 == [-1, -1]:
                self.cords2 = [((abs(event.x - multiplier / 2)) // multiplier) + 1,
                               ((abs(event.y - multiplier / 2)) // multiplier) + 1]
                self.create_cable((self.cords1[0] * multiplier, self.cords1[1] * multiplier),
                                  (self.cords2[0] * multiplier, self.cords2[1] * multiplier))
                self.cords1 = [-1, -1]
                self.cords2 = [-1, -1]
        else:
            self.cords1 = [((abs(event.x - multiplier / 2)) // multiplier) + 1,
                           ((abs(event.y - multiplier / 2)) // multiplier) + 1]
            if self.item == "bridge":
                self.create_bridge(self.cords1[0] * multiplier, self.cords1[1] * multiplier)
            self.cords1 = [-1, -1]
            self.cords2 = [-1, -1]

    def create_bridge(self, x, y):
        bridge = Bridge(x, y)
        Items.append(bridge)
        Bridges.append(bridge)
        rect = self.Board.create_rectangle(x - multiplier / 2, y - multiplier / 2, x + multiplier / 2,
                                           y + multiplier / 2,
                                           fill="yellow")

        text = self.Board.create_text(x, y, text=bridge.label, font=24)
        self.Board.tag_raise(rect)
        self.Board.tag_raise(text)

    def create_cable(self, cords1, cords2):
        cable = Cable(cords1[0], cords1[1], cords2[0], cords2[1])
        Items.append(cable)
        Cables.append(cable)
        line = self.Board.create_line(cords1[0], cords1[1], cords2[0], cords2[1], width=5, fill="red")
        vertical_offset, horizontal_offset = 0, 0
        if abs(cords1[0] - cords2[0]) < abs(cords1[1] - cords2[1]):
            horizontal_offset = multiplier // 1.5
        else:
            vertical_offset = multiplier // 1.5
        self.Board.create_text((cords1[0] + cords2[0]) / 2 + horizontal_offset,
                               (cords1[1] + cords2[1]) / 2 + vertical_offset,
                               text=cable.label, font=28)
        self.Board.tag_lower(line)


class Cable:

    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.power = 0
        self.active = 0
        self.label = "L" + str(len(Cables) + 1)
        self.messages = []


class Bridge:
    def __init__(self, x, y):
        self.label = "B" + str(len(Bridges) + 1)
        self.believed_root = self.label
        self.distance_from_root = 0
        self.x = x
        self.y = y
        self.root_cable = None
        self.root_message_sender = None

    def send_messages(self):
        for cable in Cables:
            if cable == self.root_cable:
                continue
            if (cable.start_x, cable.start_y) == (self.x, self.y) or (cable.end_x, cable.end_y) == (self.x, self.y):
                cable.messages.append(Message(self.label, self.believed_root, self.distance_from_root))

    def receive_messages(self):
        for cable in Cables:
            if (cable.start_x, cable.start_y) == (self.x, self.y) or (cable.end_x, cable.end_y) == (self.x, self.y):
                for message in cable.messages:
                    if message.sender == self.label:
                        continue
                    self.evaluate(message, cable)

    def evaluate(self, message, cable):
        if message.believed_root < self.believed_root:
            self.accept(message, cable)
            return

        if message.believed_root == self.believed_root:
            if message.distance_from_root < self.distance_from_root - 1:
                self.accept(message, cable)
                return

            if message.distance_from_root == self.distance_from_root - 1:
                if (not self.root_message_sender) or message.sender < self.root_message_sender:
                    self.accept(message, cable)
                    return

    def accept(self, message, cable):
        global change
        change = True
        self.believed_root, self.distance_from_root = message.believed_root, message.distance_from_root + 1
        self.root_cable = cable
        self.root_message_sender = message.sender
        print("Bridge {} accepted {}".format(self.label, message))

    def __str__(self):
        return "Bridge {}\n\tbelieved root: {}\n\tdistance from root: {}\n\tconnected to root through: {}\n".format(
            self.label, self.believed_root,
            self.distance_from_root, self.root_message_sender)


class Message:
    def __init__(self, sender, believed_root, distance_from_root):
        self.sender = sender
        self.believed_root = believed_root
        self.distance_from_root = distance_from_root

    def __str__(self):
        return "M({}, {}, {})".format(self.sender, self.believed_root, self.distance_from_root)


simulation = tk.Tk()
simulation.geometry("{}x{}+10+10".format(width, height))
simulation.configure(bg="#96DFCE")
Win(simulation)

simulation.mainloop()
