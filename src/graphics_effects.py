"""
Графічні ефекти та покращене малювання для гри Арканоїд
"""
import pygame
import math
import random


def draw_gradient_rect(surface, rect, color_top, color_bottom):
    """
    Малює прямокутник з вертикальним градієнтом
    
    Args:
        surface: Поверхня для малювання
        rect: pygame.Rect об'єкт
        color_top: Колір зверху (R, G, B)
        color_bottom: Колір знизу (R, G, B)
    """
    for y in range(rect.height):
        # Інтерполюємо колір
        ratio = y / rect.height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        
        pygame.draw.line(surface, (r, g, b), 
                        (rect.left, rect.top + y), 
                        (rect.right, rect.top + y))


def draw_gradient_rect_horizontal(surface, rect, color_left, color_right):
    """
    Малює прямокутник з горизонтальним градієнтом
    
    Args:
        surface: Поверхня для малювання
        rect: pygame.Rect об'єкт
        color_left: Колір зліва (R, G, B)
        color_right: Колір справа (R, G, B)
    """
    for x in range(rect.width):
        ratio = x / rect.width
        r = int(color_left[0] * (1 - ratio) + color_right[0] * ratio)
        g = int(color_left[1] * (1 - ratio) + color_right[1] * ratio)
        b = int(color_left[2] * (1 - ratio) + color_right[2] * ratio)
        
        pygame.draw.line(surface, (r, g, b), 
                        (rect.left + x, rect.top), 
                        (rect.left + x, rect.bottom))


def lighten_color(color, factor=1.3):
    """
    Освітлює колір
    
    Args:
        color: Колір (R, G, B)
        factor: Фактор освітлення (>1 - світліше)
    
    Returns:
        tuple: Новий колір
    """
    return tuple(min(255, int(c * factor)) for c in color)


def darken_color(color, factor=0.7):
    """
    Затемнює колір
    
    Args:
        color: Колір (R, G, B)
        factor: Фактор затемнення (<1 - темніше)
    
    Returns:
        tuple: Новий колір
    """
    return tuple(int(c * factor) for c in color)


def draw_brick_with_gradient(surface, rect, color):
    """
    Малює цеглинку з градієнтом та рамкою
    
    Args:
        surface: Поверхня для малювання
        rect: pygame.Rect об'єкт
        color: Базовий колір цеглинки
    """
    # Градієнт від світлішого до темнішого
    color_top = lighten_color(color, 1.4)
    color_bottom = darken_color(color, 0.8)
    
    draw_gradient_rect(surface, rect, color_top, color_bottom)
    
    # Світла обводка зверху та зліва (3D ефект)
    highlight_color = lighten_color(color, 1.6)
    pygame.draw.line(surface, highlight_color, rect.topleft, rect.topright, 2)
    pygame.draw.line(surface, highlight_color, rect.topleft, rect.bottomleft, 2)
    
    # Темна обводка знизу та справа
    shadow_color = darken_color(color, 0.5)
    pygame.draw.line(surface, shadow_color, rect.bottomleft, rect.bottomright, 2)
    pygame.draw.line(surface, shadow_color, rect.topright, rect.bottomright, 2)


def draw_glowing_ball(surface, rect, color, glow_radius=5):
    """
    Малює м'яч зі свіченням
    
    Args:
        surface: Поверхня для малювання
        rect: pygame.Rect об'єкт
        color: Базовий колір м'яча
        glow_radius: Радіус свічення
    """
    center_x = rect.centerx
    center_y = rect.centery
    radius = rect.width // 2
    
    # Малюємо свічення (кілька шарів з прозорістю)
    for i in range(glow_radius, 0, -1):
        alpha = int(50 * (1 - i / glow_radius))
        glow_surface = pygame.Surface((radius * 2 + i * 2, radius * 2 + i * 2), pygame.SRCALPHA)
        color_with_alpha = (*color, alpha)
        pygame.draw.circle(glow_surface, color_with_alpha, 
                          (radius + i, radius + i), radius + i)
        surface.blit(glow_surface, (center_x - radius - i, center_y - radius - i))
    
    # Малюємо основний м'яч з градієнтом
    for r in range(radius, 0, -1):
        # Радіальний градієнт (світліше в центрі)
        ratio = r / radius
        gradient_color = tuple(int(c * ratio + 255 * (1 - ratio) * 0.3) for c in color)
        pygame.draw.circle(surface, gradient_color, (center_x, center_y), r)
    
    # Блік (highlight)
    highlight_x = center_x - radius // 3
    highlight_y = center_y - radius // 3
    highlight_radius = radius // 3
    for r in range(highlight_radius, 0, -1):
        alpha = int(100 * (1 - r / highlight_radius))
        highlight_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surface, (255, 255, 255, alpha), (r, r), r)
        surface.blit(highlight_surface, (highlight_x - r, highlight_y - r))


def draw_3d_paddle(surface, rect, base_color=(200, 200, 200)):
    """
    Малює платформу з 3D ефектом
    
    Args:
        surface: Поверхня для малювання
        rect: pygame.Rect об'єкт
        base_color: Базовий колір платформи
    """
    # Градієнт зверху вниз
    color_top = lighten_color(base_color, 1.3)
    color_bottom = darken_color(base_color, 0.7)
    
    draw_gradient_rect(surface, rect, color_top, color_bottom)
    
    # Верхня світла смужка
    highlight_rect = pygame.Rect(rect.left, rect.top, rect.width, 2)
    pygame.draw.rect(surface, lighten_color(base_color, 1.5), highlight_rect)
    
    # Нижня темна смужка
    shadow_rect = pygame.Rect(rect.left, rect.bottom - 2, rect.width, 2)
    pygame.draw.rect(surface, darken_color(base_color, 0.5), shadow_rect)
    
    # Бокові краї
    pygame.draw.line(surface, lighten_color(base_color, 1.4), 
                    rect.topleft, rect.bottomleft, 2)
    pygame.draw.line(surface, darken_color(base_color, 0.6), 
                    rect.topright, rect.bottomright, 2)


def draw_neon_heart(surface, x, y, size, color):
    """
    Малює неонове серце
    
    Args:
        surface: Поверхня для малювання
        x, y: Координати центру
        size: Розмір серця
        color: Колір серця
    """
    # Точки серця (відносно центру 0,0)
    points = [
        (0, -size * 0.5),
        (size * 0.5, -size * 0.9),
        (size, -size * 0.5),
        (0, size * 0.8),
        (-size, -size * 0.5),
        (-size * 0.5, -size * 0.9)
    ]
    
    # Зміщення точок
    shifted_points = [(p[0] + x, p[1] + y) for p in points]
    
    # Світіння (кілька шарів)
    for i in range(3, 0, -1):
        alpha = int(100 / i)
        glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        glow_points = [(p[0] - x + size * 2, p[1] - y + size * 2) for p in shifted_points]
        pygame.draw.polygon(glow_surface, (*color, alpha), glow_points, width=i*2)
        surface.blit(glow_surface, (x - size * 2, y - size * 2))
    
    # Основний контур
    pygame.draw.polygon(surface, color, shifted_points)
    pygame.draw.polygon(surface, (255, 255, 255), shifted_points, 2)


class AnimatedBackground:
    """Анімований фон з зірками"""
    
    def __init__(self, width, height, num_stars=100):
        """
        Ініціалізація анімованого фону
        
        Args:
            width, height: Розміри екрану
            num_stars: Кількість зірок
        """
        self.width = width
        self.height = height
        self.stars = []
        
        # Створюємо зірки на різних шарах (parallax)
        for _ in range(num_stars):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            speed = size * 0.1  # Більші зірки рухаються швидше
            brightness = random.randint(150, 255)
            twinkle_speed = random.uniform(0.5, 2.0)
            twinkle_offset = random.uniform(0, math.pi * 2)
            
            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'brightness': brightness,
                'twinkle_speed': twinkle_speed,
                'twinkle_offset': twinkle_offset
            })
    
    def update(self, dt):
        """
        Оновлює позиції зірок
        
        Args:
            dt: Час з попереднього кадру
        """
        for star in self.stars:
            star['y'] += star['speed'] * dt * 60
            
            # Якщо зірка виходить за межі, повертаємо її нагору
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)
    
    def draw(self, surface, time):
        """
        Малює фон з зірками
        
        Args:
            surface: Поверхня для малювання
            time: Поточний час (для мерехтіння)
        """
        # Градієнтний фон
        color_top = (10, 10, 30)
        color_bottom = (0, 0, 10)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))
        
        # Малюємо зірки з мерехтінням
        for star in self.stars:
            # Ефект мерехтіння
            twinkle = math.sin(time * star['twinkle_speed'] + star['twinkle_offset']) * 0.3 + 0.7
            brightness = int(star['brightness'] * twinkle)
            color = (brightness, brightness, brightness)
            
            x, y = int(star['x']), int(star['y'])
            size = star['size']
            
            if size > 1:
                pygame.draw.circle(surface, color, (x, y), size)
            else:
                surface.set_at((x, y), color)


def draw_shadow(surface, rect, offset=(2, 2), alpha=100):
    """
    Малює тінь під об'єктом
    
    Args:
        surface: Поверхня для малювання
        rect: pygame.Rect об'єкт
        offset: Зміщення тіні (x, y)
        alpha: Прозорість тіні
    """
    shadow_rect = rect.move(offset)
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_surface.get_rect())
    surface.blit(shadow_surface, shadow_rect.topleft)


def draw_pulsing_text(surface, text, font, center_pos, color, time_val, scale_range=(1.0, 1.1)):
    """
    Малює текст, що пульсує
    
    Args:
        surface: Поверхня для малювання
        text: Текст
        font: Шрифт
        center_pos: Центр тексту (x, y)
        color: Колір тексту
        time_val: Поточний час для анімації
        scale_range: Діапазон масштабування (min, max)
    """
    # Обчислюємо масштаб (синусоїда)
    scale = scale_range[0] + (scale_range[1] - scale_range[0]) * (math.sin(time_val * 5) * 0.5 + 0.5)
    
    # Рендеримо текст
    text_surf = font.render(text, True, color)
    
    # Масштабуємо
    width = int(text_surf.get_width() * scale)
    height = int(text_surf.get_height() * scale)
    scaled_surf = pygame.transform.scale(text_surf, (width, height))
    
    # Центруємо
    rect = scaled_surf.get_rect(center=center_pos)
    
    # Малюємо тінь/світіння
    glow_surf = pygame.transform.scale(text_surf, (width + 4, height + 4))
    glow_surf.set_alpha(100)
    glow_rect = glow_surf.get_rect(center=center_pos)
    
    # Заливаємо світіння кольором
    glow_mask = pygame.mask.from_surface(glow_surf)
    glow_colored = glow_mask.to_surface(setcolor=color, unsetcolor=(0,0,0,0))
    glow_colored.set_alpha(100)
    
    surface.blit(glow_colored, glow_rect)
    surface.blit(scaled_surf, rect)
