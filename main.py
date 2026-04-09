import pygame
from fighter import Fighter

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Braw Bizarre")

clock = pygame.time.Clock()
FPS = 60

# Cores
RED, YELLOW, WHITE, GREEN, GRAY = (255,0,0), (255,255,0), (255,255,255), (0,255,0), (50,50,50)

# Assets
bg_image = pygame.image.load("assets/images/Background_deserto.jpg").convert_alpha()
gore_font = "assets/fonts/gorefont.ttf"
menu_font = pygame.font.Font(gore_font, 64)
level_font = pygame.font.Font(gore_font, 100)
menu_subfont = pygame.font.SysFont(None, 36)

# Estados e Fade
game_started = level_selection = is_fading = False
next_state = None
fade_alpha = 0
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0,0,0))

level1_rect = pygame.Rect(150, 250, 200, 150)
level2_rect = pygame.Rect(400, 250, 200, 150)
level3_rect = pygame.Rect(650, 250, 200, 150)

fighter_1 = Fighter(200, 380, is_ai=False)
fighter_2 = Fighter(700, 380, is_ai=True)

def draw_interface():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 580, 20)

def draw_health_bar(health, x, y):
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, GREEN, (x, y, 400 * (max(0, health)/100), 30))

def draw_menu(title_str, prompt_str, color):
    screen.fill((0,0,0))
    t = menu_font.render(title_str, True, color)
    p = menu_subfont.render(prompt_str, True, WHITE)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 180))
    screen.blit(p, (SCREEN_WIDTH//2 - p.get_width()//2, 300))

def draw_levels():
    screen.fill((20,20,20))
    t = menu_font.render("SELECIONE O NIVEL", True, WHITE)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 80))
    for i, rect in enumerate([level1_rect, level2_rect, level3_rect], 1):
        color = GREEN if i == 1 else GRAY
        pygame.draw.rect(screen, color, rect, 2)
        txt = level_font.render(str(i), True, WHITE if i == 1 else GRAY)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        if not is_fading:
            if not game_started and not level_selection:
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    is_fading, next_state = True, "LEVEL_SELECT"
            elif level_selection:
                if event.type == pygame.MOUSEBUTTONDOWN and level1_rect.collidepoint(event.pos):
                    is_fading, next_state = True, "GAMEPLAY"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    is_fading, next_state = True, "START_SCREEN"

    if game_started:
        draw_interface()
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
        fighter_2.ai_logic(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1)
        for f in [fighter_1, fighter_2]:
            f.update()
            f.draw(screen)
    elif level_selection: draw_levels()
    else: draw_menu("Braw Bizarre", "Pressione qualquer tecla", RED)

    if is_fading:
        fade_alpha += 7
        if fade_alpha >= 255:
            fade_alpha, is_fading = 255, False
            level_selection = (next_state == "LEVEL_SELECT")
            game_started = (next_state == "GAMEPLAY")
    elif fade_alpha > 0:
        fade_alpha -= 7

    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0,0))
    
    pygame.display.update()
pygame.quit()