"""
Notification System - Manages floating text and temporary messages
"""
import pygame
from ui_components import FloatingText
from game_config import YELLOW, CYAN, GREEN, MAGENTA, WHITE


class NotificationManager:
    """Manages all notifications and floating texts"""
    
    def __init__(self):
        self.floating_texts = []
        self.notifications = []
        
    def add_floating_text(self, x, y, text, color=YELLOW, font_size=36):
        """Додає спливаючий текст"""
        floating = FloatingText(x, y, text, color, font_size)
        self.floating_texts.append(floating)
        
    def add_score_popup(self, x, y, points):
        """Додає попап з очками"""
        text = f"+{points}"
        color = GREEN if points >= 100 else YELLOW
        self.add_floating_text(x, y, text, color, 42)
        
    def add_combo_popup(self, x, y, combo):
        """Додає попап комбо"""
        if combo >= 5:
            text = f"КОМБО x{combo}!"
            self.add_floating_text(x, y, text, MAGENTA, 48)
        
    def add_bonus_popup(self, x, y, bonus_name):
        """Додає попап активації бонусу"""
        self.add_floating_text(x, y, bonus_name, CYAN, 40)
        
    def update(self, dt):
        """Оновлює всі нотифікації"""
        # Оновлюємо всі спливаючі тексти
        for text in self.floating_texts[:]:
            text.update(dt)
            if not text.active:
                self.floating_texts.remove(text)
                
    def draw(self, surface):
        """Малює всі нотифікації"""
        for text in self.floating_texts:
            text.draw(surface)
            
    def clear(self):
        """Очищає всі нотифікації"""
        self.floating_texts.clear()
        self.notifications.clear()
