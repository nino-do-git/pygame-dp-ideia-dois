import pygame
from fighter import Fighter

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Braw Bizarre")

clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)

bg_image = pygame.image.load("assets/images/Background_deserto.jpg").convert_alpha()
menu_font = pygame.font.Font("assets/fonts/gorefont.ttf", 64)
menu_subfont = pygame.font.SysFont(None, 36)
level_font = pygame.font.Font("assets/fonts/gorefont.ttf", 100)

game_started = False
level_selection = False

level1_rect = pygame.Rect(150, 250, 200, 150)
level2_rect = pygame.Rect(400, 250, 200, 150)
level3_rect = pygame.Rect(650, 250, 200, 150)

fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0, 0, 0))
fade_alpha = 0
fade_speed = 5
is_fading = False
next_state = None 

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, GREEN, (x, y, 400 * ratio, 30))

def draw_start_screen():
    screen.fill((0, 0, 0))
    title = menu_font.render("Braw Bizarre", True, RED)
    prompt = menu_subfont.render("Pressione qualquer tecla para começar", True, YELLOW)
    instructions = menu_subfont.render("W = pular, A/D = mover, R = atacar", True, WHITE)
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 180))
    screen.blit(prompt, ((SCREEN_WIDTH - prompt.get_width()) // 2, 300))
    screen.blit(instructions, ((SCREEN_WIDTH - instructions.get_width()) // 2, 360))

def draw_level_select():
    screen.fill((20, 20, 20))
    title = menu_font.render("SELECIONE O NIVEL", True, WHITE)
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))
    pygame.draw.rect(screen, GREEN, level1_rect, 2)
    txt1 = level_font.render("1", True, WHITE)
    screen.blit(txt1, (level1_rect.centerx - txt1.get_width()//2, level1_rect.centery - txt1.get_height()//2))
    pygame.draw.rect(screen, GRAY, level2_rect, 2)
    txt2 = level_font.render("2", True, GRAY)
    screen.blit(txt2, (level2_rect.centerx - txt2.get_width()//2, level2_rect.centery - txt2.get_height()//2))
    pygame.draw.rect(screen, GRAY, level3_rect, 2)
    txt3 = level_font.render("3", True, GRAY)
    screen.blit(txt3, (level3_rect.centerx - txt3.get_width()//2, level3_rect.centery - txt3.get_height()//2))

fighter_1 = Fighter(200, 310, is_ai=False)
fighter_2 = Fighter(700, 310, is_ai=True)

run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if not is_fading: 
            if not game_started and not level_selection:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    is_fading = True
                    next_state = "LEVEL_SELECT"
            
            elif level_selection and not game_started:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if level1_rect.collidepoint(mouse_pos):
                        is_fading = True
                        next_state = "GAMEPLAY"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        is_fading = True
                        next_state = "START_SCREEN"

    if not game_started:
        if level_selection:
            draw_level_select()
        else:
            draw_start_screen()
    else:
        draw_bg()
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 580, 20)
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2)
        fighter_1.update()
        fighter_1.draw(screen)
        fighter_2.ai_move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1)
        fighter_2.update()
        fighter_2.draw(screen)

    if is_fading:
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            fade_alpha = 255
            is_fading = False
            
            if next_state == "LEVEL_SELECT":
                level_selection = True
                game_started = False
            elif next_state == "GAMEPLAY":
                level_selection = False
                game_started = True
            elif next_state == "START_SCREEN":
                level_selection = False
                game_started = False

    elif fade_alpha > 0:
        fade_alpha -= fade_speed
        if fade_alpha < 0: fade_alpha = 0

    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

    pygame.display.update()

pygame.quit()