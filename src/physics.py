"""
Фізичний модуль для обробки руху та зіткнень м'яча
"""
import math
from game_config import (
    WIDTH, HEIGHT, WALL_THICKNESS,
    MIN_VERTICAL_SPEED_RATIO, MAX_BOUNCE_ANGLE_DEG
)


def handle_wall_collision(ball, sound_manager):
    """
    Обробляє зіткнення м'яча зі стінами
    
    Args:
        ball: Об'єкт Ball
        sound_manager: Менеджер звуків
        
    Returns:
        bool: True якщо було зіткнення зі стіною
    """
    collided = False
    
    # Ліва стіна
    if ball.left <= WALL_THICKNESS:
        ball.rect.left = WALL_THICKNESS
        ball.vx = abs(ball.vx)
        sound_manager.play_wall_hit()
        collided = True
    # Права стіна
    elif ball.right >= WIDTH - WALL_THICKNESS:
        ball.rect.right = WIDTH - WALL_THICKNESS
        ball.vx = -abs(ball.vx)
        sound_manager.play_wall_hit()
        collided = True
    
    # Верхня стіна
    if ball.top <= WALL_THICKNESS:
        ball.rect.top = WALL_THICKNESS
        ball.vy = abs(ball.vy)
        sound_manager.play_wall_hit()
        collided = True
    
    return collided


def handle_paddle_collision(ball, paddle, sound_manager):
    """
    Обробляє зіткнення м'яча з платформою
    
    Args:
        ball: Об'єкт Ball
        paddle: Об'єкт Paddle
        sound_manager: Менеджер звуків
        
    Returns:
        bool: True якщо було зіткнення з платформою
    """
    if not ball.rect.colliderect(paddle.rect):
        return False
    
    # Перевіряємо чи м'яч рухається вниз
    if ball.vy <= 0:
        return False
    
    sound_manager.play_paddle_hit()
    
    # Зберігаємо швидкість до відбиття
    speed_before_bounce = math.sqrt(ball.vx**2 + ball.vy**2)
    
    # Позиціонуємо м'яч над платформою
    ball.rect.bottom = paddle.top
    
    # Обчислюємо кут відбиття на основі позиції удару
    difference_from_center = ball.centerx - paddle.centerx
    normalized_difference = difference_from_center / (paddle.width / 2.0)
    normalized_difference = max(-1.0, min(normalized_difference, 1.0))
    
    bounce_angle_rad = normalized_difference * math.radians(MAX_BOUNCE_ANGLE_DEG)
    
    # Обчислюємо нову швидкість
    new_vx = speed_before_bounce * math.sin(bounce_angle_rad)
    new_vy = -abs(speed_before_bounce * math.cos(bounce_angle_rad))
    
    # Гарантуємо мінімальну вертикальну швидкість
    min_vy = speed_before_bounce * MIN_VERTICAL_SPEED_RATIO
    if abs(new_vy) < min_vy:
        new_vy = -min_vy
        new_vx_sign = 1 if new_vx > 0 else -1
        arg = max(0, speed_before_bounce**2 - new_vy**2)
        new_vx = new_vx_sign * math.sqrt(arg)
    
    ball.vx = new_vx
    ball.vy = new_vy
    
    return True


def calculate_overlap(ball, brick):
    """
    Обчислює перекриття м'яча з цеглинкою
    
    Args:
        ball: Об'єкт Ball
        brick: Об'єкт Brick
        
    Returns:
        tuple: (overlap_x, overlap_y)
    """
    overlap_x = min(ball.right - brick.rect.left, brick.rect.right - ball.left)
    overlap_y = min(ball.bottom - brick.rect.top, brick.rect.bottom - ball.top)
    return overlap_x, overlap_y


def bounce_ball_from_brick(ball, brick):
    """
    Відбиває м'яч від цеглинки
    
    Args:
        ball: Об'єкт Ball
        brick: Об'єкт Brick
    """
    ball_center_x = ball.centerx
    ball_center_y = ball.centery
    brick_center_x = brick.rect.centerx
    brick_center_y = brick.rect.centery
    
    overlap_x, overlap_y = calculate_overlap(ball, brick)
    
    # Відбиття залежно від того, яке перекриття менше
    if overlap_x < overlap_y:
        # Горизонтальне відбиття
        ball.vx = -ball.vx
        if ball_center_x < brick_center_x:
            ball.rect.right = brick.rect.left
        else:
            ball.rect.left = brick.rect.right
    else:
        # Вертикальне відбиття
        ball.vy = -ball.vy
        if ball_center_y < brick_center_y:
            ball.rect.bottom = brick.rect.top
        else:
            ball.rect.top = brick.rect.bottom


def handle_brick_collision(ball, bricks, is_fire_ball, context):
    """
    Обробляє зіткнення м'яча з цеглинками
    
    Args:
        ball: Об'єкт Ball
        bricks: Список цеглинок
        is_fire_ball: Чи активний бонус Fire Ball
        context: Контекст гри (для доступу до менеджерів)
        
    Returns:
        bool: True якщо було зіткнення
    """
    from brick_system import BrickType
    
    for brick in bricks:
        if not brick.visible or not ball.rect.colliderect(brick.rect):
            continue
        
        # Обробка удару по цеглинці
        hit_result = brick.hit()
        
        if hit_result['destroyed']:
            context.score += hit_result['points']
            
            # Ефекти знищення
            context.particle_system.create_explosion(
                brick.rect.centerx, brick.rect.centery,
                brick.original_color, num_particles=25
            )
            context.particle_system.create_shockwave(
                brick.rect.centerx, brick.rect.centery, brick.original_color
            )
            
            # Вибухові цеглинки
            if hit_result['explosive']:
                context.sound_manager.play_explosion()
                context.screen_shake.start(magnitude=5, duration=0.2)
                explosion_targets = context.level_manager.get_explosion_targets(bricks, brick)
                for target in explosion_targets:
                    target_result = target.hit()
                    if target_result['destroyed']:
                        context.score += target_result['points']
                        context.particle_system.create_explosion(
                            target.rect.centerx, target.rect.centery,
                            (255, 100, 0), num_particles=20
                        )
            
            # Створення бонусів
            if hit_result['bonus_guaranteed']:
                bonus = context.bonus_manager.create_random_bonus(
                    brick.rect.centerx, brick.rect.centery
                )
                if bonus:
                    context.bonus_manager.add_bonus(bonus)
            else:
                bonus = context.bonus_manager.create_random_bonus(
                    brick.rect.centerx, brick.rect.centery
                )
                context.bonus_manager.add_bonus(bonus)
            
            context.sound_manager.play_brick_hit()
        else:
            # Цеглинка не знищена (непробивна або з HP)
            if brick.brick_type == BrickType.UNBREAKABLE:
                context.sound_manager.play_metal_hit()
            else:
                context.sound_manager.play_brick_hit()
        
        # Відбиття м'яча (якщо не Fire Ball або непробивна цеглинка)
        if not is_fire_ball or brick.brick_type == BrickType.UNBREAKABLE:
            bounce_ball_from_brick(ball, brick)
        else:
            # Fire Ball просто проходить крізь
            context.sound_manager.play_fire_hit()
            context.particle_system.create_explosion(
                brick.rect.centerx, brick.rect.centery,
                (255, 100, 0), num_particles=15
            )
        
        return True
    
    return False


def check_ball_lost(ball):
    """
    Перевіряє чи м'яч впав за межі екрану
    
    Args:
        ball: Об'єкт Ball
        
    Returns:
        bool: True якщо м'яч втрачено
    """
    return ball.bottom >= HEIGHT
