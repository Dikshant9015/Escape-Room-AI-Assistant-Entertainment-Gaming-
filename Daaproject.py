import pygame
import random
import heapq

pygame.init()
pygame.mixer.init()

# Load sound effects and images
bg_music = pygame.mixer.Sound("background_music.wav")
pickup_sound = pygame.mixer.Sound("pickup.wav")
escape_sound = pygame.mixer.Sound("escape.wav")

# Load and resize images
cell_size = 80

def load_and_resize(image_path):
    return pygame.transform.scale(pygame.image.load(image_path), (cell_size, cell_size))

player_sprite = load_and_resize("player.png")
key_sprite = load_and_resize("key.png")
exit_sprite = load_and_resize("exit.png")
wall_sprite = load_and_resize("wall.png")
floor_sprite = load_and_resize("floor.png")

bg_music.play(-1)  # Loop background music

def generate_maze(rows, cols):
    maze = [['X' for _ in range(cols)] for _ in range(rows)]
    
    def carve_passages(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 'X':
                maze[x + dx][y + dy] = '.'
                maze[nx][ny] = '.'
                carve_passages(nx, ny)
    
    maze[1][1] = '.'
    carve_passages(1, 1)
    
    empty_cells = [(r, c) for r in range(rows) for c in range(cols) if maze[r][c] == '.']
    (start_x, start_y), (key_x, key_y), (exit_x, exit_y) = random.sample(empty_cells, 3)
    maze[start_x][start_y] = 'S'
    maze[key_x][key_y] = 'K'
    maze[exit_x][exit_y] = 'E'
    
    return maze, (start_x, start_y), (key_x, key_y), (exit_x, exit_y)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {start: 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            break
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_pos = (current[0] + dx, current[1] + dy)
            if 0 <= next_pos[0] < rows and 0 <= next_pos[1] < cols and grid[next_pos[0]][next_pos[1]] != 'X':
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(open_set, (priority, next_pos))
                    came_from[next_pos] = current
    
    path = []
    current = goal
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def draw_grid(screen, grid, current_pos, path=[]):
    screen.fill((30, 30, 30))
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
            if grid[row][col] == 'X':
                screen.blit(wall_sprite, rect)
            else:
                screen.blit(floor_sprite, rect)
            if grid[row][col] == 'K':
                screen.blit(key_sprite, rect)
            elif grid[row][col] == 'E':
                screen.blit(exit_sprite, rect)
    for step in path:
        pygame.draw.rect(screen, (0, 255, 0), (step[1] * cell_size, step[0] * cell_size, cell_size, cell_size), 5)
    player_rect = pygame.Rect(current_pos[1] * cell_size, current_pos[0] * cell_size, cell_size, cell_size)
    screen.blit(player_sprite, player_rect)

def main():
    rows, cols = 11, 11
    screen = pygame.display.set_mode((cols * cell_size, rows * cell_size))
    pygame.display.set_caption("Escape Room AI")
    grid, (player_x, player_y), (key_x, key_y), (exit_x, exit_y) = generate_maze(rows, cols)
    has_key = False
    running = True
    clock = pygame.time.Clock()
    path_to_exit = []
    
    while running:
        screen.fill((30, 30, 30))
        draw_grid(screen, grid, (player_x, player_y), path_to_exit)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                new_x, new_y = player_x, player_y
                if event.key == pygame.K_UP:
                    new_x -= 1
                elif event.key == pygame.K_DOWN:
                    new_x += 1
                elif event.key == pygame.K_LEFT:
                    new_y -= 1
                elif event.key == pygame.K_RIGHT:
                    new_y += 1
                
                if 0 <= new_x < rows and 0 <= new_y < cols and grid[new_x][new_y] != 'X':
                    player_x, player_y = new_x, new_y
                    
                    if (player_x, player_y) == (key_x, key_y):
                        has_key = True
                        grid[key_x][key_y] = '.'
                        pickup_sound.play()
                    
                    if has_key:
                        path_to_exit = a_star_search(grid, (player_x, player_y), (exit_x, exit_y))
                    
                    if (player_x, player_y) == (exit_x, exit_y) and has_key:
                        escape_sound.play()
                        font = pygame.font.Font(None, 60)
                        text_surface = font.render("You Escaped!", True, (255, 215, 0))
                        screen.blit(text_surface, (cols * cell_size // 4, rows * cell_size // 2))
                        pygame.display.flip()
                        pygame.time.delay(3000)
                        running = False
        
        clock.tick(30)
    pygame.quit()
    bg_music.stop()

if __name__ == "__main__":
    main()
