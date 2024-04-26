import pygame
import random
import itertools
import numpy as np
import os
from sys import exit

class MineSweeper:
    
    # Initializes the game 
    def __init__(self, grid_size, mine_num):
        self.grid_size = grid_size
        self.mine_num = mine_num
        self.flags = mine_num
        self.mine_coord = set(random.sample(list(itertools.product(range(self.grid_size), repeat = 2)), self.mine_num))
        self.all_coord = set([(x, y) for x in range(grid_size) for y in range(grid_size)])
        self.grid = {coord: -1 if coord in self.mine_coord else None for coord in self.all_coord}
        self.unopened = set(self.all_coord)
        self.flagged = set()
        self.state = 0 # -1 for dead, 0 for alive, 1 for won.
        self.last_time = None
        self.start_time = int(pygame.time.get_ticks()/1000)
        self.adj = np.zeros(shape = (grid_size**2, grid_size**2), dtype = int)
        
        for tile in self.all_coord:
            neighbors = []
            for i in range(-1, 2, 1):
                for j in range(-1, 2, 1):
                    if i == 0 and j == 0:
                        continue
                    else:
                        if (tile[0]+i, tile[1]+j) in self.all_coord:
                            self.adj[tile[0]*self.grid_size+tile[1], (tile[0]+i)*self.grid_size+(tile[1]+j)] = 1
                            neighbors.append((tile[0]+i, tile[1]+j))
            count = 0
            
            if tile in self.mine_coord:
                continue
            else:
                for neighbor in neighbors:
                    if neighbor in self.mine_coord:
                        count += 1
                self.grid[tile] = count
                                                    
    def flag(self, tile):
        if tile in self.unopened and self.flags > 0 and tile not in self.flagged:
            self.flagged.add(tile)
            self.flags -= 1
        elif tile in self.unopened and tile in self.flagged:
            self.flagged.remove(tile)
            self.flags += 1
            
    def open_tile(self, tile, tile_size):
        if tile in self.unopened:
            self.unopened.remove(tile)
            if self.grid[tile] == -1:
                self.state = -1
                self.last_time = int(pygame.time.get_ticks()/1000)-self.start_time
                for mine in self.mine_coord:
                    if mine == tile:
                        continue
                    else:
                        self.unopened.remove(mine)
            else:
                self.dfs(tile, tile_size)
        
    def dfs(self, start, grid_size):
        num_nodes = self.adj.shape[0]
        visited = set()
        stack = [start[0]*grid_size+start[1]]
        while stack:
            node = stack.pop()
            if (node//grid_size, node%grid_size) in self.flagged:
                self.flags += 1
                self.flagged.remove((node//grid_size, node%grid_size))
            try:
                self.unopened.remove((node//grid_size, node%grid_size))
            except:
                pass
            
            if node not in visited:
                visited.add(node)
                # Check the condition for the current node
                if not (self.grid[(node//grid_size, node%grid_size)] >= 1):
                    # Explore neighbors if condition is not met
                    for neighbor in range(num_nodes):
                        if self.adj[node, neighbor] and neighbor not in visited:
                            stack.append(neighbor)
        if self.unopened == self.mine_coord:
            self.last_time = int(pygame.time.get_ticks()/1000)-self.start_time
            self.state = 1
            self.flags = 0
            
    def elapsed_time(self):
        if self.state == -1 or self.state == 1:
            return self.last_time
        return int(pygame.time.get_ticks()/1000)-self.start_time
        
    def reset(self):
        self.__init__(self.grid_size, self.mine_num)
            
class Graphics:
    def __init__(self, grid_size, tile_size):
        pygame.display.set_caption("Mine Sweeper")
        pygame.init()
        
        self.grid_size = grid_size
        self.tile_size = tile_size 
        self.width = tile_size*grid_size
        self.height = 100 + tile_size*grid_size
        self.hardcode = {"alive.png":50, "flagicon.png":30, "clockicon.png":50, "dead.png":50, "won.png":50}
        self.art_list = os.listdir("Assets")
        self.art = dict()
        self.screen = pygame.display.set_mode((grid_size*tile_size, 100+grid_size*tile_size))
        for asset in self.art_list: 
            if asset[~3:] == ".ttf":
                aux = pygame.font.Font(f"Assets/{asset}", 30)
            else:
                aux = pygame.image.load(f"Assets/{asset}").convert_alpha()
                if asset in self.hardcode:
                    aux = pygame.transform.scale(aux, (self.hardcode[asset], self.hardcode[asset]))
                else:
                    aux = pygame.transform.scale(aux, (tile_size, tile_size))
            self.art[f"{asset}"] = aux
        pygame.display.set_icon(self.art["gameicon.png"])
                
    def display(self, surface, x, y, tile = False):
        if tile:
            self.screen.blit(surface, (x*self.tile_size, 100+y*self.tile_size)) # Pixel conversion.
        else:
            self.screen.blit(surface, (x, y))
        
    def banner(self, flags, time, state):
        pygame.draw.rect(self.screen, "#eeeee4", pygame.Rect(0, 0, self.width, 100))
        self.display(self.art["clockicon.png"], 10, 30)
        self.display(self.art["flagicon.png"], self.width-120, 40)
        txt_flag_surf = self.art["PixelGameFont.ttf"].render(str(flags), False, "Black")
        self.display(txt_flag_surf, self.width - 70, 44)
        txt_time_surf = self.art["PixelGameFont.ttf"].render(str(time), False, "Black")
        self.display(txt_time_surf, 70, 44)
        if state == -1:
            self.display(self.art["dead.png"], (self.width-50)/2, 25)
        elif state == 0:
            self.display(self.art["alive.png"], (self.width-50)/2, 25)
        else:
            self.display(self.art["won.png"], (self.width-50)/2, 25)
            
    def grid(self, flagged, unopened, all_coord, grid, mine_coord, state):
        opened = all_coord-unopened
        if state == -1:
            for tile in opened:
                if tile in mine_coord:
                    self.display(self.art["mine.png"], tile[0], tile[1], tile = True)
                else:
                    self.display(self.art[f"empty{grid[tile]}.png"], tile[0], tile[1], tile = True)
            for tile in flagged:
                if tile not in mine_coord:
                    self.display(self.art["cross.png"], tile[0], tile[1], tile = True)
                else:
                    self.display(self.art["flag.png"], tile[0], tile[1], tile = True)
            for tile in unopened:
                if tile not in flagged:
                    self.display(self.art["default.png"], tile[0], tile[1], tile = True)
        elif state == 0:
            for tile in opened:
                self.display(self.art[f"empty{grid[tile]}.png"], tile[0], tile[1], tile = True)
            for tile in flagged:
                self.display(self.art["flag.png"], tile[0], tile[1], tile = True)
            for tile in unopened:
                if tile not in flagged:
                    self.display(self.art["default.png"], tile[0], tile[1], tile = True)
        elif state == 1:
            for tile in unopened:
                self.display(self.art["flag.png"], tile[0], tile[1], tile = True)
            for tile in opened:
                self.display(self.art[f"empty{grid[tile]}.png"], tile[0], tile[1], tile = True)

# Minimum width of 400 pixels is required.
            
grid_size = 20
tile_size = 20
num_mines = 25

if grid_size*tile_size < 400:
    print("Minimum width of 400 pixel is required. grid_size*tile_size must be greater than 400.")
    exit()
elif not 0 < num_mines < grid_size**2:
    print("The number of mines should be between 0 and grid_size**2.")
    exit()

game = MineSweeper(grid_size, num_mines)
graph = Graphics(grid_size, tile_size)
clock = pygame.time.Clock()

def right_click(x, y):
    game.flag((x, y))

def left_click(x, y, grid_size):
    if (x, y) in game.flagged:
        return
    game.open_tile((x, y), grid_size)
                
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        # Player clicks will only "count/register" when player is in alive state.
        if event.type == pygame.MOUSEBUTTONDOWN and game.state == 0:
            # Coordinate conversion.
            x, y = event.pos; x, y = x//tile_size, (y-100)//tile_size
            if event.button == 3:
                right_click(x, y)
            elif event.button == 1:
                left_click(x, y, grid_size)
        
        # Player presses "R" key to restart.
        if event.type == pygame.KEYDOWN and event.key == 114:
            game.reset()

    graph.banner(game.flags, game.elapsed_time(), game.state)
    graph.grid(game.flagged, game.unopened, game.all_coord, game.grid, game.mine_coord, game.state)
    
    pygame.display.update()
    clock.tick(60)