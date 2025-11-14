import random
import copy

class Sudoku:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
    
    def print_grid(self, grid=None):
        """Print the Sudoku grid with formatting"""
        if grid is None:
            grid = self.grid
        
        print("\n  " + "="*25)
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("  |-----------+-----------|")
            
            row = f"{i+1} | "
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row += "| "
                
                if grid[i][j] == 0:
                    row += ". "
                else:
                    row += f"{grid[i][j]} "
            row += "|"
            print(row)
        print("  " + "="*25)
        print("    1 2 3   4 5 6   7 8 9")
        
        print("- 'move <row> <col> <num>' - Place number (e.g., 'move 1 1 5')")
    
    def is_valid(self, grid, row, col, num):
        """Check if a number is valid at the given position"""
        # Check row
        for j in range(9):
            if grid[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if grid[i][col] == num:
                return False
        
        # Check 3x3 box
        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if grid[i][j] == num:
                    return False
        
        return True
    
    def solve(self, grid):
        """Solve the Sudoku puzzle using backtracking"""
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, i, j, num):
                            grid[i][j] = num
                            if self.solve(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True
    
    def generate_complete_grid(self):
        """Generate a complete valid Sudoku grid"""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill diagonal 3x3 boxes first (they don't affect each other)
        for box in range(0, 9, 3):
            self.fill_box(grid, box, box)
        
        # Fill remaining cells
        self.solve(grid)
        return grid
    
    def fill_box(self, grid, row, col):
        """Fill a 3x3 box with random valid numbers"""
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for i in range(3):
            for j in range(3):
                grid[row + i][col + j] = numbers[i * 3 + j]
    
    def remove_numbers(self, grid, difficulty):
        """Remove numbers from complete grid to create puzzle"""
        # Difficulty levels: easy=40, medium=50, hard=60
        numbers_to_remove = {"easy": 40, "medium": 50, "hard": 60}
        remove_count = numbers_to_remove.get(difficulty, 40)
        
        puzzle = copy.deepcopy(grid)
        cells_removed = 0
        
        while cells_removed < remove_count:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            
            if puzzle[row][col] != 0:
                backup = puzzle[row][col]
                puzzle[row][col] = 0
                
                # Check if puzzle still has unique solution
                test_grid = copy.deepcopy(puzzle)
                if self.has_unique_solution(test_grid):
                    cells_removed += 1
                else:
                    puzzle[row][col] = backup
        
        return puzzle
    
    def has_unique_solution(self, grid):
        """Check if puzzle has exactly one solution"""
        solutions = self.count_solutions(copy.deepcopy(grid), 0)
        return solutions == 1
    
    def count_solutions(self, grid, count):
        """Count number of solutions (stop at 2 for efficiency)"""
        if count > 1:
            return count
        
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, i, j, num):
                            grid[i][j] = num
                            count = self.count_solutions(grid, count)
                            grid[i][j] = 0
                    return count
        return count + 1
    
    def generate_puzzle(self, difficulty="medium"):
        """Generate a new Sudoku puzzle"""
        print(f"Generating {difficulty} puzzle...")
        complete_grid = self.generate_complete_grid()
        self.solution = copy.deepcopy(complete_grid)
        self.grid = self.remove_numbers(complete_grid, difficulty)
        print("Puzzle generated!")
    
    def make_move(self, row, col, num):
        """Make a move on the grid"""
        if self.grid[row][col] != 0:
            print("Cell already filled!")
            return False
        
        if not self.is_valid(self.grid, row, col, num):
            print("Invalid move!")
            return False
        
        self.grid[row][col] = num
        return True
    
    def remove_number(self, row, col):
        """Remove a number from the grid"""
        if self.grid[row][col] == 0:
            print("Cell is already empty!")
            return False
        
        self.grid[row][col] = 0
        return True
    
    def is_complete(self):
        """Check if the puzzle is complete"""
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return False
        return True
    
    def is_correct(self):
        """Check if the current grid is correct"""
        return self.grid == self.solution
    
    def get_hint(self):
        """Get a hint for the puzzle"""
        empty_cells = []
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        
        if not empty_cells:
            print("No empty cells!")
            return
        
        row, col = random.choice(empty_cells)
        correct_num = self.solution[row][col]
        print(f"Hint: Cell ({row+1}, {col+1}) should be {correct_num}")
    
    def show_solution(self):
        """Show the complete solution"""
        print("\nComplete Solution:")
        self.print_grid(self.solution)


def main():
    print("="*50)
    print("           WELCOME TO SUDOKU GAME")
    print("="*50)
    print("\nRules:")
    print("- Fill the 9x9 grid with digits 1-9")
    print("- Each row, column, and 3x3 box must contain all digits 1-9")
    print("- Use coordinates (row, col) to place numbers")
    print("\nCommands:")
    print("- 'move <row> <col> <num>' - Place number (e.g., 'move 1 1 5')")
    print("- 'remove <row> <col>' - Remove number")
    print("- 'hint' - Get a hint")
    print("- 'solution' - Show complete solution")
    print("- 'new <difficulty>' - Start new game (easy/medium/hard)")
    print("- 'quit' - Exit game")
    
    game = Sudoku()
    
    # Generate initial puzzle
    difficulty = input("\nChoose difficulty (easy/medium/hard) [medium]: ").lower()
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"
    
    game.generate_puzzle(difficulty)
    
    while True:
        game.print_grid()
        
        if game.is_complete():
            if game.is_correct():
                print("\n🎉 Congratulations! You solved the puzzle! 🎉")
                break
            else:
                print("\n❌ Puzzle complete but incorrect. Check your answers!")
        
        command = input("\nEnter command: ").strip().lower()
        
        if command == "quit":
            print("Thanks for playing!")
            break
        
        elif command == "hint":
            game.get_hint()
        
        elif command == "solution":
            game.show_solution()
        
        elif command.startswith("new"):
            parts = command.split()
            diff = parts[1] if len(parts) > 1 else "medium"
            if diff in ["easy", "medium", "hard"]:
                game.generate_puzzle(diff)
            else:
                print("Invalid difficulty. Use easy/medium/hard")
        
        elif command.startswith("move"):
            try:
                parts = command.split()
                row, col, num = int(parts[1]) - 1, int(parts[2]) - 1, int(parts[3])
                
                if 0 <= row < 9 and 0 <= col < 9 and 1 <= num <= 9:
                    game.make_move(row, col, num)
                else:
                    print("Invalid coordinates or number!")
            except (IndexError, ValueError):
                print("Invalid command format. Use: move <row> <col> <num>")
        
        elif command.startswith("remove"):
            try:
                parts = command.split()
                row, col = int(parts[1]) - 1, int(parts[2]) - 1
                
                if 0 <= row < 9 and 0 <= col < 9:
                    game.remove_number(row, col)
                else:
                    print("Invalid coordinates!")
            except (IndexError, ValueError):
                print("Invalid command format. Use: remove <row> <col>")
        
        else:
            print("Unknown command. Type 'quit' to exit.")


if __name__ == "__main__":
    main()