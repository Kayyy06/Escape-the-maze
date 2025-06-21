import pygame
import random
import json # saves the game statistics.
import sys

# Constants
WINDOW_SIZE = 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) # maze walls
PURPLE = (128, 0, 128) # teleportation
GREEN = (0, 255, 0) # player
RED = (255, 0, 0) # exit
YELLOW = (255, 255, 0) # traps reduces moves
ORANGE = (255, 165, 0) # riddles
BRIGHT_RED = (255, 0, 0)
GRAY = (169, 169, 169) # trace map

# Game statistics
stats = {
    "games_played": 0,
    "games_won": 0,
    "fastest_win": None
}

pygame.init()
game_font = pygame.font.SysFont(None, 20)
icon = pygame.image.load("maze.png")
pygame.display.set_icon(icon)

PUZZLES = [
    ("What gets wetter the more it dries?", "towel"),
    ("what has an eye but cannot see?", "needle"),
    ("What has to be broken to be used?", "egg"),
    ("what has many teeth but can't bite?", "comb"),
]

def draw_message(screen, font, message, color):
    screen.fill(BLACK)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

class Maze:
    def __init__(self, size, max_puzzles):
        self.size = size
        self.cell_size = WINDOW_SIZE // self.size
        self.maze = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.start_pos = (self.size - 1, 0)
        self.exit_pos = (0, self.size - 1)
        self.walls = self.generate_walls()
        self.puzzles = self.generate_puzzles(max_puzzles)
        self.traps = self.generate_traps()
        self.teleports = self.generate_teleports()

    def generate_walls(self):
        walls = []
        for i in range(self.size):
            for j in range(self.size):
                if random.random() < 0.2 and (i, j) not in [self.start_pos, self.exit_pos]:
                    self.maze[i][j] = '#'
                    walls.append((i, j))
        return walls

    def generate_puzzles(self, max_puzzles):
        puzzles = {}
        all_positions = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(all_positions)
        for pos in all_positions:
            if len(puzzles) >= max_puzzles:
                break
            if pos not in [self.start_pos, self.exit_pos, *self.walls]:
                puzzles[pos] = random.choice(PUZZLES)
        return puzzles

    def generate_traps(self):
        traps = set()
        for i in range(self.size):
            for j in range(self.size):
                if random.random() < 0.05 and (i, j) not in [self.start_pos, self.exit_pos, *self.walls, *self.puzzles]:
                    traps.add((i, j))
        return traps

    def generate_teleports(self):
        teleports = set()
        for i in range(self.size):
            for j in range(self.size):
                if random.random() < 0.05 and (i, j) not in [self.start_pos, self.exit_pos, *self.walls, *self.puzzles, *self.traps]:
                    teleports.add((i, j))
        return teleports
     
    # assigns colors to each cell
    def draw(self, screen, trace_map):
        for i in range(self.size):
            for j in range(self.size):
                color = WHITE
                if self.maze[i][j] == '#':
                    color = BLACK
                elif (i, j) == self.exit_pos:
                    color = RED
                elif (i, j) in self.traps:
                    color = YELLOW
                elif (i, j) in self.teleports:
                    color = PURPLE
                elif (i, j) in self.puzzles:
                    color = ORANGE
                elif (i, j) in trace_map:
                    color = GRAY
                pygame.draw.rect(screen, color,
                                 (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, BLACK,
                                 (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size), 1)

class Player:
    def __init__(self, maze, moves):
        self.position = maze.start_pos
        self.maze = maze
        self.moves = moves
        self.trace_map = set()

    def move(self, direction):
        x, y = self.position
        if direction == 'W':
            new_position = (x - 1, y)
        elif direction == 'S':
            new_position = (x + 1, y)
        elif direction == 'A':
            new_position = (x, y - 1)
        elif direction == 'D':
            new_position = (x, y + 1)
        else:
            return False

        if self.is_valid_move(new_position):
            self.trace_map.add(self.position)
            self.position = new_position
            self.moves = max(0, self.moves - 1)
            return True
        return False

    def is_valid_move(self, position):
        x, y = position
        return 0 <= x < self.maze.size and 0 <= y < self.maze.size and self.maze.maze[x][y] != '#'

def ask_puzzle_ui(screen, font, puzzle):
    input_text = ''
    asking = True
    clock = pygame.time.Clock()

    while asking:
        screen.fill(BLACK)
        question_text = font.render(puzzle[0], True, WHITE)
        screen.blit(question_text, (50, 150))

        input_box = font.render("Answer: " + input_text, True, GREEN)
        screen.blit(input_box, (50, 220))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text.strip().lower() == puzzle[1].strip().lower()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 20:
                        input_text += event.unicode
    return False

def load_stats():
    try:
        with open("stats.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "games_played": 0,
            "games_won": 0,
            "fastest_win": None
        }

stats = load_stats()

def save_stats():
    with open("stats.json", "w") as f:
        json.dump(stats, f)

def choose_difficulty():
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Select Difficulty")
    font = pygame.font.SysFont(None, 45)

    options = ["Easy", "Medium", "Hard"]
    selected = 0

    running = True
    while running:
        screen.fill(PURPLE)

        for i, option in enumerate(options):
            color = WHITE if i != selected else GREEN
            text = font.render(option, True, color)
            screen.blit(text, (WINDOW_SIZE // 2 - 50, 150 + i * 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]

pygame.mixer.init()
pygame.mixer.music.load("Professor Oak.mp3")
pygame.mixer.music.play(-1)

def main():
    global stats

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Escape the Maze")
    font = pygame.font.SysFont(None, 36)

    difficulty = choose_difficulty()
    if difficulty == "Easy":
        grid_size = 4
        moves = 12
        max_puzzles = 2
    elif difficulty == "Medium":
        grid_size = 6
        moves = 18
        max_puzzles = 4
    else:
        grid_size = 10
        moves = 22
        max_puzzles = 6

    maze = Maze(grid_size, max_puzzles)
    player = Player(maze, moves)

    stats["games_played"] += 1
    move_counter = 0

    running = True
    while running:
        screen.fill(PURPLE)
        maze.draw(screen, player.trace_map)

        pygame.draw.rect(screen, GREEN, (
            player.position[1] * maze.cell_size, player.position[0] * maze.cell_size, maze.cell_size, maze.cell_size))
        pygame.draw.rect(screen, BLACK, (
            player.position[1] * maze.cell_size, player.position[0] * maze.cell_size, maze.cell_size, maze.cell_size), 1)

        move_text = font.render(f'Moves Left: {player.moves}', True, BRIGHT_RED, BLACK)
        screen.blit(move_text, (10, 10))
        
        # game statistics
        stats_text = [
            f"Games Played: {stats['games_played']}",
            f"Wins: {stats['games_won']}",
            f"Win %: {(stats['games_won'] / stats['games_played']) * 100:.1f}%" if stats['games_played'] else "Win %: 0.0%",
            f"Fastest Win: {stats['fastest_win']} moves" if stats['fastest_win'] else "Fastest Win: N/A"
        ]

        # Draw grey box below "Moves Left"
        box_x = 10
        box_y = 40
        line_height = 10
        padding = 5
        box_width = 145
        box_height = len(stats_text) * line_height + padding * 2

        pygame.draw.rect(screen, (211, 211, 211), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 1)

        for i, line in enumerate(stats_text):
            stat_surface = game_font.render(line, True, BLACK)
            screen.blit(stat_surface, (box_x + padding, box_y + padding + i * line_height))

        pygame.display.flip()

        move_success = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    direction = {pygame.K_w: 'W', pygame.K_s: 'S', pygame.K_a: 'A', pygame.K_d: 'D'}[key]
                    move_success = player.move(direction)
                    if move_success:
                        move_counter += 1

        if move_success:
            pos = player.position
            if pos in maze.puzzles:
                correct = ask_puzzle_ui(screen, font, maze.puzzles[pos])
                if correct:
                    player.moves += 2
                    del maze.puzzles[pos]

            if pos in maze.traps:
                player.moves = max(0, player.moves - 2)

            if pos in maze.teleports:
                destinations = list(maze.teleports - {pos})
                if destinations:
                    player.position = random.choice(destinations)

        if player.position == maze.exit_pos:
            stats["games_won"] += 1
            if stats["fastest_win"] is None or move_counter < stats["fastest_win"]:
                stats["fastest_win"] = move_counter
            draw_message(screen, font, "YOU WIN!", GREEN)
            running = False

        elif player.moves <= 0:
            draw_message(screen, font, "GAME OVER! TRY AGAIN", BRIGHT_RED)
            running = False

        save_stats()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
