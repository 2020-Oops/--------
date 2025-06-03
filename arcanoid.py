import pygame
import sys
import os
import math
import random

pygame.init()
pygame.mixer.init()

# ... после pygame.mixer.init() ...

try:
    # Укажите путь к вашему музыкальному файлу
    pygame.mixer.music.load('chiptune-ending-212716.mp3')
    # Устанавливаем громкость (от 0.0 до 1.0)
    pygame.mixer.music.set_volume(0.5) # 50% громкости
    print("Музыка успешно загружена.")
    music_loaded_successfully = True
except pygame.error as e:
    print(f"Ошибка загрузки музыкального файла: {e}")
    music_loaded_successfully = False

# ... после успешной загрузки музыки ...

if music_loaded_successfully:
    # Начать воспроизведение музыки, -1 означает бесконечное повторение
    pygame.mixer.music.play(loops=-1)

# ==== Змінено: Нові розміри вікна ====
WIDTH, HEIGHT = 900, 600 # Збільшені розміри вікна
# ====================================

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоїд")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255) # Колір для цеглин
GREEN = (0, 255, 0) # Можна використовувати для іншого типу цеглин або платформи
YELLOW = (255, 255, 0) # Додамо жовтий для прикладу

# Параметри платформи та м’яча
paddle_width = 120 # Ширина платформи залишається такою ж
paddle_height = 10 # Висота платформи залишається такою ж
# Зберігаємо початкову позицію платформи відносно нових розмірів
initial_paddle_x = WIDTH // 2 - paddle_width // 2
initial_paddle_y = HEIGHT - 40 # Трохи більший відступ від нижнього краю
paddle = pygame.Rect(initial_paddle_x, initial_paddle_y, paddle_width, paddle_height)

ball_radius = 15 # Радіус м'яча залишається таким же

# Початкова позиція м'яча над платформою (розраховується відносно нової позиції платформи)
initial_ball_x = paddle.centerx - ball_radius
initial_ball_y = paddle.top - ball_radius * 2 # ball_radius * 2 = висота м'яча
ball = pygame.Rect(initial_ball_x, initial_ball_y, ball_radius * 2, ball_radius * 2)


# ==== Параметри швидкості м'яча ====
# Базова швидкість залишається тією ж, але вікно більше, тому м'яч здаватиметься повільнішим
# Якщо хочете зберегти відчуття швидкості, можна збільшити base_initial_speed_magnitude
base_initial_speed_magnitude = math.sqrt(5**2 + 5**2) # sqrt(50) ≈ 7.07
speed_increase_per_level = 0.7 # Можна трохи збільшити приріст швидкості за рівень

initial_ball_direction_x = 5
initial_ball_direction_y = -5
initial_direction_magnitude = math.sqrt(initial_ball_direction_x**2 + initial_ball_direction_y**2)
normalized_initial_vx = initial_ball_direction_x / initial_direction_magnitude if initial_direction_magnitude > 0 else 0
normalized_initial_vy = initial_ball_direction_y / initial_direction_magnitude if initial_direction_magnitude > 0 else -1

ball_speed_x = 0
ball_speed_y = 0
current_speed_magnitude = 0

clock = pygame.time.Clock()

# Параметри цеглин
BRICK_ROWS = 5 # Кількість рядків залишається такою ж
BRICK_COLS = 10 # Кількість стовпців залишається такою ж
BRICK_WIDTH = 55 # Ширина цеглини залишається такою ж
BRICK_HEIGHT = 20 # Висота цеглини залишається такою ж
BRICK_PADDING = 5 # Відступ між цеглинами залишається таким же

# ==== Змінено: Розрахунок офсетів цеглин для центрування в новому вікні ====
total_bricks_width = (BRICK_COLS * BRICK_WIDTH) + ((BRICK_COLS - 1) * BRICK_PADDING if BRICK_COLS > 1 else 0)
BRICK_OFFSET_LEFT = (WIDTH - total_bricks_width) // 2 # Центрування по новій ширині
BRICK_OFFSET_TOP = 60 # Збільшимо відступ зверху, щоб не накладалося на текст UI
# =======================================================================

bricks = []

# Функція для створення цеглин
def create_bricks():
    bricks_list = []
    for row in range(BRICK_ROWS):
        if row < 1:
            brick_color = YELLOW
        elif row < 3:
            brick_color = GREEN
        else:
            brick_color = BLUE

        for col in range(BRICK_COLS):
            # ==== Змінено: Розрахунок позиції цеглин з новим BRICK_OFFSET_LEFT та BRICK_OFFSET_TOP ====
            brick_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            brick_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            # =======================================================================================
            brick_rect = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
            bricks_list.append({'rect': brick_rect, 'color': brick_color, 'visible': True})
    return bricks_list


# ==== Ігрові змінні (рахунок, життя, рівень) ====
initial_lives = 3
score = 0
lives = initial_lives
level = 1
# ==== Змінено: Збільшені розміри шрифтів ====
font = pygame.font.Font(None, 42) # Трохи більший шрифт для UI
large_font = pygame.font.Font(None, 100) # Значно більший шрифт для повідомлень станів
# =========================================
score_per_brick = 10
game_over = False

# Завантаження зображення серця
try:
    heart_image = pygame.image.load('heart.png').convert_alpha()
    heart_size = 35 # Можна трохи збільшити розмір іконки серця
    heart_image = pygame.transform.scale(heart_image, (heart_size, heart_size))
except pygame.error as e:
    print(f"Не вдалося завантажити зображення серця: {e}")
    print("Використовується альтернативне зображення серця (коло).")
    heart_size = 35
    heart_image = pygame.Surface((heart_size, heart_size), pygame.SRCALPHA)
    pygame.draw.circle(heart_image, RED, (heart_size // 2, heart_size // 2), heart_size // 2 - 2)
    pygame.draw.circle(heart_image, WHITE, (heart_size // 2, heart_size // 2), heart_size // 2 - 2, 2)

heart_padding = 8 # Можна збільшити відступ між серцями
hearts_total_width = initial_lives * heart_size + (initial_lives - 1) * heart_padding
# ==== Змінено: Розрахунок позиції сердець відносно нової ширини ====
heart_start_x = WIDTH - hearts_total_width - 15 # Збільшений відступ від правого краю
heart_start_y = 15 # Збільшений відступ від верхнього краю
# =================================================================

# ==== Функція для налаштування рівня ====
def setup_level(level_num):
    global ball, ball_speed_x, ball_speed_y, paddle, bricks, current_speed_magnitude, level

    current_speed_magnitude = base_initial_speed_magnitude + (level_num - 1) * speed_increase_per_level

    ball_speed_x = normalized_initial_vx * current_speed_magnitude
    ball_speed_y = normalized_initial_vy * current_speed_magnitude

    paddle.x = initial_paddle_x
    paddle.y = initial_paddle_y

    ball.x = initial_ball_x
    ball.y = initial_ball_y

    bricks = create_bricks()


# ==== Функція для ініціалізації гри (перший старт або повний перезапуск) ====
def initialize_game_data():
     global score, lives, level, game_over
     score = 0
     lives = initial_lives
     level = 1
     game_over = False

     setup_level(1)

# ===========================================================================

# ==== Параметри для відбиття від платформи ====
# Можна трохи збільшити, якщо відчувається повільніше
max_horizontal_bounce_speed = 10
# ============================================

# ==== Змінна стану гри ====
game_state = 'waiting_to_start'
# ========================

running = True
while running:
    win.fill(BLACK) # Заливка фону

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ==== Обробка подій залежно від стану гри ====
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
        # ============================================

    # ==== Ігрова логіка, що виконується тільки у стані 'playing' ====
    if game_state == 'playing':
        keys = pygame.key.get_pressed()
        # ==== Змінено: Перевірка меж руху платформи відносно нової ширини ====
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-10, 0)
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.move_ip(10, 0)
        # =================================================================

        # Рух м’яча
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # ==== Змінено: Відбиття від бічних стінок відносно нової ширини ====
        if ball.left <= 0:
            ball.left = 0
            ball_speed_x = -ball_speed_x
        elif ball.right >= WIDTH:
            ball.right = WIDTH
            ball_speed_x = -ball_speed_x
        # ===============================================================

        # Відбиття від верхньої стінки (верхня межа залишається 0)
        if ball.top <= 0:
            ball.top = 0
            ball_speed_y = -ball_speed_y

        # Відбиття від платформи зі збереженням швидкості
        if ball.colliderect(paddle):
            if ball_speed_y > 0: # М'яч рухається вниз
                speed_before_bounce = current_speed_magnitude

                ball.bottom = paddle.top
                new_ball_speed_y_direction = -abs(ball_speed_y)

                difference_from_center = ball.centerx - paddle.centerx
                normalized_difference = difference_from_center / (paddle.width / 2.0)
                normalized_difference = max(-1.0, min(normalized_difference, 1.0))

                raw_new_ball_speed_x = normalized_difference * max_horizontal_bounce_speed

                magnitude_of_new_vector = math.sqrt(raw_new_ball_speed_x**2 + new_ball_speed_y_direction**2)

                if magnitude_of_new_vector > 0:
                    scaling_factor = speed_before_bounce / magnitude_of_new_vector
                    ball_speed_x = raw_new_ball_speed_x * scaling_factor
                    ball_speed_y = new_ball_speed_y_direction * scaling_factor


        # Зіткнення м'яча з цеглинами
        all_bricks_destroyed = True
        for i in range(len(bricks)):
            brick_data = bricks[i]
            if brick_data['visible']:
                all_bricks_destroyed = False
                if ball.colliderect(brick_data['rect']):
                    prev_ball_speed_y = ball_speed_y
                    brick_data['visible'] = False
                    score += score_per_brick

                    ball_speed_y = -ball_speed_y

                    if prev_ball_speed_y > 0:
                         ball.bottom = brick_data['rect'].top
                    elif prev_ball_speed_y < 0:
                         ball.top = brick_data['rect'].bottom

                    break # Обробляємо лише одне зіткнення з цеглиною за кадр


        # Перевірка перемоги
        if game_state == 'playing':
             all_bricks_destroyed = True
             for b in bricks:
                 if b['visible']:
                     all_bricks_destroyed = False
                     break
             if all_bricks_destroyed:
                 level += 1
                 game_state = 'level_transition'

        # ==== Змінено: Логіка втрати життя відносно нової висоти ====
        if ball.bottom >= HEIGHT:
            lives -= 1
            if lives <= 0:
                game_state = 'game_over'
            else:
                # Скидання м'яча та платформи в початкову позицію для поточного рівня
                ball.x = initial_ball_x
                ball.y = initial_ball_y
                paddle.x = initial_paddle_x
                paddle.y = initial_paddle_y
                # Швидкість залишається та, що відповідає поточному рівню
                # current_speed_magnitude вже правильно розраховано для цього рівня
                # Перераховуємо компоненти швидкості, зберігаючи початковий напрямок
                # (або можна зробити випадковим при втраті життя)
                current_speed_magnitude = base_initial_speed_magnitude + (level - 1) * speed_increase_per_level # Перераховуємо ще раз на всяк випадок
                initial_direction_magnitude = math.sqrt(initial_ball_direction_x**2 + initial_ball_direction_y**2)
                normalized_initial_vx = initial_ball_direction_x / initial_direction_magnitude if initial_direction_magnitude > 0 else 0
                normalized_initial_vy = initial_ball_direction_y / initial_direction_magnitude if initial_direction_magnitude > 0 else -1
                ball_speed_x = normalized_initial_vx * current_speed_magnitude
                ball_speed_y = normalized_initial_vy * current_speed_magnitude
        # ==========================================================


    # ==== Малювання залежно від стану гри ====

    # Малювання цеглин (завжди)
    for brick_data in bricks:
        if brick_data['visible']:
            pygame.draw.rect(win, brick_data['color'], brick_data['rect'])

    # Малювання платформи та м’яча (тільки у стані 'playing')
    if game_state == 'playing':
        pygame.draw.rect(win, WHITE, paddle)
        pygame.draw.ellipse(win, RED, ball)

    # Відображення рахунку та життів (завжди)
    score_text = font.render(f"Рахунок: {score}", True, WHITE)
    win.blit(score_text, (10, 10))

    # Відображення іконок життів (завжди)
    for i in range(lives):
        heart_x = heart_start_x + i * (heart_size + heart_padding)
        win.blit(heart_image, (heart_x, heart_start_y))

    # Відображення рівня (завжди)
    level_text = font.render(f"Рівень: {level}", True, WHITE)
    win.blit(level_text, (10, 50)) # Трохи нижче, враховуючи більший шрифт UI


    # Відображення повідомлень станів (центруються автоматично завдяки .get_rect(center=...))
    if game_state == 'waiting_to_start':
        message_text = large_font.render("АРКАНОЇД", True, WHITE)
        instruction_text = font.render("Натисніть Enter, щоб почати", True, WHITE)
        # ==== Змінено: Центрування відносно нової висоти ====
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)) # Збільшимо вертикальний відступ
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        # =================================================
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)

    elif game_state == 'level_transition':
        message_text = large_font.render(f"РІВЕНЬ {level}", True, WHITE)
        instruction_text = font.render("Натисніть Enter, щоб продовжити", True, WHITE)
        # ==== Змінено: Центрування відносно нової висоти ====
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        # =================================================
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)

    elif game_state == 'game_over':
        message_text = large_font.render("ГРА ЗАКІНЧЕНА", True, RED)
        instruction_text = font.render("Натисніть Enter, щоб перезапустити", True, WHITE)
        # ==== Змінено: Центрування відносно нової висоти ====
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        # =================================================
        win.blit(message_text, message_rect)
        win.blit(instruction_text, instruction_rect)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()