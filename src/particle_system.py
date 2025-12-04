"""
Система частинок для візуальних ефектів у грі Арканоїд
"""
import pygame
import random
import math


class Particle:
    """Окрема частинка з позицією, швидкістю та кольором"""
    
    def __init__(self, x, y, vx, vy, color, size=3, lifetime=1.0, gravity=0.2):
        """
        Ініціалізація частинки
        
        Args:
            x, y: Початкова позиція
            vx, vy: Швидкість по осях
            color: Колір частинки (R, G, B)
            size: Розмір частинки
            lifetime: Час життя в секундах
            gravity: Гравітація (вплив на vy)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.alpha = 255  # Прозорість
    
    def update(self, dt):
        """
        Оновлює позицію та стан частинки
        
        Args:
            dt: Час з попереднього кадру (в секундах)
        
        Returns:
            bool: True якщо частинка ще жива
        """
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        
        self.lifetime -= dt
        
        # Оновлюємо прозорість (затухання)
        life_ratio = max(0, self.lifetime / self.max_lifetime)
        self.alpha = int(255 * life_ratio)
        
        return self.lifetime > 0
    
    def draw(self, surface):
        """Малює частинку на поверхні"""
        if self.alpha <= 0:
            return
        
        # Створюємо напівпрозору поверхню для частинки
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Малюємо коло з прозорістю
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (self.size, self.size), self.size)
        
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """Менеджер системи частинок"""
    
    def __init__(self):
        """Ініціалізація системи частинок"""
        self.particles = []
    
    def create_explosion(self, x, y, color, num_particles=25, speed_range=(2, 8)):
        """
        Створює ефект вибуху
        
        Args:
            x, y: Позиція вибуху
            color: Базовий колір частинок
            num_particles: Кількість частинок
            speed_range: Діапазон швидкості частинок
        """
        for _ in range(num_particles):
            # Випадковий кут
            angle = random.uniform(0, 2 * math.pi)
            # Випадкова швидкість
            speed = random.uniform(*speed_range)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Варіація кольору
            r = max(0, min(255, color[0] + random.randint(-30, 30)))
            g = max(0, min(255, color[1] + random.randint(-30, 30)))
            b = max(0, min(255, color[2] + random.randint(-30, 30)))
            
            particle_color = (r, g, b)
            size = random.randint(2, 5)
            lifetime = random.uniform(0.3, 0.8)
            
            particle = Particle(x, y, vx, vy, particle_color, size, lifetime)
            self.particles.append(particle)
    
    def create_trail(self, x, y, color, size=2, lifetime=0.2):
        """
        Створює ефект трейлу (сліду)
        
        Args:
            x, y: Позиція
            color: Колір
            size: Розмір частинки
            lifetime: Час життя
        """
        particle = Particle(x, y, 0, 0, color, size, lifetime, gravity=0)
        self.particles.append(particle)
    
    def update(self, dt):
        """
        Оновлює всі частинки
        
        Args:
            dt: Час з попереднього кадру (в секундах)
        """
        # Оновлюємо частинки та видаляємо мертві
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, surface):
        """Малює всі частинки"""
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self):
        """Очищає всі частинки"""
        self.particles.clear()
    
    def get_particle_count(self):
        """Повертає кількість активних частинок"""
        return len(self.particles)


class TrailEffect:
    """Ефект сліду за об'єктом"""
    
    def __init__(self, max_length=7, fade_speed=0.05):
        """
        Ініціалізація ефекту трейлу
        
        Args:
            max_length: Максимальна довжина сліду
            fade_speed: Швидкість затухання
        """
        self.positions = []
        self.max_length = max_length
        self.fade_speed = fade_speed
    
    def add_position(self, x, y):
        """Додає нову позицію до сліду"""
        self.positions.append((x, y))
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
    
    def draw(self, surface, color, radius):
        """
        Малює слід
        
        Args:
            surface: Поверхня для малювання
            color: Колір сліду
            radius: Радіус кожного елементу сліду
        """
        for i, (x, y) in enumerate(self.positions):
            # Розраховуємо прозорість (старіші позиції більш прозорі)
            alpha = int(255 * (i + 1) / len(self.positions) * 0.5)
            size_factor = (i + 1) / len(self.positions)
            current_radius = int(radius * size_factor)
            
            if alpha > 0 and current_radius > 0:
                trail_surface = pygame.Surface((current_radius * 2, current_radius * 2), 
                                              pygame.SRCALPHA)
                color_with_alpha = (*color, alpha)
                pygame.draw.circle(trail_surface, color_with_alpha, 
                                 (current_radius, current_radius), current_radius)
                surface.blit(trail_surface, 
                           (int(x - current_radius), int(y - current_radius)))
    
    def clear(self):
        """Очищає слід"""
        self.positions.clear()


class ScreenShake:
    """Ефект тремтіння екрану"""
    
    def __init__(self):
        self.duration = 0
        self.magnitude = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def start(self, magnitude=5, duration=0.2):
        """
        Запускає тремтіння
        
        Args:
            magnitude: Сила тремтіння (пікселі)
            duration: Тривалість (секунди)
        """
        self.magnitude = magnitude
        self.duration = duration
        
    def update(self, dt):
        """Оновлює стан тремтіння"""
        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:
                self.offset_x = 0
                self.offset_y = 0
            else:
                self.offset_x = random.uniform(-self.magnitude, self.magnitude)
                self.offset_y = random.uniform(-self.magnitude, self.magnitude)
                
                # Затухання сили
                self.magnitude *= 0.9
        else:
            self.offset_x = 0
            self.offset_y = 0
            
    def get_offset(self):
        """Повертає поточне зміщення (x, y)"""
        return int(self.offset_x), int(self.offset_y)


# Розширення ParticleSystem новими методами
def create_sparkle(self, x, y, color, num_particles=10):
    """Створює ефект іскор (для бонусів)"""
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        size = random.randint(1, 3)
        lifetime = random.uniform(0.3, 0.6)
        
        # Яскраві кольори
        r = min(255, color[0] + 50)
        g = min(255, color[1] + 50)
        b = min(255, color[2] + 50)
        
        particle = Particle(x, y, vx, vy, (r, g, b), size, lifetime, gravity=0.05)
        self.particles.append(particle)

def create_shockwave(self, x, y, color):
    """Створює розширювану хвилю (як частинку)"""
    # Це спрощена реалізація через багато дрібних частинок по колу
    points = 20
    for i in range(points):
        angle = (i / points) * 2 * math.pi
        speed = 4
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        particle = Particle(x, y, vx, vy, color, size=2, lifetime=0.3, gravity=0)
        self.particles.append(particle)

# Додаємо методи до класу ParticleSystem
ParticleSystem.create_sparkle = create_sparkle
ParticleSystem.create_shockwave = create_shockwave
