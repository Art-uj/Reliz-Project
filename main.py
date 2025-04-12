
import pygame
import random

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Механічний сутінок")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 0)

font = pygame.font.Font(None, 36)


pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)

jump_sound = pygame.mixer.Sound("jump.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
collect_sound = pygame.mixer.Sound("collect.wav")


player_size = (40, 60)
player_speed = 5
jump_power = -15
gravity = 0.5
player_lives = 3
level_count = 0


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(player_size)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-100))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = player_lives
        self.resources = 0

    def update(self):
        self.vel_y += gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = jump_power
            self.on_ground = False
            jump_sound.play()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))
    
    


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left < 50 or self.rect.right > WIDTH - 50:
            self.direction *= -1


class Resource(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
    def update(self):
            pass

    

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.hp = 7
        self.speed = 2
        self.direction = 1
        self.attack_timer = 0  

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left < 50 or self.rect.right > WIDTH - 50:
            self.direction *= -1

        self.attack_timer += 1
        if self.attack_timer > 120:
            self.attack()
            self.attack_timer = 0

    def attack(self):
        if self.rect.colliderect(player.rect):
            player.lives -= 1
            hit_sound.play()
            print(f"Бос атакує! HP гравця: {player.lives}")


def generate_level():
    global level_count
    level_count += 1

    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    resources = pygame.sprite.Group()

    ground = Platform(0, HEIGHT - 20, WIDTH, 20)
    platforms.add(ground)

    for _ in range(6):
        x = random.randint(50, WIDTH - 150)
        y = random.randint(150, HEIGHT - 100)
        platform = Platform(x, y, 100, 10)
        platforms.add(platform)

        if random.random() > 0.6:
            enemy = Enemy(x, y - 40)
            enemies.add(enemy)

        if random.random() > 0.5:
            resource = Resource(x + 50, y - 10)
            resources.add(resource)

    return platforms, enemies, resources

def next_level():
    global platforms, enemies, resources, boss, level_count

    level_count += 1  
    all_sprites.empty()

    if level_count % 3 == 0:  
        boss = Boss()
        enemies = pygame.sprite.Group(boss)
        resources = pygame.sprite.Group()
    else:
        platforms, enemies, resources = generate_level()
        boss = None

    all_sprites.add(player, platforms, enemies, resources)  
    player.rect.midbottom = (WIDTH//2, HEIGHT-100)
    player.resources = 0




clock = pygame.time.Clock()
player = Player()
platforms, enemies, resources = generate_level()
boss = None
all_sprites = pygame.sprite.Group(player, platforms, enemies, resources)

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.vel_x = 0
    if keys[pygame.K_a]:
        player.vel_x = -player_speed
    if keys[pygame.K_d]:
        player.vel_x = player_speed
    if keys[pygame.K_SPACE]:
        player.jump()

    player.update()
    enemies.update()
    if boss:
        boss.update()

    if keys[pygame.K_SPACE] and boss:
        boss.hp -= 1
        print(f"Бос отримав удар! HP боса: {boss.hp}")
        if boss.hp <= 0:
            print("Бос переможений!")
            next_level()

    collected_resources = pygame.sprite.spritecollide(player, resources, True)
    if collected_resources:
        collect_sound.play()
    player.resources += len(collected_resources)

    if len(resources) == 0 and boss is None:
        next_level()

    all_sprites.draw(screen)

    hp_text = font.render(f"HP: {player.lives}", True, WHITE)
    res_text = font.render(f"Ресурси: {player.resources}", True, WHITE)
    screen.blit(hp_text, (10, 10))
    screen.blit(res_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
