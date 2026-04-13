import pygame
import random
from fighter import Fighter
from projectile import Projectile

class Vampire(Fighter):
    def __init__(self, x, y, behavior="bully"):
        super().__init__(x, y, behavior=behavior)
        self.max_health = 50
        self.health, self.projectiles = 50, []

    def load_assets(self):
        VS, VPS = 1.4 * 1.05, 1.4 * 0.7 
        self.idle = [self.load_img("assets/images/vampiro/idlevamp.png", VS)]
        self.walk = [self.load_img(f"assets/images/vampiro/walk{i}vamp.png", VS) for i in range(1, 4)]
        self.attack_anim = [self.load_img(f"assets/images/vampiro/attack{i}vamp.png", VS) for i in range(1, 3)]
        self.death = [self.load_img(f"assets/images/vampiro/die{i}vamp.png", VS) for i in range(1, 3)]
        self.eject_img = self.load_img("assets/images/vampiro/ejectvamp.png", VPS)

    def ai_logic(self, sw, sh, target):
        SPEED, dx, now = 3, 0, pygame.time.get_ticks()
        dist = abs(self.rect.centerx - target.rect.centerx)
        if self.health > 0:
            if now - self.last_ai_decision > 400:
                self.last_ai_decision, self.ai_direction = now, -SPEED if target.rect.centerx < self.rect.centerx else SPEED
                self.flip = target.rect.centerx < self.rect.centerx
            dx = self.ai_direction
            if random.randint(1, 100) <= 6 and not self.jump: self.vel_y, self.jump = -30, True
            if target.health > 20 and dist < 500: self.attack(target)
        self.apply_physics(dx, sw, sh)

    def attack(self, target):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > 800:
            self.attacking, self.last_attack_time = True, now
            proj_dir = -1 if self.flip else 1
            proj_x = self.rect.left - 20 if self.flip else self.rect.right
            proj = Projectile(proj_x, self.rect.centery - 20, proj_dir, self.eject_img, target)
            self.projectiles.append(proj)

    def update(self):
        super().update()
        for p in self.projectiles: p.update()
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface):
        super().draw(surface)
        for p in self.projectiles: p.draw(surface)