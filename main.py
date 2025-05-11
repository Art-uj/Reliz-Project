import pygame
import random

pygame.init()

# Розміри екрану
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Механічний сутінок")

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 0)

# Шрифт
font = pygame.font.Font(None, 36)

# Музика та звуки
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)

jump_sound = pygame.mixer.Sound("jump.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
collect_sound = pygame.mixer.Sound("collect.wav")
backgroung = pygame.image.load("background.jpg")

# Параметри гравця
player_size = (40, 60)
player_speed = 5
jump_power = -15
gravity = 0.4
player_lives = 5
level_count = 0

# Клас гравця
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
        self.last_hit_time = 0
        self.invincible_duration = 2000

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

# Платформа
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))

# Ворог
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

# Ресурс
class Resource(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))

# Бос
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.hp = 70
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

# Генерація рівня
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

# Перехід на наступний рівень
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

# Показати меню перед грою
def show_menu():
    start_time = pygame.time.get_ticks()
    menu_duration = 15000  # 15 секунд
    waiting = True

    while waiting:
        screen.fill(BLACK)

        title = font.render("Механічний сутінок", True, WHITE)
        control1 = font.render("A / D - рух вліво / вправо", True, WHITE)
        control2 = font.render("SPACE - стрибок", True, WHITE)
        control3 = font.render("C - атакувати боса", True, WHITE)
        control4 = font.render("R - перезапуск гри", True, WHITE)

        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, (menu_duration - elapsed_time) // 1000)
        timer_text = font.render(f"Гра почнеться через: {remaining_time} с", True, YELLOW)

        tip = font.render("Натисни будь-яку клавішу для старту!", True, GRAY)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(control1, (WIDTH // 2 - control1.get_width() // 2, 200))
        screen.blit(control2, (WIDTH // 2 - control2.get_width() // 2, 250))
        screen.blit(control3, (WIDTH // 2 - control3.get_width() // 2, 300))
        screen.blit(control4, (WIDTH // 2 - control4.get_width() // 2, 350))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 420))
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, 470))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

        if elapsed_time > menu_duration:
            waiting = False

        clock.tick(60)

# Головний код
clock = pygame.time.Clock()
player = Player()
platforms, enemies, resources = generate_level()
boss = None
all_sprites = pygame.sprite.Group(player, platforms, enemies, resources)

show_menu()

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks()
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            if current_time - player.last_hit_time > player.invincible_duration:
                player.lives -= 1
                if player.lives <= 0:
                    print("Гру завершено!")
                    running = False
                player.last_hit_time = current_time
                hit_sound.play()
                print(f"Гравець отримав удар! HP: {player.lives}")

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

    if keys[pygame.K_c] and boss:
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

    if keys[pygame.K_r]:
        player = Player()
        platforms, enemies, resources = generate_level()
        boss = None
        all_sprites = pygame.sprite.Group(player, platforms, enemies, resources)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
