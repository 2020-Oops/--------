import pygame
import math
from game_config import (
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED,
    BALL_RADIUS, BASE_BALL_SPEED, MAX_BALL_SPEED,
    WHITE, NEON_THEME
)
from graphics_effects import draw_3d_paddle, draw_glowing_ball

class Paddle:
    def __init__(self, x, y, width=PADDLE_WIDTH, height=PADDLE_HEIGHT, speed=PADDLE_SPEED, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_width = width
        self.speed = speed
        self.color = color if color else (200, 200, 200) # Default color
        
    def move(self, dx, boundary_width):
        """Moves the paddle within the screen boundaries."""
        if dx < 0 and self.rect.left > 0:
            self.rect.move_ip(dx, 0)
        if dx > 0 and self.rect.right < boundary_width:
            self.rect.move_ip(dx, 0)
            
    def draw(self, surface):
        draw_3d_paddle(surface, self.rect, self.color)
        
    def set_width(self, width):
        center = self.rect.centerx
        self.rect.width = int(width)
        self.rect.centerx = center

    @property
    def width(self):
        return self.rect.width
        
    @property
    def height(self):
        return self.rect.height

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y
        
    @property
    def centerx(self):
        return self.rect.centerx

    @property
    def top(self):
        return self.rect.top
        
    @property
    def left(self):
        return self.rect.left
        
    @property
    def right(self):
        return self.rect.right
        
    @property
    def bottom(self):
        return self.rect.bottom


class Ball:
    def __init__(self, x, y, radius=BALL_RADIUS, color=WHITE):
        self.rect = pygame.Rect(x, y, radius * 2, radius * 2)
        self.radius = radius
        self.color = color
        self.vx = 0
        self.vy = 0
        self.speed_magnitude = 0
        self.active = True

    def set_velocity(self, vx, vy):
        self.vx = vx
        self.vy = vy
        self.speed_magnitude = math.sqrt(vx**2 + vy**2)

    def set_speed_magnitude(self, speed):
        """Sets the speed magnitude while preserving direction."""
        current_speed = math.sqrt(self.vx**2 + self.vy**2)
        if current_speed > 0:
            factor = speed / current_speed
            self.vx *= factor
            self.vy *= factor
        self.speed_magnitude = speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, surface):
        draw_glowing_ball(surface, self.rect, self.color)

    def bounce_x(self):
        self.vx = -self.vx

    def bounce_y(self):
        self.vy = -self.vy
        
    def copy(self):
        """Creates a copy of the ball."""
        new_ball = Ball(self.rect.x, self.rect.y, self.radius, self.color)
        new_ball.set_velocity(self.vx, self.vy)
        return new_ball

    @property
    def x(self):
        return self.rect.x
        
    @property
    def y(self):
        return self.rect.y
        
    @property
    def centerx(self):
        return self.rect.centerx
        
    @property
    def centery(self):
        return self.rect.centery
        
    @property
    def top(self):
        return self.rect.top
        
    @property
    def bottom(self):
        return self.rect.bottom
        
    @property
    def left(self):
        return self.rect.left
        
    @property
    def right(self):
        return self.rect.right
