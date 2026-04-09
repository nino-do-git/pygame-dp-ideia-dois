import pygame
from fighter import Fighter, Vampire

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Braw Bizarre")

clock = pygame.time.Clock()
FPS = 60

RED, YELLOW, WHITE, GREEN, GRAY = (255,0,0), (255,255,0), (255,255,255), (0,255,0), (50,50,50)

bg_image = pygame.image.load("assets/images/Background_deserto.jpg").convert_alpha()
gore_font = "assets/fonts/gorefont.ttf"
menu_font = pygame.font.Font(gore_font, 64)
level_font = pygame.font.Font(gore_font, 100)
msg_font = pygame.font.Font(gore_font, 30)
menu_subfont = pygame.font.SysFont(None, 36)

c1_img = pygame.image.load("assets/images/quadrinhos/Quadrinho1.png").convert_alpha()
comic1 = pygame.transform.scale(c1_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

def scale_aspect(img):
    scale = min(SCREEN_WIDTH / img.get_width(), SCREEN_HEIGHT / img.get_height())
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

comic2 = scale_aspect(pygame.image.load("assets/images/quadrinhos/Quadrinho2.png").convert_alpha())
comic3 = scale_aspect(pygame.image.load("assets/images/quadrinhos/Quadrinho3.png").convert_alpha())
comics = [comic1, comic2, comic3]

game_started = level_selection = in_cutscene = is_fading = game_over_lost = False
next_state = None
fade_alpha = 0
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0,0,0))
current_level = 1
comic_index = 0

level_rects = [
    pygame.Rect(150, 150, 200, 150),
    pygame.Rect(400, 150, 200, 150),
    pygame.Rect(650, 150, 200, 150),
    pygame.Rect(150, 350, 200, 150),
    pygame.Rect(400, 350, 200, 150),
    pygame.Rect(650, 350, 200, 150)
]

fighter_1 = Fighter(200, 380, is_ai=False)
fighter_2 = Fighter(700, 380, is_ai=True, behavior="passive")

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
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 50))
    for i, rect in enumerate(level_rects, 1):
        pygame.draw.rect(screen, GREEN, rect, 2)
        txt = level_font.render(str(i), True, WHITE)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

def draw_cutscene():
    screen.fill((0, 0, 0))
    img = comics[comic_index]
    x = (SCREEN_WIDTH - img.get_width()) // 2
    y = (SCREEN_HEIGHT - img.get_height()) // 2
    screen.blit(img, (x, y))

def draw_lost_screen():
    screen.fill((0, 0, 0))
    t1 = menu_font.render("PERDEU", True, RED)
    t2 = msg_font.render("Voce foi agressivo demais com quem nao deveria!", True, WHITE)
    p = menu_subfont.render("Clique para voltar ao menu", True, GRAY)
    screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 150))
    screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 280))
    screen.blit(p, (SCREEN_WIDTH//2 - p.get_width()//2, 450))

run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        if not is_fading:
            if not game_started and not level_selection and not in_cutscene and not game_over_lost:
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    is_fading, next_state = True, "LEVEL_SELECT"
            elif level_selection:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(level_rects, 1):
                        if rect.collidepoint(event.pos):
                            current_level = i
                            fighter_1 = Fighter(200, 380, is_ai=False)
                            if current_level == 1:
                                fighter_2 = Fighter(700, 380, is_ai=True, behavior="passive")
                                comic_index = 0
                                is_fading, next_state = True, "CUTSCENE"
                            elif current_level == 2:
                                fighter_2 = Vampire(700, 380, behavior="bully")
                                is_fading, next_state = True, "GAMEPLAY"
                            elif current_level == 6:
                                fighter_2 = Fighter(700, 380, is_ai=True, behavior="bully", character="astronaut")
                                is_fading, next_state = True, "GAMEPLAY"
                            else:
                                fighter_2 = Fighter(700, 380, is_ai=True, behavior="bully")
                                is_fading, next_state = True, "GAMEPLAY"
                            break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    is_fading, next_state = True, "START_SCREEN"
            elif in_cutscene:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if comic_index < 2:
                        is_fading, next_state = True, "NEXT_COMIC"
                    else:
                        is_fading, next_state = True, "GAMEPLAY"
            elif game_over_lost:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_fading, next_state = True, "LEVEL_SELECT"

    if game_started:
        draw_interface()
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
        fighter_2.ai_logic(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1)
        for f in [fighter_1, fighter_2]:
            f.update()
            f.draw(screen)
        if current_level == 1 and fighter_2.health <= 0:
            is_fading, next_state = True, "LOST_SCREEN"
    elif level_selection: draw_levels()
    elif in_cutscene: draw_cutscene()
    elif game_over_lost: draw_lost_screen()
    else: draw_menu("Braw Bizarre", "Pressione qualquer tecla", RED)

    if is_fading:
        fade_alpha += 7
        if fade_alpha >= 255:
            fade_alpha, is_fading = 255, False
            if next_state == "NEXT_COMIC":
                comic_index += 1
            elif next_state == "CUTSCENE":
                in_cutscene, level_selection, game_started, game_over_lost = True, False, False, False
            elif next_state == "GAMEPLAY":
                game_started, level_selection, in_cutscene, game_over_lost = True, False, False, False
            elif next_state == "LEVEL_SELECT":
                level_selection, game_started, in_cutscene, game_over_lost = True, False, False, False
            elif next_state == "START_SCREEN":
                level_selection, game_started, in_cutscene, game_over_lost = False, False, False, False
            elif next_state == "LOST_SCREEN":
                game_over_lost, game_started, level_selection, in_cutscene = True, False, False, False
    elif fade_alpha > 0:
        fade_alpha -= 7

    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0,0))
    
    pygame.display.update()
pygame.quit()