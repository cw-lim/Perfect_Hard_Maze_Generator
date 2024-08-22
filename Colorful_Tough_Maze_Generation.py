import random
import matplotlib.pyplot as plt
from collections import deque
import os
import matplotlib.colors as mcolors

# Define a custom blue colormap
blue_colormap = mcolors.LinearSegmentedColormap.from_list(
    'custom_blue', ['white', 'blue'], N=256)
green_colormap = mcolors.LinearSegmentedColormap.from_list(
    'custom_green', ['white', 'green'], N=256)

# Directions for movement: Down, Up, Right, Left
directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def generate_maze_dfs_perfect(width, height):
    # Create a grid of walls
    maze = [[1] * (2 * width + 1) for _ in range(2 * height + 1)]

    # Start stack with the starting point
    stack = [(0, 0)]
    maze[1][1] = 0  # Mark the start point as part of the maze

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)  # Randomize the order of directions to move

        valid_neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < height and 0 <= ny < width and maze[2 * nx + 1][2 * ny + 1] == 1:
                valid_neighbors.append((nx, ny))

        if valid_neighbors:
            # Pick a random valid neighbor but bias towards the first one for longer paths
            nx, ny = random.choice(valid_neighbors)
            
            # Break the wall between the current cell and the new cell
            maze[2 * x + 1 + (nx - x)][2 * y + 1 + (ny - y)] = 0
            maze[2 * nx + 1][2 * ny + 1] = 0  # Mark the new cell as part of the maze
            stack.append((nx, ny))  # Add the new cell to the stack
        else:
            stack.pop()  # Backtrack if no valid moves are available

    # Open the entrance and exit
    maze[1][0] = 0  # Entrance at the top-left corner
    maze[2 * height - 1][2 * width] = 0  # Exit at the bottom-right corner

    return maze

def add_long_dead_ends(maze, path):
    height = len(maze)
    width = len(maze[0])
    num_dead_ends = int((height * width) * 0.03)  # Add longer dead ends to 3% of the cells

    # Copy the maze and the path
    temp_maze = [row[:] for row in maze]
    temp_path = path[:]

    for _ in range(num_dead_ends):
        # Pick a random cell from the path
        x, y = random.choice(temp_path)
        dead_end_length = random.randint(10, 20)  # Increase dead-end length between 10 and 20 cells

        # Create a longer dead end by extending in a random direction
        for _ in range(dead_end_length):
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < height - 1 and 1 <= ny < width - 1 and temp_maze[nx][ny] == 0 and (nx, ny) not in temp_path:
                    temp_maze[nx][ny] = 1  # Add a wall
                    x, y = nx, ny
                    break
            else:
                break  # Stop if no valid move

        if not solve_maze_bfs(temp_maze):  # Ensure the maze is still solvable
            # Revert the dead-end if it blocks the path
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < height - 1 and 1 <= ny < width - 1:
                    temp_maze[nx][ny] = 0

    # Return the updated maze
    return temp_maze

def solve_maze_bfs(maze):
    height = len(maze)
    width = len(maze[0])
    
    start = (1, 0)  # Entrance (top-left corner)
    end = (height - 2, width - 1)  # Exit (bottom-right corner)

    # Queue for BFS and a dictionary to track the path
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == end:
            break

        x, y = current

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < height and 0 <= ny < width and maze[nx][ny] == 0 and (nx, ny) not in came_from:
                queue.append((nx, ny))
                came_from[(nx, ny)] = current

    # Reconstruct the path from end to start
    if end not in came_from:
        print("No solution found for this maze.")
        return []  # Return an empty path if the end is not reachable

    path = []
    step = end
    while step:
        path.append(step)
        step = came_from[step]

    path.reverse()  # Reverse the path to get it from start to end

    return path

def save_maze(maze, save_path, dpi):
    plt.figure(figsize=(15, 15))
    plt.imshow(maze, cmap=blue_colormap)  # Use the custom blue colormap
    plt.xticks([]), plt.yticks([])  # Remove axis labels
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0, dpi=dpi)
    plt.close()

def save_solution(maze, path, save_path, dpi):
    maze_copy = [row[:] for row in maze]  # Copy the maze for visualization

    # Mark the solution path in the maze
    for (x, y) in path:
        maze_copy[x][y] = 2  # Use '2' to mark the solution path

    plt.figure(figsize=(15, 15))
    plt.imshow(maze_copy, cmap=green_colormap)  # Use the custom blue colormap
    plt.xticks([]), plt.yticks([])  # Remove axis labels
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0, dpi=dpi)
    plt.close()

# Example usage with harder maze
width, height = 70, 100  # Larger size to increase difficulty
output_dir = 'colorful_perfect_hard_mazes_70_by_100'
os.makedirs(output_dir, exist_ok=True)

for i in range(10):
    # Generate a perfect maze
    maze = generate_maze_dfs_perfect(width, height)
    
    # Solve the maze to get the solution path
    solution_path = solve_maze_bfs(maze)
    
    # Add long dead ends while ensuring the maze remains solvable
    harder_maze = add_long_dead_ends(maze, solution_path)
    
    # Re-solve the harder maze
    harder_solution_path = solve_maze_bfs(harder_maze)

    # Save the harder maze and its solution
    maze_save_path = os.path.join(output_dir, f'colorful_perfect_hard_mazes_70_by_100_{i+1:03d}.png')
    solution_save_path = os.path.join(output_dir, f'colorful_perfect_hard_solution_70_by_100_{i+1:03d}.png')
    
    save_maze(harder_maze, maze_save_path, dpi=600)
    save_solution(harder_maze, harder_solution_path, solution_save_path, dpi=600)
    
    print(f'Saved perfect hard maze {i+1} and its solution.')

print('All perfect hard mazes and solutions have been saved.')