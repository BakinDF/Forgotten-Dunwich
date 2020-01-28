import pygame
import sys
import traceback
from copy import deepcopy
import os
import time

from random import randint, choice, shuffle, random


def hook(*args, **kwargs):
    traceback.print_last()
    input()


sys.excepthook = hook
pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
tile_size = 125
building_collide_step = 75
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
potionshop_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
player_info_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

exit_group = pygame.sprite.Group()

weapon_group = pygame.sprite.Group()
potion_group = pygame.sprite.Group()

text = None
door = None
delt = None
# money, health
player_params = []
city_pos = None

sprites_size = 100
small_eps = 5
eps = 70

# damage, firetime, price
weapon_data = {'g': [1000, 3600000, 5000], 'r': [50, 500, 12000],
               'sr': [100, 1500, 15000], 'k': [40, 2000, 5000],
               'p': [50, 700, 7000]}

main_track = pygame.mixer.Sound('data/music/fight_shadow.wav')
main_track.play(-1)
main_track.set_volume(0.5)
fight_theme = pygame.mixer.Sound('data/music/fight_theme.wav')
shoot_sound = pygame.mixer.Sound('data/music/shoot.wav')
scream_sound = pygame.mixer.Sound('data/music/scream.wav')


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
                Tile('coin_grass', x, y)
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
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step,
                                    self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step * 2,
                                    self.rect.h + building_collide_step * 2)
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
        self.prod = prod
        # example
        """self.disc = '123\n456\n\n789'
        self.price = 456
        self.name = 'the first product
        self.image = pygame.transform.scale(tile_images["empty"], (w, h))"""
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.rect.w, self.rect.h = pos_x, pos_y, w, h

    def get_price(self):
        return self.price

    # returns sprite with black background and text information in the corner
    def show_info(self, screen, group):
        size = screen.get_rect()
        w, h = size.w, size.h
        new = pygame.Surface((w, h))
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

        info_sprite = pygame.sprite.Sprite(group)
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
                                                 (0, 0, 255), (50, 50)), shop_interface_end,
               products, buttons)

        buy_image = render_text('Buy!')
        Button(900, 600, buy_image.get_width(), buy_image.get_height(), buy_image,
               buy_function, buttons)

        # Сгенерировать предметы
        order = 'hsd'
        for i in range(5):
            for j in range(3):
                potion = Potion(f'{order[j]}{"+" + str(i) if i else ""}', 200, potionshop_group)
                Product(100 + i * 50, 100 + j * 50, 50, 50, potion, products)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    # if we clicked on product
                    for prod in products:
                        if prod.rect.collidepoint(pos):
                            if isinstance(prod, Product):
                                info_screen = prod.show_info(screen, shop_buttons)
                                shop_buttons.add(info_screen)
                                selected_prod = prod

                    # if we clicked on button
                    for btn in buttons:
                        if btn.rect.collidepoint(pos) and isinstance(btn, Button):
                            if btn.func is shop_interface_end:
                                try:
                                    running = btn.run(btn)
                                except TypeError:
                                    pass
                            elif btn.func is buy_function:
                                btn.run(player, selected_prod, info_screen)

            screen.fill((0, 0, 0))
            shop_buttons.draw(screen)
            products.draw(screen)
            buttons.draw(screen)

            coins = render_text(f'Coins: {player.get_money()}')
            screen.blit(coins, (20, 20))

            pygame.display.flip()
            clock.tick(fps)

        # deleting all buttons
        for btn in buttons:
            shop_interface_end(btn)
        player.write_params()
        potionshop_group.empty()


class LivingHouse(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("living_house", pos_x, pos_y, groups)
        self.name = "Farmer's house"


class Shop(Building):
    def __init__(self, pos_x, pos_y, *groups):
        super().__init__("shop", pos_x, pos_y, groups)
        self.name = 'Shop'

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
                                                 (0, 0, 255), (50, 50)), shop_interface_end,
               products, buttons)

        buy_image = render_text('Buy!')
        Button(900, 600, buy_image.get_width(), buy_image.get_height(), buy_image,
               buy_function, buttons)

        # Сгенерировать предметы
        order = ['g', 'r', 'sr', 'k', 'p']
        for i in range(5):
            potion = Weapon(f'{order[i]}', potionshop_group)
            Product(100 + i * 50, 100, 50, 50, potion, products)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    # if we clicked on product
                    for prod in products:
                        if prod.rect.collidepoint(pos):
                            if isinstance(prod, Product):
                                info_screen = prod.show_info(screen, shop_buttons)
                                shop_buttons.add(info_screen)
                                selected_prod = prod

                    # if we clicked on button
                    for btn in buttons:
                        if btn.rect.collidepoint(pos) and isinstance(btn, Button):
                            if btn.func is shop_interface_end:
                                try:
                                    running = btn.run(btn)
                                except TypeError:
                                    pass
                            elif btn.func is buy_function:
                                btn.run(player, selected_prod, info_screen)

            screen.fill((0, 0, 0))
            shop_buttons.draw(screen)
            products.draw(screen)
            buttons.draw(screen)

            coins = render_text(f'Coins: {player.get_money()}')
            screen.blit(coins, (20, 20))

            pygame.display.flip()
            clock.tick(fps)

        # deleting all buttons
        for btn in buttons:
            shop_interface_end(btn)
        player.write_params()
        potionshop_group.empty()


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
        Button(width - 35, 0, 35, 35,
               load_image("data/other/exit_button.png", colorkey=(0, 0, 255)), lambda: False,
               button_group, buildings_group)
        main_track.fadeout(2000)
        fight_theme.play(-1)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    for btn in button_group:
                        btn.check_selection(pos)
                        player.write_params()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    player.shoot(pos)
                    for btn in button_group:
                        if btn.rect.collidepoint(pos):
                            running = False


                elif event.type == pygame.KEYDOWN:
                    for i in tuple(range(54, 69)) + (48,):
                        if event.key == i:
                            player.use_potion(i - 54)
                            break

            data = pygame.key.get_pressed()
            player.set_moving(False)
            if data[119]:
                player.move_up()
                # player.move_point(pos, True)
                player.set_moving(True)
            if data[115]:
                player.move_down()
                # player.move_point(pos, False)
                player.set_moving(Tile)
            if data[97]:
                player.move_left()
                # player.move_point(pos, False)
                player.set_moving(Tile)

            for i in range(49, 55):
                if data[i]:
                    player.equip_weapon(i - 49)
                    break

            if data[100]:
                player.move_right()
                # player.move_point(pos, False)
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
            all_sprites.draw(screen)
            weapon_group.draw(screen)
            potion_group.draw(screen)
            for enemy in enemy_group:
                enemy.move_point(player.get_coords())
                if enemy.rect.colliderect(player.rect):
                    player.get_damage(enemy.get_damage())
                    enemy.hit()
                screen.blit(enemy.health_bar, (enemy.rect.x, enemy.rect.y - 25))
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

            if player.get_health() <= 0:
                exit_game()

        fight_theme.fadeout(2000)
        time.sleep(2.0)
        main_track.play(-1)


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
        if isinstance(obj, Tile):
            obj.move(self.dx, self.dy)
        else:
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
    speed = 1
    size_decrease = 50
    cell_mid = -25
    col_delt = 20
    moving_eps = 600

    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.frames = {'left': [], 'right': [], 'back': [], 'forward': []}
        # self.cut_sheet(load_image("data/characters/player_right.png", colorkey=(255, 0, 0)), 9, 1)
        self.frame_num = 0
        for i in range(5):
            self.frames["left"].append(load_image(f'data/characters/goblin_left_{str(i + 1)}.png',
                                                  colorkey=(255, 0, 0), size=(
                    tile_size - Goblin.size_decrease, tile_size - Goblin.size_decrease)))
        for i in range(5):
            self.frames["right"].append(load_image(f'data/characters/goblin_right_{str(i + 1)}.png',
                                                   colorkey=(255, 0, 0), size=(
                    tile_size - Goblin.size_decrease, tile_size - Goblin.size_decrease)))

        # self.image = self.frames[self.frame_num]
        self.image = self.frames['right'][self.frame_num]
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_size
        self.rect.y = y * tile_size
        self.prev_coords = self.get_coords()
        self.num = 0
        self.pos = (self.rect.x + 1, self.rect.y)
        self.col_rect = pygame.Rect(self.rect.x + Goblin.col_delt, self.rect.y + Goblin.col_delt,
                                    self.rect.w - Goblin.col_delt, self.rect.h - Goblin.col_delt)
        self.health = 100
        self.damage = 20

        self.hit_mode = False
        self.hit_counter = 0

        self.target = None
        self.health_bar = render_text(f'Health: {self.health}', 20)

        self.moving = True
        self.moving_num = 0

    def get_damage(self):
        if self.hit_mode:
            return 0
        return self.damage

    def receive_damage(self, damage):
        self.health -= damage
        self.health_bar = render_text(f'Health: {self.health}', 20)
        if self.health <= 0:
            self.kill()

    def get_health(self):
        return self.health

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def get_coords(self):
        return (self.get_x(), self.get_y())

    def set_health(self, health):
        self.health = health

    def move_point(self, pos):
        if not self.target:
            way = find_path('data/levels/lvl_1.dat', *get_cell(*self.get_coords()),
                            *get_cell(*player.get_coords()))[1:]
            if not way:
                return
            for i in range(len(way)):
                way[i] = way[i][::-1]
            if len(way) > 1:
                self.target = (
                    way[1][0] * tile_size + Goblin.cell_mid, way[1][1] * tile_size + Goblin.cell_mid)
        else:
            goblin_coords = self.get_x() - delt[0], self.get_y() - delt[1]
            target_coords = self.target
            dist = distance(goblin_coords, target_coords)
            if dist < eps:
                self.target = None
        if self.target:
            prob = random()
            if prob < 0.00709:
                self.moving = False
                self.moving_num = 0
            if (not self.moving and self.moving_num > 10) or self.moving:
                self.moving = True
                goblin_coords = self.get_x() - delt[0], self.get_y() - delt[1]
                target_coords = player.get_x() - delt[0], player.get_y() - delt[1]
                dist = distance(goblin_coords, target_coords)
                if dist < Goblin.moving_eps:
                    x, y = self.target
                    x, y = x + delt[0], y + delt[1]
                    self.prev_coords = self.get_coords()
                    self.rect.x += 0.02 * (Goblin.speed * x - self.rect.x) + randint(0, 2)
                    self.rect.y += 0.02 * (Goblin.speed * y - self.rect.y) + randint(0, 2)

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
        self.rect.x += 0.001 * (Player.speed * x - self.rect.x)
        self.rect.y += 0.001 * (Player.speed * y - self.rect.y)

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]
'''
        x = player.get_x()
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
        self.moving_num += 1

    def is_obstacle(self):
        return False


# notice new methods of getting helth, money, rect
# notice new attributes (money, health)
class Player(pygame.sprite.Sprite):
    speed = 10
    damage_boost = 1

    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.frames = {'left': [], 'right': [], 'back': [], 'forward': []}
        # self.cut_sheet(load_image("data/characters/player_right.png", colorkey=(255, 0, 0)), 9, 1)
        self.frame_num = 0
        for i in range(9):
            if i == 0:
                self.frames["left"].append(
                    load_image(f'data/characters/player_left_{str(i + 1)}.png',
                               colorkey=(237, 28, 36)))
            else:
                self.frames["left"].append(
                    load_image(f'data/characters/player_left_{str(i + 1)}.png',
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
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step,
                                    self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step,
                                    self.rect.h + building_collide_step)
        self.health = 100
        self.potions = []
        self.weapons = []
        self.current_weapon = None
        self.money = 0
        self.potion_group = pygame.sprite.Group()

        self.load_params()

    # notice calls of expected classes Weapon nd Potion
    def load_params(self):
        global player_params
        if player_params:
            self.money, self.health, self.weapons, self.potions, self.current_weapon = player_params

    def write_params(self):
        global player_params
        player_params = [self.money, self.health, self.weapons, self.potions, self.current_weapon]

    def add_product(self, prod):
        prod.change_image(prod._img, image_size=sprites_size)
        if isinstance(prod, Weapon):
            self.weapons.append(prod)
            weapon_group.add(prod)
            self.equip_weapon(self.weapons.index(prod))
        elif isinstance(prod, Potion):
            prod.change_image(prod._img, image_size=sprites_size)
            self.potions.append(prod)
            potion_group.add(prod)
            self.change_potions(screen.get_rect().w - sprites_size - 35, 35, 10)
        return True

    def shoot(self, pos):
        if self.current_weapon:
            self.current_weapon.do_damage(pos, self.damage_boost)

    def move_left(self):
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        self.rect.x -= Player.speed

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def move_right(self):
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        self.rect.x += Player.speed

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def move_up(self):
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        self.rect.y -= Player.speed

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def move_down(self):
        x, y = pos
        self.pos = pos
        dist = distance(pos, (self.rect.x, self.rect.y))
        self.prev_coords = self.get_coords()
        self.rect.y += Player.speed

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def get_damage(self, damage):
        scream_sound.play(0)
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
            self.rect.x += 0.01 * (Player.speed * x - self.rect.x)
            self.rect.y += 0.01 * (Player.speed * y - self.rect.y)
        elif not forward:
            self.rect.x -= 0.01 * (Player.speed * x - self.rect.x)
            self.rect.y -= 0.01 * (Player.speed * y - self.rect.y)

        if check_collisions(self):
            self.rect.x = self.prev_coords[0]
            self.rect.y = self.prev_coords[1]

    def equip_weapon(self, num):
        if self.weapons[num:num + 1]:
            self.current_weapon = self.weapons[num]
            self.change_weapons(20, screen.get_rect().h - sprites_size - 50, 10)

    def set_health(self, hp):
        self.health = hp

    def change_weapons(self, x, y, spaces):
        last_x = x
        for weapon in self.weapons:
            if weapon is self.current_weapon:
                weapon.change_image(weapon._img, (0, 255, 0), image_size=sprites_size)
            else:
                weapon.change_image(weapon._img, image_size=sprites_size)
            weapon.rect.x, weapon.rect.y = last_x, y
            last_x += (weapon.rect.w + spaces)

    def use_potion(self, num):
        if num == -6:
            num = 4
        if -1 < num < 5:
            try:
                self.potions[num].do_effect(self)
                self.potions[num].kill()
                del self.potions[num]
                self.change_potions(screen.get_rect().w - sprites_size - 35, 35, 10)
            except IndexError:
                pass

    def change_potions(self, x, y, spaces):
        last_y = y
        for potion in self.potions:
            potion.rect.x, potion.rect.y = x, last_y
            last_y += (potion.rect.h + spaces)

    def get_speed(self):
        return self.speed

    def set_speed(self, speed):
        self.speed = speed

    def get_damage_boost(self):
        return self.damage_boost

    def set_damage_boost(self, boost):
        self.damage_boost = boost

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
        self.first = False
        if pos_x == 0 and pos_y == 0:
            self.first = True
        groups = list(groups)
        groups.append(all_sprites)
        super().__init__(groups)
        self.type = type
        self.image = tile_images[type]
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * tile_size
        self.rect.y = pos_y * tile_size
        self.pos = (pos_x, pos_y)
        self.col_rect = pygame.Rect(self.rect.x - building_collide_step,
                                    self.rect.y - building_collide_step,
                                    self.rect.w + building_collide_step,
                                    self.rect.h + building_collide_step)
        if type == 'coin_grass':
            self.value = 1000
        else:
            self.value = 0

    def get_pos(self):
        return self.pos

    def get_value(self):
        return self.value

    def is_obstacle(self):
        if self.type in ['road', 'grass', 'roof', 'floor_4', 'floor_3', 'floor_2', 'coin_grass',
                         'green_wall_2']:
            return False
        return True

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        if self.first:
            global delt
            delt = list((self.rect.x, self.rect.y))


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
    def change_image(self, image, color=(255, 255, 255), image_size=200):
        self.image = pygame.Surface((image_size,) * 2)
        self.rect = self.image.get_rect()
        image = resize_image(image, int(image_size * 0.6))
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
        x = image.get_rect().w
        self.image.blit(image, ((image_size - x) // 2, int(image_size * 0.2)))
        pygame.draw.rect(self.image, color, self.image.get_rect(), 3)

        size = 1
        font = pygame.font.Font(None, size)
        text_label = font.render(self.text, 1, color)
        price_label = font.render(str(self.disc), 1, color)

        while text_label.get_rect().w <= image_size and price_label.get_rect().h <= image_size * 0.18 and price_label.get_rect().w <= image_size and text_label.get_rect().h <= image_size * 0.18:
            size += 1
            font = pygame.font.Font(None, size)
            text_label = font.render(self.text, 1, color)
            price_label = font.render(str(self.disc), 1, color)

        font = pygame.font.Font(None, size - 1)
        text_label = font.render(self.text, 1, color)
        self.image.blit(text_label, (int((image_size - text_label.get_rect().w) / 2), 1))

        price_label = font.render(str(self.disc), 1, color)
        self.image.blit(price_label, (
            int((image_size - price_label.get_rect().w) / 2), int(image_size * 0.8) + 6))
        self.image.set_colorkey((0, 0, 0))

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
    speed = 0.5
    damage = 0.5

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
            self.disc = f'{int(self.heal * ((self.coof + 1) / 2))} HP'
        elif self.effect == 's':
            image = load_image(r'data\potions\speed_potion.png', -1)
            self.text = 'Зелье Скорости' + (f' +{self.coof - 1}' if self.coof > 1 else '')
            self.disc = f'Уск. в {self.speed + ((self.coof + 2) / 3)} раз'
        elif self.effect == 'd':
            image = load_image(r'data\potions\damage_potion.png', -1)
            self.text = 'Зелье Урона' + (f' +{self.coof - 1}' if self.coof > 1 else '')
            self.disc = f'Увел. урон ' \
                        f'в {self.damage + ((self.coof + 9) / 10)} раз'
        else:
            raise ValueError('Effect must be "h"eal, "s"peed or "d"amage, with +"int" or without')
        self.name = self.text
        self._img = image

    def do_effect(self, player):
        if self.effect == 'h':
            player.set_health(player.get_health() + int(self.heal * ((self.coof + 1) / 2)))
        elif self.effect == 's':
            player.set_speed(player.get_speed() + self.speed + ((self.coof + 2) / 3))
        elif self.effect == 'd':
            player.set_damage_boost(
                player.get_damage_boost() + self.damage + ((self.coof + 9) / 10))
        self.kill()


class Weapon(Item):
    def __init__(self, title, number=0, *groups):
        super().__init__(*groups)
        self.damage, self.firerate, self.price = weapon_data[title]
        self.clock = pygame.time.Clock()
        self.timer = self.firerate

        def decorator(func):
            return func

        if title == 'g':  # Граната
            self.name = 'Граната'
            self.text = self.name
            self._img = load_image(r'data\weapons\grenade.png')

        elif title == 'r':  # AK-47
            self.name = 'АК-47'
            self.text = self.name
            self._img = load_image(r'data\weapons\rifle.png')
        elif title == 'sr':  # Снайперская винтовка
            self.name = 'Снайперская винтовка'
            self.text = self.name
            self._img = load_image(r'data\weapons\sniper_rifle.png')
        elif title == 'k':  # Нож
            self.name = 'Нож'
            self.text = self.name
            self._img = load_image(r'data\weapons\knife.png')
        elif title == 'p':  # Пистолет
            self.name = 'Пистолет'
            self.text = self.name
            self._img = load_image(r'data\weapons\pistol.png')
        else:
            raise ValueError('There is not weapon with this title.')
        self.disc = f"Наносит {self.damage} урона."

    def do_damage(self, pos, boost):
        self.timer += self.clock.tick()
        if self.timer >= self.firerate:
            shoot_sound.play(0)
            self.timer = 0
            for sprite in enemy_group:  # Группа спрайтов с врагами
                if sprite.rect.collidepoint(pos):
                    sprite.receive_damage(int(
                        self.damage * boost))  # У врагов должна быть функция receive_damage(damage)


class Logo(pygame.sprite.Sprite):
    image = load_image("data/other/game_over.png", None, (width, height))

    def __init__(self, *groups):
        super().__init__(groups)
        self.image = Logo.image
        self.rect = Logo.image.get_rect()
        self.rect.x = -self.rect.w
        self.action = True

    def update(self, *args):
        if self.action:
            self.rect.x += 1
            if self.rect.x >= 0:
                self.rect.x = 0
                self.action = False


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
    if isinstance(obj, Goblin):
        return False
    for sprite in all_sprites:
        if id(sprite) == id(obj):
            continue
        if sprite.rect.colliderect(obj.rect):
            if isinstance(obj, Player) and isinstance(sprite, Tile) and sprite.type == 'coin_grass':
                obj.change_money(sprite.get_value())
                a = Tile('grass', *sprite.get_pos())
                a.rect.x += delt[0]
                a.rect.y += delt[1]
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
        if sprite.is_obstacle() and sprite.col_rect.colliderect(obj.rect) and not isinstance(sprite,
                                                                                             Tile):
            font = pygame.font.Font(None, 50)
            text = font.render("[E] - enter " + sprite.name, 1, (47, 213, 175))
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - text.get_height() // 2
            # screen.blit(text, (text_x, text_y))
            door = sprite
            return
    door = None
    text = None


def find_path(path, x1, y1, x2, y2):
    file = open(path, mode='r', encoding='utf-8')
    data = [list(i[:-1]) for i in file.readlines()]
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] in 'wmb':
                data[i][j] = -1
            else:
                data[i][j] = 0
    lest = deepcopy(data)
    height = len(lest)
    width = len(lest[0])
    if x1 < height and y1 < width:
        lest[x1][y1] = 1
    if x1 < height and y1 < width:
        lest[x2][y2] = 0
    wave = True
    while wave and lest[x2][y2] == 0:
        wave = False
        for i in range(height - 1):
            for j in range(width - 1):
                if lest[i][j] not in [0, -1]:
                    if 0 <= i - 1 < height:
                        if lest[i - 1][j] == 0:
                            lest[i - 1][j] = lest[i][j] + 1
                            wave = True
                    if 0 <= i + 1 < height:
                        if lest[i + 1][j] == 0:
                            lest[i + 1][j] = lest[i][j] + 1
                            wave = True
                    if 0 <= j - 1 < width:
                        if lest[i][j - 1] == 0:
                            lest[i][j - 1] = lest[i][j] + 1
                            wave = True
                    if 0 <= j + 1 < width:
                        if lest[i][j + 1] == 0:
                            lest[i][j + 1] = lest[i][j] + 1
                            wave = True
    path_lest = []
    if lest[x2][y2] != 0:
        x, y = x2, y2
        path_lest.append((x2, y2))
        while lest[x][y] != 1:
            if 0 <= x - 1 < height:
                if lest[x - 1][y] == lest[x][y] - 1:
                    path_lest.append((x - 1, y))
                    x -= 1
            if 0 <= x + 1 < height:
                if lest[x + 1][y] == lest[x][y] - 1:
                    path_lest.append((x + 1, y))
                    x += 1
            if 0 <= y - 1 < width:
                if lest[x][y - 1] == lest[x][y] - 1:
                    path_lest.append((x, y - 1))
                    y -= 1
            if 0 <= y + 1 < width:
                if lest[x][y + 1] == lest[x][y] - 1:
                    path_lest.append((x, y + 1))
                    y += 1
    file.close()
    return path_lest[::-1]


def create_col_rect(obj):
    obj.col_rect = pygame.Rect(obj.rect.x - building_collide_step,
                               obj.rect.y - building_collide_step,
                               obj.rect.w + building_collide_step,
                               obj.rect.h + building_collide_step)


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
def render_text(line, size=50):
    font = pygame.font.Font(None, size)
    text = font.render(line, 1, (255, 255, 255))
    return text


def get_cell(x, y):
    pos = (((x - delt[0]) // tile_size)), ((y - delt[1]) // tile_size)
    return pos[::-1]


def get_cell_coords(w, h):
    pos = (w * tile_size + delt[0], h * tile_size + delt[1])
    return pos


def buy_function(player, chosen_product, info_screen):
    if player.change_money(-chosen_product.prod.get_price()):
        chosen_product.prod.kill()
        player.add_product(chosen_product.prod)
        chosen_product.kill()
        info_screen.kill()


def test():
    sys.exit()


def exit_game():
    Player.speed = 0
    running = True
    clock = pygame.time.Clock()
    Logo(all_sprites, exit_group)
    num = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
        exit_group.update()
        exit_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
        num += 1
        if num >= 750:
            sys.exit()


tile_images = {"road": load_image("data/textures/stone_1.png", (255, 0, 0), (tile_size, tile_size)),
               "living_house": load_image("data/houses/sleep_house.png", (255, 0, 0),
                                          (tile_size * 3, tile_size * 2)),
               "poison_shop": load_image("data/houses/poison_shop.png", (255, 0, 0),
                                         (tile_size * 3, tile_size * 2)),
               "shop": load_image("data/houses/shop_1.png", (255, 0, 0),
                                  (tile_size * 2, tile_size * 3)),
               "grass": load_image("data/textures/grass.png", (255, 0, 0), (tile_size, tile_size)),
               "fence": load_image("data/textures/roof_1.png", (255, 0, 0), (tile_size, tile_size)),
               "cathedral_1": load_image("data/houses/cathedral_1.png", (255, 0, 0),
                                         (tile_size * 5, tile_size * 3)),
               "cathedral_2": load_image("data/houses/cathedral_2.png", (255, 0, 0),
                                         (tile_size * 6, tile_size * 2)),
               "big_house": load_image("data/houses/big_house.png", (255, 0, 0),
                                       (tile_size * 3, tile_size * 4)),
               "empty": load_image("data/other/empty.png", (255, 0, 0),
                                   (tile_size * 2, tile_size * 2)),
               "coin": load_image("data/textures/coin.png", (255, 0, 0), (tile_size - 40, tile_size - 40)),
               "floor_4": load_image("data/textures/floor_4.png", (255, 0, 0),
                                     (tile_size, tile_size)),
               "floor_3": load_image("data/textures/floor_3.png", (255, 0, 0),
                                     (tile_size, tile_size)),
               "floor_2": load_image("data/textures/floor_2.png", (255, 0, 0),
                                     (tile_size, tile_size)),
               "wall": load_image("data/textures/wall.png", (255, 0, 0), (tile_size, tile_size)),
               "green_wall": load_image("data/textures/green_wall.png", (255, 0, 0),
                                        (tile_size, tile_size)),
               "dark": load_image("data/textures/eye.png", (255, 0, 0), (tile_size, tile_size)),
               "trap": load_image("data/textures/trap.png", (255, 0, 0), (tile_size, tile_size)),
               'green_wall_2': load_image("data/textures/green_wall.png", (255, 0, 0),
                                          (tile_size, tile_size)),
               "coin_grass": load_image("data/textures/grass.png", (255, 0, 0),
                                        (tile_size, tile_size))
               }
tile_images['coin_grass'].blit(tile_images['coin'], (0, 0))
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
        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for btn in button_group:
                btn.check_selection(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for btn in button_group:
                if btn.rect.collidepoint(pos):
                    btn.run()
        elif event.type == pygame.KEYDOWN:
            for i in tuple(range(54, 69)) + (48,):
                if event.key == i:
                    player.use_potion(i - 54)
                    break
    data = pygame.key.get_pressed()
    player.set_moving(False)
    if data[119]:
        player.move_up()
        # player.move_point(pos, True)
        player.set_moving(True)
    if data[115]:
        player.move_down()
        # player.move_point(pos, False)
        player.set_moving(Tile)
    if data[97]:
        player.move_left()
        # player.move_point(pos, False)
        player.set_moving(Tile)
    if data[100]:
        player.move_right()
        # player.move_point(pos, False)
        player.set_moving(Tile)

    if data[101]:
        if door:
            city_pos = player.get_coords()
            my_delt = delt[:]
            door.enter(player)
            for i in all_sprites:
                i.kill()
            player, level_x, level_y = generate_level(load_level('data/levels/city.dat'))
            player.rect.x, player.rect.y = city_pos[0] - my_delt[0], city_pos[1] - my_delt[1]
    for i in range(49, 55):
        if data[i]:
            player.equip_weapon(i - 49)
            break

    screen.fill((0, 0, 0))
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.update(pos)
    all_sprites.draw(screen)
    button_group.draw(screen)
    buildings_group.draw(screen)
    player_group.draw(screen)
    weapon_group.draw(screen)
    potion_group.draw(screen)
    if text:
        screen.blit(text, (0, height - 30))
    screen.blit(render_info(player, screen), (0, 0))
    pygame.display.flip()
    clock.tick(fps)
    if player.get_health() <= 0:
        exit_game()
