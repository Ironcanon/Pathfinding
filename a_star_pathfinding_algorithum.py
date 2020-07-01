from random import choice
import pygame
#pylint: disable=no-name-in-module
#pylint: disable=no-member
from pygame.locals import (K_BACKSPACE, K_RETURN, K_SPACE, K_ESCAPE, QUIT, KEYDOWN, MOUSEBUTTONDOWN, K_c)
pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600


class Grid:
    def __init__(self,rows,cols,width,height,screen):
        self.rows = rows
        self.cols = cols
        self.nodes = [[Node(row, col, width,height,self) for col in range(self.cols)] for row in range(self.rows)]
        self.width = width
        self.height = height
        self.screen = screen
        self.start_node = None
        self.finish_node = None
        self.selected_node = None
    
    def get_node(self, click_loc):
        x, y = click_loc

        if x > 0 and x < self.width:
            if y > 0 and y < self.height:
                h_gap = self.width // self.cols
                v_gap = self.height // self.rows

                col = x // h_gap
                row = y // v_gap

                return self.nodes[row][col]

        return False
    
    def set_start_node(self, node):
        self.start_node = node
    
    def set_finish_node(self, node):
        self.finish_node = node
    
    def get_neighbours(self, node):
        node_row = node.row
        node_col = node.col

        neighbours = []
        for row in range(node_row-1,node_row+2):
            if row < 0 or row > self.rows-1:
                continue
            else:
                for col in range(node_col-1,node_col+2):
                    if col < 0 or col > self.cols-1:
                        continue
                    elif row == node_row and col == node_col:
                        continue
                    else:
                        neighbours.append(self.nodes[row][col])
        return neighbours

    def get_lowest_f_cost(self, node_list):
        lowest_f_cost_nodes = []
        lowest_f_cost = -1
        for node in node_list:
            if lowest_f_cost == -1:
                lowest_f_cost = node.f_cost
                lowest_f_cost_nodes.append(node)

            elif node.f_cost == lowest_f_cost:
                lowest_f_cost_nodes.append(node)

            elif node.f_cost < lowest_f_cost:
                lowest_f_cost = node.f_cost
                lowest_f_cost_nodes.clear()
                lowest_f_cost_nodes.append(node)

        if len(lowest_f_cost_nodes) == 1:
            return lowest_f_cost_nodes[0]

        else:
            lowest_g_cost_nodes = []
            lowest_g_cost = -1
            for node in lowest_f_cost_nodes:
                if lowest_g_cost == -1:
                    lowest_g_cost = node.g_cost
                    lowest_g_cost_nodes.append(node)

                elif node.g_cost == lowest_g_cost:
                    lowest_g_cost_nodes.append(node)

                elif node.g_cost < lowest_g_cost:
                    lowest_g_cost = node.g_cost
                    lowest_g_cost_nodes.clear()
                    lowest_g_cost_nodes.append(node)

            return choice(lowest_g_cost_nodes)

    def get_dist_between_nodes(self, node1, node2):
        dist = 0
        if node1 == node2:
            return dist

        x_diff = abs(node1.col - node2.col)
        y_diff = abs(node1.row - node2.row)

        if x_diff < y_diff:
            dist = 14*x_diff + 10*(y_diff-x_diff)
        else:
            dist = 14*y_diff + 10*(x_diff-y_diff)

        return dist

    def get_path(self):
        path = []
        current_node = self.finish_node
        while True:
            path.append(current_node)
            if current_node.parent == None:
                break
            current_node = current_node.parent
        return path

    def is_path_valid(self):
        return self.start_node != None and self.finish_node != None

    def pathfind(self):
        self.selected_node.is_selected = False
        self.selected_node = None
        open_nodes = []
        closed_nodes = []
        open_nodes.append(self.start_node)

        while len(open_nodes) > 0:
            current_node = self.get_lowest_f_cost(open_nodes)
            open_nodes.remove(current_node)
            closed_nodes.append(current_node)
            current_node.closed = True

            if current_node == self.finish_node:
                path = self.get_path()
                for node in path:
                    node.is_path = True
                self.draw()
                pygame.display.flip()
                return True
            else:
                neighbours = self.get_neighbours(current_node)
                for node in neighbours:
                    if not node.is_walkable or node in closed_nodes:
                        continue
                    new_h_cost = current_node.h_cost + self.get_dist_between_nodes(current_node, node)
                    
                    if new_h_cost < node.h_cost or node not in open_nodes:
                        node.h_cost = new_h_cost
                        node.g_cost = self.get_dist_between_nodes(node, self.finish_node)
                        node.f_cost = node.h_cost + node.g_cost

                        node.parent = current_node

                        if node not in open_nodes:
                            open_nodes.append(node)
                            node.open = True
            self.draw()
            pygame.display.flip()

        return False

    def clear_board(self):
        self.screen.fill((255,255,255))
        self.start_node = None
        self.finish_node = None
        for row in range(self.rows):
            for col in range(self.cols):
                self.nodes[row][col].parent = None
                self.nodes[row][col].is_walkable = True
                self.nodes[row][col].selected = False
                self.nodes[row][col].open = False
                self.nodes[row][col].closed = False
                self.nodes[row][col].is_special = False
                self.nodes[row][col].is_path = False
                self.nodes[row][col].draw()

    def draw(self):
        self.screen.fill((255,255,255))
        for row in range(self.rows):
            for col in range(self.cols):
                self.nodes[row][col].draw()

class Node:
    def __init__(self, row, col, width, height, grid):
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.grid = grid
        self.rect = self.create_rect()
        self.parent = None
        self.is_walkable = True
        self.selected = False
        self.open = False
        self.closed = False
        self.is_special = False
        self.is_path = False
        self.f_cost = -1
        self.g_cost = -1
        self.h_cost = -1

    def create_rect(self):
        x_gap = self.width // self.grid.cols
        y_gap = self.height // self.grid.rows

        x = self.col * x_gap
        y = self.row * y_gap

        return pygame.Rect(x,y,x_gap,y_gap)

    def draw(self):
        x_gap = self.rect.width
        y_gap = self.rect.height

        x = self.rect.left
        y = self.rect.top
        
        if not self.open and not self.closed:
            pygame.draw.rect(self.grid.screen,(255,255,255),self.rect)
        elif self.closed:
            pygame.draw.rect(self.grid.screen,(255,0,0),self.rect)
        else:
            pygame.draw.rect(self.grid.screen,(0,255,0),self.rect)

        if not self.is_walkable:
            pygame.draw.rect(self.grid.screen,(0,0,0),self.rect)

        if self.is_path:
            pygame.draw.rect(self.grid.screen,(0,100,0),self.rect)
        
        if self.is_special:
            pygame.draw.rect(self.grid.screen,(0,0,255),self.rect)

        if self.selected:
            pygame.draw.lines(self.grid.screen, (0, 255, 0), True, [(x+2,y+2), (x+x_gap-2,y+2), (x+x_gap-2,y+y_gap-2),(x+2,y+y_gap-2)])
        pygame.draw.lines(self.grid.screen, (0, 0, 0), True, [(x,y), (x+x_gap,y), (x+x_gap,y+y_gap),(x,y+y_gap)])
        

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((255,255,255))
    pygame.display.set_caption("A* Pathfinding")
    grid = Grid(20,20,600,600,screen)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                    break
                if event.key == K_RETURN:
                    if grid.selected_node and (grid.selected_node.is_walkable and not grid.selected_node.is_special):
                        if not grid.start_node:
                            grid.selected_node.is_special = True
                            grid.start_node = grid.selected_node
                        elif not grid.finish_node:
                            grid.selected_node.is_special = True
                            grid.finish_node = grid.selected_node

                if event.key == K_BACKSPACE:
                    if grid.selected_node:
                        if grid.selected_node.is_special:
                            grid.selected_node.is_special = False
                            if grid.selected_node == grid.start_node:
                                grid.start_node = None
                            else:
                                grid.finish_node = None

                if event.key == K_SPACE:
                    if grid.is_path_valid():
                        grid.pathfind()
                        print("Path found")

                if event.key == K_c:
                    grid.clear_board()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if grid.selected_node:
                        grid.selected_node.selected = False
                    grid.selected_node = grid.get_node(event.pos)
                    grid.selected_node.selected = True
                    break

                elif event.button == 3:
                    if not grid.get_node(event.pos).is_special:
                        grid.get_node(event.pos).is_walkable = not grid.get_node(event.pos).is_walkable

        grid.draw()
        pygame.display.flip()

main()