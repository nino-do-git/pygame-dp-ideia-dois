import pygame
import random
from fighter import Fighter

class BossGnomo(Fighter):
    def __init__(self, x, y):
        super().__init__(x, y, is_ai=True, behavior="bully")
        self.max_health = 100
        self.health = 100
        self.phase = 1

    def load_assets(self):
        S_MAE = 1.0
        self.idle_mae = [self.load_img("idlegnomomae.png", S_MAE)]
        self.walk_mae = [self.load_img("walk1gnomomae.png", S_MAE), self.load_img("walk2gnomomae.png", S_MAE)]
        self.attack_mae = [self.load_img("attack1gnomomae.png", S_MAE), self.load_img("attack2gnomomae.png", S_MAE)]

        S_PAI = 0.8
        self.idle_pai = [self.load_img("idlegnomopai.png", S_PAI)]
        self.walk_pai = [self.load_img("walk1gnomopai.png", S_PAI), self.load_img("walk2gnomopai.png", S_PAI)]
        self.attack_pai = [self.load_img("attack1gnomopai.png", S_PAI), self.load_img("attack2gnomopai.png", S_PAI)]

        self.death = [self.load_img("die1gnomopai.png", S_PAI), self.load_img("die2gnomopai.png", S_PAI)]

        self.idle = self.idle_mae
        self.walk = self.walk_mae
        self.attack_anim = self.attack_mae

    def ai_logic(self, sw, sh, target):
        dx = 0
        if self.health > 0:
            if self.health <= self.max_health / 2 and self.phase == 1:
                self.phase = 2
                self.idle = self.idle_pai
                self.walk = self.walk_pai
                self.attack_anim = self.attack_pai
                
            SPEED, now = 4, pygame.time.get_ticks()
            if now - self.last_ai_decision > 400:
                self.last_ai_decision = now
                self.ai_direction, self.flip = -SPEED if target.rect.centerx < self.rect.centerx else SPEED, target.rect.centerx < self.rect.centerx
            dx = self.ai_direction
            if random.randint(1, 100) <= 5 and not self.jump: self.vel_y, self.jump = -30, True
            if abs(self.rect.centerx - target.rect.centerx) < 120: self.attack(target)
            
        self.apply_physics(dx, sw, sh)

    def update_animation_state(self, dx):
        if self.health <= 0:
            if self.current_animation != self.death: self.current_animation, self.frame_index = self.death, 0
        elif self.attacking: self.current_animation = self.attack_anim
        elif dx != 0: self.current_animation = self.walk
        else: self.current_animation = self.idle

    def update(self):
        if pygame.time.get_ticks() - self.update_time > 150:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.current_animation):
            if self.health <= 0: self.frame_index = len(self.current_animation) - 1
            else: self.frame_index, self.attacking = 0, False
        self.image = self.current_animation[self.frame_index]