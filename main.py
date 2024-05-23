import random
import pygame
import os
import csv
import datetime

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
ENTER_NAME_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 80)
LEADERBOARD_FONT = pygame.font.Font(os.path.join('assets', 'pixel_font.ttf'), 120)

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'hit_sound.mp3'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('assets', 'shoot_sound.mp3'))
GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('assets', 'game_over.mp3'))

SPACESHIP_IMAGE = pygame.image.load(os.path.join('assets', 'spaceship.png'))
BASE_LINE_IMAGE = pygame.image.load(os.path.join('assets', 'base_line.png'))
ENEMY_SHIP_IMAGE = pygame.image.load(os.path.join('assets', 'enemy_ship.png'))
EXPLOSION_IMAGE = pygame.image.load(os.path.join('assets', 'explosion.png'))

EXPLOSION = pygame.transform.scale(EXPLOSION_IMAGE, (150, 150))
SPACESHIP = pygame.transform.rotate(pygame.transform.scale(SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 180)
BASE_LINE = pygame.transform.scale(BASE_LINE_IMAGE, (WIDTH, 20))
ENEMY_SHIP = pygame.transform.scale(ENEMY_SHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
SPACE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space.png')), (WIDTH, HEIGHT))
SURFACE = pygame.Surface((WIDTH, HEIGHT))
SURFACE.set_alpha(128)

ENEMY_SHIP_HIT = pygame.USEREVENT + 1


# Making a new class as a modified version of the pygame.Rect class with addtional parameters
class EnemyShip(pygame.Rect):

    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        super().__init__(x, y, width, height)
        self.moving_right = True

    def handle_enemy_ship_movement(self):
        global ENEMY_SHIP_VEL

        if self.moving_right:
            self.x += ENEMY_SHIP_VEL
            if self.x + self.width >= WIDTH:
                self.moving_right = False
                self.y += ENEMY_SHIP_DOWN_VEL
        else:
            self.x -= ENEMY_SHIP_VEL
            if self.x <= 0:
                self.moving_right = True
                self.y += ENEMY_SHIP_DOWN_VEL

def draw_menu():
    WIN.blit(SPACE, (0, 0))
    play_text = PLAY_TEXT_FONT.render("PLAY", 1, BLACK)
    leaderboard_text = LEADERBOARD_FONT.render("LEADERBOARD", 1, BLACK)
    game_name_1 = GAME_OVER_FONT.render("ALIEN", 1, YELLOW)
    game_name_2 = GAME_OVER_FONT.render("ASSAULT", 1, YELLOW)

    play_base = pygame.Rect(WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2 - play_text.get_height() // 2, play_text.get_width() + 15,
                         play_text.get_height() - 10)
    leaderboard_base = pygame.Rect(WIDTH // 2 - leaderboard_text.get_width() // 2, HEIGHT // 2 + play_text.get_height(), leaderboard_text.get_width() + 15,
                         leaderboard_text.get_height() - 10)
    pygame.draw.rect(WIN, YELLOW, play_base)
    pygame.draw.rect(WIN, YELLOW, leaderboard_base)
    
    WIN.blit(game_name_1, (WIDTH // 2 - game_name_1.get_width() // 2 + 15, 50))
    WIN.blit(game_name_2, (WIDTH // 2 - game_name_2.get_width() // 2 + 15, 200))
    WIN.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2 + 15, HEIGHT // 2 - play_text.get_height() // 2))
    WIN.blit(leaderboard_text, (WIDTH // 2 - leaderboard_text.get_width() // 2 + 15, HEIGHT // 2 + play_text.get_height()))
    pygame.display.update()

def draw_window(spaceship, base_line, bullet_list, enemy_ship_list, score):
    score_text = SCORE_FONT.render(f"Score: {str(score)}", 1, YELLOW)
    WIN.blit(SPACE, (0, 0))
    WIN.blit(SPACESHIP, (spaceship.x, spaceship.y))
    WIN.blit(BASE_LINE, (base_line.x, base_line.y))
    WIN.blit(score_text, (10, 10))
    
    for bullet in bullet_list: 
        pygame.draw.rect(WIN, YELLOW, bullet)
    
    for enemy_ship in enemy_ship_list:
        WIN.blit(ENEMY_SHIP, (enemy_ship.x, enemy_ship.y))
        for bullet in bullet_list:
            if enemy_ship.colliderect(bullet):
                pygame.event.post(pygame.event.Event(ENEMY_SHIP_HIT))
                BULLET_HIT_SOUND.play()
                WIN.blit(EXPLOSION, (enemy_ship.x - 30, enemy_ship.y - 30))
                enemy_ship_list.remove(enemy_ship)
                bullet_list.remove(bullet)
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
    pygame.display.update()


def save_score(entered_name, score):
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    with open('scores.csv', 'a+') as scores:
        csv_writer = csv.writer(scores)
        csv_writer.writerow([entered_name, str(score), current_date])

def enter_name(score):
    entered_name = ""
    name_entered = False

    name_entry_area = WIN.subsurface(pygame.Rect(500, 550, WIDTH - 500, 100)).copy()

    enter_name_text = ENTER_NAME_FONT.render("ENTER NAME:", 1, YELLOW)
    WIN.blit(enter_name_text, (50, 550))
    pygame.display.update()

    while not name_entered:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name_entered = True
                elif event.key == pygame.K_BACKSPACE:
                    entered_name = entered_name[:-1]
                else:
                    entered_name += event.unicode

                WIN.blit(name_entry_area, (500, 550))
                WIN.blit(enter_name_text, (50, 550))

                name_surface = ENTER_NAME_FONT.render(entered_name, 1, YELLOW)
                WIN.blit(name_surface, (500, 550))
                pygame.display.update()

    return entered_name


def load_scores():
    # Scores will be a list containing (name, score, date) tuples
    scores = []
    try:
        with open('scores.csv', 'r') as scores_file:
            csv_reader = csv.reader(scores_file)
            for row in csv_reader:
                if len(row) == 3: 
                    scores.append((row[0], int(row[1]), row[2]))
    # If the scores.csv file doesn't exsist
    except FileNotFoundError:
        pass
    
    # We sort through the scores list, where the key to sort is x[1], which is the 'score' in the (name, score date) tuple
    # Here lambda is a small function that gets us the above mentioned 'score'
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores[:10] #Saving only the top 10 scores

def draw_leaderboard():
    scores = load_scores()
    WIN.blit(SPACE, (0, 0))

    transparent_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    transparent_surface.fill((0, 0, 0, 128))  # Black transparent layer with some opacity
    WIN.blit(transparent_surface, (0, 0))

    # Title
    title_text = LEADERBOARD_FONT.render("LEADERBOARD", 1, YELLOW)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    # Headings
    name_heading = SCORE_FONT.render("NAME", 1, WHITE)
    score_heading = SCORE_FONT.render("SCORE", 1, WHITE)
    date_heading = SCORE_FONT.render("DATE", 1, WHITE)

    WIN.blit(name_heading, (50, 200))
    WIN.blit(score_heading, (300, 200))
    WIN.blit(date_heading, (500, 200))

    # Display the scores
    for i, (name, score, date) in enumerate(scores): # enumarate is for holding the index postion of each tuple,
                                                     #this is to print the postion of the player in the leaderboard
        
        # Initialising the variables to print and giving them their respective values, that are present in (name, score, date) tuple
        name_text = SCORE_FONT.render(f"{i+1}. {name}", 1, WHITE)
        score_text = SCORE_FONT.render(f"{score}", 1, WHITE)
        date_text = SCORE_FONT.render(f"{date}", 1, WHITE)
        
        WIN.blit(name_text, (50, 250 + i * 50))
        WIN.blit(score_text, (300, 250 + i * 50))
        WIN.blit(date_text, (500, 250 + i * 50))

    pygame.display.update()

    # Wait for the user to press 'escape' key to return to the main menu
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
                

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
    leaderboard_clicked = False

    while run:
        clock.tick(FPS)

        if not play_clicked and not leaderboard_clicked:
            draw_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    play_text = PLAY_TEXT_FONT.render("PLAY", 1, WHITE)
                    leaderboard_text = PLAY_TEXT_FONT.render("LEADERBOARD", 1, WHITE)
                    if (WIDTH // 2 - play_text.get_width() // 2 <= mouse_x <= WIDTH // 2 + play_text.get_width() // 2 and
                        HEIGHT // 2 - play_text.get_height() // 2 <= mouse_y <= HEIGHT // 2 + play_text.get_height() // 2):
                        play_clicked = True
                        break
                    elif (WIDTH // 2 - leaderboard_text.get_width() // 2 <= mouse_x <= WIDTH // 2 + leaderboard_text.get_width() // 2 and
                        HEIGHT // 2 + play_text.get_height() <= mouse_y <= HEIGHT // 2 + play_text.get_height() + leaderboard_text.get_height()):
                        leaderboard_clicked = True
                        break
        elif leaderboard_clicked:
            draw_leaderboard()
            leaderboard_clicked = False  # Reset to allow re-entering the leaderboard menu
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
                    entered_name = enter_name(score)
                    save_score(entered_name, score)
                    run = False
                else:
                    enemy_ship.handle_enemy_ship_movement()

    main()

if __name__ == '__main__':
    main()
