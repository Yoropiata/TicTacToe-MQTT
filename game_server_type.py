class GameServer:
    def __init__(self, player1 = None, player2 = None):
        self.player1 = player1
        self.player2 = player2
        self.board = [list('   ') for _ in range(3)]

    def check_victory(self, y, x):
        #check if previous move caused a win on horizontal line
        if self.board[0][x] == self.board[1][x] == self.board [2][x]:
            return True

        #check if previous move caused a win on vertical line
        if self.board[y][0] == self.board[y][1] == self.board [y][2]:
            return True

        #check if previous move was on the main diagonal and caused a win
        if x == y and self.board[0][0] == self.board[1][1] == self.board [2][2]:
            return True

        #check if previous move was on the secondary diagonal and caused a win
        if x + y == 2 and self.board[0][2] == self.board[1][1] == self.board [2][0]:
            return True

        return False
