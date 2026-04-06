import pygame
import random

class Fighter():
    def __init__(self, x, y, is_ai=False):
        self.flip = False
        self.rect = pygame.Rect((x, y, 80, 130))
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 100
        self.last_attack_time = 0
        self.is_ai = is_ai
        self.counter_attack = 0

        base_path = "assets/images/astronauta"
        image_size = (80, 130)
        self.idle = [pygame.transform.scale(pygame.image.load(f"{base_path}/idlefuturista.png").convert_alpha(), image_size)]
        self.walk = [pygame.transform.scale(pygame.image.load(f"{base_path}/walk1futurista.png").convert_alpha(), image_size),
                     pygame.transform.scale(pygame.image.load(f"{base_path}/walk2futurista.png").convert_alpha(), image_size),
                     pygame.transform.scale(pygame.image.load(f"{base_path}/walk3futurista.png").convert_alpha(), image_size)]
        self.attack_anim = [pygame.image.load(f"{base_path}/attack1futurista.png").convert_alpha(),
                            pygame.image.load(f"{base_path}/attack2futurista.png").convert_alpha(),
                            pygame.image.load(f"{base_path}/attack3futurista.png").convert_alpha()]
        self.death = [pygame.transform.scale(pygame.image.load(f"{base_path}/die1futurista.png").convert_alpha(), image_size),
                      pygame.transform.scale(pygame.image.load(f"{base_path}/die2futurista.png").convert_alpha(), image_size),
                      pygame.transform.scale(pygame.image.load(f"{base_path}/die3futurista.png").convert_alpha(), image_size)]

        self.ai_direction = 0
        self.last_ai_decision = 0
        self.ai_retreat = False
        self.current_animation = self.idle
        self.frame_index = 0
        self.image = self.current_animation[self.frame_index]
        self.update_time = pygame.time.get_ticks()

    def move(self, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2
        ATTACK_COOLDOWN = 800
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if key[pygame.K_a]:
            dx = -SPEED
        if key[pygame.K_d]:
            dx = SPEED

        if key[pygame.K_w] and not self.jump:
            self.vel_y = -30
            self.jump = True

        if key[pygame.K_r] and current_time - self.last_attack_time > ATTACK_COOLDOWN:
            self.attack(surface, target)
            self.last_attack_time = current_time

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False

        self.rect.x += dx
        self.rect.y += dy

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

        if self.frame_index >= len(self.current_animation):
            self.frame_index = 0

    def ai_move(self, screen_width, screen_height, surface, target):
        SPEED = 3
        GRAVITY = 2
        ATTACK_COOLDOWN = 4000
        DECISION_COOLDOWN = 600
        dx = 0
        dy = 0

        distance = abs(self.rect.centerx - target.rect.centerx)
        current_time = pygame.time.get_ticks()

        if current_time - self.last_ai_decision > DECISION_COOLDOWN:
            self.last_ai_decision = current_time

            if self.ai_retreat:
                if distance > 120:
                    self.ai_retreat = False
                    self.ai_direction = 0
                else:
                    if target.rect.centerx < self.rect.centerx:
                        self.ai_direction = SPEED
                    else:
                        self.ai_direction = -SPEED
            else:
                if distance < 80:
                    self.ai_retreat = True
                    if target.rect.centerx < self.rect.centerx:
                        self.ai_direction = SPEED
                    else:
                        self.ai_direction = -SPEED
                elif distance < 120:
                    if random.randint(1, 100) <= 50:
                        if target.rect.centerx < self.rect.centerx:
                            self.ai_direction = -SPEED
                        else:
                            self.ai_direction = SPEED
                    else:
                        self.ai_direction = 0
                else:
                    if random.randint(1, 100) <= 75:
                        self.ai_direction = 0
                    else:
                        self.ai_direction = random.choice([-2, 2])

        dx = self.ai_direction

        if random.randint(1, 100) <= 4 and not self.jump:
            self.vel_y = -30
            self.jump = True

        if self.counter_attack > 0 and distance < 100 and current_time - self.last_attack_time > ATTACK_COOLDOWN:
            self.attack(surface, target)
            self.last_attack_time = current_time
            self.counter_attack -= 1
        elif not self.ai_retreat and self.counter_attack == 0 and distance < 50 and current_time - self.last_attack_time > ATTACK_COOLDOWN and random.randint(1, 100) <= 12:
            self.attack(surface, target)
            self.last_attack_time = current_time

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = 0
        if self.rect.right + dx > screen_width:
            dx = 0

        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False

        self.rect.x += dx
        self.rect.y += dy

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

        if self.frame_index >= len(self.current_animation):
            self.frame_index = 0

    def attack(self, surface, target):
        attacking_rect = pygame.Rect(
            self.rect.centerx - (2 * self.rect.width * self.flip),
            self.rect.y,
            2 * self.rect.width,
            self.rect.height
        )
        if attacking_rect.colliderect(target.rect):
            target.health -= 10
            if not self.is_ai and getattr(target, 'is_ai', False):
                target.counter_attack = 3

        if self.current_animation != self.attack_anim:
            self.current_animation = self.attack_anim
            self.frame_index = 0
            self.attacking = True

        pygame.draw.rect(surface, (0, 255, 0), attacking_rect)

    def update(self):
        ANIMATION_COOLDOWN = 120

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

            if self.frame_index >= len(self.current_animation):
                self.frame_index = 0
                self.attacking = False

        if not self.current_animation:
            return

        if self.frame_index >= len(self.current_animation):
            self.frame_index = 0

        self.image = self.current_animation[self.frame_index]

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.centerx - img.get_width() // 2
        draw_y = self.rect.bottom - img.get_height()
        surface.blit(img, (draw_x, draw_y))
