import os
from pathlib import Path

# Конфигурация игры Арканоид
# Этот файл содержит настройки, которые можно изменять

# Настройки окна
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

# Файли ресурсів
# Використовуємо pathlib для коректних шляхів відносно цього файлу
# game_config.py знаходиться в src/, тому піднімаємось на рівень вище
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / 'assets'
DATA_DIR = BASE_DIR / 'data'

MUSIC_FILE = str(ASSETS_DIR / 'music' / 'chiptune-ending-212716.mp3')
HEART_IMAGE_FILE = str(ASSETS_DIR / 'images' / 'heart.png')
HIGH_SCORES_FILE = str(DATA_DIR / 'high_scores.json')

# Настройки звуку
MUSIC_VOLUME = 0.5

# Настройки игры
INITIAL_LIVES = 3
SCORE_PER_BRICK = 10

# Кольори для меню та UI (Neon Theme)
NEON_THEME = {
    'BACKGROUND': (10, 10, 20),      # Глибокий космос
    'TEXT_MAIN': (255, 255, 255),    # Білий
    'TEXT_ACCENT': (0, 255, 255),    # Неоновий ціан
    'BUTTON_BG': (20, 20, 40),       # Темний фон кнопок
    'BUTTON_BORDER': (0, 255, 255),  # Ціан обводка
    'BUTTON_HOVER': (255, 0, 255),   # Маджента при наведенні
    'BUTTON_TEXT': (255, 255, 255),  # Білий текст
    'BUTTON_TEXT_HOVER': (255, 255, 255)
}

# Основні кольори
WHITE = NEON_THEME['TEXT_MAIN']
BLACK = NEON_THEME['BACKGROUND']
RED = NEON_THEME['BUTTON_HOVER']     # Magenta as Red replacement
BLUE = NEON_THEME['BUTTON_BORDER']   # Cyan as Blue replacement
GREEN = (57, 255, 20)                # Neon Green
YELLOW = (255, 255, 0)               # Neon Yellow
CYAN = NEON_THEME['TEXT_ACCENT']
MAGENTA = (255, 0, 255)

# Кольори меню
MENU_COLOR = NEON_THEME['TEXT_ACCENT']
MENU_HOVER_COLOR = NEON_THEME['BUTTON_HOVER']
MENU_SELECTED_COLOR = NEON_THEME['BUTTON_HOVER']
BUTTON_BG_COLOR = NEON_THEME['BUTTON_BG']
BUTTON_BORDER_COLOR = NEON_THEME['BUTTON_BORDER']

# Параметри меню
MENU_BUTTON_WIDTH = 300
MENU_BUTTON_HEIGHT = 60
MENU_BUTTON_SPACING = 20

MAX_HIGH_SCORES = 10

# Параметри платформи
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 10
PADDLE_SPEED = 10

# Параметри м'яча
BALL_RADIUS = 15
BASE_BALL_SPEED = 7.07
MAX_BALL_SPEED = 12.0
SPEED_INCREASE_PER_LEVEL = 0.7

# Параметри цеглинок
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = 55
BRICK_HEIGHT = 20
BRICK_PADDING = 5

# Параметри UI
FONT_SIZE = 42
LARGE_FONT_SIZE = 100
MENU_FONT_SIZE = 36
SMALL_FONT_SIZE = 28
HEART_SIZE = 35
HEART_PADDING = 8

# Параметри стін
WALL_THICKNESS = 3

# Візуальні ефекти
ENABLE_PARTICLES = True
ENABLE_BALL_TRAIL = True
ENABLE_BRICK_GRADIENTS = True
ENABLE_GLOWING_BALL = True
ENABLE_ANIMATED_BACKGROUND = True

# Параметри частинок
EXPLOSION_PARTICLES = 25
EXPLOSION_SPEED_RANGE = (2, 8)
PARTICLE_LIFETIME = 0.6

# Параметри трейлу м'яча
BALL_TRAIL_LENGTH = 7
BALL_TRAIL_ENABLED = True

# Параметри фону
BACKGROUND_STARS = 100
STAR_SPEED_MULTIPLIER = 1.0

# Фізика
MIN_VERTICAL_SPEED_RATIO = 0.35  # Мінімальна вертикальна складова швидкості
MAX_BOUNCE_ANGLE_DEG = 75        # Максимальний кут відбиття від нормалі
MAX_HORIZONTAL_BOUNCE_SPEED = 10

# Система бонусів
BONUS_DROP_CHANCE = 0.20  # 20% шанс випадання
BONUS_FALL_SPEED = 3
ENABLE_BONUSES = True

# Ефекти бонусів
PADDLE_EXPAND_MULTIPLIER = 1.5  # +50%
PADDLE_SHRINK_MULTIPLIER = 0.7  # -30%
FIRE_BALL_DURATION = 10.0       # 10 секунд