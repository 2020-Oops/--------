"""
Менеджер звуків та генератор SFX для Арканоїда
"""
import pygame
import os
import math
import struct
import random
import wave

class SoundGenerator:
    """Генератор звукових ефектів (WAV)"""
    
    @staticmethod
    def generate_wave(frequency, duration, volume=0.5, wave_type='sine', sample_rate=44100):
        """Генерує хвилю"""
        n_samples = int(sample_rate * duration)
        data = []
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            
            if wave_type == 'sine':
                value = math.sin(2.0 * math.pi * frequency * t)
            elif wave_type == 'square':
                value = 1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                value = 2.0 * (frequency * t - math.floor(frequency * t + 0.5))
            elif wave_type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = 0.0
                
            # Затухання (envelope)
            envelope = 1.0
            if i > n_samples * 0.9: # Fade out last 10%
                envelope = (n_samples - i) / (n_samples * 0.1)
            elif i < n_samples * 0.1: # Fade in first 10%
                envelope = i / (n_samples * 0.1)
                
            data.append(int(value * volume * envelope * 32767.0))
            
        return data

    @staticmethod
    def save_wav(filename, data, sample_rate=44100):
        """Зберігає дані у WAV файл"""
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            for sample in data:
                wav_file.writeframes(struct.pack('h', sample))

    @staticmethod
    def create_sounds():
        """Створює всі необхідні звуки гри"""
        from pathlib import Path
        sounds_dir = Path(__file__).parent.parent / 'assets' / 'sounds'
        
        if not sounds_dir.exists():
            sounds_dir.mkdir(parents=True, exist_ok=True)
            
        # 1. Paddle Hit (Ping)
        data = SoundGenerator.generate_wave(440, 0.1, 0.6, 'sine')
        SoundGenerator.save_wav(str(sounds_dir / 'paddle_hit.wav'), data)
        
        # 2. Brick Hit (Glass Ding)
        # Змішуємо дві синусоїди для "скляного" звуку
        freq1 = 2000
        freq2 = 3000
        duration = 0.3
        n_samples = int(44100 * duration)
        data = []
        
        for i in range(n_samples):
            t = float(i) / 44100
            # Експоненційне затухання
            envelope = math.exp(-15 * t)
            
            val1 = math.sin(2.0 * math.pi * freq1 * t)
            val2 = math.sin(2.0 * math.pi * freq2 * t) * 0.5
            
            value = (val1 + val2) * 0.5 * envelope
            data.append(int(value * 32767.0))
            
        SoundGenerator.save_wav(str(sounds_dir / 'brick_hit.wav'), data)
        
        # 3. Wall Hit (Tick)
        data = SoundGenerator.generate_wave(220, 0.05, 0.4, 'sine')
        SoundGenerator.save_wav(str(sounds_dir / 'wall_hit.wav'), data)
        
        # 4. Powerup (Magic)
        data = []
        # Арпеджіо
        for freq in [440, 554, 659, 880]:
            data.extend(SoundGenerator.generate_wave(freq, 0.05, 0.5, 'sine'))
        SoundGenerator.save_wav(str(sounds_dir / 'powerup.wav'), data)
        
        # 5. Fire Ball Hit (Explosion-like)
        data = SoundGenerator.generate_wave(100, 0.2, 0.6, 'noise')
        SoundGenerator.save_wav(str(sounds_dir / 'fire_hit.wav'), data)
        
        # 6. Life Lost (Sad slide)
        data = []
        for i in range(100):
            freq = 440 - i * 3
            data.extend(SoundGenerator.generate_wave(freq, 0.01, 0.5, 'sawtooth'))
        SoundGenerator.save_wav(str(sounds_dir / 'life_lost.wav'), data)

        # 7. Menu Move (Blip)
        data = SoundGenerator.generate_wave(880, 0.05, 0.3, 'sine')
        SoundGenerator.save_wav(str(sounds_dir / 'menu_move.wav'), data)

        # 8. Menu Select (Confirm)
        data = []
        data.extend(SoundGenerator.generate_wave(880, 0.1, 0.4, 'sine'))
        data.extend(SoundGenerator.generate_wave(1760, 0.2, 0.4, 'sine'))
        SoundGenerator.save_wav(str(sounds_dir / 'menu_select.wav'), data)

        # 9. Level Complete (Victory Jingle)
        data = []
        for freq in [523, 659, 784, 1046, 784, 1046]: # C E G C G C
            data.extend(SoundGenerator.generate_wave(freq, 0.1, 0.5, 'square'))
        SoundGenerator.save_wav(str(sounds_dir / 'level_complete.wav'), data)

        # 10. Game Over (Defeat)
        data = []
        for freq in [300, 250, 200, 150]:
            data.extend(SoundGenerator.generate_wave(freq, 0.3, 0.5, 'sawtooth'))
        SoundGenerator.save_wav(str(sounds_dir / 'game_over.wav'), data)

        # 11. Metal Hit (Unbreakable brick)
        data = []
        data.extend(SoundGenerator.generate_wave(200, 0.05, 0.4, 'square'))
        data.extend(SoundGenerator.generate_wave(150, 0.1, 0.3, 'square'))
        SoundGenerator.save_wav(str(sounds_dir / 'metal_hit.wav'), data)

        # 12. Explosion (Explosive brick)
        data = []
        for i in range(5):
            freq = 100 + random.randint(-20, 20)
            data.extend(SoundGenerator.generate_wave(freq, 0.08, 0.6, 'noise'))
        SoundGenerator.save_wav(str(sounds_dir / 'explosion.wav'), data)


class SoundManager:
    """Менеджер звуків"""
    
    def __init__(self):
        from pathlib import Path
        self.sounds = {}
        self.enabled = True
        self.sounds_dir = Path(__file__).parent.parent / 'assets' / 'sounds'
        
        # Генеруємо звуки якщо їх немає (перевіряємо один з нових звуків)
        if not (self.sounds_dir / 'explosion.wav').exists() or not (self.sounds_dir / 'paddle_hit.wav').exists():
            print("Генерація звукових ефектів...")
            SoundGenerator.create_sounds()
            
        self.load_sounds()
    
    def load_sounds(self):
        """Завантажує звуки в пам'ять"""
        try:
            self.sounds['paddle_hit'] = pygame.mixer.Sound(str(self.sounds_dir / 'paddle_hit.wav'))
            self.sounds['brick_hit'] = pygame.mixer.Sound(str(self.sounds_dir / 'brick_hit.wav'))
            self.sounds['wall_hit'] = pygame.mixer.Sound(str(self.sounds_dir / 'wall_hit.wav'))
            self.sounds['powerup'] = pygame.mixer.Sound(str(self.sounds_dir / 'powerup.wav'))
            self.sounds['fire_hit'] = pygame.mixer.Sound(str(self.sounds_dir / 'fire_hit.wav'))
            self.sounds['life_lost'] = pygame.mixer.Sound(str(self.sounds_dir / 'life_lost.wav'))
            
            # Звуки меню
            self.sounds[' menu_move'] = pygame.mixer.Sound(str(self.sounds_dir / 'menu_move.wav'))
            self.sounds['menu_select'] = pygame.mixer.Sound(str(self.sounds_dir / 'menu_select.wav'))
            self.sounds['level_complete'] = pygame.mixer.Sound(str(self.sounds_dir / 'level_complete.wav'))
            self.sounds['game_over'] = pygame.mixer.Sound(str(self.sounds_dir / 'game_over.wav'))
            
            # Звуки цеглинок
            self.sounds['metal_hit'] = pygame.mixer.Sound(str(self.sounds_dir / 'metal_hit.wav'))
            self.sounds['explosion'] = pygame.mixer.Sound(str(self.sounds_dir / 'explosion.wav'))
            
            # Налаштування гучності
            for sound in self.sounds.values():
                sound.set_volume(0.4)
                
        except pygame.error as e:
            print(f"Помилка завантаження звуків: {e}")
            self.enabled = False

    def play(self, sound_name):
        """Відтворює звук за назвою"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def play_paddle_hit(self): self.play('paddle_hit')
    def play_brick_hit(self): self.play('brick_hit')
    def play_wall_hit(self): self.play('wall_hit')
    def play_powerup(self): self.play('powerup')
    def play_fire_hit(self): self.play('fire_hit')
    def play_life_lost(self): self.play('life_lost')
    
    # Звуки меню
    def play_menu_move(self): self.play('menu_move')
    def play_menu_select(self): self.play('menu_select')
    def play_level_complete(self): self.play('level_complete')
    def play_game_over(self): self.play('game_over')
    
    # Звуки цеглинок
    def play_metal_hit(self): self.play('metal_hit')
    def play_explosion(self): self.play('explosion')
