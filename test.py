import pygame

pygame.init()
size = width, height = 1100, 700
screen = pygame.display.set_mode(size)  # , pygame.FULLSCREEN)
tile_size = 200
building_collide_step = 75
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
player_info_group = pygame.sprite.Group()
text = None
door = None


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'f':
                Tile('fence', x, y)
            elif level[y][x] == 'g':
                Tile('grass', x, y)
            elif level[y][x] == 'r':
                Tile('road', x, y)
            elif level[y][x] == '@':
                Tile('road', x, y)
                new_player = Player(x, y, all_sprites, player_group)
            elif level[y][x] == '1':
                PoisonShop(x, y)
                Tile('grass', x, y)
            elif level[y][x] == '2':
                CathedralEasy(x, y)
                Tile('grass', x, y)
            elif level[y][x] == '3':
                Shop(x, y)
                Tile('grass', x, y)
            elif level[y][x] == '4':
                CathedralHard(x, y)
                Tile('grass', x, y)
            elif level[y][x] == '5':
                LivingHouse(x, y)
                Tile('grass', x, y)
            elif level[y][x] == '6':
                BigHouse(x, y)
                Tile('grass', x, y)
    return new_player, x, y


def load_level(filename):
    data = open(filename, mode="r", encoding="utf-8")
    level_map = [line.strip() for line in data]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(path, colorkey=None, size=None):
    image = pygame.image.load(path).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image


class Player(pygame.sprite.Sprite):
    step = 1

    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.frames = {'left': [], 'right': [], 'back': [], 'forward': []}
        # self.cut_sheet(load_image("data/characters/player_right.png", colorkey=(255, 0, 0)), 9, 1)
        self.frame_num = 0
        for i in range(9):
            self.frames["left"].append(load_image(f'data/characters/player_left_{str(i + 1)}.png',
                                                  colorkey=(255, 0, 0)))
        for i in range(9):
            self.frames["right"].append(load_image(f'data/characters/player_right_{str(i + 1)}.png',
                                                   colorkey=(255, 0, 0)))
        '''for i in range(9):
            self.frames["forward"].append(load_image(f'data/characters/player_forward_{str(i + 1)}.png',
                                                  colorkey=(255, 0, 0)))
        for i in range(9):
            self.frames["back"].append(load_image(f'data/characters/player_back_{str(i + 1)}.png',
                                                  colorkey=(255, 0, 0)))'''

        # self.image = self.frames[self.frame_num]
        self.image = self.frames['right'][self.frame_num]
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_size
        self.rect.y = y * tile_size
        self.moving = True
        self.prev_coords = self.get_coords()
        self.num = 0
        self.pos = (self.rect.x + 10, self.rect.y)
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step, self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step, self.rect.h + building_collide_step)
        self.health = 100
        self.poisons = []
        self.weapons = []
        self.money = 10000

    # notice calls of expected classes Weapon nd Poison
    def add_product(self, prod):
        if isinstance(prod, Weapon):
            self.weapons.append(prod)
        elif isinstance(prod, Poison):
            self.poisons.append(prod)
        return True

    def reduce_money(self, amount):
        prev = self.money
        self.money -= amount
        if self.money >= 0:
            return True
        else:
            self.money = prev
            return False

    '''def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))'''

    def get_health(self):
        return self.health

    def get_money(self):
        return self.money

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def get_coords(self):
        return (self.get_x(), self.get_y())

    def get_info(self):
        return self.money, self.health

    def move_point(self, pos, forward):
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        if forward:
            self.rect.x += 0.01 * (Player.step * x - self.rect.x)
            self.rect.y += 0.01 * (Player.step * y - self.rect.y)
        elif not forward:
            self.rect.x -= 0.01 * (Player.step * x - self.rect.x)
            self.rect.y -= 0.01 * (Player.step * y - self.rect.y)

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def set_moving(self, value):
        self.moving = bool(value)

    def update(self, pos):
        self.pos = pos
        x = self.pos[0]
        self.num += 1
        if self.num == 10:
            self.frame_num = (self.frame_num + 1) % len(self.frames['left'])
            if self.moving:
                if x > self.rect.x:
                    self.image = self.frames['right'][self.frame_num]
                else:
                    self.image = self.frames['left'][self.frame_num]
            else:
                if x > self.rect.x:
                    self.image = self.frames['right'][0]
                else:
                    self.image = self.frames['left'][0]
            self.num = 1


class Tile(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y, *groups):
        groups = list(groups)
        groups.append(all_sprites)
        super().__init__(groups)
        self.type = type
        self.image = tile_images[type]
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * tile_size
        self.rect.y = pos_y * tile_size
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step, self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step, self.rect.h + building_collide_step)

    def is_obstacle(self):
        if self.type in ['road', 'grass', "roof"]:
            return False
        return True


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image, func, *groups):
        groups = list(groups)
        groups.extend([button_group, buildings_group])
        super().__init__(groups)
        self.h = h
        self.w = w
        self.image = pygame.transform.scale(image, (self.w, self.h))
        # self.image = image
        self.rect = self.image.get_rect()
        self.func = func
        self.rect.x, self.rect.y = x, y
        self.frames = [self.image] * 2
        self.frames[0].set_alpha(50)
        self.frames[1].set_alpha(300)
        self.image = self.frames[0]

    def run(self, *args):
        self.func(*args)

    def check_selection(self, pos):
        if self.rect.collidepoint(pos):
            self.image = self.frames[1]
        else:
            self.image = self.frames[0]

    def is_obstacle(self):
        return False


def distance(coords_1, coords_2):
    x1, y1 = coords_1
    x2, y2 = coords_2
    dist = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    return dist


def check_collisions(obj):
    global text
    a = None
    for sprite in all_sprites:
        if id(sprite) == id(obj):
            continue
        if sprite.is_obstacle() and sprite.rect.colliderect(obj.rect):
            check_active_zones(obj)
            return True
    check_active_zones(obj)
    return False


def check_active_zones(obj):
    global text, door
    for sprite in all_sprites:
        if id(sprite) == id(obj):
            continue
        if sprite.is_obstacle() and sprite.col_rect.colliderect(obj.rect) and not isinstance(sprite, Tile):
            font = pygame.font.Font(None, 50)
            text = font.render("[E] - enter " + sprite.name, 1, (47, 213, 175))
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - text.get_height() // 2
            # screen.blit(text, (text_x, text_y))
            door = sprite
            return
    door = None
    text = None


def create_col_rect(obj):
    obj.col_rect = pygame.Rect(obj.rect.x - building_collide_step, obj.rect.y - building_collide_step,
                               obj.rect.w + building_collide_step, obj.rect.h + building_collide_step)



# renfering main info about player
# returns surface with the text
def render_info(player, screen):
    money, health = player.get_info()
    font = pygame.font.Font(None, 30)
    text = font.render(f'{str(money)}  coins     {str(health)}     health', 1, (255, 255, 255))
    # new = pygame.display.set_mode((text.get_width(), text.get_height()))
    # new.fill((122, 86, 33))
    # new.blit(text, (0, 0))
    return text


# renders any text
# returns Surface
def render_text(line):
    font = pygame.font.Font(None, 50)
    text = font.render(line, 1, (255, 255, 255))
    return text


# nothing, but it works)
def test():
    quit()


tile_images = {"road": load_image("data/textures/stone_1.png", (255, 0, 0), (tile_size, tile_size)),
               "living_house": load_image("data/houses/sleep_house.png", (255, 0, 0), (tile_size * 2, tile_size)),
               "poison_shop": load_image("data/houses/poison_shop.png", (255, 0, 0), (tile_size * 2, tile_size)),
               "shop": load_image("data/houses/shop_1.png", (255, 0, 0), (tile_size * 2, tile_size * 3)),
               "grass": load_image("data/textures/grass.png", (255, 0, 0), (tile_size, tile_size)),
               "fence": load_image("data/textures/roof_1.png", (255, 0, 0), (tile_size, tile_size)),
               "cathedral_1": load_image("data/houses/cathedral_1.png", (255, 0, 0), (tile_size * 5, tile_size * 2)),
               "cathedral_2": load_image("data/houses/cathedral_2.png", (255, 0, 0), (tile_size * 3, tile_size * 2)),
               "big_house": load_image("data/houses/big_house.png", (255, 0, 0), (tile_size * 2, tile_size * 2)),
               "empty": load_image("data/other/empty.png", (255, 0, 0), (tile_size * 2, tile_size * 2))}
tile_images['road'].set_alpha(150)
player, level_x, level_y = generate_level(load_level('data/levels/city.dat'))
fps = 60
'''a = PoisonShop(0, 0)
a.enter(player)'''
running = True
clock = pygame.time.Clock()
pos = (0, 0)
camera = Camera()
camera.update(player)
Button(width - 35, 0, 35, 35, load_image("data/other/exit_button.png", colorkey=(0, 0, 255)), test,
       button_group, buildings_group)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for btn in button_group:
                btn.check_selection(pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for btn in button_group:
                if btn.rect.collidepoint(pos):
                    btn.run()
    data = pygame.key.get_pressed()
    player.set_moving(False)
    if data[119]:
        player.move_point(pos, True)
        player.set_moving(True)
    elif data[115]:
        player.move_point(pos, False)
        player.set_moving(Tile)
    elif data[101]:
        if door:
            door.enter(player)
    screen.fill((0, 0, 0))
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.update(pos)
    all_sprites.draw(screen)
    button_group.draw(screen)
    buildings_group.draw(screen)
    player_group.draw(screen)
    if text:
        screen.blit(text, (0, height - 30))
    screen.blit(render_info(player, screen), (0, 0))
    pygame.display.flip()
    clock.tick(fps)
