import pygame

class Projectile():
    def __init__(self, x, y, direction, image, target):
        self.image = image
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.direction = direction
        self.speed = 15
        self.active = True
        self.target = target

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.colliderect(self.target.rect):
            self.target.health -= 15
            self.active = False
        if self.rect.x < -200 or self.rect.x > 1200:
            self.active = False

    def draw(self, surface):
        img = self.image
        if self.direction < 0:
            img = pygame.transform.flip(self.image, True, False)
        surface.blit(img, (self.rect.x, self.rect.y))
