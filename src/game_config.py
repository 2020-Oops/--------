# Конфигурация игры Арканоид
# Этот файл содержит настройки, которые можно изменять

# Настройки окна
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

# Настройки игры
INITIAL_LIVES = 3
SCORE_PER_BRICK = 10

BRICK_ROWS = 5
BRICK_COLS = 10

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

MENU_COLOR = NEON_THEME['TEXT_ACCENT']
MENU_HOVER_COLOR = NEON_THEME['BUTTON_HOVER']
MENU_SELECTED_COLOR = NEON_THEME['BUTTON_HOVER']
BUTTON_BG_COLOR = NEON_THEME['BUTTON_BG']
BUTTON_BORDER_COLOR = NEON_THEME['BUTTON_BORDER']

# Параметри меню
MENU_BUTTON_WIDTH = 300
MENU_BUTTON_HEIGHT = 60
MENU_BUTTON_SPACING = 20

# Файл рекордів
HIGH_SCORES_FILE = 'high_scores.json'
MAX_HIGH_SCORES = 10

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

# Параметри м'яча
BASE_BALL_SPEED = 7.07
MAX_BALL_SPEED = 12.0
SPEED_INCREASE_PER_LEVEL = 0.7

# Фізика
MIN_VERTICAL_SPEED_RATIO = 0.35  # Мінімальна вертикальна складова швидкості
MAX_BOUNCE_ANGLE_DEG = 75        # Максимальний кут відбиття від нормалі

# Система бонусів
BONUS_DROP_CHANCE = 0.20  # 20% шанс випадання
BONUS_FALL_SPEED = 3
ENABLE_BONUSES = True

# Ефекти бонусів
PADDLE_EXPAND_MULTIPLIER = 1.5  # +50%
PADDLE_SHRINK_MULTIPLIER = 0.7  # -30%
FIRE_BALL_DURATION = 10.0       # 10 секунд