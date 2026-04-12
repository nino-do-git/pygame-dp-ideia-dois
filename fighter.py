import pygame
import random

class Fighter():
    def __init__(self, x, y, is_ai=False, behavior="passive", character=None):
        self.is_ai = is_ai
        self.flip = False
        self.character = character if character else ("et" if is_ai else "astronaut")
        self.rect = pygame.Rect((x, y, 40, 80))
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 100
        self.last_health = 100
        self.last_attack_time = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.load_assets()
        self.current_animation = self.idle
        self.image = self.current_animation[self.frame_index]
        self.ai_direction = 0
        self.last_ai_decision = 0
        self.behavior = behavior
        self.aggro = False if behavior == "passive" else True

    def load_assets(self):
        SCALE = 1.4
        if self.character == "astronaut":
            path = "assets/images/astronauta"
            self.idle = [self.load_img(f"{path}/idlefuturista.png", SCALE * 0.35)]
            self.walk = [self.load_img(f"{path}/walk{i}futurista.png", SCALE) for i in range(1, 4)]
            self.attack_anim = [self.load_img(f"{path}/attack{i}futurista.png", SCALE) for i in range(1, 4)]
            self.death = [self.load_img(f"{path}/die{i}futurista.png", SCALE) for i in range(1, 4)]
        elif self.character == "et":
            path = "assets/images/et"
            self.idle = [self.load_img(f"{path}/idlegnomo.png", SCALE * 0.756)]
            self.walk = [self.load_img(f"{path}/walk{i}ET.png", SCALE) for i in range(1, 4)]
            self.attack_anim = [self.load_img(f"{path}/attack{i}ET.png", SCALE) for i in range(1, 4)]
            self.death = [self.load_img(f"{path}/idlegnomo.png", SCALE * 0.756)]

    def load_img(self, path, scale):
        img = pygame.image.load(path).convert_alpha()
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        return pygame.transform.scale(img, (w, h))

    def apply_physics(self, dx, sw, sh):
        GRAVITY = 2
        self.vel_y += GRAVITY
        dy = self.vel_y
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > sw: dx = sw - self.rect.right
        if self.rect.bottom + dy > sh - 90:
            self.vel_y = 0
            self.jump = False
            dy = sh - 90 - self.rect.bottom
        self.rect.x += dx
        self.rect.y += dy
        self.update_animation_state(dx)

    def move(self, sw, sh, target):
        SPEED = 10
        dx = 0
        key = pygame.key.get_pressed()
        if not self.attacking and self.health > 0:
            if key[pygame.K_a]:
                dx = -SPEED
                self.flip = True
            if key[pygame.K_d]:
                dx = SPEED
                self.flip = False
            if key[pygame.K_w] and not self.jump:
                self.vel_y = -30
                self.jump = True
            if key[pygame.K_r]:
                self.attack(target)
        self.apply_physics(dx, sw, sh)

    def ai_logic(self, sw, sh, target):
        SPEED = 3
        dx = 0
        now = pygame.time.get_ticks()
        if self.behavior == "passive" and self.health < self.last_health:
            self.aggro = True
        self.last_health = self.health
        if self.health > 0:
            if self.behavior == "passive" and not self.aggro:
                if now - self.last_ai_decision > 1000:
                    self.last_ai_decision = now
                    self.ai_direction = random.choice([-SPEED, 0, SPEED])
                    if self.ai_direction < 0: self.flip = True
                    elif self.ai_direction > 0: self.flip = False
                dx = self.ai_direction
                if random.randint(1, 100) <= 2 and not self.jump:
                    self.vel_y = -30
                    self.jump = True
            elif self.behavior == "bully":
                if target.health > 20 or self.character == "astronaut":
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
                    if abs(self.rect.centerx - target.rect.centerx) < 150:
                        self.attack(target)
        self.apply_physics(dx, sw, sh)

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
            attack_img_width = self.attack_anim[0].get_width()
            if not self.flip:
                att_rect = pygame.Rect(self.rect.centerx, self.rect.y, attack_img_width // 2, self.rect.height)
            else:
                att_rect = pygame.Rect(self.rect.centerx - (attack_img_width // 2), self.rect.y, attack_img_width // 2, self.rect.height)
            if att_rect.colliderect(target.rect):
                damage = 10
                if self.is_ai and self.behavior == "bully" and self.character == "astronaut":
                    if self.health <= 20 or target.health <= 20:
                        damage = 100
                target.health -= damage

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

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.centerx - (img.get_width() // 2)
        draw_y = self.rect.bottom - img.get_height()
        surface.blit(img, (draw_x, draw_y))