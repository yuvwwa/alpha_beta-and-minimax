import numpy as np

# поле
rows = 6
cols = 7
#как игроки будут отображаться на поле и пустые ячейки
player = 1
ai = 2
empty = 0


# создаем пустое поле из нулей
def create_board():
    return np.zeros((rows, cols), dtype=int)

# задаем параметры как оно должно выглядеть
def print_board(board):
    flipped_board = np.flip(board, 0)
    rows, cols = flipped_board.shape

    flipped_board = flipped_board.astype(int)

    for i in range(rows):
        print("|", end="")
        for j in range(cols):
            print(f"{flipped_board[i, j]:2}", end=" |")
        print()

    print("-" * (cols * 4))

    print("|", end=" ")
    for j in range(cols):
        print(f"{j}", end=" | ")
    print("\n******************************")

# можно ли сделать ход в нужную колонку
def is_valid_move(board, col):
    return board[rows - 1, col] == empty

# индекс первой доступной строки в указанной колонке (пригодится в самой функции игры)
def get_next_open_row(board, col):
    for row in range(rows):
        if board[row, col] == empty:
            return row
    return None

# делаем ход
def make_move(board, row, col, player):
    board[row, col] = player

# проверяем является последний сделанный ход победным
def win(board, player):
    # проверка по горизонтали
    for row in range(rows):
        for col in range(cols - 3):
            if all(board[row, col + i] == player for i in range(4)):
                return True

    # проверка по вертикали
    for row in range(rows - 3):
        for col in range(cols):
            if all(board[row + i, col] == player for i in range(4)):
                return True

    # проверка по положительной диагонали
    for row in range(rows - 3):
        for col in range(cols - 3):
            if all(board[row + i, col + i] == player for i in range(4)):
                return True

    # проверка по отрицательной диагонали
    for row in range(3, rows):
        for col in range(cols - 3):
            if all(board[row - i, col + i] == player for i in range(4)):
                return True

    return False

# проверяем, завершилась ли игра
def is_terminal_node(board):
    return win(board, player) or win(board, ai) or all(board[rows - 1, col] != empty for col in range(cols))

# определяем место, куда можно сходить (сколько пустых ячеек осталось в столбце)
def evaluate_place(place, player):
    if player == ai:
        opponent = 1
    else:
        opponent = 2

    score = 0

    # чем выигрышнее ситуация у играющего, тем больше очков начисляется, если проигрышная ситуация, уходим в минус
    if np.count_nonzero(place == player) == 4:
        score += 100
    elif np.count_nonzero(place== player) == 3 and np.count_nonzero(place == empty) == 1:
        score += 5
    elif np.count_nonzero(place == player) == 2 and np.count_nonzero(place == empty) == 2:
        score += 2

    if np.count_nonzero(place == opponent) == 3 and np.count_nonzero(place == empty) == 1:
        score -= 4

    return score

# оцениваем текущую позицию на доске
def score_position(board, player):
    score = 0

    # центр (он выигрышный) каждая занятая клетка добавляет 3 очка к score
    center_array = board[:, cols // 2]
    center_count = np.count_nonzero(center_array == player)
    score += center_count * 3

    # проходим по всем комбинациям и смотрим, являются ли они приближенными к победе
    # горизонталь
    for row in range(rows):
        row_array = board[row, :]
        for col in range(cols - 3):
            place = row_array[col:col + 4]
            score += evaluate_place(place, player)

    # вертикаль
    for col in range(cols):
        col_array = board[:, col]
        for row in range(rows - 3):
            place = col_array[row:row + 4]
            score += evaluate_place(place, player)

    # положительная диагональ
    for row in range(rows - 3):
        for col in range(cols - 3):
            place = [board[row + i, col + i] for i in range(4)]
            score += evaluate_place(place, player)

    # отрицательная диагональ
    for row in range(3, rows):
        for col in range(cols - 3):
            place = [board[row - i, col + i] for i in range(4)]
            score += evaluate_place(place, player)

    return score

# минимакс с альфабетой
def minimaxAndAlphabeta(board, depth, alpha, beta, ai_player):
    # проверка на окончание игры
    if depth == 0 or is_terminal_node(board):
        # вывод победившего игрока
        if is_terminal_node(board):
            if win(board, ai):
                return None, 1000000
            elif win(board, player):
                return None, -1000000
            else:
                return None, 0
        # проводим оценку ситуации
        else:
            return None, score_position(board, ai)

    # получаем доступные ходы
    valid_moves = []
    for col in range(cols):
        if is_valid_move(board, col):
            valid_moves.append(col)

    # если ходит компьютер (задаем самое низкое значение value и рандомно выбираем лучший ход, в дальнейшем меняем его на более выгодный)
    if ai_player:
        value = -np.inf
        best_col = np.random.choice(valid_moves)
        # вызываем некоторые ранее написанные функции для оптимизации хода 
        for col in valid_moves:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            make_move(temp_board, row, col, ai)
            # рекурсивно вызываем функцию, чтобы узнать наилучшие ходы вперед
            new_score = minimaxAndAlphabeta(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    
    # оцениваем ход игрока и выводим счет
    else:
        value = np.inf
        best_col = np.random.choice(valid_moves)
        for col in valid_moves:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            make_move(temp_board, row, col, player)
            new_score = minimaxAndAlphabeta(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value
    
# создаем доску, рисуем ее, задаем статус игры и выбираем игрока 
def play_game():
    board = create_board()
    print_board(board)
    game_over = False
    turn = player

    while not game_over:
        if turn == player:
            col = int(input("Ваш ход (0-6): "))
            if is_valid_move(board, col):
                row = get_next_open_row(board, col)
                make_move(board, row, col, player)

                if win(board, player):
                    print_board(board)
                    print("Вы выиграли!")
                    game_over = True

                turn = ai
            else:
                print("Невозможный ход!")
        else:
            col, _ = minimaxAndAlphabeta(board, 5, -np.inf, np.inf, True)
            if is_valid_move(board, col):
                row = get_next_open_row(board, col)
                make_move(board, row, col, ai)

                if win(board, ai):
                    print_board(board)
                    print("Компьютер победил!")
                    game_over = True
                    
                turn = player

        print_board(board)
        if not any(is_valid_move(board, c) for c in range(cols)):
            print("Ничья!")
            game_over = True

play_game()
