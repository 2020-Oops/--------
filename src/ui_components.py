"""
UI Components Module - Reusable UI elements for the game
"""
import pygame
import math
from game_config import (
    WHITE, BLACK, CYAN, MAGENTA, YELLOW, GREEN,
    NEON_THEME, SMALL_FONT_SIZE
)


class ProgressBar:
    """Прогрес-бар з градієнтом"""
    
    def __init__(self, x, y, width, height, color_start=CYAN, color_end=MAGENTA):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_start = color_start
        self.color_end = color_end
        self.progress = 0.0  # 0.0 to 1.0
        
    def set_progress(self, value):
        """Встановити прогрес (0.0 - 1.0)"""
        self.progress = max(0.0, min(1.0, value))
        
    def draw(self, surface):
        """Малює прогрес-бар"""
        # Фон
        pygame.draw.rect(surface, (40, 40, 60), self.rect, border_radius=5)
        pygame.draw.rect(surface, CYAN, self.rect, 2, border_radius=5)
        
        # Заповнення
        if self.progress > 0:
            fill_width = int(self.rect.width * self.progress)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            
            # Градієнт ефект (простий)
            for i in range(fill_width):
                ratio = i / max(1, fill_width)
                color = (
                    int(self.color_start[0] * (1 - ratio) + self.color_end[0] * ratio),
                    int(self.color_start[1] * (1 - ratio) + self.color_end[1] * ratio),
                    int(self.color_start[2] * (1 - ratio) + self.color_end[2] * ratio)
                )
                pygame.draw.line(surface, color, 
                               (self.rect.x + i, self.rect.y),
                               (self.rect.x + i, self.rect.y + self.rect.height))


class BonusTimer:
    """Візуальний таймер для бонусів"""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
    def draw(self, surface, bonus_type, time_remaining, max_time):
        """Малює таймер бонусу"""
        # Фон
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (20, 20, 40), bg_rect, border_radius=5)
        pygame.draw.rect(surface, CYAN, bg_rect, 2, border_radius=5)
        
        # Іконка/текст бонусу
        bonus_name = self._get_bonus_name(bonus_type)
        text = self.font.render(bonus_name, True, YELLOW)
        surface.blit(text, (self.x + 10, self.y + 5))
        
        # Прогрес-бар часу
        progress = time_remaining / max_time
        bar_width = self.width - 20
        bar_height = 8
        bar_x = self.x + 10
        bar_y = self.y + self.height - bar_height - 5
        
        # Фон бару
        pygame.draw.rect(surface, (40, 40, 60), 
                        (bar_x, bar_y, bar_width, bar_height), border_radius=3)
        
        # Заповнення
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            color = GREEN if progress > 0.3 else YELLOW if progress > 0.1 else MAGENTA
            pygame.draw.rect(surface, color,
                           (bar_x, bar_y, fill_width, bar_height), border_radius=3)
        
        # Час
        time_text = self.font.render(f"{time_remaining:.1f}s", True, WHITE)
        surface.blit(time_text, (self.x + self.width - 50, self.y + 5))
    
    def _get_bonus_name(self, bonus_type):
        """Отримує назву бонусу"""
        from bonus_system import BonusType
        names = {
            BonusType.EXPAND_PADDLE: "▬ Розширення",
            BonusType.SHRINK_PADDLE: "─ Звуження",
            BonusType.EXTRA_LIFE: "♥ Життя",
            BonusType.MULTI_BALL: "● Мульті-м'яч",
            BonusType.SLOW_BALL: "⊙ Сповільнення",
            BonusType.FIRE_BALL: "🔥 Вогонь"
        }
        return names.get(bonus_type, "Бонус")


class AnimatedCounter:
    """Анімований лічильник (для рахунку)"""
    
    def __init__(self, x, y, font_size=42):
        self.x = x
        self.y = y
        self.current_value = 0
        self.target_value = 0
        self.display_value = 0.0
        self.font = pygame.font.Font(None, font_size)
        self.animation_speed = 50  # points per second
        
    def set_value(self, value):
        """Встановити цільове значення"""
        self.target_value = value
        
    def update(self, dt):
        """Оновити анімацію"""
        if self.display_value < self.target_value:
            increment = self.animation_speed * dt
            self.display_value = min(self.display_value + increment, self.target_value)
        elif self.display_value > self.target_value:
            self.display_value = self.target_value
            
    def draw(self, surface, color=WHITE):
        """Малює лічильник"""
        text = self.font.render(str(int(self.display_value)), True, color)
        rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, rect)


class FloatingText:
    """Спливаючий текст ("+100", "COMBO!")"""
    
    def __init__(self, x, y, text, color=YELLOW, font_size=36):
        self.x = x
        self.y = y
        self.start_y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.lifetime = 1.5  # seconds
        self.elapsed = 0.0
        self.active = True
        
    def update(self, dt):
        """Оновити анімацію"""
        self.elapsed += dt
        if self.elapsed >= self.lifetime:
            self.active = False
            return
            
        # Рух вгору
        self.y = self.start_y - (self.elapsed / self.lifetime) * 60
        
    def draw(self, surface):
        """Малює текст"""
        if not self.active:
            return
            
        # Прозорість
        alpha = int(255 * (1 - self.elapsed / self.lifetime))
        
        # Створюємо surface з прозорістю
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        
        rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surface, rect)


class ComboMeter:
    """Лічильник комбо"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.combo = 0
        self.display_time = 2.0  # seconds
        self.elapsed = 0.0
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 28)
        
    def add_combo(self):
        """Додати комбо"""
        self.combo += 1
        self.elapsed = 0.0
        
    def reset(self):
        """Скинути комбо"""
        self.combo = 0
        self.elapsed = 0.0
        
    def update(self, dt):
        """Оновити таймер"""
        if self.combo > 0:
            self.elapsed += dt
            if self.elapsed >= self.display_time:
                self.reset()
                
    def draw(self, surface):
        """Малює комбо-метр"""
        if self.combo <= 1:
            return
            
        # Пульсація
        scale = 1.0 + 0.1 * math.sin(self.elapsed * 10)
        
        # Колір залежить від комбо
        if self.combo >= 10:
            color = MAGENTA
        elif self.combo >= 5:
            color = YELLOW
        else:
            color = CYAN
            
        # Текст
        combo_text = self.font_large.render(f"COMBO x{self.combo}!", True, color)
        
        # Масштабування (простий ефект)
        width = int(combo_text.get_width() * scale)
        height = int(combo_text.get_height() * scale)
        scaled = pygame.transform.scale(combo_text, (width, height))
        
        rect = scaled.get_rect(center=(self.x, self.y))
        surface.blit(scaled, rect)


class Tooltip:
    """Підказки при наведенні"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.visible = False
        self.text = ""
        self.x = 0
        self.y = 0
        self.padding = 10
        
    def show(self, text, x, y):
        """Показати підказку"""
        self.text = text
        self.x = x
        self.y = y
        self.visible = True
        
    def hide(self):
        """Сховати підказку"""
        self.visible = False
        
    def draw(self, surface):
        """Малює підказку"""
        if not self.visible or not self.text:
            return
            
        # Текст
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect()
        
        # Фон
        bg_rect = text_rect.inflate(self.padding * 2, self.padding * 2)
        bg_rect.center = (self.x, self.y + 30)
        
        pygame.draw.rect(surface, (20, 20, 40), bg_rect, border_radius=5)
        pygame.draw.rect(surface, CYAN, bg_rect, 2, border_radius=5)
        
        # Текст
        text_rect.center = bg_rect.center
        surface.blit(text_surface, text_rect)
