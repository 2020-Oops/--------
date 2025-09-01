"""
Арканоид - классическая игра-головоломка
Управление: стрелки влево/вправо для движения платформы
Цель: разбить все кирпичи, отбивая мяч
"""
import pygame
import sys
import os
import math
import random

# =============================================================================
# КОНСТАНТЫ ИГРЫ
# =============================================================================

# Размеры окна
WIDTH, HEIGHT = 900, 600

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Параметры платформы
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 10
PADDLE_SPEED = 10

# Параметры мяча
BALL_RADIUS = 15
BASE_BALL_SPEED = math.sqrt(5**2 + 5**2)  # sqrt(50) ≈ 7.07
SPEED_INCREASE_PER_LEVEL = 0.7
MAX_BALL_SPEED = 12  # Максимальная скорость мяча для предотвращения туннелирования

# Параметры кирпичей
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = 55
BRICK_HEIGHT = 20
BRICK_PADDING = 5

# Игровые параметры
INITIAL_LIVES = 3
SCORE_PER_BRICK = 10
MAX_HORIZONTAL_BOUNCE_SPEED = 10

# Параметры UI
FONT_SIZE = 42
LARGE_FONT_SIZE = 100
HEART_SIZE = 35
HEART_PADDING = 8

# Параметры стен
WALL_THICKNESS = 3

# Файлы ресурсов
MUSIC_FILE = 'chiptune-ending-212716.mp3'
HEART_IMAGE_FILE = 'heart.png'
MUSIC_VOLUME = 0.5

# =============================================================================
# ИНИЦИАЛИЗАЦИЯ PYGAME
# =============================================================================

pygame.init()
# Отключаем звук в headless среде
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False
    print("Аудио недоступно в данной среде")

# =============================================================================
# ЗАГРУЗКА РЕСУРСОВ
# =============================================================================

def load_music():
    """Загружает и воспроизводит фоновую музыку"""
    if not AUDIO_AVAILABLE:
        print("Аудио недоступно - музыка отключена")
        return False
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(loops=-1)
        print("Музыка успешно загружена.")
        return True
    except pygame.error as e:
        print(f"Ошибка загрузки музыкального файла: {e}")
        return False

def load_heart_image():
    """Загружает изображение сердечка для отображения жизней"""
    try:
        heart_image = pygame.image.load(HEART_IMAGE_FILE).convert_alpha()
        heart_image = pygame.transform.scale(heart_image, (HEART_SIZE, HEART_SIZE))
        return heart_image
    except pygame.error as e:
        print(f"Не удалось загрузить изображение сердца: {e}")
        print("Используется альтернативное изображение сердца (круг).")
        # Создаем альтернативное изображение сердца
        heart_image = pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(heart_image, RED, (HEART_SIZE // 2, HEART_SIZE // 2), HEART_SIZE // 2 - 2)
        pygame.draw.circle(heart_image, WHITE, (HEART_SIZE // 2, HEART_SIZE // 2), HEART_SIZE // 2 - 2, 2)
        return heart_image

# =============================================================================
# ИНИЦИАЛИЗАЦИЯ ИГРЫ
# =============================================================================

# Состояние полноэкранного режима
is_fullscreen = False
windowed_size = (WIDTH, HEIGHT)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид")

# Загрузка ресурсов
music_loaded_successfully = load_music()
heart_image = load_heart_image()

# Вычисляемые позиции
initial_paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
initial_paddle_y = HEIGHT - 40
paddle = pygame.Rect(initial_paddle_x, initial_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)

initial_ball_x = paddle.centerx - BALL_RADIUS
initial_ball_y = paddle.top - BALL_RADIUS * 2
ball = pygame.Rect(initial_ball_x, initial_ball_y, BALL_RADIUS * 2, BALL_RADIUS * 2)

# Параметры направления мяча
initial_ball_direction_x = 5
initial_ball_direction_y = -5
initial_direction_magnitude = math.sqrt(initial_ball_direction_x**2 + initial_ball_direction_y**2)
normalized_initial_vx = initial_ball_direction_x / initial_direction_magnitude if initial_direction_magnitude > 0 else 0
normalized_initial_vy = initial_ball_direction_y / initial_direction_magnitude if initial_direction_magnitude > 0 else -1

ball_speed_x = 0
ball_speed_y = 0
current_speed_magnitude = 0

clock = pygame.time.Clock()

# Параметры кирпичей
total_bricks_width = (BRICK_COLS * BRICK_WIDTH) + ((BRICK_COLS - 1) * BRICK_PADDING if BRICK_COLS > 1 else 0)
BRICK_OFFSET_LEFT = (WIDTH - total_bricks_width) // 2
BRICK_OFFSET_TOP = 60

bricks = []

# =============================================================================
# ФУНКЦИИ ИГРЫ
# =============================================================================

def create_bricks():
    """Создает массив кирпичей разных цветов"""
    bricks_list = []
    for row in range(BRICK_ROWS):
        if row < 1:
            brick_color = YELLOW
        elif row < 3:
            brick_color = GREEN
        else:
            brick_color = BLUE

        for col in range(BRICK_COLS):
            brick_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            brick_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            brick_rect = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
            bricks_list.append({'rect': brick_rect, 'color': brick_color, 'visible': True})
    return bricks_list

def setup_level(level_num):
    """Настраивает параметры для указанного уровня"""
    global ball, ball_speed_x, ball_speed_y, paddle, bricks, current_speed_magnitude, level

    current_speed_magnitude = BASE_BALL_SPEED + (level_num - 1) * SPEED_INCREASE_PER_LEVEL
    # Ограничиваем максимальную скорость для предотвращения туннелирования
    current_speed_magnitude = min(current_speed_magnitude, MAX_BALL_SPEED)

    ball_speed_x = normalized_initial_vx * current_speed_magnitude
    ball_speed_y = normalized_initial_vy * current_speed_magnitude

    paddle.x = initial_paddle_x
    paddle.y = initial_paddle_y

    ball.x = initial_ball_x
    ball.y = initial_ball_y

    bricks = create_bricks()

def toggle_fullscreen():
    """Переключает полноэкранный режим"""
    global win, is_fullscreen
    
    if is_fullscreen:
        # Переключение в оконный режим
        win = pygame.display.set_mode(windowed_size)
        is_fullscreen = False
    else:
        # Переключение в полноэкранный режим
        win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        is_fullscreen = True
    
    pygame.display.set_caption("Арканоид")

def get_display_transform():
    """Возвращает параметры трансформации для отображения игры"""
    if not is_fullscreen:
        # В оконном режиме - без трансформации
        return 1.0, 0, 0
    
    # В полноэкранном режиме - вычисляем масштаб и смещение
    screen_width, screen_height = win.get_size()
    game_width, game_height = WIDTH, HEIGHT
    
    # Вычисляем масштаб для сохранения соотношения сторон
    scale_x = screen_width / game_width
    scale_y = screen_height / game_height
    scale = min(scale_x, scale_y)  # Используем меньший масштаб для сохранения пропорций
    
    # Вычисляем смещение для центрирования
    scaled_width = game_width * scale
    scaled_height = game_height * scale
    offset_x = (screen_width - scaled_width) // 2
    offset_y = (screen_height - scaled_height) // 2
    
    return scale, offset_x, offset_y

def initialize_game_data():
    """Инициализирует все игровые данные (первый старт или полный перезапуск)"""
    global score, lives, level, game_over
    score = 0
    lives = INITIAL_LIVES
    level = 1
    game_over = False
    setup_level(1)

def render_ui(win, font, large_font):
    """Отрисовывает элементы пользовательского интерфейса"""
    # Отображение счета
    score_text = font.render(f"Счет: {score}", True, WHITE)
    win.blit(score_text, (10, 10))
    
    # Отображение уровня
    level_text = font.render(f"Уровень: {level}", True, WHITE)
    win.blit(level_text, (10, 50))
    
    # Отображение жизней в виде сердечек
    hearts_total_width = INITIAL_LIVES * HEART_SIZE + (INITIAL_LIVES - 1) * HEART_PADDING
    heart_start_x = WIDTH - hearts_total_width - 15
    heart_start_y = 15
    
    for i in range(lives):
        heart_x = heart_start_x + i * (HEART_SIZE + HEART_PADDING)
        win.blit(heart_image, (heart_x, heart_start_y))

def render_game_state_messages(win, font, large_font, game_state):
    """Отрисовывает сообщения состояний игры"""
    if game_state == 'waiting_to_start':
        message_text = large_font.render("АРКАНОИД", True, WHITE)
        instruction_text = font.render("Нажмите Enter, чтобы начать", True, WHITE)
        fullscreen_text = font.render("F11 - полноэкранный режим", True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        fullscreen_rect = fullscreen_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)
        win.blit(fullscreen_text, fullscreen_rect)

    elif game_state == 'level_transition':
        message_text = large_font.render(f"УРОВЕНЬ {level}", True, WHITE)
        instruction_text = font.render("Нажмите Enter, чтобы продолжить", True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)

    elif game_state == 'game_over':
        message_text = large_font.render("ИГРА ЗАКОНЧЕНА", True, RED)
        instruction_text = font.render("Нажмите Enter, чтобы перезапустить", True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)

# =============================================================================
# ОСНОВНОЙ КОД ИГРЫ
# =============================================================================

# Игровые переменные
score = 0
lives = INITIAL_LIVES
level = 1
font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, LARGE_FONT_SIZE)
game_over = False
game_state = 'waiting_to_start'

running = True
# Создаем виртуальную поверхность для игры (всегда стандартного размера)
game_surface = pygame.Surface((WIDTH, HEIGHT))

while running:
    # Очищаем виртуальную поверхность игры
    game_surface.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Обработка нажатия клавиши F11 для полноэкранного режима
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE and is_fullscreen:
                toggle_fullscreen()

        # Обработка событий в зависимости от состояния игры
        if game_state == 'waiting_to_start':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    initialize_game_data()
                    game_state = 'playing'

        elif game_state == 'level_transition':
             if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    setup_level(level)
                    game_state = 'playing'

        elif game_state == 'game_over':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = 'waiting_to_start'

    # Игровая логика выполняется только в состоянии 'playing'
    if game_state == 'playing':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-PADDLE_SPEED, 0)
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.move_ip(PADDLE_SPEED, 0)

        # Движение мяча
        ball.x += ball_speed_x
        ball.y += ball_speed_y
        
        # Убеждаемся, что мяч не выходит за границы и не застревает в стенах
        if ball.left <= WALL_THICKNESS:
            ball.left = WALL_THICKNESS
            ball_speed_x = abs(ball_speed_x)
        elif ball.right >= WIDTH - WALL_THICKNESS:
            ball.right = WIDTH - WALL_THICKNESS
            ball_speed_x = -abs(ball_speed_x)
        
        if ball.top <= WALL_THICKNESS:
            ball.top = WALL_THICKNESS
            ball_speed_y = abs(ball_speed_y)

        # Отражение от платформы с сохранением скорости
        if ball.colliderect(paddle):
            if ball_speed_y > 0:  # Мяч движется вниз
                speed_before_bounce = current_speed_magnitude

                ball.bottom = paddle.top
                new_ball_speed_y_direction = -abs(ball_speed_y)

                difference_from_center = ball.centerx - paddle.centerx
                normalized_difference = difference_from_center / (paddle.width / 2.0)
                normalized_difference = max(-1.0, min(normalized_difference, 1.0))

                raw_new_ball_speed_x = normalized_difference * MAX_HORIZONTAL_BOUNCE_SPEED

                magnitude_of_new_vector = math.sqrt(raw_new_ball_speed_x**2 + new_ball_speed_y_direction**2)

                if magnitude_of_new_vector > 0:
                    scaling_factor = speed_before_bounce / magnitude_of_new_vector
                    ball_speed_x = raw_new_ball_speed_x * scaling_factor
                    ball_speed_y = new_ball_speed_y_direction * scaling_factor

        # Столкновение мяча с кирпичами
        all_bricks_destroyed = True
        for i in range(len(bricks)):
            brick_data = bricks[i]
            if brick_data['visible']:
                all_bricks_destroyed = False
                if ball.colliderect(brick_data['rect']):
                    brick_data['visible'] = False
                    score += SCORE_PER_BRICK

                    # Определяем с какой стороны кирпича произошло столкновение
                    ball_center_x = ball.centerx
                    ball_center_y = ball.centery
                    brick_center_x = brick_data['rect'].centerx
                    brick_center_y = brick_data['rect'].centery
                    
                    # Вычисляем перекрытие по осям
                    overlap_x = min(ball.right - brick_data['rect'].left, brick_data['rect'].right - ball.left)
                    overlap_y = min(ball.bottom - brick_data['rect'].top, brick_data['rect'].bottom - ball.top)
                    
                    # Столкновение произошло с той стороны, где перекрытие меньше
                    if overlap_x < overlap_y:
                        # Столкновение с левой или правой стороной кирпича
                        ball_speed_x = -ball_speed_x
                        if ball_center_x < brick_center_x:
                            # Столкновение с левой стороной кирпича
                            ball.right = brick_data['rect'].left
                        else:
                            # Столкновение с правой стороной кирпича
                            ball.left = brick_data['rect'].right
                    else:
                        # Столкновение с верхней или нижней стороной кирпича
                        ball_speed_y = -ball_speed_y
                        if ball_center_y < brick_center_y:
                            # Столкновение с верхней стороной кирпича
                            ball.bottom = brick_data['rect'].top
                        else:
                            # Столкновение с нижней стороной кирпича
                            ball.top = brick_data['rect'].bottom

                    break  # Обрабатываем только одно столкновение за кадр

        # Проверка победы
        if game_state == 'playing':
             all_bricks_destroyed = True
             for b in bricks:
                 if b['visible']:
                     all_bricks_destroyed = False
                     break
             if all_bricks_destroyed:
                 level += 1
                 game_state = 'level_transition'

        # Логика потери жизни
        if ball.bottom >= HEIGHT:
            lives -= 1
            if lives <= 0:
                game_state = 'game_over'
            else:
                # Сброс мяча и платформы в начальную позицию для текущего уровня
                ball.x = initial_ball_x
                ball.y = initial_ball_y
                paddle.x = initial_paddle_x
                paddle.y = initial_paddle_y
                # Пересчитываем компоненты скорости
                current_speed_magnitude = BASE_BALL_SPEED + (level - 1) * SPEED_INCREASE_PER_LEVEL
                current_speed_magnitude = min(current_speed_magnitude, MAX_BALL_SPEED)
                ball_speed_x = normalized_initial_vx * current_speed_magnitude
                ball_speed_y = normalized_initial_vy * current_speed_magnitude

    # =============================================================================
    # ОТРИСОВКА
    # =============================================================================

    # Отрисовка стен
    pygame.draw.rect(game_surface, WHITE, (0, 0, WALL_THICKNESS, HEIGHT))  # Левая стена
    pygame.draw.rect(game_surface, WHITE, (WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))  # Правая стена
    pygame.draw.rect(game_surface, WHITE, (0, 0, WIDTH, WALL_THICKNESS))  # Верхняя стена

    # Отрисовка кирпичей
    for brick_data in bricks:
        if brick_data['visible']:
            pygame.draw.rect(game_surface, brick_data['color'], brick_data['rect'])

    # Отрисовка платформы и мяча (только в состоянии 'playing')
    if game_state == 'playing':
        pygame.draw.rect(game_surface, WHITE, paddle)
        pygame.draw.ellipse(game_surface, RED, ball)

    # Отрисовка UI элементов
    render_ui(game_surface, font, large_font)
    
    # Отрисовка сообщений состояний игры
    render_game_state_messages(game_surface, font, large_font, game_state)

    # Применение трансформации для отображения
    scale, offset_x, offset_y = get_display_transform()
    
    if is_fullscreen and scale != 1.0:
        # В полноэкранном режиме: очищаем экран и масштабируем/центрируем игру
        win.fill(BLACK)
        scaled_surface = pygame.transform.scale(game_surface, 
                                              (int(WIDTH * scale), int(HEIGHT * scale)))
        win.blit(scaled_surface, (offset_x, offset_y))
    else:
        # В оконном режиме: просто копируем поверхность игры
        win.blit(game_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()