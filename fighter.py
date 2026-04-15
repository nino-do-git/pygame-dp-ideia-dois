import os
import pygame
import random

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

class Fighter():
    def __init__(self, x, y, is_ai=False, behavior="passive", character=None):
        self.is_ai, self.flip = is_ai, False
        self.character = character if character else ("et" if is_ai else "astronaut")
        self.rect = pygame.Rect((x, y, 40, 80))
        self.vel_y, self.jump, self.attacking = 0, False, False
        self.max_health = 100
        self.health, self.last_health = 100, 100
        self.last_attack_time, self.frame_index = 0, 0
        self.update_time = pygame.time.get_ticks()
        self.load_assets()
        self.current_animation = self.idle
        self.image = self.current_animation[self.frame_index]
        self.ai_direction, self.last_ai_decision = 0, 0
        self.behavior, self.aggro = behavior, False if behavior == "passive" else True

    def load_assets(self):
        S = 1.4
        if self.character == "astronaut":
            self.idle = [self.load_img("assets/images/astronauta/idlefuturista.png", S * 0.35)]
            self.walk = [self.load_img(f"assets/images/astronauta/walk{i}futurista.png", S) for i in range(1, 4)]
            self.attack_anim = [self.load_img(f"assets/images/astronauta/attack{i}futurista.png", S) for i in range(1, 4)]
            self.death = [self.load_img(f"assets/images/astronauta/die{i}futurista.png", S) for i in range(1, 4)]
        elif self.character == "et":
            self.idle = [self.load_img("assets/images/et/idleET.png", S * 0.75)]
            self.walk = [self.load_img(f"assets/images/et/walk{i}ET.png", S) for i in range(1, 4)]
            self.attack_anim = [self.load_img(f"assets/images/et/attack{i}ET.png", S) for i in range(1, 4)]
            self.death = [self.load_img("assets/images/et/die1ET.png", S * 0.20), self.load_img("assets/images/et/di2ET.png", S * 0.20)]

    def load_img(self, filepath, scale):
        paths = [filepath, filepath.replace('ã', 'a')]
        if "/" not in filepath:
            base = filepath
            paths.extend([
                f"assets/images/{base}",
                f"assets/images/gnomopaiemae/{base}",
                f"assets/images/et/{base}",
                f"assets/images/astronauta/{base}",
                f"assets/images/vampiro/{base}"
            ])
            paths.extend([p.replace('ã', 'a') for p in paths])
            
        img = None
        for p in paths:
            try:
                img = pygame.image.load(p).convert_alpha()
                break
            except:
                pass
        
        if not img:
            img = pygame.Surface((50, 50))
            img.fill((255, 0, 255))
            
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        return pygame.transform.scale(img, (w, h))

    def apply_physics(self, dx, sw, sh):
        self.vel_y += 2
        dy = self.vel_y
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > sw: dx = sw - self.rect.right
        if self.rect.bottom + dy > sh - 90: self.vel_y, self.jump, dy = 0, False, sh - 90 - self.rect.bottom
        self.rect.x += dx
        self.rect.y += dy
        self.update_animation_state(dx)

    def move(self, sw, sh, target):
        SPEED, dx = 10, 0
        key = pygame.key.get_pressed()
        if not self.attacking and self.health > 0:
            if key[pygame.K_a]: dx, self.flip = -SPEED, True
            if key[pygame.K_d]: dx, self.flip = SPEED, False
            if key[pygame.K_w] and not self.jump: self.vel_y, self.jump = -30, True
            if key[pygame.K_r]: self.attack(target)
        self.apply_physics(dx, sw, sh)

    def ai_logic(self, sw, sh, target):
        SPEED, dx, now = 3, 0, pygame.time.get_ticks()
        if self.behavior == "passive" and self.health < self.last_health: self.aggro = True
        self.last_health = self.health
        if self.health > 0:
            if self.behavior == "passive" and not self.aggro:
                if now - self.last_ai_decision > 1000:
                    self.last_ai_decision, self.ai_direction = now, random.choice([-SPEED, 0, SPEED])
                    if self.ai_direction != 0: self.flip = self.ai_direction < 0
                dx = self.ai_direction
                if random.randint(1, 100) <= 2 and not self.jump: self.vel_y, self.jump = -30, True
            elif self.behavior == "bully":
                if now - self.last_ai_decision > 400:
                    self.last_ai_decision, self.ai_direction = now, -SPEED if target.rect.centerx < self.rect.centerx else SPEED
                    self.flip = target.rect.centerx < self.rect.centerx
                dx = self.ai_direction
                if random.randint(1, 100) <= 6 and not self.jump: self.vel_y, self.jump = -30, True
                if abs(self.rect.centerx - target.rect.centerx) < 150: self.attack(target)
        self.apply_physics(dx, sw, sh)

    def update_animation_state(self, dx):
        if self.health <= 0:
            if self.current_animation != self.death: self.current_animation, self.frame_index = self.death, 0
        elif self.attacking:
            if self.current_animation != self.attack_anim: self.current_animation, self.frame_index = self.attack_anim, 0
        elif dx != 0:
            if self.current_animation != self.walk: self.current_animation, self.frame_index = self.walk, 0
        else:
            if self.current_animation != self.idle: self.current_animation, self.frame_index = self.idle, 0

    def attack(self, target):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > 800:
            self.attacking, self.last_attack_time = True, now
            W = self.attack_anim[0].get_width()
            att_rect = pygame.Rect(self.rect.centerx if not self.flip else self.rect.centerx - W//2, self.rect.y, W//2, self.rect.height)
            if att_rect.colliderect(target.rect):
                target.health -= 10

    def update(self):
        if pygame.time.get_ticks() - self.update_time > 120:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.current_animation):
            if self.health <= 0: self.frame_index = len(self.current_animation) - 1
            else: self.frame_index, self.attacking = 0, False
        self.image = self.current_animation[self.frame_index]

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.centerx - (img.get_width() // 2), self.rect.bottom - img.get_height()))