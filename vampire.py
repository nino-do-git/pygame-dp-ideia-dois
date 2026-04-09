import pygame
import random
from projectile import Projectile


class Vampire():
    def __init__(self, x, y, behavior="bully"):
        self.flip = False
        self.rect = pygame.Rect((x, y, 40, 80))
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 50
        self.last_health = 100
        self.last_attack_time = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.projectiles = []
        self.behavior = behavior
        self.aggro = True 

        self.load_assets()
        self.current_animation = self.idle
        self.image = self.current_animation[self.frame_index]

        self.ai_direction = 0
        self.last_ai_decision = 0

    def load_assets(self):
        SCALE = 1.4
        VAMP_SCALE = SCALE * 1.05
        VAMP_PROJECTILE_SCALE = SCALE * 0.7 
        path = "assets/images/vampiro"
        
        self.idle = [self.load_img(f"{path}/idlevamp.png", VAMP_SCALE)]
        self.walk = [self.load_img(f"{path}/walk{i}vamp.png", VAMP_SCALE) for i in range(1, 4)]
        self.attack_anim = [self.load_img(f"{path}/attack{i}vamp.png", VAMP_SCALE) for i in range(1, 3)]
        self.death = [self.load_img(f"{path}/die{i}vamp.png", VAMP_SCALE) for i in range(1, 3)]
        self.eject_img = self.load_img(f"{path}/ejectvamp.png", VAMP_PROJECTILE_SCALE)

    def load_img(self, path, scale):
        img = pygame.image.load(path).convert_alpha()
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        return pygame.transform.scale(img, (w, h))

    def ai_logic(self, screen_width, screen_height, target):
        SPEED = 3
        GRAVITY = 2
        dx = 0
        dy = 0
        dist = abs(self.rect.centerx - target.rect.centerx)
        now = pygame.time.get_ticks()
        attack_range = 500 

        if self.health > 0:
            if self.behavior == "bully":
                if now - self.last_ai_decision > 400:
                    self.last_ai_decision = now
                    if target.rect.centerx < self.rect.centerx:
                        self.ai_direction = -SPEED
                        self.flip = True
                    else:
                        self.ai_direction = SPEED
                        self.flip = False
                
                dx = self.ai_direction
                
                if random.randint(1, 100) <= 6 and not self.jump:
                    self.vel_y = -30
                    self.jump = True
                
                if target.health > 20 and dist < attack_range:
                    self.attack(target)

        self.vel_y += GRAVITY
        dy += self.vel_y
        self.apply_constraints(dx, dy, screen_width, screen_height)
        self.update_animation_state(dx)

    def apply_constraints(self, dx, dy, sw, sh):
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > sw: dx = sw - self.rect.right
        if self.rect.bottom + dy > sh - 90:
            self.vel_y = 0
            self.jump = False
            dy = sh - 90 - self.rect.bottom
        self.rect.x += dx
        self.rect.y += dy

    def update_animation_state(self, dx):
        if self.health <= 0:
            if self.current_animation != self.death:
                self.current_animation = self.death
                self.frame_index = 0
        elif self.attacking:
            if self.current_animation != self.attack_anim:
                self.current_animation = self.attack_anim
                self.frame_index = 0
        elif dx != 0:
            if self.current_animation != self.walk:
                self.current_animation = self.walk
                self.frame_index = 0
        else:
            if self.current_animation != self.idle:
                self.current_animation = self.idle
                self.frame_index = 0

    def attack(self, target):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > 800:
            self.attacking = True
            self.last_attack_time = now
            
            proj_dir = -1 if self.flip else 1
            proj_x = self.rect.left - 20 if self.flip else self.rect.right
            proj = Projectile(proj_x, self.rect.centery - 20, proj_dir, self.eject_img, target)
            self.projectiles.append(proj)

    def update(self):
        animation_cooldown = 120
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            
        if self.frame_index >= len(self.current_animation):
            if self.health <= 0:
                self.frame_index = len(self.current_animation) - 1
            else:
                self.frame_index = 0
                self.attacking = False
        
        self.image = self.current_animation[self.frame_index]
        
        for p in self.projectiles:
            p.update()
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.centerx - (img.get_width() // 2)
        draw_y = self.rect.bottom - img.get_height()
        surface.blit(img, (draw_x, draw_y))
        
        for p in self.projectiles:
            p.draw(surface)