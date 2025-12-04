"""
Система цеглинок для гри Арканоїд
Різні типи цеглинок з унікальною поведінкою
"""
import pygame
import random
import math
from enum import Enum


class BrickType(Enum):
    """Типи цеглинок"""
    NORMAL = "normal"           # Звичайна цеглинка (1 HP)
    DURABLE = "durable"         # Міцна цеглинка (2-3 HP)
    UNBREAKABLE = "unbreakable" # Незнищенна (металева)
    EXPLOSIVE = "explosive"     # Вибухова (ланцюгова реакція)
    BONUS = "bonus"             # Гарантований бонус


# Конфігурація типів цеглинок
BRICK_CONFIG = {
    BrickType.NORMAL: {
        'hp': 1,
        'points': 10,
        'can_destroy': True
    },
    BrickType.DURABLE: {
        'hp': 2,  # Можна 3 для золотих
        'points': 25,
        'can_destroy': True
    },
    BrickType.UNBREAKABLE: {
        'hp': 999,
        'points': 0,
        'can_destroy': False
    },
    BrickType.EXPLOSIVE: {
        'hp': 1,
        'points': 15,
        'can_destroy': True,
        'explosion_radius': 1  # Клітинки навколо
    },
    BrickType.BONUS: {
        'hp': 1,
        'points': 20,
        'can_destroy': True,
        'guaranteed_bonus': True
    }
}

# Кольори для типів цеглинок
BRICK_COLORS = {
    BrickType.NORMAL: {
        'row_colors': [
            (255, 0, 255),   # Neon Magenta
            (0, 255, 255),   # Neon Cyan
            (57, 255, 20),   # Neon Green
        ]
    },
    BrickType.DURABLE: {
        'colors': [
            (192, 192, 192),  # Silver (2 HP)
            (255, 215, 0),    # Gold (3 HP)
        ]
    },
    BrickType.UNBREAKABLE: {
        'color': (80, 80, 100)  # Dark metallic
    },
    BrickType.EXPLOSIVE: {
        'color': (255, 100, 50)  # Orange-red
    },
    BrickType.BONUS: {
        'color': (255, 200, 100)  # Golden glow
    }
}


class Brick:
    """Клас цеглинки з HP та типом"""
    
    def __init__(self, x, y, width, height, brick_type=BrickType.NORMAL, row=0):
        """
        Ініціалізація цеглинки
        
        Args:
            x, y: Позиція
            width, height: Розміри
            brick_type: Тип цеглинки
            row: Рядок (для кольору звичайних цеглинок)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.brick_type = brick_type
        self.row = row
        self.visible = True
        
        # HP з конфігурації
        config = BRICK_CONFIG[brick_type]
        self.max_hp = config['hp']
        self.hp = self.max_hp
        self.points = config['points']
        self.can_destroy = config['can_destroy']
        
        # Визначаємо колір
        self.color = self._get_color()
        self.original_color = self.color
        
        # Анімація
        self.shake_offset = 0
        self.shake_time = 0
        
    def _get_color(self):
        """Повертає колір цеглинки залежно від типу"""
        if self.brick_type == BrickType.NORMAL:
            colors = BRICK_COLORS[BrickType.NORMAL]['row_colors']
            return colors[self.row % len(colors)]
        elif self.brick_type == BrickType.DURABLE:
            colors = BRICK_COLORS[BrickType.DURABLE]['colors']
            # Золота якщо 3+ HP
            return colors[1] if self.max_hp >= 3 else colors[0]
        elif self.brick_type == BrickType.UNBREAKABLE:
            return BRICK_COLORS[BrickType.UNBREAKABLE]['color']
        elif self.brick_type == BrickType.EXPLOSIVE:
            return BRICK_COLORS[BrickType.EXPLOSIVE]['color']
        elif self.brick_type == BrickType.BONUS:
            return BRICK_COLORS[BrickType.BONUS]['color']
        return (255, 255, 255)
    
    def hit(self):
        """
        Обробляє удар по цеглинці
        
        Returns:
            dict: Результат удару
        """
        if not self.can_destroy:
            # Незнищенна - тільки ефект
            self.shake_time = 0.2
            return {
                'destroyed': False,
                'points': 0,
                'type': self.brick_type,
                'explosive': False,
                'bonus_guaranteed': False
            }
        
        self.hp -= 1
        self.shake_time = 0.1
        
        # Оновлюємо колір для пошкоджених міцних цеглинок
        if self.brick_type == BrickType.DURABLE and self.hp > 0:
            # Темнішаємо колір
            damage_ratio = self.hp / self.max_hp
            self.color = tuple(int(c * (0.5 + 0.5 * damage_ratio)) for c in self.original_color)
        
        if self.hp <= 0:
            self.visible = False
            return {
                'destroyed': True,
                'points': self.points,
                'type': self.brick_type,
                'explosive': self.brick_type == BrickType.EXPLOSIVE,
                'bonus_guaranteed': self.brick_type == BrickType.BONUS,
                'position': (self.rect.centerx, self.rect.centery)
            }
        
        return {
            'destroyed': False,
            'points': 0,
            'type': self.brick_type,
            'explosive': False,
            'bonus_guaranteed': False
        }
    
    def update(self, dt):
        """Оновлює анімації"""
        if self.shake_time > 0:
            self.shake_time -= dt
            self.shake_offset = random.uniform(-2, 2)
        else:
            self.shake_offset = 0
    
    def draw(self, surface, current_time=0):
        """Малює цеглинку"""
        if not self.visible:
            return
            
        draw_rect = self.rect.copy()
        draw_rect.x += int(self.shake_offset)
        
        # Основний колір з градієнтом
        self._draw_with_gradient(surface, draw_rect)
        
        # Спеціальні ефекти для різних типів
        if self.brick_type == BrickType.UNBREAKABLE:
            self._draw_metal_effect(surface, draw_rect)
        elif self.brick_type == BrickType.EXPLOSIVE:
            self._draw_explosive_effect(surface, draw_rect, current_time)
        elif self.brick_type == BrickType.BONUS:
            self._draw_bonus_effect(surface, draw_rect, current_time)
        elif self.brick_type == BrickType.DURABLE and self.hp < self.max_hp:
            self._draw_cracks(surface, draw_rect)
    
    def _draw_with_gradient(self, surface, rect):
        """Малює цеглинку з градієнтом"""
        # Градієнт зверху вниз
        color_top = tuple(min(255, int(c * 1.3)) for c in self.color)
        color_bottom = tuple(int(c * 0.7) for c in self.color)
        
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.left, rect.top + y), 
                           (rect.right, rect.top + y))
        
        # 3D ефект
        highlight = tuple(min(255, int(c * 1.5)) for c in self.color)
        shadow = tuple(int(c * 0.5) for c in self.color)
        pygame.draw.line(surface, highlight, rect.topleft, rect.topright, 2)
        pygame.draw.line(surface, highlight, rect.topleft, rect.bottomleft, 2)
        pygame.draw.line(surface, shadow, rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(surface, shadow, rect.topright, rect.bottomright, 2)
    
    def _draw_metal_effect(self, surface, rect):
        """Малює металевий ефект"""
        # Горизонтальні смуги
        stripe_color = (100, 100, 120)
        for i in range(3):
            y = rect.top + (i + 1) * rect.height // 4
            pygame.draw.line(surface, stripe_color, (rect.left + 2, y), (rect.right - 2, y), 1)
        
        # Болти по кутах
        bolt_color = (60, 60, 80)
        bolt_radius = 3
        offsets = [(5, 5), (rect.width - 5, 5), (5, rect.height - 5), (rect.width - 5, rect.height - 5)]
        for ox, oy in offsets:
            pygame.draw.circle(surface, bolt_color, (rect.left + ox, rect.top + oy), bolt_radius)
    
    def _draw_explosive_effect(self, surface, rect, current_time):
        """Малює ефект вибухової цеглинки"""
        # Пульсуюча обводка
        pulse = math.sin(current_time * 8) * 0.3 + 0.7
        glow_color = (255, int(50 * pulse), 0)
        pygame.draw.rect(surface, glow_color, rect, 3)
        
        # Символ вибуху
        font = pygame.font.Font(None, 20)
        text = font.render("💥", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
    
    def _draw_bonus_effect(self, surface, rect, current_time):
        """Малює ефект бонусної цеглинки"""
        # Веселкова обводка
        hue = (current_time * 100) % 360
        # Спрощений HSV до RGB
        c = 1.0
        x = 1 - abs((hue / 60) % 2 - 1)
        if hue < 60:
            r, g, b = c, x, 0
        elif hue < 120:
            r, g, b = x, c, 0
        elif hue < 180:
            r, g, b = 0, c, x
        elif hue < 240:
            r, g, b = 0, x, c
        elif hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        rainbow_color = (int(r * 255), int(g * 255), int(b * 255))
        pygame.draw.rect(surface, rainbow_color, rect, 3)
        
        # Зірочка
        font = pygame.font.Font(None, 18)
        text = font.render("★", True, rainbow_color)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
    
    def _draw_cracks(self, surface, rect):
        """Малює тріщини на пошкодженій цеглинці"""
        crack_color = (50, 50, 50)
        damage = 1 - (self.hp / self.max_hp)
        
        # Більше тріщин при більшому пошкодженні
        if damage >= 0.5:
            # Велика тріщина
            points = [
                (rect.left + 5, rect.top + 5),
                (rect.centerx, rect.centery),
                (rect.right - 5, rect.bottom - 5)
            ]
            pygame.draw.lines(surface, crack_color, False, points, 2)
            
        if damage >= 0.3:
            # Маленька тріщина
            pygame.draw.line(surface, crack_color, 
                           (rect.right - 10, rect.top + 3),
                           (rect.centerx + 5, rect.centery - 3), 2)


class LevelManager:
    """Менеджер рівнів з патернами цеглинок"""
    
    # Легенда: N=Normal, .=Empty
    LEVELS = [
        # Рівень 1: Класичний
        [
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
        ],
        # Рівень 2: Класичний
        [
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
        ],
        # Рівень 3: Класичний
        [
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
        ],
        # Рівень 4: Класичний
        [
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
        ],
        # Рівень 5: Класичний
        [
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
            "NNNNNNNNNN",
        ],
    ]
    
    CHAR_TO_TYPE = {
        'N': BrickType.NORMAL,
        'D': BrickType.DURABLE,
        'U': BrickType.UNBREAKABLE,
        'E': BrickType.EXPLOSIVE,
        'B': BrickType.BONUS,
        '.': None  # Порожнє місце
    }
    
    def __init__(self, brick_width, brick_height, brick_padding, offset_left, offset_top):
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.brick_padding = brick_padding
        self.offset_left = offset_left
        self.offset_top = offset_top
    
    def get_level_count(self):
        """Повертає кількість рівнів"""
        return len(self.LEVELS)
    
    def create_level(self, level_num):
        """
        Створює цеглинки для рівня
        
        Args:
            level_num: Номер рівня (1-indexed)
            
        Returns:
            list: Список Brick об'єктів
        """
        # Циклічно повторюємо рівні
        level_index = (level_num - 1) % len(self.LEVELS)
        pattern = self.LEVELS[level_index]
        
        bricks = []
        
        for row, row_pattern in enumerate(pattern):
            for col, char in enumerate(row_pattern):
                brick_type = self.CHAR_TO_TYPE.get(char)
                
                if brick_type is None:
                    continue
                
                x = self.offset_left + col * (self.brick_width + self.brick_padding)
                y = self.offset_top + row * (self.brick_height + self.brick_padding)
                
                # Для міцних цеглинок - випадково 2 або 3 HP
                brick = Brick(x, y, self.brick_width, self.brick_height, brick_type, row)
                
                if brick_type == BrickType.DURABLE:
                    # На вищих рівнях - більше HP
                    if level_num >= 4:
                        brick.max_hp = 3
                        brick.hp = 3
                        brick.color = BRICK_COLORS[BrickType.DURABLE]['colors'][1]  # Gold
                        brick.original_color = brick.color
                
                bricks.append(brick)
        
        return bricks
    
    def get_explosion_targets(self, bricks, exploded_brick):
        """
        Знаходить цеглинки в радіусі вибуху
        
        Args:
            bricks: Список всіх цеглинок
            exploded_brick: Цеглинка, що вибухнула
            
        Returns:
            list: Список цеглинок для знищення
        """
        targets = []
        explosion_rect = exploded_brick.rect.inflate(
            self.brick_width + self.brick_padding * 2,
            self.brick_height + self.brick_padding * 2
        )
        
        for brick in bricks:
            if brick == exploded_brick:
                continue
            if brick.visible and brick.can_destroy:
                if explosion_rect.colliderect(brick.rect):
                    targets.append(brick)
        
        return targets
