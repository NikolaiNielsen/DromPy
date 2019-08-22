import numpy as np
import os
import subprocess

PREAMBLE = r"""\documentclass[tikz]{standalone}
\begin{document}
\begin{tikzpicture}

"""

POSTAMBLE = r"""\end{tikzpicture}
\end{document}
"""


class hex:
    """
    The main class for the program - hosts the vertices, creates the .tex code,
    Has the ability to create hexes to the board.
    """
    def __init__(self, start=np.array([[0], [0]]).T, i=0):
        self.own_verts = np.array([[0, 1, 1.5, 1, 0, -0.5],
                                   [0, 0, np.sqrt(3)/2, np.sqrt(3),
                                    np.sqrt(3), np.sqrt(3)/2]]).T
        self.set_start(start, i)
        self._create_center()
        self._create_hex()
        self._create_tex()

    def set_start(self, start, i=0):
        """
        Sets the starting position of the hex. Making the i'th vertex' absolute
        coordinate equal to start.
        """
        self.start = start - self.own_verts[i]

    def _create_hex(self):
        """
        Calculates the absolute position of the hex
        """
        self.vertices = self.own_verts + self.start

    def _print_verts(self):
        """
        Prints the absolute position of the vertices
        """
        for i in self.vertices:
            print(f'({i[0]}, {i[1]})')

    def _create_tex(self):
        """
        Creates the TiKZ code for the hex.
        """
        s = "\draw "
        for i in self.vertices:
            s = s + f'({i[0]}, {i[1]}) -- '
        else:
            s = s[:-4] + f"-- ({self.start[0,0]}, {self.start[0,1]});"
        self.tex = s

    def get_vert(self, i):
        """
        Returns the absolute postion of the i'th vertex
        """
        return self.vertices[i].reshape((1, 2))

    def _create_center(self):
        """
        Calculates the coordinate of the center of hex.
        """
        self.center = self.start + np.array([[0.5, np.sqrt(3)/2]])

    def create_center_tex(self, text):
        """
        Creates TiKZ code for text at the center of the hex
        """
        s = r'\node[draw] at (' + f'{self.center[0, 0]}, {self.center[0, 1]}'
        s = s + ') {' + f'{text}' + '};'
        self.center_tex = s
        return self.center_tex

    def add_hex_under(self):
        start_vert = self.get_vert(0)
        h = hex(start_vert, 4)
        return h

    def add_hex_bottom_right(self):
        start_vert = self.get_vert(1)
        h = hex(start_vert, 5)
        return h

    def add_hex_top_right(self):
        start_vert = self.get_vert(2)
        h = hex(start_vert, 0)
        return h

    def add_hex_over(self):
        start_vert = self.get_vert(4)
        h = hex(start_vert, 0)
        return h

    def add_hex_top_left(self):
        start_vert = self.get_vert(5)
        h = hex(start_vert, 1)
        return h

    def add_hex_bottom_left(self):
        start_vert = self.get_vert(5)
        h = hex(start_vert, 3)
        return h

    def add_hex(self, num):
        """
        Generalizations of the above functions. Returns a hex bordering edge
        "num". Num starts at bottom and goes in the positive direction (bottom,
        bottom right, top right, etc).
        """
        start_vert_num = [0, 1, 2, 4, 5, 5]
        end_vert_num = [4, 5, 0, 0, 1, 3]
        start_vert = self.get_vert(start_vert_num[num])
        h = hex(start_vert, end_vert_num)
        return h

    def print_edges(self):
        """
        Creates and returns TiKZ code for numbering the edges of the hex.
        """
        self.edge_centers = self.vertices + self.vertices[[1, 2, 3, 4, 5, 0]]
        self.edge_centers = self.edge_centers * 0.5
        self.edge_tex = []
        for n, edge in enumerate(self.edge_centers):
            s = r'\node at (' + \
                f'{edge[0]}, {edge[1]}'
            s = s + ') {' + f'{n}' + '};'
            self.edge_tex.append(s)
        return self.edge_tex


def write_latex(list_of_hexes, print_index=True, print_edges=False):
    filename = 'Drom'
    count = 0
    with open(f"{filename}.tex", 'w') as f:
        f.write(PREAMBLE)
        for h in list_of_hexes:
            f.write(h.tex + "\n")
            if print_index:
                f.write(h.create_center_tex(count) + "\n")
            count += 1
        if isinstance(print_edges, int):
            for edge in list_of_hexes[print_edges].print_edges():
                f.write(edge + "\n")
        f.write(POSTAMBLE)
    try:
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['pdflatex', f"{filename}.tex"], stdout=FNULL,
                             stderr=subprocess.STDOUT)
        p.wait()
        os.remove(f"{filename}.aux")
        os.remove(f"{filename}.log")
    except:
        pass


def main():
    loop = True
    start_hex = hex()
    list_of_hexes = [start_hex]
    current_hex_num = 0
    current_hex = list_of_hexes[current_hex_num]
    write_latex(list_of_hexes, print_index=True, print_edges=0)
    print_help()
    while loop:
        i = input("> ")
        i = i.lower()

        if i == "quit":
            loop = False

        elif i == "help":
            print_help()

        elif i in ["0", "1", "2", "3", "4", "5"]:
            num = int(i)
            d = [current_hex.add_hex_under, current_hex.add_hex_bottom_right,
                 current_hex.add_hex_top_right, current_hex.add_hex_over,
                 current_hex.add_hex_top_left, current_hex.add_hex_bottom_left]
            new_hex = d[num]()
            last_hex = current_hex
            last_hex_num = current_hex_num
            list_of_hexes.append(new_hex)
            current_hex_num = len(list_of_hexes)-1
            current_hex = new_hex
            write_latex(list_of_hexes, print_index=True,
                        print_edges=current_hex_num)

        elif i == "print":
            current_hex._print_verts()

        elif i == "change_hex":
            print("Changing hex. Which hex do you want to switch to?")
            I = input("> ")
            try:
                I = int(I)
                current_hex_num = I
                current_hex = list_of_hexes[current_hex_num]
                write_latex(list_of_hexes, print_edges=I)
            except Exception as e:
                print("Couldn't interpret input. Back to main menu")

        elif i == "print_full":
            write_latex(list_of_hexes, print_index=False, print_edges=None)

        elif i == "show_all":
            write_latex(list_of_hexes, print_edges=current_hex_num)

        elif i == "remove_last":
            list_of_hexes.pop()
            current_hex_num = last_hex_num
            current_hex = last_hex
            write_latex(list_of_hexes, print_edges=current_hex_num)

        else:
            print("input not recognized. Try again\n")


def print_help():
    print("Welcome to the Drom Editor. Input one of the following commands:")
    print("0:           Create a hex below the current")
    print("1:           Create a hex to the bottom right of the current")
    print("2:           Create a hex to the top right of the current")
    print("3:           Create a hex above the current")
    print("4:           Create a hex to the top left of the current")
    print("5:           Create a hex to the bottom left of the current")
    print("show_all:    show the index of all hexes")
    print("print_full:  Print the full Drom with no indices")
    print("remove_last: deletes the last placed hex")
    print("remove:      initiates removing of a hex")
    print("change_hex:  Initiates the changing of the current hex")
    print("help:        Show this message")
    print("quit:        Quits the program")

start_hex = hex()

# h1 = start_hex.add_hex_under()
# # h2 = h1.add_hex_bottom_right()
# # h3 = h2.add_hex_top_right()
# # h4 = h3.add_hex_over()
# # h5 = h4.add_hex_top_left()
# # h6 = h4.add_hex_bottom_left()


# list_of_hexes = [start_hex] #, h1, h2, h3, h4, h5, h6]
# write_latex(list_of_hexes, print_edges=0)

if __name__ == "__main__":
    main()
