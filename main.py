import pygame
from fighter import Fighter, BossGnomo
from vampire import Vampire

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eclipse Lunar")

clock = pygame.time.Clock()
FPS = 60

RED, YELLOW, WHITE, GREEN, GRAY, BLACK = (255,0,0), (255,255,0), (255,255,255), (0,255,150), (50,50,50), (20,20,20)

def load_safe(path, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        surface = pygame.Surface((width, height))
        surface.fill((0, 0, 0))
        return surface

bg_image1 = pygame.transform.scale(load_safe("assets/images/Background_deserto.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_image2 = pygame.transform.scale(load_safe("assets/images/background2.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_image3 = pygame.transform.scale(load_safe("assets/images/backgroundcaverna.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

gore_font_path = "assets/fonts/gorefont.ttf"
try:
    menu_font = pygame.font.Font(gore_font_path, 64)
    level_font = pygame.font.Font(gore_font_path, 100)
    msg_font = pygame.font.Font(gore_font_path, 30)
except:
    menu_font = pygame.font.SysFont(None, 64)
    level_font = pygame.font.SysFont(None, 100)
    msg_font = pygame.font.SysFont(None, 30)
menu_subfont = pygame.font.SysFont(None, 36)

def scale_aspect(img):
    scale = min(SCREEN_WIDTH / img.get_width(), SCREEN_HEIGHT / img.get_height())
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

comic1 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho1.png"))
comic_prologo = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinhoprologo.png"))
comic_1e_prologo = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho1eprologo.png"))
comic2 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho2.png"))
comic3 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho3.png"))
comic4 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho4.png"))
comic5 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho5.png"))
comic_nivel3_2 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinhonivel3.2.png"))

comics = [comic1, comic_prologo, comic_1e_prologo, comic2, comic3, comic4, comic5, comic_nivel3_2]

game_started = level_selection = is_fading = game_over_lost = pacifist_broken = False
in_cutscene = True
next_state = None
fade_alpha = 0
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0,0,0))
current_level = 1
comic_index = 0
pacifist_timer = 0

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
    if current_level == 3: bg = bg_image3
    elif current_level == 2: bg = bg_image2
    else: bg = bg_image1
    screen.blit(bg, (0, 0))
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 580, 20)
    
def draw_health_bar(health, x, y):
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34), border_radius=5)
    pygame.draw.rect(screen, BLACK, (x, y, 400, 30), border_radius=5)
    pygame.draw.rect(screen, GREEN if health > 30 else RED, (x, y, 400 * (max(0, health)/100), 30), border_radius=5)

def draw_levels():
    screen.fill((20,20,20))
    t = menu_font.render("SELECIONE O NIVEL", True, WHITE)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 50))
    for i, rect in enumerate(level_rects, 1):
        pygame.draw.rect(screen, GREEN, rect, 2, border_radius=10)
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
    t2 = msg_font.render("Voce foi agressivo demais ou foi derrotado!", True, WHITE)
    p = menu_subfont.render("Clique para voltar ao menu", True, GRAY)
    screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 150))
    t2_rect = t2.get_rect(center=(SCREEN_WIDTH//2, 280))
    screen.blit(t2, t2_rect)
    screen.blit(p, (SCREEN_WIDTH//2 - p.get_width()//2, 450))

run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        if not is_fading:
            if in_cutscene:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if comic_index == 0:
                        is_fading, next_state = True, "LEVEL_SELECT"
                    else:
                        if current_level == 2: max_comic = 5
                        elif current_level == 3: max_comic = 7
                        else: max_comic = comic_index
                        if comic_index < max_comic:
                            is_fading, next_state = True, "NEXT_COMIC"
                        else:
                            is_fading, next_state = True, "GAMEPLAY"
            elif level_selection:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(level_rects, 1):
                        if rect.collidepoint(event.pos):
                            current_level = i
                            fighter_1 = Fighter(200, 380, is_ai=False)
                            if current_level == 1:
                                fighter_2 = Fighter(700, 380, is_ai=True, behavior="passive")
                                pacifist_timer = pygame.time.get_ticks()
                                pacifist_broken = False
                                is_fading, next_state = True, "GAMEPLAY"
                            elif current_level == 2:
                                fighter_2 = Vampire(700, 380, behavior="bully")
                                comic_index = 5
                                is_fading, next_state = True, "CUTSCENE"
                            elif current_level == 3:
                                fighter_2 = BossGnomo(700, 380)
                                comic_index = 6
                                is_fading, next_state = True, "CUTSCENE"
                            else:
                                fighter_2 = Fighter(700, 380, is_ai=True, behavior="bully")
                                is_fading, next_state = True, "GAMEPLAY"
                            break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    comic_index = 0
                    is_fading, next_state = True, "START_SCREEN"
            elif game_over_lost:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_fading, next_state = True, "LEVEL_SELECT"

    if game_started:
        draw_interface()
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
        fighter_2.ai_logic(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1)
        
        if current_level == 1:
            if fighter_2.health < 100:
                pacifist_broken = True
                fighter_2.behavior = "bully"
            
            if not pacifist_broken:
                p_time = pygame.time.get_ticks() - pacifist_timer
                if p_time > 3000:
                    rem_ms = 10000 - p_time
                    if rem_ms > 0:
                        bar_w = 400
                        bar_h = 12
                        fill_w = (rem_ms / 7000) * bar_w
                        timer_color = GREEN if rem_ms > 4000 else YELLOW
                        if rem_ms < 2000: timer_color = RED
                        
                        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - bar_w//2 - 2, 88, bar_w + 4, bar_h + 4), border_radius=10)
                        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - bar_w//2, 90, bar_w, bar_h), border_radius=10)
                        pygame.draw.rect(screen, timer_color, (SCREEN_WIDTH//2 - bar_w//2, 90, fill_w, bar_h), border_radius=10)
                        
                        txt_time = msg_font.render(str(int(rem_ms // 1000) + 1), True, WHITE)
                        screen.blit(txt_time, (SCREEN_WIDTH//2 - txt_time.get_width()//2, 50))
                
                if p_time > 10000 and not is_fading:
                    comic_index = 5
                    is_fading, next_state = True, "TRANSITION_L1_L2"

        for f in [fighter_1, fighter_2]:
            f.update()
            f.draw(screen)
            
        if current_level == 1 and fighter_2.health <= 0 and not is_fading:
            is_fading, next_state = True, "LOST_SCREEN"
        if current_level == 2 and fighter_2.health <= 0 and not is_fading:
            comic_index = 6
            is_fading, next_state = True, "TRANSITION_L2_L3"
        if fighter_1.health <= 0 and not is_fading:
            is_fading, next_state = True, "LOST_SCREEN"
            
    elif level_selection: draw_levels()
    elif in_cutscene: draw_cutscene()
    elif game_over_lost: draw_lost_screen()

    if is_fading:
        fade_alpha += 7
        if fade_alpha >= 255:
            fade_alpha, is_fading = 255, False
            if next_state == "NEXT_COMIC": comic_index += 1
            elif next_state == "START_SCREEN": in_cutscene, level_selection, game_started, game_over_lost = True, False, False, False
            elif next_state == "CUTSCENE": in_cutscene, level_selection, game_started, game_over_lost = True, False, False, False
            elif next_state == "TRANSITION_L1_L2":
                current_level, fighter_1 = 2, Fighter(200, 380, is_ai=False)
                fighter_2 = Vampire(700, 380, behavior="bully")
                in_cutscene, level_selection, game_started, game_over_lost = True, False, False, False
            elif next_state == "TRANSITION_L2_L3":
                current_level, fighter_1 = 3, Fighter(200, 380, is_ai=False)
                fighter_2 = BossGnomo(700, 380)
                in_cutscene, level_selection, game_started, game_over_lost = True, False, False, False
            elif next_state == "GAMEPLAY": game_started, level_selection, in_cutscene, game_over_lost = True, False, False, False
            elif next_state == "LEVEL_SELECT": level_selection, game_started, in_cutscene, game_over_lost = True, False, False, False
            elif next_state == "LOST_SCREEN": game_over_lost, game_started, level_selection, in_cutscene = True, False, False, False
    elif fade_alpha > 0: fade_alpha -= 7

    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0,0))
    pygame.display.update()
pygame.quit()