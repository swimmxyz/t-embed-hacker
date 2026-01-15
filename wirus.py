import pygame
import sys
import os
from PIL import Image

# Inicjalizacja pygame
pygame.init()

# Ustawienia fullscreen
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("App")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Pobierz ścieżkę do folderu ze skryptem
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()

# Załaduj GIF
gif_frames = []
try:
    gif_path = os.path.join(script_dir, 'hed.gif')
    gif = Image.open(gif_path)
    print(f"Załadowano GIF z: {gif_path}")
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert('RGBA')
        # Zmień rozmiar GIFa (możesz dostosować)
        new_size = (150, 150)
        frame_image = frame_image.resize(new_size, Image.Resampling.LANCZOS)
        mode = frame_image.mode
        size = frame_image.size
        data = frame_image.tobytes()
        pygame_image = pygame.image.fromstring(data, size, mode)
        gif_frames.append(pygame_image)
except Exception as e:
    print(f"Nie można załadować hed.gif: {e}")
    # Placeholder
    placeholder = pygame.Surface((150, 150))
    placeholder.fill((200, 200, 200))
    gif_frames.append(placeholder)

# Rozmiar pojedynczego GIFa
gif_size = gif_frames[0].get_size() if gif_frames else (150, 150)

# Parametry animacji pasków PIONOWYCH od dołu do góry
num_bars = 5
bar_width = WIDTH // num_bars
bars = []
bar_delay = 80  # ms między kolejnymi paskami

# Inicjalizacja pasków
for i in range(num_bars):
    bars.append({
        'x': i * bar_width,
        'height': 0,
        'target_height': HEIGHT,
        'speed': 0,
        'active': False,
        'done': False
    })

# Font dla tekstu
font = pygame.font.Font(None, 120)

# Parametry animacji GIF
current_frame = 0
frame_delay = 100
last_frame_time = pygame.time.get_ticks()

# Stany animacji
STATE_BARS = 0
STATE_FLASH = 1
STATE_CONTENT = 2

current_state = STATE_BARS
start_time = pygame.time.get_ticks()
flash_start_time = 0
flash_duration = 300
bars_visible_height = [0] * num_bars  # Zapisz wysokości pasków

# Główna pętla
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    # Sprawdź eventy
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Czarne tło
    screen.fill(BLACK)
    
    if current_state == STATE_BARS:
        print(f"STATE_BARS - Active bars: {sum(1 for b in bars if b['active'])}, Done: {sum(1 for b in bars if b['done'])}")  # DEBUG
        # Animacja pasków
        all_bars_done = True
        
        for i, bar in enumerate(bars):
            if not bar['active'] and current_time - start_time >= i * bar_delay:
                bar['active'] = True
            
            if bar['active'] and not bar['done']:
                distance = bar['target_height'] - bar['height']
                
                if bar['height'] < bar['target_height']:
                    bar['speed'] = 50  # Stała szybkość
                    bar['height'] += bar['speed']
                    if bar['height'] >= bar['target_height']:
                        bar['height'] = bar['target_height']
                        bar['done'] = True
                    all_bars_done = False
                else:
                    bar['height'] = bar['target_height']
                    bar['done'] = True
            
            # Zapisz wysokość i rysuj pasek OD GÓRY
            bars_visible_height[i] = int(bar['height'])
            pygame.draw.rect(screen, WHITE, 
                           (int(bar['x']), 0, 
                            bar_width + 2, bars_visible_height[i]))
        
        if all_bars_done and bars[-1]['active']:
            print("SWITCHING TO FLASH!")  # DEBUG
            current_state = STATE_FLASH
            flash_start_time = current_time
    
    elif current_state == STATE_FLASH:
        print(f"STATE_FLASH - elapsed: {current_time - flash_start_time}ms")  # DEBUG
        # Biały flash - paski już nie widoczne
        screen.fill(WHITE)
        
        if current_time - flash_start_time >= flash_duration:
            print("SWITCHING TO CONTENT!")  # DEBUG
            current_state = STATE_CONTENT
    
    elif current_state == STATE_CONTENT:
        # Białe tło
        screen.fill(WHITE)
        
        print(f"STATE_CONTENT - Drawing {len(gif_frames)} frames")  # DEBUG
        
        # Animacja GIF
        if current_time - last_frame_time > frame_delay:
            current_frame = (current_frame + 1) % len(gif_frames)
            last_frame_time = current_time
        
        # Rysuj GIFy w siatce (tapeta)
        if gif_frames:
            gif_surface = gif_frames[current_frame]
            
            # Oblicz ile GIFów zmieści się w poziomie i pionie
            cols = (WIDTH // gif_size[0]) + 2
            rows = (HEIGHT // gif_size[1]) + 2
            
            print(f"Drawing grid: {cols}x{rows}")  # DEBUG
            
            # Rysuj GIFy w siatce
            for row in range(rows):
                for col in range(cols):
                    x = col * gif_size[0]
                    y = row * gif_size[1]
                    screen.blit(gif_surface, (x, y))
        
        # Tekst na środku bez tła
        text = font.render("hacked by swimm", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        print(f"Text drawn at: {text_rect}")  # DEBUG
    
    pygame.display.flip()
    clock.tick(60)

# Cleanup
pygame.quit()
sys.exit()
