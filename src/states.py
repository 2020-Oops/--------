"""
Система управління станами гри (State Machine)
"""
import pygame
import time
import math
from abc import ABC, abstractmethod
from game_config import (
    WIDTH, HEIGHT, WHITE, BLACK, RED, BLUE, GREEN, YELLOW, CYAN, MAGENTA,
    MENU_COLOR, MENU_HOVER_COLOR, MENU_SELECTED_COLOR,
    BUTTON_BG_COLOR, BUTTON_BORDER_COLOR,
    FONT_SIZE, LARGE_FONT_SIZE, MENU_FONT_SIZE, SMALL_FONT_SIZE,
    INITIAL_LIVES, NEON_THEME, WALL_THICKNESS, BALL_RADIUS,
    PADDLE_SPEED, BASE_BALL_SPEED, MAX_BALL_SPEED, SPEED_INCREASE_PER_LEVEL,
    MIN_VERTICAL_SPEED_RATIO, MAX_BOUNCE_ANGLE_DEG
)
from graphics_effects import draw_pulsing_text, draw_neon_heart
from bonus_system import BonusType
import physics


class GameState(ABC):
    """Базовий клас для всіх станів гри"""
    
    def __init__(self, game_context):
        """
        Ініціалізація стану
        
        Args:
            game_context: Контекст гри з доступом до всіх менеджерів та даних
        """
        self.context = game_context
    
    @abstractmethod
    def handle_event(self, event):
        """
        Обробка подій
        
        Args:
            event: pygame event
            
        Returns:
            str або None: Назва нового стану для переходу (або None)
        """
        pass
    
    @abstractmethod
    def update(self, dt):
        """
        Оновлення логіки стану
        
        Args:
            dt: Delta time в секундах
        """
        pass
    
    @abstractmethod
    def draw(self, surface):
        """
        Відрисовка стану
        
        Args:
            surface: Поверхня для малювання
        """
        pass
    
    def on_enter(self):
        """Викликається при вході в стан"""
        pass
    
    def on_exit(self):
        """Викликається при виході зі стану"""
        pass


class StateManager:
    """Менеджер станів гри"""
    
    def __init__(self, game_context):
        """
        Ініціалізація менеджера
        
        Args:
            game_context: Контекст гри
        """
        self.context = game_context
        self.states = {}
        self.current_state = None
        self.current_state_name = None
    
    def register_state(self, name, state):
        """
        Реєструє стан
        
        Args:
            name: Назва стану
            state: Екземпляр GameState
        """
        self.states[name] = state
    
    def change_state(self, name):
        """
        Змінює поточний стан
        
        Args:
            name: Назва нового стану
        """
        if name not in self.states:
            raise ValueError(f"State '{name}' not registered")
        
        # Вихід з поточного стану
        if self.current_state:
            self.current_state.on_exit()
        
        # Перехід до нового стану
        self.current_state_name = name
        self.current_state = self.states[name]
        self.current_state.on_enter()
    
    def handle_event(self, event):
        """Передає подію поточному стану"""
        if self.current_state:
            new_state = self.current_state.handle_event(event)
            if new_state:
                self.change_state(new_state)
    
    def update(self, dt):
        """Оновлює поточний стан"""
        if self.current_state:
            self.current_state.update(dt)
    
    def draw(self, surface):
        """Малює поточний стан"""
        if self.current_state:
            self.current_state.draw(surface)


# Допоміжні функції для UI

def draw_button(surface, text, rect, font, is_selected=False):
    """Малює кнопку"""
    color = MENU_SELECTED_COLOR if is_selected else BUTTON_BG_COLOR
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BUTTON_BORDER_COLOR, rect, 3)
    
    text_color = BLACK if is_selected else WHITE
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


# Конкретні стани

class MainMenuState(GameState):
    """Головне меню"""
    
    def __init__(self, game_context):
        super().__init__(game_context)
        self.selected_index = 0
        self.menu_items = ["ПОЧАТИ ГРУ", "РЕКОРДИ", "ВИХІД"]
        self.font = pygame.font.Font(None, LARGE_FONT_SIZE)
        self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.context.is_fullscreen:
                    self.context.toggle_fullscreen()
                else:
                    self.context.running = False
            elif event.key == pygame.K_UP:
                self.context.sound_manager.play_menu_move()
                self.selected_index = (self.selected_index - 1) % 3
            elif event.key == pygame.K_DOWN:
                self.context.sound_manager.play_menu_move()
                self.selected_index = (self.selected_index + 1) % 3
            elif event.key == pygame.K_RETURN:
                self.context.sound_manager.play_menu_select()
                if self.selected_index == 0:
                    self.context.initialize_game_data()
                    return 'playing'
                elif self.selected_index == 1:
                    return 'high_scores'
                elif self.selected_index == 2:
                    self.context.running = False
        return None
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        self.context.background.draw(surface, self.context.current_time)
        
        # Pulsing Title
        draw_pulsing_text(surface, "АРКАНОЇД", self.font, (WIDTH // 2, 100), CYAN, self.context.current_time)
        
        subtitle = pygame.font.Font(None, 32).render("✨ З ВІЗУАЛЬНИМИ ЕФЕКТАМИ ✨", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 160))
        surface.blit(subtitle, subtitle_rect)
        
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_y = 250
        
        for i, item in enumerate(self.menu_items):
            button_rect = pygame.Rect(
                WIDTH // 2 - button_width // 2,
                start_y + i * (button_height + button_spacing),
                button_width,
                button_height
            )
            draw_button(surface, item, button_rect, self.menu_font, i == self.selected_index)
        
        # Інструкції
        mode_text = "Повноекранний режим" if self.context.is_fullscreen else "Віконний режим"
        instructions = [
            "Керування: Стрілки ← →",
            "Пауза: ESC або P",
            f"Режим: {mode_text} (F11 - перемкнути)",
            "ESC - вихід з повноекранного" if self.context.is_fullscreen else "ESC - вихід з гри"
        ]
        small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        y_offset = HEIGHT - 120
        for instruction in instructions:
            text = small_font.render(instruction, True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, y_offset))
            surface.blit(text, rect)
            y_offset += 30


class HighScoresState(GameState):
    """Екран рекордів"""
    
    def __init__(self, game_context):
        super().__init__(game_context)
        self.font = pygame.font.Font(None, LARGE_FONT_SIZE)
        self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return 'main_menu'
        return None
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        self.context.background.draw(surface, self.context.current_time)
        
        title_text = self.font.render("РЕКОРДИ", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 60))
        surface.blit(title_text, title_rect)
        
        scores = self.context.high_score_manager.get_scores()
        
        if not scores:
            no_scores_text = self.menu_font.render("Рекордів поки немає", True, WHITE)
            no_scores_rect = no_scores_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(no_scores_text, no_scores_rect)
        else:
            headers = ["#", "РАХУНОК", "РІВЕНЬ", "ДАТА"]
            header_y = 120
            x_positions = [150, 300, 500, 620]
            
            small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
            for i, header in enumerate(headers):
                text = small_font.render(header, True, CYAN)
                surface.blit(text, (x_positions[i], header_y))
            
            y_offset = header_y + 40
            for i, score_data in enumerate(scores[:10]):
                rank_text = small_font.render(f"{i + 1}", True, WHITE)
                score_text = small_font.render(str(score_data['score']), True, WHITE)
                level_text = small_font.render(str(score_data['level']), True, WHITE)
                date_text = small_font.render(score_data['date'][:16], True, WHITE)
                
                surface.blit(rank_text, (x_positions[0], y_offset))
                surface.blit(score_text, (x_positions[1], y_offset))
                surface.blit(level_text, (x_positions[2], y_offset))
                surface.blit(date_text, (x_positions[3], y_offset))
                
                y_offset += 35
        
        back_text = self.menu_font.render("Натисніть ESC для повернення", True, MENU_COLOR)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        surface.blit(back_text, back_rect)


class PauseState(GameState):
    """Стан паузи"""
    
    def __init__(self, game_context):
        super().__init__(game_context)
        self.selected_index = 0
        self.menu_items = ["ПРОДОВЖИТИ", "ГОЛОВНЕ МЕНЮ"]
        self.font = pygame.font.Font(None, LARGE_FONT_SIZE)
        self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    
    def on_enter(self):
        self.selected_index = 0
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.context.sound_manager.play_menu_move()
                self.selected_index = (self.selected_index - 1) % 2
            elif event.key == pygame.K_DOWN:
                self.context.sound_manager.play_menu_move()
                self.selected_index = (self.selected_index + 1) % 2
            elif event.key == pygame.K_RETURN:
                self.context.sound_manager.play_menu_select()
                if self.selected_index == 0:
                    return 'playing'
                elif self.selected_index == 1:
                    return 'main_menu'
            elif event.key == pygame.K_ESCAPE:
                return 'playing'
        return None
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        # Малюємо гру під паузою (затемнену)
        self.context.draw_game_background(surface)
        
        pause_surface = pygame.Surface((WIDTH, HEIGHT))
        pause_surface.set_alpha(180)
        pause_surface.fill(BLACK)
        surface.blit(pause_surface, (0, 0))
        
        title_text = self.font.render("ПАУЗА", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
        surface.blit(title_text, title_rect)
        
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_y = 280
        
        for i, item in enumerate(self.menu_items):
            button_rect = pygame.Rect(
                WIDTH // 2 - button_width // 2,
                start_y + i * (button_height + button_spacing),
                button_width,
                button_height
            )
            draw_button(surface, item, button_rect, self.menu_font, i == self.selected_index)


class LevelTransitionState(GameState):
    """Перехід між рівнями"""
    
    def __init__(self, game_context):
        super().__init__(game_context)
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.large_font = pygame.font.Font(None, LARGE_FONT_SIZE)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.context.setup_level(self.context.level)
                return 'playing'
        return None
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        self.context.draw_game_background(surface)
        
        message_text = self.large_font.render(f"РІВЕНЬ {self.context.level}", True, WHITE)
        instruction_text = self.font.render("Натисніть Enter", True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        surface.blit(message_text, message_rect)
        surface.blit(instruction_text, instruction_rect)


class GameOverState(GameState):
    """Кінець гри"""
    
    def __init__(self, game_context):
        super().__init__(game_context)
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.large_font = pygame.font.Font(None, LARGE_FONT_SIZE)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.context.high_score_manager.add_score(self.context.score, self.context.level)
                return 'main_menu'
        return None
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        self.context.draw_game_background(surface)
        
        draw_pulsing_text(surface, "ГРА ЗАКІНЧЕНА", self.large_font, (WIDTH // 2, HEIGHT // 2 - 80), 
                         RED, self.context.current_time, scale_range=(1.0, 1.2))
        
        score_text = self.font.render(f"Ваш рахунок: {self.context.score}", True, WHITE)
        instruction_text = self.font.render("Натисніть Enter для головного меню", True, WHITE)
        
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        
        surface.blit(score_text, score_rect)
        surface.blit(instruction_text, instruction_rect)
        
        if self.context.high_score_manager.is_high_score(self.context.score):
            new_record_text = self.font.render("🏆 НОВИЙ РЕКОРД! 🏆", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            surface.blit(new_record_text, new_record_rect)


class PlayingState(GameState):
    """Активна гра"""
    
    def __init__(self, game_context):
        super().__init__(game_context)
        self.font = pygame.font.Font(None, FONT_SIZE)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                return 'paused'
        return None
    
    def update(self, dt):
        ctx = self.context
        
        # Керування платформою
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ctx.paddle.move(-PADDLE_SPEED, WIDTH)
        if keys[pygame.K_RIGHT]:
            ctx.paddle.move(PADDLE_SPEED, WIDTH)
        
        # Застосування ефектів бонусів
        target_width = ctx.original_paddle_width * ctx.bonus_manager.get_paddle_modifier()
        if abs(ctx.paddle.width - target_width) > 1:
            ctx.paddle.set_width(int(target_width))
        
        # Збирання бонусів
        collected_bonuses = ctx.bonus_manager.check_collection(ctx.paddle.rect)
        for bonus in collected_bonuses:
            ctx.sound_manager.play_powerup()
            ctx.particle_system.create_sparkle(bonus.rect.centerx, bonus.rect.centery, bonus.color)
            ctx.bonus_manager.apply_bonus(bonus)
            
            if bonus.bonus_type == BonusType.EXTRA_LIFE:
                ctx.lives += 1
            elif bonus.bonus_type == BonusType.MULTI_BALL:
                ctx.activate_multiball()
        
        # Оновлення м'ячів
        self._update_balls(dt)
        
        # Перевірка перемоги
        all_bricks_destroyed = True
        for brick in ctx.bricks:
            if brick.visible and brick.can_destroy:
                all_bricks_destroyed = False
                break
        
        if all_bricks_destroyed:
            ctx.sound_manager.play_level_complete()
            ctx.level += 1
            return 'level_transition'
        
        return None
    
    def _update_balls(self, dt):
        ctx = self.context
        balls_to_remove = []
        speed_modifier = ctx.bonus_manager.get_ball_speed_modifier()
        
        for i in range(len(ctx.balls)):
            b = ctx.balls[i]
            
            # Застосовуємо модифікатор швидкості
            original_vx, original_vy = b.vx, b.vy
            b.vx *= speed_modifier
            b.vy *= speed_modifier
            
            b.update()
            
            b.vx, b.vy = original_vx, original_vy
            
            # Трейл
            if i == 0:
                ctx.ball_trail.add_position(b.centerx, b.centery)
            
            # Відбиття від стін
            physics.handle_wall_collision(b, ctx.sound_manager)
            
            # Відбиття від платформи
            physics.handle_paddle_collision(b, ctx.paddle, ctx.sound_manager)
            
            # Зіткнення з цеглинками
            is_fire_ball = ctx.bonus_manager.has_active_effect(BonusType.FIRE_BALL)
            physics.handle_brick_collision(b, ctx.bricks, is_fire_ball, ctx)
            
            # Втрата м'яча
            if physics.check_ball_lost(b):
                balls_to_remove.append(i)
        
        # Видалення втрачених м'ячів
        for index in sorted(balls_to_remove, reverse=True):
            ctx.balls.pop(index)
        
        # Якщо всі м'ячі втрачено
        if not ctx.balls:
            ctx.lives -= 1
            ctx.sound_manager.play_life_lost()
            ctx.screen_shake.start(magnitude=10, duration=0.4)
            if ctx.lives <= 0:
                ctx.sound_manager.play_game_over()
                return 'game_over'
            else:
                ctx.reset_ball()
                ctx.ball_trail.clear()
                ctx.bonus_manager.clear()
        
        return None
    
    def draw(self, surface):
        ctx = self.context
        ctx.draw_game_background(surface)
        ctx.render_ui(surface, self.font)

