import random
import pygame
import os

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 950
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ALIEN ASSAULT")

VEL = 10
FPS = 60
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 100, 60
BULLET_VEL = 5
MAX_BULLETS = 3
ENEMY_SHIP_VEL = 5
ENEMY_SHIP_DOWN_VEL = 60
ENEMY_SHIPS_NUM = 10

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0,0,0)

SCORE_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 40)
GAME_OVER_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 160)
FINAL_SCORE_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 125)
GAME_NAME_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 150)
PLAY_TEXT_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 140)

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'hit_sound.mp3'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'shoot_sound.mp3'))
GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('assets', 'game_over.mp3'))

SPACESHIP_IMAGE = pygame.image.load(os.path.join('assets', 'spaceship.png'))
BASE_LINE_IMAGE = pygame.image.load(os.path.join('assets', 'base_line.png'))
ENEMY_SHIP_IMAGE = pygame.image.load(os.path.join('assets', 'enemy_ship.png'))
EXPL_IMAGE = pygame.image.load(os.path.join('assets', 'explosion.png'))

EXPL = pygame.transform.scale(EXPL_IMAGE, (150, 150))
SPACESHIP = pygame.transform.rotate(pygame.transform.scale(SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 180)
BASE_LINE = pygame.transform.scale(BASE_LINE_IMAGE, (WIDTH, 20))
ENEMY_SHIP = pygame.transform.scale(ENEMY_SHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
SPACE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space.png')), (WIDTH, HEIGHT))
SURFACE = pygame.Surface((WIDTH, HEIGHT))
SURFACE.set_alpha(128)

ENEMY_SHIP_HIT = pygame.USEREVENT + 1

class EnemyShip(pygame.Rect):

    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        super().__init__(x, y, width, height)
        self.moving_right = True  # Track the enemy's movement direction

    def handle_enemy_ship_movement(self):
        global ENEMY_SHIP_VEL

        if self.moving_right:
            self.x += ENEMY_SHIP_VEL
            if self.x + self.width >= WIDTH:
                self.moving_right = False
                self.y += ENEMY_SHIP_DOWN_VEL  # Move down when reaching edge
        else:
            self.x -= ENEMY_SHIP_VEL
            if self.x <= 0:
                self.moving_right = True
                self.y += ENEMY_SHIP_DOWN_VEL  # Move down when reaching edge


def draw_window(spaceship, base_line, bullet_list, enemy_ship_list, score):
    score_text = SCORE_FONT.render(f"Score: {str(score)}", 1, YELLOW)
    WIN.blit(SPACE, (0, 0))
    WIN.blit(SPACESHIP, (spaceship.x, spaceship.y))
    WIN.blit(BASE_LINE, (base_line.x, base_line.y))
    WIN.blit(score_text, (10, 10))
    for enemy_ship in enemy_ship_list:
        WIN.blit(ENEMY_SHIP, (enemy_ship.x, enemy_ship.y))
        for bullet in bullet_list:
            if enemy_ship.colliderect(bullet):
                pygame.event.post(pygame.event.Event(ENEMY_SHIP_HIT))
                BULLET_HIT_SOUND.play()
                WIN.blit(EXPL, (enemy_ship.x - 30, enemy_ship.y - 30))
                enemy_ship_list.remove(enemy_ship)
                bullet_list.remove(bullet)

    for bullet in bullet_list:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()


def handle_movement(spaceship, keys_pressed):
    if keys_pressed[pygame.K_a] and spaceship.x - VEL > 0:
        spaceship.x -= VEL
    if keys_pressed[pygame.K_d] and (spaceship.x + spaceship.width + VEL) < WIDTH:
        spaceship.x += VEL


def handle_bullet_movement(bullet_list):
    for bullet in bullet_list:
        bullet.y -= BULLET_VEL
        if bullet.y - bullet.height < 0:
            bullet_list.remove(bullet)


def game_over(score):
    GAME_OVER_SOUND.play()
    game_over_text = GAME_OVER_FONT.render('GAME OVER', 1, YELLOW)
    score_text = FINAL_SCORE_FONT.render(f"SCORE: {str(score)}", 1, YELLOW)
    WIN.blit(SURFACE, (0, 0))
    WIN.blit(game_over_text,(WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2 - 200))
    WIN.blit(score_text, (WIDTH // 2 - game_over_text.get_width() // 2 + 150, HEIGHT // 2 - 100))
    pygame.display.flip()
    pygame.time.delay(3000)

def draw_menu():
    WIN.blit(SPACE, (0,0))  # Fill screen with black color for the menu
    play_text = PLAY_TEXT_FONT.render("PLAY", 1 , BLACK)
    game_name_1 = GAME_OVER_FONT.render("ALIEN", 1, YELLOW)
    game_name_2 = GAME_OVER_FONT.render("ASSAULT", 1, YELLOW)

    base = pygame.Rect(WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2 - play_text.get_height() // 2, play_text.get_width() +15,
                         play_text.get_height() - 10 )
    pygame.draw.rect(WIN, YELLOW, base)
    WIN.blit(game_name_1, (WIDTH // 2 - game_name_1.get_width() // 2 + 15, 50))
    WIN.blit(game_name_2, (WIDTH // 2 - game_name_2.get_width() // 2 + 15, 200))
    WIN.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2 + 15, HEIGHT // 2 - play_text.get_height() // 2))
    pygame.display.update()

def main():

    score = 0
    bullet_list = []
    enemy_ship_list = []
    spaceship = pygame.Rect(300, 850, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    bullet = pygame.Rect(spaceship.x + spaceship.width // 2 - 3, spaceship.y, 5, 10)
    base_line = pygame.Rect(0, 750, WIDTH, 5)

    for i in range(ENEMY_SHIPS_NUM):
        enemy_ship = EnemyShip(random.randint(0, WIDTH), random.randrange(0, 600, 5), SPACESHIP_WIDTH,
                               SPACESHIP_HEIGHT)
        enemy_ship_list.append(enemy_ship)

    clock = pygame.time.Clock()
    run = True
    play_clicked = False

    while run:
        clock.tick(FPS)

        if not play_clicked:
            draw_menu()

            # Check for events in the menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    play_text = PLAY_TEXT_FONT.render("PLAY", 1 , WHITE)
                    if (WIDTH // 2 - play_text.get_width() // 2 <= mouse_x <= WIDTH // 2 + play_text.get_width() // 2 \
                            and HEIGHT // 2 - play_text.get_height() // 2 <= mouse_y <= HEIGHT // 2 + play_text.get_height() // 2):
                        play_clicked = True
                        break
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and len(bullet_list) < MAX_BULLETS:
                        BULLET_FIRE_SOUND.play()
                        bullet = pygame.Rect(spaceship.x + spaceship.width // 2 - 3, spaceship.y, 5, 10)
                        bullet_list.append(bullet)

                if event.type == ENEMY_SHIP_HIT:
                    score += 1

            draw_window(spaceship, base_line, bullet_list, enemy_ship_list, score)
            keys_pressed = pygame.key.get_pressed()
            handle_bullet_movement(bullet_list)
            handle_movement(spaceship, keys_pressed)

            if len(enemy_ship_list) < ENEMY_SHIPS_NUM:
                enemy_ship = EnemyShip(random.randint(0, WIDTH), random.randrange(0, 600, 5), SPACESHIP_WIDTH,
                                       SPACESHIP_HEIGHT)
                enemy_ship_list.append(enemy_ship)

            for enemy_ship in enemy_ship_list:
                if enemy_ship.colliderect(base_line):
                    enemy_ship_list.remove(enemy_ship)
                    ship_x, ship_y = enemy_ship.x, enemy_ship.y
                    WIN.blit(ENEMY_SHIP, (ship_x, ship_y))
                    pygame.display.update()
                    game_over(score)
                    run = False
            for enemy_ship in enemy_ship_list:
                enemy_ship.handle_enemy_ship_movement()

    main()


if __name__ == '__main__':
    main()
