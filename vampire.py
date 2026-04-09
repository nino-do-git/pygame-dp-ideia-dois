import pygame
import random
from fighter import Fighter
from projectile import Projectile


class Vampire(Fighter):
    def __init__(self, x, y, behavior="bully"):
        super().__init__(x, y, behavior=behavior)
        self.health = 50
        self.projectiles = []
        self.behavior = behavior
        self.aggro = True 

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
        super().update()

        for p in self.projectiles:
            p.update()
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface):
        super().draw(surface)
        
        for p in self.projectiles:
            p.draw(surface)