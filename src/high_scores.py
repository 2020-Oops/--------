"""
Модуль для управління системою рекордів у грі Арканоїд
"""
import json
import os
from datetime import datetime


class HighScoreManager:
    """Менеджер для роботи з таблицею рекордів"""
    
    def __init__(self, filename='high_scores.json', max_scores=10):
        """
        Ініціалізація менеджера рекордів
        
        Args:
            filename: Ім'я файлу для збереження рекордів
            max_scores: Максимальна кількість рекордів для збереження
        """
        self.filename = filename
        self.max_scores = max_scores
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Завантажує рекорди з JSON файлу"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Помилка завантаження рекордів: {e}")
                return []
        return []
    
    def save_scores(self):
        """Зберігає рекорди у JSON файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Помилка збереження рекордів: {e}")
    
    def add_score(self, score, level):
        """
        Додає новий рекорд до списку
        
        Args:
            score: Отримані очки
            level: Досягнутий рівень
            
        Returns:
            int або None: Позиція в таблиці рекордів (1-based) або None якщо не потрапив
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = {
            'score': score,
            'level': level,
            'date': timestamp
        }
        
        # Додаємо новий рекорд
        self.scores.append(new_entry)
        
        # Сортуємо за очками (від більшого до меншого)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Знаходимо позицію нового рекорду
        position = None
        for i, entry in enumerate(self.scores):
            if entry == new_entry:
                position = i + 1  # 1-based позиція
                break
        
        # Зберігаємо тільки топ-N рекордів
        self.scores = self.scores[:self.max_scores]
        
        # Зберігаємо у файл
        self.save_scores()
        
        # Повертаємо позицію тільки якщо рекорд потрапив у топ-N
        return position if position and position <= self.max_scores else None
    
    def is_high_score(self, score):
        """
        Перевіряє, чи є результат достатньо високим для потрапляння в таблицю
        
        Args:
            score: Очки для перевірки
            
        Returns:
            bool: True якщо рекорд потрапить у таблицю
        """
        if len(self.scores) < self.max_scores:
            return True
        return score > self.scores[-1]['score']
    
    def get_scores(self):
        """
        Повертає список рекордів
        
        Returns:
            list: Список рекордів
        """
        return self.scores
    
    def clear_scores(self):
        """Очищає всі рекорди"""
        self.scores = []
        self.save_scores()
