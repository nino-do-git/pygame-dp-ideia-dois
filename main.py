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

bg_image = pygame.image.load("assets/images/Background_deserto.jpg").convert_alpha()
menu_font = pygame.font.SysFont(None, 64)
menu_subfont = pygame.font.SysFont(None, 36)

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
    title = menu_font.render("Braw Bizarre", True, WHITE)
    prompt = menu_subfont.render("Pressione qualquer tecla para jogar", True, YELLOW)
    instructions = menu_subfont.render("W = pular, A/D = mover, R = atacar", True, WHITE)

    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 180))
    screen.blit(prompt, ((SCREEN_WIDTH - prompt.get_width()) // 2, 300))
    screen.blit(instructions, ((SCREEN_WIDTH - instructions.get_width()) // 2, 360))

fighter_1 = Fighter(200, 310, is_ai=False)
fighter_2 = Fighter(700, 310, is_ai=True)

game_started = False
run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and not game_started:
            game_started = True

    if not game_started:
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

    pygame.display.update()

pygame.quit()