#Original

import pygame, sys 

pygame.init()
pygame.font.init()

invalids =   (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,
             19,37,55,73,91,109,127,145,163,181,
             182,183,184,185,186,187,188,189,190,
             191,192,193,194,195,196,197,198,
             36,54,72,90,108,126,144,162,180,198)

screen = pygame.display.set_mode((720, 440))

def text_to_screen(screen, text, x, y, size = 15,
            color = (255, 255, 255), font_type = 'monospace'):
    try:
        
        text = str(text)
        font = pygame.font.SysFont(font_type, size)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))
    except Exception, e:
        print 'Font Error, saw it coming'
        raise e


class Tile(pygame.Rect):

    List = []
    width, height = 40, 40
    total_tiles = 1
    H, V = 1, 18

    def __init__(self, x, y, Type):

        self.parent = None
        self.H, self.G, self.F = 0,0,0

        self.type = Type
        self.number = Tile.total_tiles
        Tile.total_tiles += 1

        if Type == 'empty':
            self.walkable = True
        else:
            self.walkable = False

        pygame.Rect.__init__(self, (x, y) , (Tile.width, Tile.height) )

        Tile.List.append(self)

    @staticmethod
    def get_tile(number):
        for tile in Tile.List:
            if tile.number == number:
                return tile

    @staticmethod
    def draw_tiles(screen):
        half = Tile.width / 2

        for tile in Tile.List:

            if not(tile.type == 'empty'):
                pygame.draw.rect(screen, [40, 40, 40], tile )

            if tile.G != 0:
                text_to_screen(screen, tile.G, tile.x, tile.y + half, color = [120, 157, 40])
            if tile.H != 0:
                text_to_screen(screen, tile.H, tile.x + half, tile.y + half, color = [20 , 67, 150])
            if tile.F != 0:
                text_to_screen(screen, tile.F, tile.x + half, tile.y, color = [56, 177, 177])

            text_to_screen(screen, tile.number, tile.x, tile.y)

for y in range(0, screen.get_height(), 40):
    for x in range(0, screen.get_width(), 40):
        if Tile.total_tiles in invalids:
            Tile(x, y, 'solid')
        else:
            Tile(x, y, 'empty')

clock = pygame.time.Clock()
FPS = 20
total_frames = 0

class Character(pygame.Rect):

    width, height = 40, 40

    def __init__(self, x, y):

        pygame.Rect.__init__(self, x, y, Character.width, Character.height)

    def __str__(self):
        return str(self.get_number())

    def get_number(self):
        
        return ((self.x / self.width) + Tile.H) + ((self.y / self.height) * Tile.V)

    def get_tile(self):

        return Tile.get_tile(self.get_number())


class Zombie(Character):

    List = []

    def __init__(self, x, y):

        Character.__init__(self, x, y)
        Zombie.List.append(self)

    @staticmethod
    def draw_zombies(screen):
        for zombie in Zombie.List:
            pygame.draw.rect(screen, [210, 24, 77], zombie)


class Survivor(Character):

    def __init__(self, x, y):

        Character.__init__(self, x, y)

    def draw(self, screen):
        r = self.width / 2
        pygame.draw.circle(screen, [77, 234, 156], (self.x + r, self.y + r), r)

zombie1 = Zombie(80, 80)
survivor = Survivor(200, 360)

def A_Star(screen, survivor, total_frames, FPS):
    
    half = Tile.width / 2

    N = -18
    S = 18
    E = 1
    W = -1

    NW = -19
    NE = -17
    SE = 19
    SW = 17

    def blocky(tiles, diagonals, surrounding_node):
        if surrounding_node.number not in diagonals:
            tiles.append(surrounding_node)
        return tiles

    def get_surrounding_tiles(base_node):
        
        array =(
            (base_node.number + N),
            (base_node.number + NE),
            (base_node.number + E),
            (base_node.number + SE),
            (base_node.number + S),
            (base_node.number + SW),
            (base_node.number + W),
            (base_node.number + NW),
            )

        tiles = []

        onn = base_node.number 
        diagonals = [onn + NE, onn + NW, onn + SE, onn + SW]

        for tile_number in array:

            surrounding_tile = Tile.get_tile(tile_number)

            if surrounding_tile.walkable and surrounding_tile not in closed_list:
                # tiles.append(surrounding_tile) # Diagonal movement
                tiles = blocky(tiles, diagonals, surrounding_tile)

        return tiles

    def G(tile):
        
        diff = tile.number - tile.parent.number

        if diff in (N, S, E, W):
            tile.G = tile.parent.G + 10
        elif diff in (NE, NW, SW, SE):
            tile.G = tile.parent.G + 14

    def H():
        for tile in Tile.List:
            tile.H = 10 * (abs(tile.x - survivor.x) + abs(tile.y - survivor.y)) / Tile.width

    def F(tile):
        # F = G + H
        tile.F = tile.G + tile.H

    def swap(tile):
        open_list.remove(tile)
        closed_list.append(tile)

    def get_LFT(): # get Lowest F Value

        F_Values = []
        for tile in open_list:
            F_Values.append(tile.F)

        o = open_list[::-1]

        for tile in o:
            if tile.F == min(F_Values):
                return tile

    def move_to_G_cost(LFT, tile):

        GVal = 0
        diff = LFT.number - tile.number

        if diff in (N, S, E, W):
            GVal = LFT.G + 10
        elif diff in (NE, NW, SE, SW):
            GVal = LFT.G + 14

        return GVal

    def loop():

        LFT = get_LFT() 

        swap(LFT)
        surrounding_nodes = get_surrounding_tiles(LFT)

        for node in surrounding_nodes:

            if node not in open_list:

                open_list.append(node)
                node.parent = LFT

            elif node in open_list:
                
                calculated_G = move_to_G_cost(LFT, node)
                if calculated_G < node.G:

                    node.parent = LFT
                    G(node)
                    F(node)

        if open_list == [] or survivor.get_tile() in closed_list:
            return

        for node in open_list:
            G(node)
            F(node)

            # pygame.draw.line(screen, [255, 0, 0],
            # [node.parent.x + half, node.parent.y + half],
            # [node.x + half, node.y + half] )

        loop()

        

    for zombie in Zombie.List:

        open_list = []
        closed_list = []

        zombie_tile = zombie.get_tile()
        open_list.append(zombie_tile)

        surrounding_nodes = get_surrounding_tiles(zombie_tile)

        for node in surrounding_nodes:
            node.parent = zombie_tile
            open_list.append(node)      

        swap(zombie_tile)

        H()

        for node in surrounding_nodes:
            G(node)
            F(node) 

        loop()

        return_tiles = []

        parent = survivor.get_tile()

        while True:

            return_tiles.append(parent)

            parent = parent.parent

            if parent == None:
                break

            if parent.number == zombie.get_number():
                break

        for tile in return_tiles:
            pygame.draw.circle(screen, [34, 95, 200],
            [tile.x + half - 2, tile.y + half - 2], 5 )

        if len(return_tiles) > 1:
            if total_frames % (FPS / 4) == 0:
                next_tile = return_tiles[-1]
                zombie.x = next_tile.x
                zombie.y = next_tile.y
def interaction(screen, survivor):

    Mpos = pygame.mouse.get_pos() # [x, y] 
    Mx = Mpos[0] / Tile.width
    My = Mpos[1] / Tile.height

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for tile in Tile.List:
                if tile.x == (Mx * Tile.width) and tile.y == (My * Tile.width):
                    tile.type = 'solid'
                    tile.walkable = False
                    break


        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP: # North
                future_tile_number = survivor.get_number() - Tile.V

                if Tile.get_tile(future_tile_number).walkable:
                    survivor.y -= survivor.height                   

            if event.key == pygame.K_DOWN: # South
                future_tile_number = survivor.get_number() + Tile.V

                if Tile.get_tile(future_tile_number).walkable:
                    survivor.y += survivor.height 

            if event.key == pygame.K_LEFT: # West
                future_tile_number = survivor.get_number() - Tile.H

                if Tile.get_tile(future_tile_number).walkable:
                    survivor.x -= survivor.width 

            if event.key == pygame.K_RIGHT: # East
                future_tile_number = survivor.get_number() + Tile.H

                if Tile.get_tile(future_tile_number).walkable:
                    survivor.x += survivor.width 

while True:

    screen.fill([0,0,0])    
    A_Star(screen, survivor, total_frames, FPS)
    interaction(screen, survivor)
    Tile.draw_tiles(screen)
    survivor.draw(screen)
    Zombie.draw_zombies(screen)

    pygame.display.flip()
    clock.tick(FPS)
    total_frames += 1





