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
        try:
            img = pygame.image.load(path).convert_alpha()
        except:
            img = pygame.Surface((100, 100))
            img.fill((255, 0, 255))
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
            self.vel_y, self.jump, dy = 0, False, sh - 90 - self.rect.bottom
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
                if target.health > 20 or self.character == "astronaut":
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
            attack_img_width = self.attack_anim[0].get_width()
            if not self.flip: att_rect = pygame.Rect(self.rect.centerx, self.rect.y, attack_img_width // 2, self.rect.height)
            else: att_rect = pygame.Rect(self.rect.centerx - (attack_img_width // 2), self.rect.y, attack_img_width // 2, self.rect.height)
            if att_rect.colliderect(target.rect):
                damage = 100 if (self.is_ai and self.behavior == "bully" and self.character == "astronaut" and (self.health <= 20 or target.health <= 20)) else 10
                target.health -= damage

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

class BossGnomo(Fighter):
    def __init__(self, x, y):
        super().__init__(x, y, is_ai=True, behavior="bully")
        self.health, self.state = 100, 'mae'

    def load_assets(self):
        S, path = 1.6, "assets/images/gnomopaiem"
        alt_path = "assets/images/et"
        self.idle_mae = [self.load_img(f"{path}/idlegnomomae.png", S)]
        self.walk_mae = [self.load_img(f"{path}/walk1gnomomae.png", S), self.load_img(f"{path}/walk2gnomomae.png", S)]
        self.attack_mae = [self.load_img(f"{path}/attack1gnomomae.png", S), self.load_img(f"{path}/attack2gnomomae.png", S)]
        self.transform_anim = [self.load_img(f"{path}/tansform1gnomo.png", S), self.load_img(f"{path}/transform2gnomo.png", S), self.load_img(f"{path}/transform3gnomo.png", S)]
        self.idle_pai = [self.load_img(f"{path}/idlegnomopai.png", S)]
        self.walk_pai = [self.load_img(f"{path}/walk1gnomopai.png", S), self.load_img(f"{path}/walk2gnomopai.png", S)]
        self.attack_pai = [self.load_img(f"{path}/attack1gnomopai.png", S), self.load_img(f"{path}/attack2gnomopai.png", S)]
        self.death = self.idle_pai
        self.idle, self.walk, self.attack_anim = self.idle_mae, self.walk_mae, self.attack_mae

    def ai_logic(self, sw, sh, target):
        if self.health <= 0 or self.state == 'transforming': return
        if self.state == 'mae' and self.health <= 50:
            self.state, self.frame_index, self.current_animation = 'transforming', 0, self.transform_anim
            return
        speed, now = 5 if self.state == 'pai' else 3, pygame.time.get_ticks()
        if now - self.last_ai_decision > 400:
            self.last_ai_decision = now
            self.ai_direction, self.flip = -speed if target.rect.centerx < self.rect.centerx else speed, target.rect.centerx < self.rect.centerx
        dx = self.ai_direction
        if self.state == 'pai' and random.randint(1, 100) <= 5 and not self.jump: self.vel_y, self.jump = -30, True
        if abs(self.rect.centerx - target.rect.centerx) < 100: self.attack(target)
        self.apply_physics(dx, sw, sh)

    def update_animation_state(self, dx):
        if self.state == 'transforming': return
        if self.state == 'mae':
            if self.attacking: self.current_animation = self.attack_mae
            elif dx != 0: self.current_animation = self.walk_mae
            else: self.current_animation = self.idle_mae
        else:
            if self.attacking: self.current_animation = self.attack_pai
            elif dx != 0: self.current_animation = self.walk_pai
            else: self.current_animation = self.idle_pai

    def attack(self, target):
        now = pygame.time.get_ticks()
        cooldown = 400 if self.state == 'pai' else 800
        if now - self.last_attack_time > cooldown:
            self.attacking, self.last_attack_time = True, now
            if self.rect.inflate(80, 0).colliderect(target.rect):
                target.health -= 15 if self.state == 'pai' else 10

    def update(self):
        if pygame.time.get_ticks() - self.update_time > 150:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.current_animation):
            if self.state == 'transforming': self.state, self.frame_index = 'pai', 0
            else: self.frame_index, self.attacking = 0, False
        self.image = self.current_animation[self.frame_index]