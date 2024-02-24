import pygame
import time
pygame.font.init()

GRID_DIM = 9
SUBGRIDS = 3

FONT_SIZE = 30
SMALL_FONT_SIZE = 25
LARGE_FONT_SIZE = 40

PRIMARY_FONT = pygame.font.SysFont("Arial", FONT_SIZE)
SECONDARY_FONT = pygame.font.SysFont("Arial", SMALL_FONT_SIZE)
TITLE_FONT = pygame.font.SysFont("Arial", LARGE_FONT_SIZE)

ALL_VALUES = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}

initial_sudoku = [
    [0, 0, 6, 0, 0, 5, 0, 0, 0],
    [0, 0, 0, 9, 0, 2, 4, 5, 0],
    [0, 9, 0, 3, 0, 0, 7, 0, 8],
    [0, 0, 0, 7, 0, 0, 0, 8, 0],
    [6, 0, 3, 0, 0, 0, 2, 0, 5],
    [8, 5, 0, 0, 0, 3, 0, 0, 0],
    [0, 0, 2, 0, 4, 7, 0, 0, 0],
    [9, 6, 7, 0, 8, 1, 5, 3, 0],
    [5, 4, 0, 0, 3, 9, 1, 2, 7]
]

class Cell:
    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp_value = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def render(self, window):
        gap = self.width / GRID_DIM
        x, y = self.col * gap, self.row * gap

        if self.temp_value != 0 and self.value == 0:
            text = PRIMARY_FONT.render(str(self.temp_value), 1, (128, 128, 128))
            window.blit(text, (x + 5, y + 5))
        elif self.value != 0:
            text = PRIMARY_FONT.render(str(self.value), 1, (0, 0, 0))
            window.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))

        if self.selected:
            pygame.draw.rect(window, (255, 0, 0), (x, y, gap, gap), 3)

    def set_value(self, value):
        self.value = value

    def set_temp_value(self, value):
        self.temp_value = value


class SudokuBoard:
    def __init__(self, rows, cols, width, height, window):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.window = window
        self.cells = [[Cell(initial_sudoku[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.model = None
        self.selected_cell = None
        self.update_model()

    def update_model(self):
        self.model = [[self.cells[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def render(self):
        gap = self.width / GRID_DIM
        for i in range(self.rows + 1):
            thickness = 4 if i % SUBGRIDS == 0 and i != 0 else 1
            pygame.draw.line(self.window, (0, 0, 0), (0, i * gap), (self.width, i * gap), thickness)
            pygame.draw.line(self.window, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thickness)

        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].render(self.window)

    def select_cell(self, row, col):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].selected = False
        self.cells[row][col].selected = True
        self.selected_cell = (row, col)

    def clear_cell(self):
        row, col = self.selected_cell
        if self.cells[row][col].value == 0:
            self.cells[row][col].set_temp_value(0)

    def click_on_board(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / GRID_DIM
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        return None

    def place_value(self, value):
        row, col = self.selected_cell
        if self.cells[row][col].value == 0:
            self.cells[row][col].set_value(value)
            self.update_model()

            if is_valid(self.model, value, (row, col)) and self.solve_board():
                return True
            else:
                self.cells[row][col].set_value(0)
                self.cells[row][col].set_temp_value(0)
                self.update_model()
                return False

    def set_temp_value(self, value):
        row, col = self.selected_cell
        self.cells[row][col].set_temp_value(value)

    def is_complete(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cells[i][j].value == 0:
                    return False
        return True

    def solve_board(self):
        possible_values, pos, flag = find_possible_values(self.model)
        if flag == 0:
            return True
        if not pos:
            return False

        row, col = pos
        for val in possible_values:
            if is_valid(self.model, val, (row, col)):
                self.model[row][col] = val
                if self.solve_board():
                    return True
                self.model[row][col] = 0
        return False

    def solve_with_gui(self):
        possible_values, pos, flag = find_possible_values(self.model)
        if flag == 0:
            return True
        if not pos:
            return False

        row, col = pos
        for val in possible_values:
            if is_valid(self.model, val, (row, col)):
                self.model[row][col] = val
                self.cells[row][col].set_value(val)
                self.cells[row][col].render(self.window)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(100)

                if self.solve_with_gui():
                    return True

                self.model[row][col] = 0
                self.cells[row][col].set_value(0)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(100)
        return False


def is_valid(board, num, pos):
    for i in range(len(board[0])):
        if board[pos[0]][i] == num and pos[1] != i:
            return False
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False
    box_x = pos[1] // SUBGRIDS
    box_y = pos[0] // SUBGRIDS
    for i in range(box_y * SUBGRIDS, box_y * SUBGRIDS + SUBGRIDS):
        for j in range(box_x * SUBGRIDS, box_x * SUBGRIDS + SUBGRIDS):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True


def find_possible_values(board):
    min_possibilities = 10
    best_values = set()
    pos = ()
    flag = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                flag = 1
                possible_values = get_best_values(board, i, j)
                if min_possibilities > len(possible_values) and len(possible_values) > 0:
                    min_possibilities = len(possible_values)
                    best_values = possible_values
                    pos = (i, j)
    if min_possibilities == 10:
        return (None, None, flag)
    return (best_values, pos, flag)


def get_best_values(board, i, j):
    excluded = {0}
    for row in range(len(board)):
        excluded.add(board[row][j])
    for col in range(len(board)):
        excluded.add(board[i][col])
    i -= i % SUBGRIDS
    j -= j % SUBGRIDS
    for row in range(int(len(board) / SUBGRIDS)):
        for col in range(int(len(board) / SUBGRIDS)):
            excluded.add(board[i + row][j + col])
    remaining_values = ALL_VALUES.difference(excluded)
    return remaining_values


def format_time(seconds):
    sec = seconds % 60
    minute = seconds // 60
    return f" {minute}:{sec}"


def update_window(window, board, time, strikes):
    window.fill((255, 255, 0)) 
    time_text = SECONDARY_FONT.render("Time!: " + format_time(time), 1, (0, 0, 0))
    window.blit(time_text, (540 - 160, 560))
    board.render()



def show_message(window, message):
    text = SECONDARY_FONT.render(message, True, (0, 0, 0))
    text_rect = text.get_rect(center=(270, 300))
    pygame.draw.rect(window, (255, 255, 255), (100, 250, 340, 100))
    pygame.draw.rect(window, (0, 0, 0), (100, 250, 340, 100), 2)
    window.blit(text, text_rect)


def main():
    window = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku!")
    board = SudokuBoard(GRID_DIM, GRID_DIM, 540, 540, window)
    key = None
    running = True
    start_time = time.time()
    incorrect_attempts = 0
    user_solved = False

    while running:
        elapsed_time = round(time.time() - start_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear_cell()
                    key = None
                if event.key == pygame.K_SPACE:
                    if board.solve_with_gui():
                        user_solved = False
                        show_message(window, "Computer solved it!")
                        pygame.display.update()
                        time.sleep(2)
                        running = False
                    else:
                        show_message(window, "Sudoku is not solvable!")
                        pygame.display.update()
                        time.sleep(2)
                if event.key == pygame.K_RETURN:
                    i, j = board.selected_cell
                    if board.cells[i][j].temp_value != 0:
                        if board.place_value(board.cells[i][j].temp_value):
                            print("Correct")
                            if board.is_complete():
                                user_solved = True
                                show_message(window, "You won!")
                                pygame.display.update()
                                time.sleep(2)
                                running = False
                        else:
                            print("Incorrect")
                            incorrect_attempts += 1
                        key = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click_on_board(pos)
                if clicked:
                    board.select_cell(clicked[0], clicked[1])
                    key = None

        if board.selected_cell and key != None:
            board.set_temp_value(key)

        update_window(window, board, elapsed_time, incorrect_attempts)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
