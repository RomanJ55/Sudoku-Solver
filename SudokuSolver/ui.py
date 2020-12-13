from tkinter import *
from threading import Thread
import time

MARGIN = 10
CELL_WIDTH = 50
WIDTH = HEIGHT = MARGIN * 2 + CELL_WIDTH * \
    9  # Width and height of the whole board


class SudokuUI(Frame):
    def __init__(self, board):
        self.sudoku = board
        self.parent = Tk()
        Frame.__init__(self, self.parent)

        self.row, self.col = -1, -1
        self.solve_thread = Thread(target=self.__solve)
        self.__initialize()

    def __initialize(self):
        self.parent.title("Sudoku Solver")
        self.parent.option_add("*Font", "comicsans 15")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self,
                              text="Clear",
                              command=self.__clear)
        clear_button.pack(fill=BOTH, side=BOTTOM)
        solve_button = Button(self,
                              text="Solve",
                              command=lambda: self.solve_thread.start())
        solve_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        for i in range(10):
            color = "black" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * CELL_WIDTH
            y0 = MARGIN
            x1 = MARGIN + i * CELL_WIDTH
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * CELL_WIDTH
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * CELL_WIDTH
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("result")  # remove time stamp from view
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                cell = self.sudoku.board[i][j]
                number = cell.number
                if number != 0:
                    x = MARGIN + j * CELL_WIDTH + CELL_WIDTH / 2
                    y = MARGIN + i * CELL_WIDTH + CELL_WIDTH / 2
                    self.canvas.create_text(
                        x, y, text=number, tags="numbers", fill="black", font="arial 24"
                    )

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * CELL_WIDTH + 1
            y0 = MARGIN + self.row * CELL_WIDTH + 1
            x1 = MARGIN + (self.col + 1) * CELL_WIDTH - 1
            y1 = MARGIN + (self.row + 1) * CELL_WIDTH - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __draw_result(self, success, time):
        # create a oval (which will be a circle)
        x0 = y0 = MARGIN + CELL_WIDTH * 2
        x1 = y1 = MARGIN + CELL_WIDTH * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="result", fill="dark gray", outline="black"
        )
        # create text
        x = y = MARGIN + 4 * CELL_WIDTH + CELL_WIDTH / 2
        text = "{0:.3f}s".format(time) if success else "Invalid Board"
        self.canvas.create_text(
            x, y,
            text=text, tags="result",
            fill="white", font=("Arial", 28)
        )

    def __cell_clicked(self, event):
        self.canvas.delete("result")  # remove time stamp from view
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // CELL_WIDTH, (x - MARGIN) // CELL_WIDTH

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_pressed(self, event):
        # Catch all key press events and handle them
        if self.row >= 0 and self.col >= 0:
            if event.keysym in ["Up", "w"]:
                self.row = ((self.row + 8) % 9)
            elif event.keysym in ["Down", "s"]:
                self.row = ((self.row + 10) % 9)
            elif event.keysym in ["Right", "d"]:
                self.col = ((self.col + 10) % 9)
            elif event.keysym in ["Left", "a"]:
                self.col = ((self.col + 8) % 9)
            elif event.keysym in ["Delete", "BackSpace"]:
                self.sudoku.board[self.row][self.col].reset()
            elif event.char != "" and event.char in "1234567890":
                self.sudoku.board[self.row][self.col].set_number(int(
                    event.char))
            else:
                pass
            self.__draw_puzzle()
            self.__draw_cursor()

    def __clear(self):
        self.sudoku.clear()
        self.__draw_puzzle()

    def __update_cells_solver(self, cell):
        num = cell.number
        x = MARGIN + cell.column * CELL_WIDTH + CELL_WIDTH / 2
        y = MARGIN + cell.row * CELL_WIDTH + CELL_WIDTH / 2
        c2 = Canvas(self, width=CELL_WIDTH-10, height=CELL_WIDTH-10)
        c2.place(x=x-20, y=y-20)
        c2.create_text(
            20, 20, text=num, tags="numbers", fill="blue", font="arial 24"
        )
        self.update()
        time.sleep(0.005)

    def __solve(self):
        if self.sudoku.is_valid():
            #start = time()
            attempted_cells = []
            row = 0
            while row < 9:
                column = 0
                while column < 9:
                    cell = self.sudoku.board[row][column]
                    backtracking = False
                    if not cell.number:  # if the cell's number is 0

                        # Check that this cell is not exhausted
                        if not cell.exhausted and not cell.possible_numbers:
                            # Find and set the possible numbers
                            possible = self.sudoku.possible_numbers(
                                row, column)
                            cell.set_possible_numbers(possible)

                        # If the cell has possible numbers, try one
                        if cell.possible_numbers:
                            cell.try_new_number()
                            attempted_cells.append(cell)
                            self.__update_cells_solver(cell)
                        # Otherwise we must back track to the previous cell
                        elif attempted_cells:
                            backtracking = True
                            cell.reset()
                            prev_cell = attempted_cells.pop(-1)
                            prev_cell.reset_number()
                            row = prev_cell.row
                            column = prev_cell.column

                        # Otherwise there are no possible solutions
                        else:
                            return False

                    # If we are not going to backtrack, simply
                    # advance to the next column
                    if not backtracking:
                        column += 1

                # After we have gone through all columns,
                # advance to the next row and repeat
                row += 1

            # All cells have been fit successfully
            # self.__draw_puzzle()
            return True
        # The initial puzzle was not valid
        else:
            return False
