import pygame
import random

class Fighter():
    def __init__(self, x, y, is_ai=False):
        self.is_ai = is_ai
        self.flip = False
        self.rect = pygame.Rect((x, y, 80, 130))
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 100
        self.last_attack_time = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        self.load_assets()
        self.current_animation = self.idle
        self.image = self.current_animation[self.frame_index]

        self.ai_direction = 0
        self.last_ai_decision = 0

    def load_assets(self):
        SCALE = 1.4
        IDLE_SCALE = SCALE * 0.35
        
        if not self.is_ai:
            path = "assets/images/astronauta"
            self.idle = [self.load_img(f"{path}/idlefuturista.png", IDLE_SCALE)]
            self.walk = [self.load_img(f"{path}/walk{i}futurista.png", SCALE) for i in range(1, 4)]
            self.attack_anim = [self.load_img(f"{path}/attack{i}futurista.png", SCALE) for i in range(1, 4)]
            self.death = [self.load_img(f"{path}/die{i}futurista.png", SCALE) for i in range(1, 4)]
        else:
            self.image_placeholder = pygame.Surface((80, 130))
            self.image_placeholder.fill((255, 0, 0))
            self.idle = self.walk = self.attack_anim = self.death = [self.image_placeholder]

    def load_img(self, path, scale):
        img = pygame.image.load(path).convert_alpha()
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        return pygame.transform.scale(img, (w, h))

    def move(self, screen_width, screen_height, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0

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

        self.vel_y += GRAVITY
        dy += self.vel_y

        self.apply_constraints(dx, dy, screen_width, screen_height)
        self.update_animation_state(dx)

    def ai_logic(self, screen_width, screen_height, target):
        SPEED = 3
        GRAVITY = 2
        dx = 0
        dy = 0
        dist = abs(self.rect.centerx - target.rect.centerx)
        now = pygame.time.get_ticks()

        if self.health > 0:
            if now - self.last_ai_decision > 600:
                self.last_ai_decision = now
                if target.rect.centerx < self.rect.centerx:
                    self.ai_direction = -SPEED
                    self.flip = True
                else:
                    self.ai_direction = SPEED
                    self.flip = False

            dx = self.ai_direction
            if random.randint(1, 100) <= 4 and not self.jump:
                self.vel_y = -30
                self.jump = True

            if dist < 150:
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
            att_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if att_rect.colliderect(target.rect):
                target.health -= 10

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
        if not self.is_ai:
            img = pygame.transform.flip(self.image, self.flip, False)
            draw_x = self.rect.centerx - (img.get_width() // 2)
            draw_y = self.rect.bottom - img.get_height()
            surface.blit(img, (draw_x, draw_y))
        else:
            pygame.draw.rect(surface, (255, 0, 0), self.rect)