"""
Система бонусів для гри Арканоїд
"""
import pygame
import random
import time
from enum import Enum


class BonusType(Enum):
    """Типи бонусів"""
    EXPAND_PADDLE = "expand"      # Збільшення платформи
    SHRINK_PADDLE = "shrink"      # Зменшення платформи
    EXTRA_LIFE = "life"           # Додаткове життя
    FIRE_BALL = "fire"            # Вогняний м'яч
    MULTI_BALL = "multi"          # Мультибол


# Налаштування бонусів (Neon Palette)
BONUS_CONFIG = {
    BonusType.EXPAND_PADDLE: {
        'color': (57, 255, 20),      # Neon Green
        'icon': '▬',
        'duration': 15.0,
        'weight': 25
    },
    BonusType.SHRINK_PADDLE: {
        'color': (255, 100, 0),      # Neon Orange
        'icon': '▭',
        'duration': 10.0,
        'weight': 15
    },
    BonusType.EXTRA_LIFE: {
        'color': (255, 20, 147),     # Neon Pink
        'icon': '♥',
        'duration': 0,
        'weight': 10
    },
    BonusType.FIRE_BALL: {
        'color': (255, 0, 0),        # Neon Red
        'icon': '🔥',
        'duration': 10.0,
        'weight': 25
    },
    BonusType.MULTI_BALL: {
        'color': (255, 255, 0),      # Neon Yellow
        'icon': '●●',
        'duration': 0,
        'weight': 25
    }
}


class Bonus:
    """Падаючий бонус"""
    
    def __init__(self, x, y, bonus_type):
        """
        Ініціалізація бонусу
        
        Args:
            x, y: Початкова позиція
            bonus_type: Тип бонусу (BonusType)
        """
        self.x = x
        self.y = y
        self.bonus_type = bonus_type
        self.width = 40
        self.height = 20
        self.speed = 3  # Швидкість падіння
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        
        # Візуальні параметри
        self.config = BONUS_CONFIG[bonus_type]
        self.color = self.config['color']
        self.icon = self.config['icon']
        
        # Анімація
        self.alpha = 255
        self.wobble_offset = random.uniform(0, 3.14)
    
    def update(self, dt):
        """
        Оновлює позицію бонусу
        
        Args:
            dt: Час з попереднього кадру
            
        Returns:
            bool: False якщо бонус вийшов за межі екрану
        """
        self.y += self.speed
        self.rect.y = int(self.y)
        
        # Перевіряємо чи не вийшов за межі
        return self.y < 700  # Трохи нижче екрану для плавності
    
    def draw(self, surface, current_time):
        """
        Малює бонус на поверхні
        
        Args:
            surface: Поверхня для малювання
            current_time: Поточний час для анімації
        """
        import math
        
        # Легке коливання (wobble)
        wobble = math.sin(current_time * 3 + self.wobble_offset) * 2
        draw_x = self.rect.x + wobble
        
        # Малюємо фон бонусу з градієнтом
        bonus_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Основний колір
        pygame.draw.rect(bonus_surface, (*self.color, 200), 
                        bonus_surface.get_rect(), border_radius=5)
        
        # Світла обводка
        lighter_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.rect(bonus_surface, lighter_color, 
                        bonus_surface.get_rect(), 2, border_radius=5)
        
        surface.blit(bonus_surface, (int(draw_x), self.rect.y))
        
        # Малюємо іконку
        font = pygame.font.Font(None, 24)
        icon_text = font.render(self.icon, True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(int(draw_x) + self.width // 2, 
                                               self.rect.centery))
        surface.blit(icon_text, icon_rect)


class ActiveEffect:
    """Активний тимчасовий ефект"""
    
    def __init__(self, effect_type, duration):
        """
        Ініціалізація ефекту
        
        Args:
            effect_type: Тип ефекту (BonusType)
            duration: Тривалість в секундах (0 для постійних)
        """
        self.effect_type = effect_type
        self.duration = duration
        self.start_time = time.time()
        self.config = BONUS_CONFIG[effect_type]
    
    def get_remaining_time(self):
        """Повертає залишковий час в секундах"""
        if self.duration == 0:
            return 0
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)
    
    def is_expired(self):
        """Перевіряє чи закінчився ефект"""
        if self.duration == 0:
            return False
        return self.get_remaining_time() <= 0
    
    def draw_indicator(self, surface, x, y):
        """
        Малює індикатор ефекту
        
        Args:
            surface: Поверхня для малювання
            x, y: Позиція індикатора
        """
        width = 120
        height = 30
        
        # Фон індикатора
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (40, 40, 80, 200), bg_surface.get_rect(), border_radius=5)
        pygame.draw.rect(bg_surface, self.config['color'], bg_surface.get_rect(), 2, border_radius=5)
        surface.blit(bg_surface, (x, y))
        
        # Іконка
        font = pygame.font.Font(None, 20)
        icon = font.render(self.config['icon'], True, self.config['color'])
        surface.blit(icon, (x + 5, y + 5))
        
        # Прогрес-бар (якщо тимчасовий)
        if self.duration > 0:
            remaining = self.get_remaining_time()
            progress = remaining / self.duration
            bar_width = int((width - 35) * progress)
            bar_rect = pygame.Rect(x + 30, y + 10, bar_width, 10)
            pygame.draw.rect(surface, self.config['color'], bar_rect, border_radius=3)
            
            # Час що залишився
            time_text = font.render(f"{int(remaining)}s", True, (255, 255, 255))
            surface.blit(time_text, (x + 30, y + 5))


class BonusManager:
    """Менеджер системи бонусів"""
    
    def __init__(self):
        """Ініціалізація менеджера"""
        self.bonuses = []
        self.active_effects = []
        self.drop_chance = 0.20  # 20% шанс випадання
    
    def create_random_bonus(self, x, y):
        """
        Створює випадковий бонус
        
        Args:
            x, y: Позиція створення
            
        Returns:
            Bonus або None
        """
        if random.random() > self.drop_chance:
            return None
        
        # Зважений вибір типу бонусу
        weights = [BONUS_CONFIG[bt]['weight'] for bt in BonusType]
        bonus_type = random.choices(list(BonusType), weights=weights)[0]
        
        return Bonus(x, y, bonus_type)
    
    def add_bonus(self, bonus):
        """Додає бонус до списку"""
        if bonus:
            self.bonuses.append(bonus)
    
    def update(self, dt):
        """
        Оновлює всі бонуси та ефекти
        
        Args:
            dt: Час з попереднього кадру
        """
        # Оновлюємо бонуси
        self.bonuses = [b for b in self.bonuses if b.update(dt)]
        
        # Оновлюємо ефекти (видаляємо закінчені)
        self.active_effects = [e for e in self.active_effects if not e.is_expired()]
    
    def check_collection(self, paddle_rect):
        """
        Перевіряє зіткнення бонусів з платформою
        
        Args:
            paddle_rect: Rect платформи
            
        Returns:
            list: Список зібраних бонусів
        """
        collected = []
        remaining = []
        
        for bonus in self.bonuses:
            if bonus.rect.colliderect(paddle_rect):
                collected.append(bonus)
            else:
                remaining.append(bonus)
        
        self.bonuses = remaining
        return collected
    
    def apply_bonus(self, bonus):
        """
        Застосовує ефект бонусу
        
        Args:
            bonus: Зібраний бонус
            
        Returns:
            dict: Інформація про зміни для гри
        """
        bonus_type = bonus.bonus_type
        config = BONUS_CONFIG[bonus_type]
        
        # Для тимчасових ефектів - додаємо до активних
        if config['duration'] > 0:
            # Видаляємо протилежний ефект якщо є
            if bonus_type == BonusType.EXPAND_PADDLE:
                self.active_effects = [e for e in self.active_effects 
                                      if e.effect_type != BonusType.SHRINK_PADDLE]
            elif bonus_type == BonusType.SHRINK_PADDLE:
                self.active_effects = [e for e in self.active_effects 
                                      if e.effect_type != BonusType.EXPAND_PADDLE]
            
            # Додаємо новий ефект
            self.active_effects.append(ActiveEffect(bonus_type, config['duration']))
        
        # Повертаємо інформацію про ефект
        return {
            'type': bonus_type,
            'duration': config['duration']
        }
    
    def has_active_effect(self, effect_type):
        """Перевіряє чи активний певний ефект"""
        return any(e.effect_type == effect_type for e in self.active_effects)
    
    def draw_bonuses(self, surface, current_time):
        """Малює всі падаючі бонуси"""
        for bonus in self.bonuses:
            bonus.draw(surface, current_time)
    
    def draw_effects_ui(self, surface, x, y):
        """
        Малює UI індикатори активних ефектів
        
        Args:
            surface: Поверхня для малювання
            x, y: Початкова позиція
        """
        offset_y = 0
        for effect in self.active_effects:
            effect.draw_indicator(surface, x, y + offset_y)
            offset_y += 35
    
    def clear(self):
        """Очищає всі бонуси та ефекти"""
        self.bonuses.clear()
        self.active_effects.clear()
    
    def get_paddle_modifier(self):
        """
        Повертає модифікатор розміру платформи
        
        Returns:
            float: Множник розміру (1.0 = нормальний, 1.5 = +50%, 0.7 = -30%)
        """
        if self.has_active_effect(BonusType.EXPAND_PADDLE):
            return 1.5
        elif self.has_active_effect(BonusType.SHRINK_PADDLE):
            return 0.7
        return 1.0
    
    def get_ball_speed_modifier(self):
        """
        Повертає модифікатор швидкості м'яча
        
        Returns:
            float: Множник швидкості (1.0 = нормальна)
        """
        return 1.0
