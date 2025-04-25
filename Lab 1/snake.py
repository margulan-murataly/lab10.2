import pygame
import random
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

DB_RESULTS     = "snake_scores"
DB_USER        = "postgres"
DB_PASSWORD    = ""
DB_HOST        = "localhost"
DB_PORT        = "5432"

admin_conn = psycopg2.connect(
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
admin_cur = admin_conn.cursor()
admin_cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_RESULTS,))
if not admin_cur.fetchone():
    admin_cur.execute(f"CREATE DATABASE {DB_RESULTS} ENCODING 'UTF8'")
    print(f"База данных '{DB_RESULTS}' создана.")
else:
    print(f"База данных '{DB_RESULTS}' уже существует.")
admin_cur.close()
admin_conn.close()

res_conn = psycopg2.connect(
    dbname=DB_RESULTS,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
res_cur = res_conn.cursor()

res_cur.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        score INTEGER NOT NULL,
        level INTEGER NOT NULL,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
res_conn.commit()

username = input("Enter your username: ").strip()

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Snake Game")

CELL_SIZE  = 20
SCORE_FONT = pygame.font.Font(None, 26)

walls = [
    (0, 360, CELL_SIZE * 10, CELL_SIZE),
    (400, 360, CELL_SIZE * 10, CELL_SIZE),
    (0, 0, CELL_SIZE * 10, CELL_SIZE),
    (400, 0, CELL_SIZE * 10, CELL_SIZE),
    (180, 380, CELL_SIZE, CELL_SIZE),
    (400, 380, CELL_SIZE, CELL_SIZE),
    (0, 20, CELL_SIZE, CELL_SIZE * 5),
    (580, 20, CELL_SIZE, CELL_SIZE * 5),
    (0, 260, CELL_SIZE, CELL_SIZE * 5),
    (580, 260, CELL_SIZE, CELL_SIZE * 5)
]
walls1 = [
    (100, 100, 140, 20),
    (100, 120, 20, 40),
    (360, 260, 140, 20),
    (480, 220, 20, 40)
]
walls2 = [
    (100, 260, 140, 20),
    (100, 220, 20, 40),
    (360, 100, 140, 20),
    (480, 120, 20, 40)
]

def draw_snake(snake):
    for seg in snake:
        pygame.draw.rect(screen, (0, 255, 0), (*seg, CELL_SIZE, CELL_SIZE))

def generate_food(snake, level):
    while True:
        out_walls = True
        while out_walls:
            food = (
                random.randint(1, 28) * CELL_SIZE,
                random.randint(1, 17) * CELL_SIZE
            )
            out_walls = False
            if level >= 2:
                for w in walls1:
                    if w[0] <= food[0] < w[0] + w[2] and w[1] <= food[1] < w[1] + w[3]:
                        out_walls = True
            if level >= 3:
                for w in walls2:
                    if w[0] <= food[0] < w[0] + w[2] and w[1] <= food[1] < w[1] + w[3]:
                        out_walls = True
        if food not in snake:
            return food, pygame.time.get_ticks()

clock      = pygame.time.Clock()
snake      = [(600 // 2, 400 // 2)]
direction  = (CELL_SIZE, 0)
running    = True
speed      = 10
game_over  = False
score      = 0
level      = 1
food, food_timer = generate_food(snake, level)

while running:
    screen.fill((0, 0, 0))
    now = pygame.time.get_ticks()

    if now - food_timer > 10000:
        food, food_timer = generate_food(snake, level)

    screen.blit(SCORE_FONT.render(f"Score: {score}", True, (255,255,255)), (0, 380))
    screen.blit(SCORE_FONT.render(f"Level: {level}", True, (255,255,255)), (420, 380))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w] and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif event.key in [pygame.K_DOWN, pygame.K_s] and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif event.key in [pygame.K_LEFT, pygame.K_a] and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif event.key in [pygame.K_RIGHT, pygame.K_d] and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)

    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    head = (head[0] % 600, head[1] % 400)

    if head in snake:
        game_over = True
    for w in walls + (walls1 if level>=2 else []) + (walls2 if level>=3 else []):
        if w[0] <= head[0] < w[0] + w[2] and w[1] <= head[1] < w[1] + w[3]:
            game_over = True

    if game_over:
        break

    snake.insert(0, head)
    if head == food:
        score += 1
        food, food_timer = generate_food(snake, level)
        if score % 10 == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    draw_snake(snake)
    pygame.draw.rect(screen, (255, 0, 0), (*food, CELL_SIZE, CELL_SIZE))
    for w in walls:
        pygame.draw.rect(screen, (255,255,255), w)
    if level >= 2:
        for w in walls1:
            pygame.draw.rect(screen, (255,255,255), w)
    if level >= 3:
        for w in walls2:
            pygame.draw.rect(screen, (255,255,255), w)

    pygame.display.flip()
    clock.tick(speed)

screen.blit(SCORE_FONT.render("GAME OVER", True, (125,0,0)), (245, 0))
pygame.display.flip()
pygame.time.delay(2000)
pygame.quit()

res_cur.execute(
    "INSERT INTO results (username, score, level, saved_at) VALUES (%s, %s, %s, %s)",
    (username, score, level, datetime.now())
)
res_conn.commit()
print(f"Game over. Score: {score}, Level: {level}. Saved to DB '{DB_RESULTS}'")

res_cur.close()
res_conn.close()