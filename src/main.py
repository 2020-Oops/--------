"""
Арканоїд - класична гра с візуальними ефектами та бонусами
Керування: стрілки вліво/вправо для руху платформи
Мета: розбити всі цеглини, відбиваючи м'яч
"""
import pygame
import sys
import os
import math
import random
import time
from high_scores import HighScoreManager
from particle_system import ParticleSystem, TrailEffect, ScreenShake
from graphics_effects import (
    draw_brick_with_gradient, draw_glowing_ball, draw_3d_paddle,
    AnimatedBackground, darken_color, lighten_color, draw_neon_heart,
    draw_pulsing_text
)
from bonus_system import BonusManager, BonusType
from sound_manager import SoundManager
from brick_system import Brick, BrickType, LevelManager, BRICK_CONFIG
from entities import Paddle, Ball

from game_config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WHITE, BLACK, RED, BLUE, GREEN, YELLOW, CYAN, MAGENTA,
    MENU_COLOR, MENU_HOVER_COLOR, MENU_SELECTED_COLOR,
    BUTTON_BG_COLOR, BUTTON_BORDER_COLOR,
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED,
    BALL_RADIUS,
    BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, BRICK_PADDING,
    INITIAL_LIVES, SCORE_PER_BRICK, MAX_HORIZONTAL_BOUNCE_SPEED,
    FONT_SIZE, LARGE_FONT_SIZE, MENU_FONT_SIZE, SMALL_FONT_SIZE,
    HEART_SIZE, HEART_PADDING,
    WALL_THICKNESS,
    ASSETS_DIR, DATA_DIR, MUSIC_FILE, HEART_IMAGE_FILE,
    MUSIC_VOLUME, HIGH_SCORES_FILE,
    NEON_THEME, MIN_VERTICAL_SPEED_RATIO, MAX_BOUNCE_ANGLE_DEG,
    BASE_BALL_SPEED, MAX_BALL_SPEED, SPEED_INCREASE_PER_LEVEL
)

WIDTH, HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT

# =============================================================================
# ІНІЦІАЛІЗАЦІЯ PYGAME
# =============================================================================

pygame.init()
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False
    print("Аудіо недоступне")

# =============================================================================
# ЗАВАНТАЖЕННЯ РЕСУРСІВ
# =============================================================================

def load_music():
    if not AUDIO_AVAILABLE:
        return False
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(loops=-1)
        return True
    except pygame.error as e:
        print(f"Помилка завантаження музики: {e}")
        return False



# =============================================================================
# ІНІЦІАЛІЗАЦІЯ ГРИ
# =============================================================================

# Гра запускається у повноекранному режимі за замовчуванням
is_fullscreen = True
windowed_size = (WIDTH, HEIGHT)

# Запуск у повноекранному режимі
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Арканоїд - Візуальна версія")

music_loaded_successfully = load_music()
high_score_manager = HighScoreManager(HIGH_SCORES_FILE)
sound_manager = SoundManager()

# Системи ефектів
particle_system = ParticleSystem()
screen_shake = ScreenShake()
ball_trail = TrailEffect(max_length=7)
background = AnimatedBackground(WIDTH, HEIGHT, num_stars=100)
bonus_manager = BonusManager()

# Обчислювані позиції
initial_paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
initial_paddle_y = HEIGHT - 40
original_paddle_width = PADDLE_WIDTH
paddle = Paddle(initial_paddle_x, initial_paddle_y)

initial_ball_x = paddle.centerx - BALL_RADIUS
initial_ball_y = paddle.top - BALL_RADIUS * 2
ball_rect_template = pygame.Rect(initial_ball_x, initial_ball_y, BALL_RADIUS * 2, BALL_RADIUS * 2)

# Підтримка мультиболу
balls = []  # Список об'єктів Ball

# Параметри напрямку м'яча
initial_ball_direction_x = 5
initial_ball_direction_y = -5
initial_direction_magnitude = math.sqrt(initial_ball_direction_x**2 + initial_ball_direction_y**2)
normalized_initial_vx = initial_ball_direction_x / initial_direction_magnitude if initial_direction_magnitude > 0 else 0
normalized_initial_vy = initial_ball_direction_y / initial_direction_magnitude if initial_direction_magnitude > 0 else -1

current_speed_magnitude = 0

clock = pygame.time.Clock()
start_time = time.time()

# Параметри цеглинок
total_bricks_width = (BRICK_COLS * BRICK_WIDTH) + ((BRICK_COLS - 1) * BRICK_PADDING if BRICK_COLS > 1 else 0)
BRICK_OFFSET_LEFT = (WIDTH - total_bricks_width) // 2
BRICK_OFFSET_TOP = 60

# Менеджер рівнів (після визначення BRICK_OFFSET_LEFT та BRICK_OFFSET_TOP)
level_manager = LevelManager(BRICK_WIDTH, BRICK_HEIGHT, BRICK_PADDING, BRICK_OFFSET_LEFT, BRICK_OFFSET_TOP)

bricks = []

# =============================================================================
# ФУНКЦІЇ ГРИ
# =============================================================================

# create_bricks() function removed - now using LevelManager from brick_system.py

def setup_level(level_num):
    global balls, ball_speeds, paddle, bricks, current_speed_magnitude, level

    current_speed_magnitude = BASE_BALL_SPEED + (level_num - 1) * SPEED_INCREASE_PER_LEVEL
    current_speed_magnitude = min(current_speed_magnitude, MAX_BALL_SPEED)

    # Скидаємо м'яч
    reset_ball()

    paddle.rect.x = initial_paddle_x
    paddle.rect.y = initial_paddle_y
    paddle.set_width(original_paddle_width)

    # Створюємо цеглинки через LevelManager
    bricks = level_manager.create_level(level_num)
    ball_trail.clear()
    bonus_manager.clear()

def reset_ball():
    """Скидає м'яч на початкову позицію"""
    global balls
    
    start_ball = Ball(initial_ball_x, initial_ball_y, BALL_RADIUS, WHITE)
    
    vx = normalized_initial_vx * current_speed_magnitude
    vy = normalized_initial_vy * current_speed_magnitude
    
    start_ball.set_velocity(vx, vy)
    
    balls = [start_ball]

def toggle_fullscreen():
    global win, is_fullscreen
    
    if is_fullscreen:
        win = pygame.display.set_mode(windowed_size)
        is_fullscreen = False
    else:
        win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        is_fullscreen = True
    
    pygame.display.set_caption("Арканоїд - Візуальна версія")

def get_display_transform():
    if not is_fullscreen:
        return 1.0, 0, 0
    
    screen_width, screen_height = win.get_size()
    game_width, game_height = WIDTH, HEIGHT
    
    scale_x = screen_width / game_width
    scale_y = screen_height / game_height
    scale = min(scale_x, scale_y)
    
    scaled_width = game_width * scale
    scaled_height = game_height * scale
    offset_x = (screen_width - scaled_width) // 2
    offset_y = (screen_height - scaled_height) // 2
    
    return scale, offset_x, offset_y

def initialize_game_data():
    global score, lives, level, game_over
    score = 0
    lives = INITIAL_LIVES
    level = 1
    game_over = False
    particle_system.clear()
    ball_trail.clear()
    bonus_manager.clear()
    setup_level(1)

def activate_multiball():
    """Активує мультибол - додає 2 нових м'яча"""
    global balls, ball_speeds
    
    if not balls:
        return
        
    # Беремо перший м'яч як основу
    base_ball = balls[0]
    base_vx, base_vy = base_ball.vx, base_ball.vy
    
    # Створюємо 2 нових м'яча
    for angle_offset in [-0.5, 0.5]:
        new_ball = base_ball.copy()
        
        # Повертаємо вектор швидкості
        speed = math.sqrt(base_vx**2 + base_vy**2)
        angle = math.atan2(base_vy, base_vx)
        new_angle = angle + angle_offset
        
        new_vx = math.cos(new_angle) * speed
        new_vy = math.sin(new_angle) * speed
        
        new_ball.set_velocity(new_vx, new_vy)
        balls.append(new_ball)

def render_ui(win, font, large_font):
    score_text = font.render(f"Рахунок: {score}", True, WHITE)
    win.blit(score_text, (10, 10))
    
    level_text = font.render(f"Рівень: {level}", True, WHITE)
    win.blit(level_text, (10, 50))
    
    # Відображення життів (Neon Style)
    if lives > 5:
        # Компактний режим для багатьох життів
        draw_neon_heart(win, WIDTH - 100, 30, 15, NEON_THEME['BUTTON_HOVER'])
        lives_text = font.render(f"x {lives}", True, WHITE)
        win.blit(lives_text, (WIDTH - 70, 15))
    else:
        # Стандартний режим
        for i in range(lives):
            # Малюємо справа наліво
            heart_x = WIDTH - 40 - i * (40)
            draw_neon_heart(win, heart_x, 30, 15, NEON_THEME['BUTTON_HOVER'])
    
    # Індикатори бонусів
    bonus_manager.draw_effects_ui(win, WIDTH - 140, 60)

    # Індикатор швидкості
    speed_percent = (current_speed_magnitude - BASE_BALL_SPEED) / (MAX_BALL_SPEED - BASE_BALL_SPEED)
    speed_percent = max(0.0, min(speed_percent, 1.0))
    
    bar_width = 100
    bar_height = 10
    bar_x = WIDTH - 120
    bar_y = HEIGHT - 20
    
    # Background
    pygame.draw.rect(win, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    # Fill (Green to Red)
    red_comp = int(255 * speed_percent)
    green_comp = int(255 * (1 - speed_percent))
    fill_color = (red_comp, green_comp, 0)
    
    fill_width = int(bar_width * speed_percent)
    if fill_width > 0:
        pygame.draw.rect(win, fill_color, (bar_x, bar_y, fill_width, bar_height))
    
    pygame.draw.rect(win, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    speed_label = pygame.font.Font(None, 20).render("SPEED", True, WHITE)
    win.blit(speed_label, (bar_x - 45, bar_y))

def draw_button(surface, text, rect, font, is_selected=False):
    color = MENU_SELECTED_COLOR if is_selected else BUTTON_BG_COLOR
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BUTTON_BORDER_COLOR, rect, 3)
    
    text_color = BLACK if is_selected else WHITE
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def render_main_menu(win, font, menu_font, selected_index):
    # Pulsing Title
    draw_pulsing_text(win, "АРКАНОЇД", font, (WIDTH // 2, 100), CYAN, time.time())
    # title_text = font.render("АРКАНОЇД", True, CYAN)
    # title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
    # win.blit(title_text, title_rect)
    
    subtitle = pygame.font.Font(None, 32).render("✨ З ВІЗУАЛЬНИМИ ЕФЕКТАМИ ✨", True, YELLOW)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 160))
    win.blit(subtitle, subtitle_rect)
    
    menu_items = ["ПОЧАТИ ГРУ", "РЕКОРДИ", "ВИХІД"]
    button_width = 300
    button_height = 60
    button_spacing = 20
    start_y = 250
    
    for i, item in enumerate(menu_items):
        button_rect = pygame.Rect(
            WIDTH // 2 - button_width // 2,
            start_y + i * (button_height + button_spacing),
            button_width,
            button_height
        )
        draw_button(win, item, button_rect, menu_font, i == selected_index)
    
    # Інструкції з вказівкою поточного режиму
    mode_text = "Повноекранний режим" if is_fullscreen else "Віконний режим"
    instructions = [
        "Керування: Стрілки ← →",
        "Пауза: ESC або P",
        f"Режим: {mode_text} (F11 - перемкнути)",
        "ESC - вихід з повноекранного" if is_fullscreen else "ESC - вихід з гри"
    ]
    small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
    y_offset = HEIGHT - 120
    for instruction in instructions:
        text = small_font.render(instruction, True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, y_offset))
        win.blit(text, rect)
        y_offset += 30

def render_high_scores(win, font, menu_font):
    title_text = font.render("РЕКОРДИ", True, YELLOW)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 60))
    win.blit(title_text, title_rect)
    
    scores = high_score_manager.get_scores()
    
    if not scores:
        no_scores_text = menu_font.render("Рекордів поки немає", True, WHITE)
        no_scores_rect = no_scores_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(no_scores_text, no_scores_rect)
    else:
        headers = ["#", "РАХУНОК", "РІВЕНЬ", "ДАТА"]
        header_y = 120
        x_positions = [150, 300, 500, 620]
        
        small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        for i, header in enumerate(headers):
            text = small_font.render(header, True, CYAN)
            win.blit(text, (x_positions[i], header_y))
        
        y_offset = header_y + 40
        for i, score_data in enumerate(scores[:10]):
            rank_text = small_font.render(f"{i + 1}", True, WHITE)
            score_text = small_font.render(str(score_data['score']), True, WHITE)
            level_text = small_font.render(str(score_data['level']), True, WHITE)
            date_text = small_font.render(score_data['date'][:16], True, WHITE)
            
            win.blit(rank_text, (x_positions[0], y_offset))
            win.blit(score_text, (x_positions[1], y_offset))
            win.blit(level_text, (x_positions[2], y_offset))
            win.blit(date_text, (x_positions[3], y_offset))
            
            y_offset += 35
    
    back_text = menu_font.render("Натисніть ESC для повернення", True, MENU_COLOR)
    back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    win.blit(back_text, back_rect)

def render_pause_menu(win, font, menu_font, selected_index):
    pause_surface = pygame.Surface((WIDTH, HEIGHT))
    pause_surface.set_alpha(180)
    pause_surface.fill(BLACK)
    win.blit(pause_surface, (0, 0))
    
    title_text = font.render("ПАУЗА", True, YELLOW)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
    win.blit(title_text, title_rect)
    
    menu_items = ["ПРОДОВЖИТИ", "ГОЛОВНЕ МЕНЮ"]
    button_width = 300
    button_height = 60
    button_spacing = 20
    start_y = 280
    
    for i, item in enumerate(menu_items):
        button_rect = pygame.Rect(
            WIDTH // 2 - button_width // 2,
            start_y + i * (button_height + button_spacing),
            button_width,
            button_height
        )
        draw_button(win, item, button_rect, menu_font, i == selected_index)

def render_game_state_messages(win, font, large_font, game_state):
    if game_state == 'level_transition':
        message_text = large_font.render(f"РІВЕНЬ {level}", True, WHITE)
        instruction_text = font.render("Натисніть Enter", True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)

    elif game_state == 'game_over':
        draw_pulsing_text(win, "ГРА ЗАКІНЧЕНА", large_font, (WIDTH // 2, HEIGHT // 2 - 80), RED, time.time(), scale_range=(1.0, 1.2))
        # message_text = large_font.render("ГРА ЗАКІНЧЕНА", True, RED)
        score_text = font.render(f"Ваш рахунок: {score}", True, WHITE)
        instruction_text = font.render("Натисніть Enter для головного меню", True, WHITE)
        
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        
        # win.blit(message_text, message_rect)
        win.blit(score_text, score_rect)
        win.blit(instruction_text, instruction_rect)
        
        if high_score_manager.is_high_score(score):
            new_record_text = font.render("🏆 НОВИЙ РЕКОРД! 🏆", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            win.blit(new_record_text, new_record_rect)

# =============================================================================
# ОСНОВНИЙ КОД ГРИ
# =============================================================================

score = 0
lives = INITIAL_LIVES
level = 1
font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, LARGE_FONT_SIZE)
menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
game_over = False
game_state = 'main_menu'
menu_selection = 0

running = True
game_surface = pygame.Surface((WIDTH, HEIGHT))

while running:
    dt = clock.tick(60) / 1000.0  # Delta time в секундах
    current_time = time.time() - start_time
    
    game_surface.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # F11 - перемикання повноекранного режиму
            if event.key == pygame.K_F11:
                toggle_fullscreen()
            
            # ESC в головному меню (лише у віконному режимі) - вихід з повноекранного
            if game_state == 'main_menu':
                if event.key == pygame.K_ESCAPE and is_fullscreen:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and not is_fullscreen:
                    running = False
                if event.key == pygame.K_UP:
                    sound_manager.play_menu_move()
                    menu_selection = (menu_selection - 1) % 3
                elif event.key == pygame.K_DOWN:
                    sound_manager.play_menu_move()
                    menu_selection = (menu_selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    sound_manager.play_menu_select()
                    if menu_selection == 0:
                        initialize_game_data()
                        game_state = 'playing'
                    elif menu_selection == 1:
                        game_state = 'high_scores'
                    elif menu_selection == 2:
                        running = False
            
            elif game_state == 'high_scores':
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    game_state = 'main_menu'
            
            elif game_state == 'playing':
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    game_state = 'paused'
                    menu_selection = 0
            
            elif game_state == 'paused':
                if event.key == pygame.K_UP:
                    sound_manager.play_menu_move()
                    menu_selection = (menu_selection - 1) % 2
                elif event.key == pygame.K_DOWN:
                    sound_manager.play_menu_move()
                    menu_selection = (menu_selection + 1) % 2
                elif event.key == pygame.K_RETURN:
                    sound_manager.play_menu_select()
                    if menu_selection == 0:
                        game_state = 'playing'
                    elif menu_selection == 1:
                        game_state = 'main_menu'
                        menu_selection = 0
                elif event.key == pygame.K_ESCAPE:
                    game_state = 'playing'
            
            elif game_state == 'level_transition':
                if event.key == pygame.K_RETURN:
                    setup_level(level)
                    game_state = 'playing'
            
            elif game_state == 'game_over':
                if event.key == pygame.K_RETURN:
                    high_score_manager.add_score(score, level)
                    game_state = 'main_menu'
                    menu_selection = 0

    # Оновлюємо фон
    background.update(dt)
    
    # Оновлюємо ефекти
    screen_shake.update(dt)
    particle_system.update(dt)
    
    # Оновлюємо бонуси
    bonus_manager.update(dt)

    # Ігрова логіка
    if game_state == 'playing':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move(-PADDLE_SPEED, WIDTH)
        if keys[pygame.K_RIGHT]:
            paddle.move(PADDLE_SPEED, WIDTH)
            
        # Застосування ефектів бонусів
        # 1. Розмір платформи
        target_width = original_paddle_width * bonus_manager.get_paddle_modifier()
        if abs(paddle.width - target_width) > 1:
            paddle.set_width(int(target_width))
            
        # 2. Збирання бонусів
        collected_bonuses = bonus_manager.check_collection(paddle.rect)
        for bonus in collected_bonuses:
            sound_manager.play_powerup()
            particle_system.create_sparkle(bonus.rect.centerx, bonus.rect.centery, bonus.color)
            effect = bonus_manager.apply_bonus(bonus)
            
            # Обробка миттєвих ефектів
            if bonus.bonus_type == BonusType.EXTRA_LIFE:
                lives += 1
            elif bonus.bonus_type == BonusType.MULTI_BALL:
                activate_multiball()

        # Оновлення м'ячів
        balls_to_remove = []
        speed_modifier = bonus_manager.get_ball_speed_modifier()
        
        for i in range(len(balls)):
            b = balls[i]
            
            # Застосовуємо модифікатор швидкості (тимчасово змінюємо швидкість для оновлення)
            original_vx, original_vy = b.vx, b.vy
            b.vx *= speed_modifier
            b.vy *= speed_modifier
            
            b.update()
            
            # Повертаємо базову швидкість (щоб ефект не накопичувався експоненційно, якщо він застосовується щокадру)
            # Але тут логіка трохи складна. Якщо speed_modifier = 1.0, то все ок.
            # Якщо ми хочемо щоб м'яч рухався швидше, ми маємо змінювати позицію на більшу величину.
            # b.update() використовує b.vx, b.vy.
            # Краще просто відновити вектори, бо update вже змінив rect.
            b.vx, b.vy = original_vx, original_vy
            
            # Додаємо трейл
            if i == 0: # Трейл тільки для основного м'яча для продуктивності
                ball_trail.add_position(b.centerx, b.centery)
            
            # Відбиття від стін
            if b.left <= WALL_THICKNESS:
                b.rect.left = WALL_THICKNESS
                b.vx = abs(b.vx)
                sound_manager.play_wall_hit()
            elif b.right >= WIDTH - WALL_THICKNESS:
                b.rect.right = WIDTH - WALL_THICKNESS
                b.vx = -abs(b.vx)
                sound_manager.play_wall_hit()
            
            if b.top <= WALL_THICKNESS:
                b.rect.top = WALL_THICKNESS
                b.vy = abs(b.vy)
                sound_manager.play_wall_hit()

            # Відбиття від платформи
            if b.rect.colliderect(paddle.rect):
                if b.vy > 0: # Тільки якщо летить вниз
                    sound_manager.play_paddle_hit()
                    speed_before_bounce = math.sqrt(b.vx**2 + b.vy**2)

                    b.rect.bottom = paddle.top
                    
                    # Розрахунок кута відбиття на основі позиції удару
                    difference_from_center = b.centerx - paddle.centerx
                    normalized_difference = difference_from_center / (paddle.width / 2.0)
                    normalized_difference = max(-1.0, min(normalized_difference, 1.0))
                    
                    # Обчислюємо кут відбиття (від вертикалі)
                    bounce_angle_rad = normalized_difference * math.radians(MAX_BOUNCE_ANGLE_DEG)
                    
                    # Нові компоненти швидкості
                    new_vx = speed_before_bounce * math.sin(bounce_angle_rad)
                    new_vy = -abs(speed_before_bounce * math.cos(bounce_angle_rad))
                    
                    # Гарантуємо мінімальну вертикальну швидкість
                    min_vy = speed_before_bounce * MIN_VERTICAL_SPEED_RATIO
                    if abs(new_vy) < min_vy:
                        # Якщо вертикальна швидкість замала, коригуємо її
                        new_vy = -min_vy
                        # Перераховуємо vx щоб зберегти загальну швидкість
                        new_vx_sign = 1 if new_vx > 0 else -1
                        # Захист від помилок округлення
                        arg = max(0, speed_before_bounce**2 - new_vy**2)
                        new_vx = new_vx_sign * math.sqrt(arg)

                    b.vx = new_vx
                    b.vy = new_vy

            # Зіткнення з цеглинками
            for brick in bricks:
                if brick.visible and b.rect.colliderect(brick.rect):
                    # Перевіряємо тип м'яча для вогняного режиму
                    is_fire_ball = bonus_manager.has_active_effect(BonusType.FIRE_BALL)
                    
                    # Обробляємо удар
                    hit_result = brick.hit()
                    
                    if hit_result['destroyed']:
                        score += hit_result['points']
                        
                        # Ефекти знищення
                        particle_system.create_explosion(
                            brick.rect.centerx,
                            brick.rect.centery,
                            brick.original_color,
                            num_particles=25
                        )
                        particle_system.create_shockwave(brick.rect.centerx, brick.rect.centery, brick.original_color)
                        
                        # Вибухові цеглинки - ланцюгова реакція
                        if hit_result['explosive']:
                            sound_manager.play_explosion()
                            screen_shake.start(magnitude=5, duration=0.2)
                            explosion_targets = level_manager.get_explosion_targets(bricks, brick)
                            for target in explosion_targets:
                                target_result = target.hit()
                                if target_result['destroyed']:
                                    score += target_result['points']
                                    particle_system.create_explosion(
                                        target.rect.centerx,
                                        target.rect.centery,
                                        (255, 100, 0),
                                        num_particles=20
                                    )
                        
                        # Бонус
                        if hit_result['bonus_guaranteed']:
                            bonus = bonus_manager.create_random_bonus(
                                brick.rect.centerx,
                                brick.rect.centery
                            )
                            if bonus:
                                bonus_manager.add_bonus(bonus)
                        else:
                            bonus = bonus_manager.create_random_bonus(
                                brick.rect.centerx,
                                brick.rect.centery
                            )
                            bonus_manager.add_bonus(bonus)
                        
                        sound_manager.play_brick_hit()
                    else:
                        # Цеглинка не зруйнована (міцна або незнищенна)
                        if brick.brick_type == BrickType.UNBREAKABLE:
                            sound_manager.play_metal_hit()
                        else:
                            sound_manager.play_brick_hit()
                    
                    # Фізика відбиття (якщо не вогняний м'яч або незнищенна цеглинка)
                    if not is_fire_ball or brick.brick_type == BrickType.UNBREAKABLE:
                        ball_center_x = b.centerx
                        ball_center_y = b.centery
                        brick_center_x = brick.rect.centerx
                        brick_center_y = brick.rect.centery
                        
                        overlap_x = min(b.right - brick.rect.left, brick.rect.right - b.left)
                        overlap_y = min(b.bottom - brick.rect.top, brick.rect.bottom - b.top)
                        
                        if overlap_x < overlap_y:
                            b.vx = -b.vx
                            if ball_center_x < brick_center_x:
                                b.rect.right = brick.rect.left
                            else:
                                b.rect.left = brick.rect.right
                        else:
                            b.vy = -b.vy
                            if ball_center_y < brick_center_y:
                                b.rect.bottom = brick.rect.top
                            else:
                                b.rect.top = brick.rect.bottom
                    else:
                        # Вогняний м'яч - додаткові частинки
                        sound_manager.play_fire_hit()
                        particle_system.create_explosion(
                            brick.rect.centerx,
                            brick.rect.centery,
                            (255, 100, 0),
                            num_particles=15
                        )
                    break  # Тільки одна цеглинка за кадр

            # Втрата м'яча
            if b.bottom >= HEIGHT:
                balls_to_remove.append(i)
        
        # Видалення втрачених м'ячів (у зворотному порядку щоб не збити індекси)
        for index in sorted(balls_to_remove, reverse=True):
            balls.pop(index)
            
        # Якщо всі м'ячі втрачено
        if not balls:
            lives -= 1
            sound_manager.play_life_lost()
            screen_shake.start(magnitude=10, duration=0.4)
            if lives <= 0:
                sound_manager.play_game_over()
                game_state = 'game_over'
            else:
                reset_ball()
                ball_trail.clear()
                bonus_manager.clear()

        # Перевірка перемоги (тільки знищувані цеглинки)
        if game_state == 'playing':
             all_bricks_destroyed = True
             for brick in bricks:
                 if brick.visible and brick.can_destroy:
                     all_bricks_destroyed = False
                     break
             if all_bricks_destroyed:
                 sound_manager.play_level_complete()
                 level += 1
                 game_state = 'level_transition'

    # =============================================================================
    # ВІДРИСОВКА
    # =============================================================================

    if game_state == 'main_menu':
        background.draw(game_surface, current_time)
        render_main_menu(game_surface, large_font, menu_font, menu_selection)
    
    elif game_state == 'high_scores':
        background.draw(game_surface, current_time)
        render_high_scores(game_surface, large_font, menu_font)
    
    elif game_state in ['playing', 'paused', 'level_transition', 'game_over']:
        # Малюємо анімований фон
        background.draw(game_surface, current_time)
        
        # Відрисовка стін
        pygame.draw.rect(game_surface, WHITE, (0, 0, WALL_THICKNESS, HEIGHT))
        pygame.draw.rect(game_surface, WHITE, (WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))
        pygame.draw.rect(game_surface, WHITE, (0, 0, WIDTH, WALL_THICKNESS))

        # Відрисовка цеглинок
        for brick in bricks:
            brick.update(dt)
            brick.draw(game_surface, current_time)

        # Відрисовка платформи та м'ячів
        if game_state in ['playing', 'paused']:
            # Трейл (тільки для першого м'яча)
            ball_trail.draw(game_surface, RED, BALL_RADIUS)
            
            # 3D платформа
            paddle.draw(game_surface)
            
            # М'ячі
            for b in balls:
                b.draw(game_surface)
        
        # Відрисовка бонусів
        bonus_manager.draw_bonuses(game_surface, current_time)
        
        # Відрисовка частинок
        particle_system.draw(game_surface)

        # UI елементи
        render_ui(game_surface, font, large_font)
        
        # Повідомлення станів
        render_game_state_messages(game_surface, font, large_font, game_state)
        
        # Меню паузи
        if game_state == 'paused':
            render_pause_menu(game_surface, large_font, menu_font, menu_selection)

    # Застосування трансформації та тремтіння
    scale, offset_x, offset_y = get_display_transform()
    shake_x, shake_y = screen_shake.get_offset()
    
    final_offset_x = offset_x + shake_x
    final_offset_y = offset_y + shake_y
    
    if is_fullscreen and scale != 1.0:
        win.fill(BLACK)
        scaled_surface = pygame.transform.scale(game_surface, 
                                              (int(WIDTH * scale), int(HEIGHT * scale)))
        win.blit(scaled_surface, (final_offset_x, final_offset_y))
    else:
        win.blit(game_surface, (shake_x, shake_y))

    pygame.display.flip()

pygame.quit()
