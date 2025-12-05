"""
Арканоїд - класична гра с візуальними ефектами та бонусами
Керування: стрілки вліво/вправо для руху платформи
Мета: розбити всі цеглини, відбиваючи м'яч
"""
import pygame
import sys
import math
import time
from high_scores import HighScoreManager
from particle_system import ParticleSystem, TrailEffect, ScreenShake
from graphics_effects import AnimatedBackground, draw_neon_heart
from bonus_system import BonusManager
from sound_manager import SoundManager
from brick_system import LevelManager
from entities import Paddle, Ball
from states import (
    StateManager, MainMenuState, HighScoresState, PauseState,
    LevelTransitionState, GameOverState, PlayingState
)

from game_config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WHITE, BLACK, RED,
    PADDLE_WIDTH, PADDLE_HEIGHT,
    BALL_RADIUS,
    BRICK_ROWS, BRICK_COLS, BRICK_WIDTH, BRICK_HEIGHT, BRICK_PADDING,
    INITIAL_LIVES, SCORE_PER_BRICK,
    FONT_SIZE, LARGE_FONT_SIZE,
    WALL_THICKNESS,
    MUSIC_FILE, HIGH_SCORES_FILE,
    MUSIC_VOLUME,
    NEON_THEME, BASE_BALL_SPEED, MAX_BALL_SPEED, SPEED_INCREASE_PER_LEVEL
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
# GAME CONTEXT CLASS
# =============================================================================

class GameContext:
    """Контекст гри - зберігає всі дані та менеджери"""
    
    def __init__(self):
        # Вікно та режим
        self.is_fullscreen = True
        self.windowed_size = (WIDTH, HEIGHT)
        self.win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Арканоїд - Візуальна версія")
        
        # Менеджери
        self.high_score_manager = HighScoreManager(HIGH_SCORES_FILE)
        self.sound_manager = SoundManager()
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.ball_trail = TrailEffect(max_length=7)
        self.background = AnimatedBackground(WIDTH, HEIGHT, num_stars=100)
        self.bonus_manager = BonusManager()
        
        # Параметри цеглинок
        total_bricks_width = (BRICK_COLS * BRICK_WIDTH) + ((BRICK_COLS - 1) * BRICK_PADDING if BRICK_COLS > 1 else 0)
        brick_offset_left = (WIDTH - total_bricks_width) // 2
        brick_offset_top = 60
        self.level_manager = LevelManager(BRICK_WIDTH, BRICK_HEIGHT, BRICK_PADDING, brick_offset_left, brick_offset_top)
        
        # Ігрові об'єкти
        self.initial_paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
        self.initial_paddle_y = HEIGHT - 40
        self.original_paddle_width = PADDLE_WIDTH
        self.paddle = Paddle(self.initial_paddle_x, self.initial_paddle_y)
        
        self.initial_ball_x = self.paddle.centerx - BALL_RADIUS
        self.initial_ball_y = self.paddle.top - BALL_RADIUS * 2
        
        # Параметри напрямку м'яча
        initial_ball_direction_x = 5
        initial_ball_direction_y = -5
        initial_direction_magnitude = math.sqrt(initial_ball_direction_x**2 + initial_ball_direction_y**2)
        self.normalized_initial_vx = initial_ball_direction_x / initial_direction_magnitude if initial_direction_magnitude > 0 else 0
        self.normalized_initial_vy = initial_ball_direction_y / initial_direction_magnitude if initial_direction_magnitude > 0 else -1
        
        self.balls = []
        self.bricks = []
        self.current_speed_magnitude = 0
        
        # Ігрові дані
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        
        # Час
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.current_time = 0
        
        # Поверхня гри
        self.game_surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Контроль виконання
        self.running = True
        
        # Завантаження музики
        self.load_music()
    
    def load_music(self):
        """Завантажує фонову музику"""
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
    
    def toggle_fullscreen(self):
        """Перемикає повноекранний режим"""
        if self.is_fullscreen:
            self.win = pygame.display.set_mode(self.windowed_size)
            self.is_fullscreen = False
        else:
            self.win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
        pygame.display.set_caption("Арканоїд - Візуальна версія")
    
    def get_display_transform(self):
        """Повертає параметри трансформації для масштабування"""
        if not self.is_fullscreen:
            return 1.0, 0, 0
        
        screen_width, screen_height = self.win.get_size()
        game_width, game_height = WIDTH, HEIGHT
        
        scale_x = screen_width / game_width
        scale_y = screen_height / game_height
        scale = min(scale_x, scale_y)
        
        scaled_width = game_width * scale
        scaled_height = game_height * scale
        offset_x = (screen_width - scaled_width) // 2
        offset_y = (screen_height - scaled_height) // 2
        
        return scale, offset_x, offset_y
    
    def initialize_game_data(self):
        """Ініціалізує дані для нової гри"""
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.particle_system.clear()
        self.ball_trail.clear()
        self.bonus_manager.clear()
        self.setup_level(1)
    
    def setup_level(self, level_num):
        """Налаштовує рівень"""
        self.current_speed_magnitude = BASE_BALL_SPEED + (level_num - 1) * SPEED_INCREASE_PER_LEVEL
        self.current_speed_magnitude = min(self.current_speed_magnitude, MAX_BALL_SPEED)
        
        self.reset_ball()
        
        self.paddle.rect.x = self.initial_paddle_x
        self.paddle.rect.y = self.initial_paddle_y
        self.paddle.set_width(self.original_paddle_width)
        
        self.bricks = self.level_manager.create_level(level_num)
        self.ball_trail.clear()
        self.bonus_manager.clear()
    
    def reset_ball(self):
        """Скидає м'яч на початкову позицію"""
        start_ball = Ball(self.initial_ball_x, self.initial_ball_y, BALL_RADIUS, WHITE)
        
        vx = self.normalized_initial_vx * self.current_speed_magnitude
        vy = self.normalized_initial_vy * self.current_speed_magnitude
        
        start_ball.set_velocity(vx, vy)
        
        self.balls = [start_ball]
    
    def activate_multiball(self):
        """Активує мультибол - додає 2 нових м'яча"""
        if not self.balls:
            return
        
        base_ball = self.balls[0]
        base_vx, base_vy = base_ball.vx, base_ball.vy
        
        for angle_offset in [-0.5, 0.5]:
            new_ball = base_ball.copy()
            
            speed = math.sqrt(base_vx**2 + base_vy**2)
            angle = math.atan2(base_vy, base_vx)
            new_angle = angle + angle_offset
            
            new_vx = math.cos(new_angle) * speed
            new_vy = math.sin(new_angle) * speed
            
            new_ball.set_velocity(new_vx, new_vy)
            self.balls.append(new_ball)
    
    def render_ui(self, surface, font):
        """Відрисовує UI"""
        score_text = font.render(f"Рахунок: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        level_text = font.render(f"Рівень: {self.level}", True, WHITE)
        surface.blit(level_text, (10, 50))
        
        # Відображення життів
        if self.lives > 5:
            draw_neon_heart(surface, WIDTH - 100, 30, 15, NEON_THEME['BUTTON_HOVER'])
            lives_text = font.render(f"x {self.lives}", True, WHITE)
            surface.blit(lives_text, (WIDTH - 70, 15))
        else:
            for i in range(self.lives):
                heart_x = WIDTH - 40 - i * 40
                draw_neon_heart(surface, heart_x, 30, 15, NEON_THEME['BUTTON_HOVER'])
        
        # Індикатори бонусів
        self.bonus_manager.draw_effects_ui(surface, WIDTH - 140, 60)
        
        # Індикатор швидкості
        speed_percent = (self.current_speed_magnitude - BASE_BALL_SPEED) / (MAX_BALL_SPEED - BASE_BALL_SPEED)
        speed_percent = max(0.0, min(speed_percent, 1.0))
        
        bar_width = 100
        bar_height = 10
        bar_x = WIDTH - 120
        bar_y = HEIGHT - 20
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        red_comp = int(255 * speed_percent)
        green_comp = int(255 * (1 - speed_percent))
        fill_color = (red_comp, green_comp, 0)
        
        fill_width = int(bar_width * speed_percent)
        if fill_width > 0:
            pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
        
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        speed_label = pygame.font.Font(None, 20).render("SPEED", True, WHITE)
        surface.blit(speed_label, (bar_x - 45, bar_y))
    
    def draw_game_background(self, surface):
        """Малює фон гри з цеглинками та об'єктами"""
        self.background.draw(surface, self.current_time)
        
        # Стіни
        pygame.draw.rect(surface, WHITE, (0, 0, WALL_THICKNESS, HEIGHT))
        pygame.draw.rect(surface, WHITE, (WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))
        pygame.draw.rect(surface, WHITE, (0, 0, WIDTH, WALL_THICKNESS))
        
        # Цеглинки
        for brick in self.bricks:
            brick.update(self.clock.get_time() / 1000.0)
            brick.draw(surface, self.current_time)
        
        # Трейл, платформа, м'ячі
        self.ball_trail.draw(surface, RED, BALL_RADIUS)
        self.paddle.draw(surface)
        
        for ball in self.balls:
            ball.draw(surface)
        
        # Бонуси
        self.bonus_manager.draw_bonuses(surface, self.current_time)
        
        # Частинки
        self.particle_system.draw(surface)


# =============================================================================
# ГОЛОВНИЙ ЦИКЛ ГРИ
# =============================================================================

def main():
    """Головна функція гри"""
    # Створюємо контекст гри
    ctx = GameContext()
    
    # Створюємо state manager
    state_manager = StateManager(ctx)
    
    # Реєструємо всі стани
    state_manager.register_state('main_menu', MainMenuState(ctx))
    state_manager.register_state('high_scores', HighScoresState(ctx))
    state_manager.register_state('playing', PlayingState(ctx))
    state_manager.register_state('paused', PauseState(ctx))
    state_manager.register_state('level_transition', LevelTransitionState(ctx))
    state_manager.register_state('game_over', GameOverState(ctx))
    
    # Початковий стан
    state_manager.change_state('main_menu')
    
    # Головний цикл
    while ctx.running:
        dt = ctx.clock.tick(60) / 1000.0
        ctx.current_time = time.time() - ctx.start_time
        
        # Обробка подій
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
            
            # F11 - перемикання повноекранного режиму
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                ctx.toggle_fullscreen()
            
            # Передаємо подію поточному стану
            state_manager.handle_event(event)
        
        # Оновлюємо фон та ефекти
        ctx.background.update(dt)
        ctx.screen_shake.update(dt)
        ctx.particle_system.update(dt)
        ctx.bonus_manager.update(dt)
        
        # Оновлюємо поточний стан
        new_state = state_manager.current_state.update(dt)
        if new_state:
            state_manager.change_state(new_state)
        
        # Очищаємо поверхню
        ctx.game_surface.fill(BLACK)
        
        # Малюємо поточний стан
        state_manager.draw(ctx.game_surface)
        
        # Застосовуємо screen shake
        offset_x, offset_y = ctx.screen_shake.get_offset()
        
        # Масштабування для повноекранного режиму
        scale, display_offset_x, display_offset_y = ctx.get_display_transform()
        
        if ctx.is_fullscreen and scale != 1.0:
            scaled_surface = pygame.transform.scale(
                ctx.game_surface,
                (int(WIDTH * scale), int(HEIGHT * scale))
            )
            ctx.win.fill(BLACK)
            ctx.win.blit(scaled_surface, (display_offset_x + offset_x, display_offset_y + offset_y))
        else:
            ctx.win.blit(ctx.game_surface, (offset_x, offset_y))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
