import os
import pygame
from fighter import Fighter
from bossgnomo import BossGnomo
from vampire import Vampire

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eclipse Lunar")

clock = pygame.time.Clock()
FPS = 60

RED, YELLOW, WHITE, GREEN, GRAY, BLACK, MAGENTA = (255,0,0), (255,255,0), (255,255,255), (0,255,150), (50,50,50), (20,20,20), (255,0,255)

def find_asset(filename):
    if not os.path.exists("assets"): return filename
    target_name = filename.split('/')[-1].rsplit('.', 1)[0].replace('ã', 'a').lower()
    for root, _, files in os.walk("assets"):
        for f in files:
            if '.' in f:
                f_name = f.rsplit('.', 1)[0].replace('ã', 'a').lower()
                if f_name == target_name:
                    return os.path.join(root, f)
    return filename

def load_safe(filepath, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
    try:
        return pygame.image.load(filepath).convert_alpha()
    except:
        surface = pygame.Surface((width, height))
        surface.fill(MAGENTA)
        return surface

bg_image1 = pygame.transform.scale(load_safe("assets/images/Background_deserto.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_image2 = pygame.transform.scale(load_safe("assets/images/background2.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_image3 = pygame.transform.scale(load_safe("assets/images/backgroundcaverna.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

try:
    menu_font = pygame.font.Font(find_asset("Pixel Digivolve.otf"), 64)
    level_font = pygame.font.Font(find_asset("Pixel Digivolve.otf"), 100)
    button_font = pygame.font.Font(find_asset("Pixel Digivolve.otf"), 30)
    msg_font = pygame.font.Font(find_asset("gorefont.ttf"), 30)
except:
    menu_font = pygame.font.SysFont(None, 64)
    level_font = pygame.font.SysFont(None, 100)
    button_font = pygame.font.SysFont(None, 30)
    msg_font = pygame.font.SysFont(None, 30)

try:
    go_font = pygame.font.Font(find_asset("game_over.ttf"), 150)
    go_msg_font = pygame.font.Font(find_asset("game_over.ttf"), 80)
except:
    go_font = pygame.font.SysFont(None, 150)
    go_msg_font = pygame.font.SysFont(None, 80)

try:
    t_font = pygame.font.Font(find_asset("digital-7.ttf"), 50)
except:
    t_font = pygame.font.SysFont(None, 50)

menu_subfont = pygame.font.SysFont(None, 36)

txt_jogar = button_font.render("JOGAR", True, WHITE)
play_button_center_rect = pygame.Rect(SCREEN_WIDTH//2 - txt_jogar.get_width()//2 - 15, SCREEN_HEIGHT - 70, txt_jogar.get_width() + 30, txt_jogar.get_height() + 10)
play_button_right_rect = pygame.Rect(SCREEN_WIDTH - txt_jogar.get_width() - 30, SCREEN_HEIGHT - 70, txt_jogar.get_width() + 20, txt_jogar.get_height() + 10)

txt_proxima = button_font.render("PROXIMA", True, WHITE)
next_button_rect = pygame.Rect(SCREEN_WIDTH - txt_proxima.get_width() - 30, SCREEN_HEIGHT - 70, txt_proxima.get_width() + 20, txt_proxima.get_height() + 10)

txt_voltar = button_font.render("VOLTAR", True, WHITE)
back_button_rect = pygame.Rect(10, SCREEN_HEIGHT - 70, txt_voltar.get_width() + 20, txt_voltar.get_height() + 10)

def scale_aspect(img):
    if img.get_width() == 0 or img.get_height() == 0: return img
    scale = min(SCREEN_WIDTH / img.get_width(), SCREEN_HEIGHT / img.get_height())
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

c0 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinhoinicial.png"))
c1 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho1.1.png"))
c2 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho1.2.png"))
c3 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho1.3.png"))
c4 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho1.4.png"))
c5 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho2.1.png"))
c6 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho3.1.png"))
c7 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinhonivel3.2.png"))
c8 = scale_aspect(load_safe("assets/images/quadrinhos/Quadrinho3.3.png"))

comics = [c0, c1, c2, c3, c4, c5, c6, c7, c8]

game_started = level_selection = is_fading = game_over_lost = pacifist_broken = False
in_cutscene = True
next_state = None
fade_alpha = 0
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0,0,0))
current_level = 1
comic_index = 0
pacifist_timer = 0

boss_phase_2 = False
in_boss_transition = False
transition_start_time = 0
base_snap = None
boss_center = (0, 0)
transicao_anim = []
transicao_index = 0
transicao_timer = 0

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

def load_transicao_sprites():
    global transicao_anim
    S = 1.0
    try:
        t1 = pygame.image.load(find_asset("tansform1gnomo.png")).convert_alpha()
        t2 = pygame.image.load(find_asset("transform2gnomo.png")).convert_alpha()
        transicao_anim = [
            pygame.transform.scale(t1, (int(t1.get_width() * S), int(t1.get_height() * S))),
            pygame.transform.scale(t2, (int(t2.get_width() * S), int(t2.get_height() * S)))
        ]
    except:
        surface = pygame.Surface((50, 50))
        surface.fill(MAGENTA)
        transicao_anim = [surface, surface]

load_transicao_sprites()

def draw_interface():
    if current_level == 3: bg = bg_image3
    elif current_level == 2: bg = bg_image2
    else: bg = bg_image1
    screen.blit(bg, (0, 0))
    draw_health_bar(fighter_1.health, fighter_1.max_health, 20, 20)
    draw_health_bar(fighter_2.health, fighter_2.max_health, 580, 20)
    
def draw_health_bar(health, max_health, x, y):
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34), border_radius=5)
    pygame.draw.rect(screen, BLACK, (x, y, 400, 30), border_radius=5)
    ratio = max(0, health) / max_health
    pygame.draw.rect(screen, GREEN if ratio > 0.3 else RED, (x, y, 400 * ratio, 30), border_radius=5)

def draw_levels():
    screen.fill((20,20,20))
    t = menu_font.render("SELECIONE O NIVEL", True, WHITE)
    screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 50))
    mouse_pos = pygame.mouse.get_pos()
    
    for i, rect in enumerate(level_rects, 1):
        color = GREEN if rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10)
        txt = level_font.render(str(i), True, WHITE)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

def draw_cutscene():
    screen.fill((0, 0, 0))
    img = comics[comic_index]
    x = (SCREEN_WIDTH - img.get_width()) // 2
    y = (SCREEN_HEIGHT - img.get_height()) // 2
    screen.blit(img, (x, y))
    
    mouse_pos = pygame.mouse.get_pos()
    
    max_c = 5
    if current_level == 2: max_c = 6
    elif current_level == 3: max_c = 9
    
    is_last_comic = (comic_index != 0 and comic_index == max_c - 1)
    
    if comic_index == 0:
        color = GREEN if play_button_center_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, play_button_center_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, play_button_center_rect, 2, border_radius=5)
        txt = button_font.render("JOGAR", True, WHITE)
        screen.blit(txt, (play_button_center_rect.centerx - txt.get_width()//2, play_button_center_rect.centery - txt.get_height()//2))
    elif is_last_comic:
        color = GREEN if play_button_right_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, play_button_right_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, play_button_right_rect, 2, border_radius=5)
        txt = button_font.render("JOGAR", True, WHITE)
        screen.blit(txt, (play_button_right_rect.centerx - txt.get_width()//2, play_button_right_rect.centery - txt.get_height()//2))
    else:
        color = GREEN if next_button_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, next_button_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, next_button_rect, 2, border_radius=5)
        txt = button_font.render("PROXIMA", True, WHITE)
        screen.blit(txt, (next_button_rect.centerx - txt.get_width()//2, next_button_rect.centery - txt.get_height()//2))
        
    if comic_index != 0:
        base_c = 1
        if current_level == 2: base_c = 5
        elif current_level == 3: base_c = 6
        
        if comic_index > base_c:
            color = GREEN if back_button_rect.collidepoint(mouse_pos) else GRAY
            pygame.draw.rect(screen, color, back_button_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, back_button_rect, 2, border_radius=5)
            txt = button_font.render("VOLTAR", True, WHITE)
            screen.blit(txt, (back_button_rect.centerx - txt.get_width()//2, back_button_rect.centery - txt.get_height()//2))

def draw_lost_screen():
    screen.fill((0, 0, 0))
    t1 = go_font.render("PERDEU", True, RED)
    
    if current_level == 1:
        msg = "Voce foi agressivo demais ou foi derrotado!"
    elif current_level == 2:
        msg = "O vampiro sugou toda sua energia!"
    else:
        msg = "A familia de gnomos te esmagou!"
        
    t2 = go_msg_font.render(msg, True, RED)
    p = menu_subfont.render("Clique para voltar ao menu", True, GRAY)
    
    screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 100))
    screen.blit(t2, t2.get_rect(center=(SCREEN_WIDTH//2, 280)))
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
                        if play_button_center_rect.collidepoint(event.pos):
                            is_fading, next_state = True, "LEVEL_SELECT"
                    else:
                        base_c = 1
                        max_c = 5
                        if current_level == 2: 
                            base_c = 5
                            max_c = 6
                        elif current_level == 3: 
                            base_c = 6
                            max_c = 9
                            
                        is_last_comic = (comic_index == max_c - 1)
                        
                        if is_last_comic:
                            if play_button_right_rect.collidepoint(event.pos):
                                if current_level == 1: pacifist_timer = pygame.time.get_ticks()
                                is_fading, next_state = True, "GAMEPLAY"
                        else:
                            if next_button_rect.collidepoint(event.pos):
                                is_fading, next_state = True, "NEXT_COMIC"
                                
                        if back_button_rect.collidepoint(event.pos) and comic_index > base_c:
                            is_fading, next_state = True, "PREV_COMIC"
            elif level_selection:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(level_rects, 1):
                        if rect.collidepoint(event.pos):
                            current_level = i
                            fighter_1 = Fighter(200, 380, is_ai=False)
                            boss_phase_2 = False
                            in_boss_transition = False
                            if current_level == 1:
                                fighter_2 = Fighter(700, 380, is_ai=True, behavior="passive")
                                pacifist_broken = False
                                comic_index = 1
                                is_fading, next_state = True, "CUTSCENE"
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
                if event.type == pygame.MOUSEBUTTONDOWN: is_fading, next_state = True, "LEVEL_SELECT"

    if game_started:
        if current_level == 3 and fighter_2.health <= fighter_2.max_health / 2 and not boss_phase_2:
            boss_phase_2 = True
            in_boss_transition = True
            transition_start_time = pygame.time.get_ticks()
            transicao_index = 0
            transicao_timer = pygame.time.get_ticks()
            
            screen.blit(bg_image3, (0, 0))
            for f in [fighter_1, fighter_2]:
                f.draw(screen)
            base_snap = screen.copy()
            boss_center = (fighter_2.rect.centerx, fighter_2.rect.centery - 30)

        if not in_boss_transition:
            draw_interface()
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
            fighter_2.ai_logic(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1)
            
            if current_level == 1:
                if fighter_2.health < fighter_2.max_health:
                    pacifist_broken = True
                    fighter_2.behavior = "bully"
                if not pacifist_broken:
                    p_time = pygame.time.get_ticks() - pacifist_timer
                    if p_time > 3000:
                        rem_ms = 13000 - p_time
                        if rem_ms > 0:
                            bw, bh = 400, 12
                            fw = (rem_ms / 10000) * bw
                            color = GREEN if rem_ms > 4000 else YELLOW
                            if rem_ms < 2000: color = RED
                            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - bw//2 - 2, 88, bw + 4, bh + 4), border_radius=10)
                            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - bw//2, 90, bw, bh), border_radius=10)
                            pygame.draw.rect(screen, color, (SCREEN_WIDTH//2 - bw//2, 90, fw, bh), border_radius=10)
                            txt = t_font.render(str(int(rem_ms // 1000) + 1), True, WHITE)
                            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 40))
                    if p_time >= 13000 and not is_fading:
                        comic_index = 5
                        is_fading, next_state = True, "TRANSITION_L1_L2"
                        
            for f in [fighter_1, fighter_2]:
                f.update()
                f.draw(screen)
                
            if fighter_1.health <= 0 or (current_level == 1 and fighter_2.health <= 0) and not is_fading:
                is_fading, next_state = True, "LOST_SCREEN"
            if current_level == 2 and fighter_2.health <= 0 and not is_fading:
                comic_index = 6
                is_fading, next_state = True, "TRANSITION_L2_L3"
                
        else:
            draw_interface()
            fighter_1.draw(screen)
            
            t = pygame.time.get_ticks() - transition_start_time
            
            if t < 1000:
                fighter_2.image = fighter_2.idle_mae[0]
            elif t < 3000:
                if pygame.time.get_ticks() - transicao_timer > 200:
                    transicao_index = (transicao_index + 1) % len(transicao_anim)
                    transicao_timer = pygame.time.get_ticks()
                fighter_2.image = transicao_anim[transicao_index]
            else:
                fighter_2.image = fighter_2.idle_pai[0]
            
            fighter_2.draw(screen)
            
            target_zoom = 1.4
            
            if t < 1000:
                current_zoom = 1.0 + (target_zoom - 1.0) * (t / 1000)
                alpha = 255
            elif t < 3000:
                current_zoom = target_zoom
                alpha = 255
            else:
                current_zoom = target_zoom
                alpha = max(0, 255 - int(((t - 3000) / 1000) * 255))
                
            if base_snap:
                screen.blit(bg_image3, (0, 0))
                fighter_1.draw(screen)
                fighter_2.draw(screen)
                snap_atualizado = screen.copy()
                
                zoomed = pygame.transform.scale(snap_atualizado, (int(SCREEN_WIDTH * current_zoom), int(SCREEN_HEIGHT * current_zoom)))
                bx, by = boss_center
                offset_x = (SCREEN_WIDTH // 2) - int(bx * current_zoom)
                offset_y = (SCREEN_HEIGHT // 2) - int(by * current_zoom)
                
                zoom_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                zoom_surface.blit(zoomed, (offset_x, offset_y))
                zoom_surface.set_alpha(alpha)
                
                draw_interface()
                fighter_1.draw(screen)
                fighter_2.draw(screen)
                screen.blit(zoom_surface, (0, 0))
            
            if t >= 4000:
                in_boss_transition = False
                fighter_2.image = fighter_2.idle_pai[0]

    elif level_selection: draw_levels()
    elif in_cutscene: draw_cutscene()
    elif game_over_lost: draw_lost_screen()

    if is_fading:
        fade_alpha += 7
        if fade_alpha >= 255:
            fade_alpha, is_fading = 255, False
            if next_state == "NEXT_COMIC": comic_index += 1
            elif next_state == "PREV_COMIC": comic_index -= 1
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