import pygame
import sys
import traceback

def hook(*args):
    traceback.print_last()
    input()

sys.excepthook = hook

class Item(pygame.sprite.Sprite):
    def change_image(self, image, image_size=200):
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
            self.text = 'Зелье Лечения' + (f' +{self.coof}' if self.coof > 1 else '')
        elif self.effect == 's':
            image = load_image(r'data\potions\speed_potion.png', -1)
            self.text = 'Зелье Скорости' + (f' +{self.coof}' if self.coof > 1 else '')
        elif self.effect == 'd':
            image = load_image(r'data\potions\damage_potion.png', -1)
            self.text = 'Зелье Урона' + (f' +{self.coof}' if self.coof > 1 else '')
        else:
            raise ValueError('Effect must be "h"eal, "s"peed or "d"amage, with +"int" or without')

        self.change_image(image)


    def do_effect(self, player):
        if self.effect == 'h':
            player.set_health(player.get_health() + int(self.heal * self.coof / 2))
        elif self.effect == 's':
            player.set_speed(player.get_speed() + int(self.speed * self.coof / 2))
        elif self.effect == 'd':
            player.set_damage_boost(player.get_damage_boost() + int(self.damage + self.coof / 10))
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

def resize_image(image, biggest_side):
    x, y = image.get_rect().w, image.get_rect().h
    prop = biggest_side / max((x, y))
    return pygame.transform.scale(image, (int(x * prop), int(y * prop)))

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


pygame.init()
screen = pygame.display.set_mode((200, 200))
all_sprites = pygame.sprite.Group()
potion = Weapon('g', 200, 200, 45, all_sprites)
potion.rect = potion.rect.move((0, 0))
all_sprites.draw(screen)
pygame.display.flip()

input()