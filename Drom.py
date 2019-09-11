#!/usr/bin/env python3

import numpy as np
import os
import subprocess

PREAMBLE = r"""\documentclass[tikz]{standalone}
\begin{document}

% Set the scale to 1.9.
% The scale parameter sets the side lengths of the hexes in cm.
% A scale of 1 (the defualt) corresponds to side lengths of 1cm, for example.
\begin{tikzpicture}[scale=1.9]
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
        self.thicc = [True] * 6
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
        s = "\draw [line width=1mm]"
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
        self.neighbour_center = self.center + np.array([[0, -np.sqrt(3)],
                                                        [1.5, -np.sqrt(3)/2],
                                                        [1.5, np.sqrt(3)/2],
                                                        [0, np.sqrt(3)],
                                                        [-1.5, np.sqrt(3)/2],
                                                        [-1.5, -np.sqrt(3)/2]])

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
        h = hex(start_vert, end_vert_num[num])
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

    def check_neighbours(self, all_centers):
        """
        Checks whether or not there are neighbouring hexes. Sets line widths
        accordingly.
        """
        for n, neigh in enumerate(self.neighbour_center):
            # Check if the neighbour is close to any center. At least one full
            # row must be True.
            val = np.isclose(neigh, all_centers).all(axis=1).any()
            # Thicc is "not val" - if we have a neighbour, we want a thin line
            self.thicc[n] = not val


def write_latex(list_of_hexes, filename="Drom", print_index=True,
                print_edges=False):
    with open(f"{filename}.tex", 'w') as f:
        f.write(PREAMBLE)
        for count, h in enumerate(list_of_hexes):
            f.write(r'%hex' + "\n")
            f.write(h.tex + "\n")
            if print_index:
                f.write(h.create_center_tex(count) + "\n")
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


def read_tex(filename):
    """
    Reads a .tex file generated by this script.
    """
    hexes = []

    with open(filename, 'r') as f:
        lines = f.readlines()

        # Strip newline
        lines = [line[:-1] for line in lines]

        # Get line number for hexes (they are always after the lines reading
        # "%hex")
        linenum_with_hexes = [n+1 for n,
                              line in enumerate(lines) if line == r'%hex']

        # We only keep the 2nd through 7th of the split strings.
        splits_to_keep = [1, 2, 3, 4, 5, 6]
        for line in [lines[n] for n in linenum_with_hexes]:
            splits = line.split('(')

            # We only need the x- and y-coordinates for the first vertex.
            x, y = (float(n) for n in splits[1][:-5].split(', '))

            start = np.array([[x, y]])
            a = hex(start, i=0)
            hexes.append(a)

        return hexes


def main(list_of_hexes=None):
    """
    Initiates the process of creating a Drom. Requires pdflatex to be installed
    and accessible with the subprocess module. Currently tested on Debian.
    """
    # Create the starting hex and initialize all variables
    if list_of_hexes is None:
        start_hex = hex()
        list_of_hexes = [start_hex]

    current_hex = list_of_hexes[-1]
    current_hex_num = len(list_of_hexes) - 1

    # Create the starting Drom, print the help and start the loop
    write_latex(list_of_hexes, print_index=True, print_edges=0)
    print_help()
    loop = True
    while loop:
        i = input("> ")
        i = i.lower()

        if i == "quit":
            # Prints full Drom and quits program.
            write_latex(list_of_hexes, print_index=False, print_edges=None)
            loop = False

        elif i == "help":
            print_help()

        elif i in ["0", "1", "2", "3", "4", "5"]:
            # Adds a new hex
            num = int(i)
            new_hex = current_hex.add_hex(num)

            # Sets the "last_hex" stuff. Used whem removing hexes
            last_hex = current_hex
            last_hex_num = current_hex_num

            # Add the new hex, update current hex, and update Drom
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
                # Sorry for the Pokèmon exception...
                print("Couldn't interpret input. Back to main menu\n")

        elif i == "print_full":
            # Generate the full/final pdf
            write_latex(list_of_hexes, print_index=False, print_edges=None)

        elif i == "show_all":
            # Generate pdf showing hex indices and current hex edges
            write_latex(list_of_hexes, print_edges=current_hex_num)

        elif i == "remove_last":
            # Removes the last placed hex
            list_of_hexes.pop()
            current_hex_num = last_hex_num
            current_hex = last_hex
            write_latex(list_of_hexes, print_edges=current_hex_num)

        elif i == "remove":
            # Remove a selected hex
            print("which hex do you want to remove?")
            I = input("> ")
            try:
                I = int(I)
                list_of_hexes.pop(I)
                if I == current_hex_num:
                    # If the selected hex is the current hex, then we change
                    # the current hex to the last current hex
                    current_hex = last_hex

                # Find the new current_hex_num (it might have changed, either
                # if the removed hex was the current one, or if the current hex
                # had a higher index than the removed hex.)
                current_hex_num = list_of_hexes.index(current_hex)
                write_latex(list_of_hexes, print_edges=current_hex_num)
            except Exception as e:
                # Again with the Pokèmon exception. Soz.
                print("Couldn't interpret input. Back to main menu\n")

        elif i == "save":
            print("What do you want the filename to be?")
            print("(don't include file extension)")
            filename = input("> ")
            write_latex(list_of_hexes, filename, print_index=False,
                        print_edges=None)

        elif i == "load":
            print(
                "What file do you wish to load (don't include .tex extension)"
                )
            filename = input("> ") + ".tex"
            list_of_hexes = read_tex(filename)
            current_hex = list_of_hexes[-1]
            current_hex_num = len(list_of_hexes) - 1
            filename = "Drom"
            write_latex(list_of_hexes, filename, print_index=True,
                        print_edges=current_hex_num)

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
    print("save:        saves the current Drom")
    print("load:        loads a Drom from a .tex file")
    print("help:        Show this message")
    print("quit:        prints the full drom and quits the program")


if __name__ == "__main__":
    main()
