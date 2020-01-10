import pygame
from abc import abstractmethod, ABC

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
trap_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
text = None
door = None

# money, health
player_params = []


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
                if level[0][0] == 'w':
                    Tile('floor_4', x, y)
                else:
                    Tile('road', x, y)
                new_player = Player(x, y, all_sprites, player_group)
            elif level[y][x] == '1':
                PotionShop(x, y)
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
            elif level[y][x] == 't':
                Trap(x, y, all_sprites, trap_group)
            elif level[y][x] == 'm':
                Tile('green_wall', x, y)
            elif level[y][x] == 'w':
                Tile('wall', x, y)
            elif level[y][x] == 'b':
                Tile('dark', x, y)
            elif level[y][x] == 'c':
                # Tile('green_wall', x, y)
                Tile('coin', x, y)
            elif level[y][x] == '7':
                Tile('floor_2', x, y)
            elif level[y][x] == '8':
                Tile('floor_3', x, y)
            elif level[y][x] == '9':
                Tile('floor_4', x, y)
            elif level[y][x] == 'e':
                Goblin(x, y, enemy_group, all_sprites)
                Tile('green_wall_2', x, y)

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


class Building(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y, *groups):
        groups = list(groups)
        groups.extend([all_sprites, buildings_group])
        super().__init__(groups)
        self.image = tile_images[type]
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * tile_size
        self.rect.y = pos_y * tile_size
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step, self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step * 2, self.rect.h + building_collide_step * 2)
        self.name = 'not stated'

    def is_obstacle(self):
        return True

    def enter(self, player):
        pass


# единица отрисовки в магазине
# notice the way i work with prod. I call get_disc() and so on
class Product(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, w, h, prod, *groups):
        super().__init__(groups)
        # prod - object we can buy
        self.image = pygame.transform.scale(prod.get_image(), (w, h))
        self.disc = prod.get_disc()
        self.price = prod.get_price()
        self.name = prod.get_name()
        # example
        """self.prod = prod
        self.disc = '123\n456\n\n789'
        self.price = 456
        self.name = 'the first product
        self.image = pygame.transform.scale(tile_images["empty"], (w, h))"""
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.rect.w, self.rect.h = pos_x, pos_y, w, h

    def get_price(self):
        return self.price

    # returns sprite with black background and text information in the corner
    def show_info(self, screen):
        size = screen.get_rect()
        w, h = size.w, size.h
        new = pygame.display.set_mode((w, h))
        new.fill((0, 0, 0))

        font = pygame.font.Font(None, 50)
        text = font.render(self.name, 1, (255, 255, 255))
        new.blit(text, (500, 300))

        text = font.render('Price: ' + str(self.price), 1, (142, 176, 215))
        new.blit(text, (500, 350))

        data = self.disc.split('\n')
        font = pygame.font.Font(None, 30)
        for i in range(len(data)):
            text = font.render(data[i], 1, (142, 176, 215))
            new.blit(text, (500, 400 + i * 25))
        # this is the bigger picture of the selected item
        image_sprite = pygame.sprite.Sprite()
        # image_sprite.image = pygame.transform.scale(self.prod.image, (100, 100))
        image_sprite.image = pygame.transform.scale(self.image, (100, 100))
        image_sprite.rect = image_sprite.image.get_rect()
        image_sprite.rect.x, image_sprite.rect.y = 864, 163
        gr = pygame.sprite.Group()
        gr.add(image_sprite)
        gr.draw(new)

        info_sprite = pygame.sprite.Sprite()
        info_sprite.image = pygame.transform.scale(new, (w, h))
        info_sprite.rect = info_sprite.image.get_rect()

        return info_sprite


class PotionShop(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("poison_shop", pos_x, pos_y, groups)
        self.name = 'Poison shop'

    # enter is called when we enter he building
    def enter(self, player):
        buttons = pygame.sprite.Group()
        size = screen.get_rect()
        width, height = size.w, size.h
        fps = 60
        shop_buttons = pygame.sprite.Group()
        products = pygame.sprite.Group()
        running = True
        clock = pygame.time.Clock()
        pos = (0, 0)
        info_screen = None
        selected_prod = None
        Button(width - 50, 0, 50, 50, load_image("data/other/exit_button.png",
                                                 (0, 0, 255), (50, 50)), shop_interface_end, products, buttons)
        buy_image = render_text('Buy!')
        Button(900, 600, buy_image.get_width(), buy_image.get_height(), buy_image,
               None, buttons)
        for i in range(5):
            for j in range(5):
                heal = Potion('h+1', 200, all_sprites)
                Product(100 + i * 50, 100 + j * 50, 50, 50, heal, products)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    # if we clicked on product
                    for prod in products:
                        if prod.rect.collidepoint(pos):
                            if isinstance(prod, Product):
                                info_screen = prod.show_info(screen)
                                shop_buttons.add(info_screen)
                                selected_prod = prod
                    # if we clicked on button
                    for btn in buttons:
                        if btn.rect.collidepoint(pos) and isinstance(btn, Button):
                            try:
                                running = btn.run(btn)
                            except TypeError:
                                pass
            data = pygame.key.get_pressed()
            screen.fill((0, 0, 0))
            '''if info_screen:
                info_screen.blit(screen, (0, 0))'''
            shop_buttons.draw(screen)
            products.draw(screen)
            buttons.draw(screen)
            pygame.display.flip()
            clock.tick(fps)
        # deleting all buttons
        for btn in buttons:
            shop_interface_end(btn)


class LivingHouse(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("living_house", pos_x, pos_y, groups)
        self.name = "Farmer's house"


class Shop(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("shop", pos_x, pos_y, groups)
        self.name = 'Shop'


class CathedralEasy(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("cathedral_1", pos_x, pos_y, groups)
        self.name = 'New cathedral'

    def enter(self, player):
        global delt_x, delt_y
        delt_x, delt_y = 0, 0
        player.write_params()
        for i in all_sprites:
            i.kill()
        player, level_x, level_y = generate_level(load_level('data/levels/lvl_1.dat'))
        running = True
        clock = pygame.time.Clock()
        pos = (0, 0)
        camera = Camera()
        camera.update(player)
        Button(width - 35, 0, 35, 35, load_image("data/other/exit_button.png", colorkey=(0, 0, 255)), lambda: False,
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
                            running = btn.run()
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
            for trap in trap_group:
                if trap.rect.colliderect(player.rect):
                    player.get_damage(trap.get_damage())
            screen.fill((0, 0, 0))
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            all_sprites.update(pos)
            for enemy in enemy_group:
                enemy.move_point(player.get_coords())
                if enemy.rect.colliderect(player.rect):
                    player.get_damage(enemy.get_damage())
                    enemy.hit()
            all_sprites.draw(screen)
            button_group.draw(screen)
            buildings_group.draw(screen)
            trap_group.draw(screen)
            enemy_group.draw(screen)
            player_group.draw(screen)
            if text:
                screen.blit(text, (0, height - 30))
            screen.blit(render_info(player, screen), (0, 0))
            pygame.display.flip()
            clock.tick(fps)


class CathedralHard(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("cathedral_2", pos_x, pos_y, groups)
        self.name = 'Old cathedral'


class BigHouse(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("big_house", pos_x, pos_y, groups)
        self.name = "Old Whateley's house"


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        try:
            obj.col_rect.x += self.dx
            obj.col_rect.y += self.dy
        except AttributeError:
            pass

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Goblin(pygame.sprite.Sprite):
    step = 1

    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.frames = {'left': [], 'right': [], 'back': [], 'forward': []}
        # self.cut_sheet(load_image("data/characters/player_right.png", colorkey=(255, 0, 0)), 9, 1)
        self.frame_num = 0
        for i in range(5):
            self.frames["left"].append(load_image(f'data/characters/goblin_left_{str(i + 1)}.png',
                                                  colorkey=(255, 0, 0), size=(tile_size, tile_size)))
        for i in range(5):
            self.frames["right"].append(load_image(f'data/characters/goblin_right_{str(i + 1)}.png',
                                                   colorkey=(255, 0, 0), size=(tile_size, tile_size)))

        # self.image = self.frames[self.frame_num]
        self.image = self.frames['right'][self.frame_num]
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_size + delt_x
        self.rect.y = y * tile_size + delt_y
        self.prev_coords = self.get_coords()
        self.num = 0
        self.pos = (self.rect.x + 1, self.rect.y)
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step, self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step, self.rect.h + building_collide_step)
        self.health = 100
        self.damage = 20

        self.hit_mode = False
        self.hit_counter = 0

    def get_damage(self):
        if self.hit_mode:
            return 0
        return self.damage

    def get_health(self):
        return self.health

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def get_coords(self):
        return (self.get_x(), self.get_y())

    def move_point(self, pos):
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        self.rect.x += 0.01 * (Player.step * x - self.rect.x)
        self.rect.y += 0.01 * (Player.step * y - self.rect.y)

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def hit(self):
        self.hit_mode = True

    def update(self, pos):
        '''self.pos = pos
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        self.rect.x += 0.001 * (Player.step * x - self.rect.x)
        self.rect.y += 0.001 * (Player.step * y - self.rect.y)

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]
'''
        x = self.pos[0]
        self.num += 1
        if self.num == 16:
            self.frame_num = (self.frame_num + 1) % (len(self.frames['left']) - 2)
            if x > self.rect.x:
                self.image = self.frames['right'][self.frame_num]
            else:
                self.image = self.frames['left'][self.frame_num]
            self.num = 1
        if self.hit_mode:
            self.hit_counter += 1

        if self.hit_counter < 100 and self.hit_mode:
            if x > self.rect.x:
                self.image = self.frames['right'][4]
            else:
                self.image = self.frames['left'][4]

        if self.hit_counter > 100 and self.hit_mode:
            self.hit_mode = False
            self.hit_counter = 0

    def is_obstacle(self):
        return False


# notice new methods of getting helth, money, rect
# notice new attributes (money, health)
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
        self.money = 0

        self.load_params()

    # notice calls of expected classes Weapon nd Poison
    def load_params(self):
        global player_params
        if player_params:
            self.money = player_params[0]
            self.health = player_params[1]

    def write_params(self):
        global player_params
        player_params = [self.money, self.health]

    def add_product(self, prod):
        if isinstance(prod, Weapon):
            self.weapons.append(prod)
        elif isinstance(prod, Potion):
            self.poisons.append(prod)
        return True

    def get_damage(self, damage):
        self.health -= damage

    def change_money(self, amount):
        prev = self.money
        self.money += amount
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
        if self.num == 8:
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

    def is_obstacle(self):
        return False


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
        if type == 'coin':
            self.value = 1000
        else:
            self.value = 0

    def get_value(self):
        return self.value

    def is_obstacle(self):
        if self.type in ['road', 'grass', 'roof', 'floor_4', 'floor_3', 'floor_2', 'coin', 'green_wall_2']:
            return False
        return True


class Trap(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__(groups)
        self.image = tile_images['green_wall']
        self.image.blit(tile_images['trap'], (0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos_x * tile_size, pos_y * tile_size
        self.damage = 2
        self.tick_num = 0
        self.damage_each = 10

    def get_damage(self):
        self.tick_num += 1
        if self.tick_num > self.damage_each:
            self.tick_num = 0
            return self.damage
        return 0

    def is_obstacle(self):
        return False


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


class Item(pygame.sprite.Sprite):
    def change_image(self, image, image_size=200):
        self._img = image
        self.image = pygame.Surface((image_size,) * 2)
        self.rect = self.image.get_rect()
        image = resize_image(image, int(image_size * 0.6))
        x = image.get_rect().w
        self.image.blit(image, ((image_size - x) // 2, int(image_size * 0.2)))
        pygame.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 3)

        size = 1
        font = pygame.font.Font(None, size)
        text_label = font.render(self.text, 1, (0, 255, 0))
        price_label = font.render(str(self.price), 1, (0, 255, 0))

        while text_label.get_rect().w <= image_size and price_label.get_rect().h <= image_size * 0.18 and price_label.get_rect().w <= image_size and text_label.get_rect().h <= image_size * 0.18:
            size += 1
            font = pygame.font.Font(None, size)
            text_label = font.render(self.text, 1, (0, 255, 0))
            price_label = font.render(str(self.price), 1, (0, 255, 0))

        font = pygame.font.Font(None, size - 1)
        text_label = font.render(self.text, 1, (0, 255, 0))
        self.image.blit(text_label, (int((image_size - text_label.get_rect().w) / 2), 1))

        price_label = font.render(str(self.price), 1, (0, 255, 0))
        self.image.blit(price_label, (int((image_size - price_label.get_rect().w) / 2), int(image_size * 0.8) + 6))

    def get_image(self):
        return self._img

    def get_name(self):
        return self.name

    def get_disc(self):
        return self.disc

    def get_price(self):
        return self.price

    def is_obstacle(self):
        return True


class Potion(Item):
    # Базовые усиления
    heal = 25
    speed = 2
    damage = 1

    def __init__(self, title, price, *groups):
        super().__init__(groups)
        effects = title.split('+')
        if len(effects) == 2:
            self.coof = (int(effects[1]) + 1)
        else:
            self.coof = 1
        self.effect = effects[0]

        self.price = price
        if self.effect == 'h':
            image = load_image(r'data\potions\healing_potion.png', -1)
            self.text = 'Зелье Лечения' + (f' +{self.coof - 1}' if self.coof > 1 else '')
            self.disc = f'Лечит на {int(self.heal * ((self.coof + 1) / 2))} HP'
        elif self.effect == 's':
            image = load_image(r'data\potions\speed_potion.png', -1)
            self.text = 'Зелье Скорости' + (f' +{self.coof - 1}' if self.coof > 1 else '')
            self.disc = f'Ускоряет персонажа в {int(self.speed * ((self.coof + 1) / 2))} раз'
        elif self.effect == 'd':
            image = load_image(r'data\potions\damage_potion.png', -1)
            self.text = 'Зелье Урона' + (f' +{self.coof - 1}' if self.coof > 1 else '')
            self.disc = f'Увеличивает урон персонажа в {int(self.damage + ((self.coof + 9) / 10))} раз'
        else:
            raise ValueError('Effect must be "h"eal, "s"peed or "d"amage, with +"int" or without')
        self.name = self.text
        self.change_image(image)

    def do_effect(self, player):
        if self.effect == 'h':
            player.set_health(player.get_health() + int(self.heal * ((self.coof + 1) / 2)))
        elif self.effect == 's':
            player.set_speed(player.get_speed() + int(self.speed * (self.coof / 2 + 1)))
        elif self.effect == 'd':
            player.set_damage_boost(player.get_damage_boost() + int(self.damage + ((self.coof + 9) / 10)))
        self.kill()


class Weapon(Item):
    def __init__(self, title, damage, price, number=0, *groups):
        super().__init__(*groups)
        self.damage = damage
        self.price = price
        self.clock = pygame.time.Clock()
        self.timer = 0

        def decorator(func):
            return func

        if title == 'g':  # Граната
            self.firerate = 0
            self.name = 'Граната'
            self.text = self.name
            self.change_image(load_image(r'data\weapons\grenade.png'))

            def decorator(func):
                def function(self, *args, **kwargs):
                    func(self, *args, **kwargs)
                    self.kill()

            self.do_damage = decorator(self.do_damage)

        elif title == 'r':  # AK-47
            self.name = 'АК-47'
            self.text = self.name
            self.firerate = 50
            self.change_image(load_image(r'data\weapons\rifle.png'))
        elif title == 'sr':  # Снайперская винтовка
            self.name = 'Снайперская винтовка'
            self.text = self.name
            self.firerate = 5000
            self.change_image(load_image(r'data\weapons\sniper_rifle.png'))
        elif title == 'k':  # Нож
            self.name = 'Нож'
            self.text = self.name
            self.firerate = 1000
            self.change_image(load_image(r'data\weapons\knife.png'))
        elif title == 'p':  # Пистолет
            self.name = 'Пистолет'
            self.text = self.name
            self.firerate = 500
            self.change_image(load_image(r'data\weapons\pistol.png'))
        else:
            raise ValueError('There is not weapon with this title.')

    def do_damage(self, pos):
        self.timer += self.clock.tick()
        if self.timer >= self.firerate:
            self.timer = 0
            for sprite in enemies:  # Группа спрайтов с врагами
                if sprite.rect.collidepoint(pos):
                    sprite.get_damage(self.damage)  # У врагов должна быть функция get_damage(damage)


def cut_sheet(sheet, columns, rows, number=0):
    rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                       sheet.get_height() // rows)
    frames = []
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, rect.size)))
    if frames:
        return frames[number:number + 1][0]
    raise ValueError('Number is bigger than possible sprite')


def resize_image(image, biggest_side):
    x, y = image.get_rect().w, image.get_rect().h
    prop = biggest_side / max((x, y))
    return pygame.transform.scale(image, (int(x * prop), int(y * prop)))


def distance(coords_1, coords_2):
    x1, y1 = coords_1
    x2, y2 = coords_2
    dist = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    return dist


def check_collisions(obj):
    global text
    a = None
    del_objects = []
    for sprite in all_sprites:
        if id(sprite) == id(obj):
            continue
        if sprite.rect.colliderect(obj.rect):
            if isinstance(obj, Player) and isinstance(sprite, Tile) and sprite.type == 'coin':
                obj.change_money(sprite.get_value())
                sprite.kill()
            if sprite.is_obstacle():
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


# KOSTIL))   deleting buttons after shop interface
def shop_interface_end(*args):
    args[0].kill()
    return False


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
               "empty": load_image("data/other/empty.png", (255, 0, 0), (tile_size * 2, tile_size * 2)),
               "coin": load_image("data/textures/coin.png", (255, 0, 0), (tile_size, tile_size)),
               "floor_4": load_image("data/textures/floor_4.png", (255, 0, 0), (tile_size, tile_size)),
               "floor_3": load_image("data/textures/floor_3.png", (255, 0, 0), (tile_size, tile_size)),
               "floor_2": load_image("data/textures/floor_2.png", (255, 0, 0), (tile_size, tile_size)),
               "wall": load_image("data/textures/wall.png", (255, 0, 0), (tile_size, tile_size)),
               "green_wall": load_image("data/textures/green_wall.png", (255, 0, 0), (tile_size, tile_size)),
               "dark": load_image("data/textures/eye.png", (255, 0, 0), (tile_size, tile_size)),
               "trap": load_image("data/textures/trap.png", (255, 0, 0), (tile_size, tile_size)),
               'green_wall_2': load_image("data/textures/green_wall.png", (255, 0, 0), (tile_size, tile_size))
               }
tile_images['road'].set_alpha(150)
player, level_x, level_y = generate_level(load_level('data/levels/city.dat'))
fps = 60
'''a = PotionShop(0, 0)
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
