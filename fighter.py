import pygame

def load_images(paths):
    images = []
    for path in paths:
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (120, 120))
            images.append(img)
        except (FileNotFoundError, pygame.error):
            img = pygame.Surface((120, 120), pygame.SRCALPHA)
            img.fill((255, 0, 0, 255))
            images.append(img)
    return images


class Fighter():
    def __init__(self, x, y):
        self.flip = False
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 100

        self.idle = load_images([
            "assets/images/astronauta/idlefuturista.png"
        ])
        self.walk = load_images([
            "assets/images/astronauta/walk1futurista.png",
            "assets/images/astronauta/walk2futurista.png",
            "assets/images/astronauta/walk3futurista.png"
        ])
        self.attack_anim = load_images([
            "assets/images/astronauta/attack1futurista.png",
            "assets/images/astronauta/attack2futurista.png",
            "assets/images/astronauta/attack3futurista.png"
        ])
        self.death = load_images([
            "assets/images/astronauta/die1futurista.png",
            "assets/images/astronauta/die2futurista.png",
            "assets/images/astronauta/die3futurista.png"
        ])

        self.current_animation = self.idle
        self.frame_index = 0
        self.image = self.current_animation[self.frame_index]
        self.update_time = pygame.time.get_ticks()

    def move(self, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()
        if not self.attacking:
            if key[pygame.K_a]:
                dx = -SPEED
            if key[pygame.K_d]:
                dx = SPEED
            if key[pygame.K_w] and not self.jump:
                self.vel_y = -30
                self.jump = True
            if key[pygame.K_r]:
                self.attack(surface, target)

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

    def attack(self, surface, target):
        self.attacking = True
        attacking_rect = pygame.Rect(
            self.rect.centerx - (2 * self.rect.width * self.flip),
            self.rect.y,
            2 * self.rect.width,
            self.rect.height
        )
        if attacking_rect.colliderect(target.rect):
            target.health -= 10
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
        surface.blit(img, (self.rect.x - 20, self.rect.y - 40))
