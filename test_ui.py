"""
Тестовий скрипт для перевірки UI компонентів
"""
import pygame
import sys
sys.path.insert(0, 'src')

from ui_components import ProgressBar, AnimatedCounter, ComboMeter, FloatingText
from notification_system import NotificationManager

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Тестуємо компоненти
progress = ProgressBar(50, 50, 200, 20)
counter = AnimatedCounter(400, 100)
combo = ComboMeter(400, 200)
notifications = NotificationManager()

progress.set_progress(0.5)
counter.set_value(1500)

notifications.add_score_popup(400, 300, 100)
combo.add_combo()
combo.add_combo()
combo.add_combo()

running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                notifications.add_score_popup(400, 300, 100)
                combo.add_combo()
    
    # Оновлення
    counter.update(dt)
    combo.update(dt)
    notifications.update(dt)
    
    # Малювання
    screen.fill((10, 10, 20))
    progress.draw(screen)
    counter.draw(screen)
    combo.draw(screen)
    notifications.draw(screen)
    
    # Інструкція
    font = pygame.font.Font(None, 24)
    text = font.render("Press SPACE to test, ESC to exit", True, (255, 255, 255))
    screen.blit(text, (200, 500))
    
    pygame.display.flip()

pygame.quit()
print("✅ UI Components test passed!")
