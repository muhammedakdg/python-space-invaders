
import tkinter as tk
import random

# -----------------------------
# GAME SETTINGS
# -----------------------------

WIDTH = 800
HEIGHT = 600

PLAYER_SPEED = 7
BULLET_SPEED = 12
ENEMY_BULLET_SPEED = 5

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 25

STARTING_LIVES = 3

# -----------------------------
# GAME WINDOW
# -----------------------------

window = tk.Tk()
window.title("Space Invaders - Python")
window.resizable(False, False)

canvas = tk.Canvas(
    window,
    width=WIDTH,
    height=HEIGHT,
    bg="#080B18",
    highlightthickness=0
)
canvas.pack()

# -----------------------------
# GAME VARIABLES
# -----------------------------

player = None

enemies = []
bullets = []
enemy_bullets = []

keys_pressed = set()

score = 0
lives = STARTING_LIVES
level = 1

enemy_direction = 1
enemy_speed = 1.5

game_running = False
game_over = False

shoot_cooldown = 0
enemy_shoot_timer = 0

# -----------------------------
# PLAYER
# -----------------------------

def create_player():
    global player

    x = WIDTH // 2
    y = HEIGHT - 65

    player = canvas.create_polygon(
        x, y - 25,
        x - 25, y + 20,
        x + 25, y + 20,
        fill="#39FF14",
        outline="white",
        width=2,
        tags="player"
    )


def move_player():
    if player is None:
        return

    x1, y1, x2, y2 = canvas.bbox(player)

    dx = 0

    if "Left" in keys_pressed or "a" in keys_pressed:
        dx -= PLAYER_SPEED

    if "Right" in keys_pressed or "d" in keys_pressed:
        dx += PLAYER_SPEED

    if x1 + dx < 0:
        dx = -x1

    if x2 + dx > WIDTH:
        dx = WIDTH - x2

    canvas.move(player, dx, 0)


# -----------------------------
# SHOOTING
# -----------------------------

def shoot():
    global shoot_cooldown

    if not game_running:
        return

    if shoot_cooldown > 0:
        return

    x1, y1, x2, y2 = canvas.bbox(player)

    center_x = (x1 + x2) / 2

    bullet = canvas.create_rectangle(
        center_x - 3,
        y1 - 15,
        center_x + 3,
        y1,
        fill="#00E5FF",
        outline=""
    )

    bullets.append(bullet)

    shoot_cooldown = 12


def move_bullets():
    for bullet in bullets[:]:

        canvas.move(bullet, 0, -BULLET_SPEED)

        coords = canvas.coords(bullet)

        if not coords or coords[3] < 0:
            remove_bullet(bullet)


def remove_bullet(bullet):
    if bullet in bullets:
        bullets.remove(bullet)

    canvas.delete(bullet)


# -----------------------------
# ENEMIES
# -----------------------------

def create_enemy(x, y, color):
    enemy = canvas.create_rectangle(
        x,
        y,
        x + 40,
        y + 30,
        fill=color,
        outline="white",
        width=2
    )

    # Add eyes to the enemy
    left_eye = canvas.create_oval(
        x + 8, y + 8,
        x + 14, y + 14,
        fill="black"
    )

    right_eye = canvas.create_oval(
        x + 26, y + 8,
        x + 32, y + 14,
        fill="black"
    )

    return {
        "body": enemy,
        "left_eye": left_eye,
        "right_eye": right_eye
    }


def create_wave():
    global enemy_direction
    global enemy_speed

    enemies.clear()

    enemy_direction = 1
    enemy_speed = 1.5 + (level - 1) * 0.4

    rows = min(3 + (level - 1) // 2, 5)
    columns = 8

    colors = [
        "#FF4D6D",
        "#FFB703",
        "#9B5DE5",
        "#00F5D4",
        "#F15BB5"
    ]

    for row in range(rows):
        for col in range(columns):

            x = 110 + col * 70
            y = 80 + row * 55

            enemy = create_enemy(
                x,
                y,
                colors[row % len(colors)]
            )

            enemies.append(enemy)


def move_enemy(enemy, dx, dy):
    canvas.move(enemy["body"], dx, dy)
    canvas.move(enemy["left_eye"], dx, dy)
    canvas.move(enemy["right_eye"], dx, dy)


def delete_enemy(enemy):
    canvas.delete(enemy["body"])
    canvas.delete(enemy["left_eye"])
    canvas.delete(enemy["right_eye"])

    if enemy in enemies:
        enemies.remove(enemy)


def move_enemies():
    global enemy_direction

    if not enemies:
        return

    touch_edge = False

    for enemy in enemies:
        coords = canvas.coords(enemy["body"])

        if not coords:
            continue

        x1, y1, x2, y2 = coords

        if enemy_direction == 1 and x2 + enemy_speed >= WIDTH - 15:
            touch_edge = True

        if enemy_direction == -1 and x1 - enemy_speed <= 15:
            touch_edge = True

    if touch_edge:
        enemy_direction *= -1

        for enemy in enemies:
            move_enemy(enemy, 0, 20)

    else:
        for enemy in enemies:
            move_enemy(
                enemy,
                enemy_speed * enemy_direction,
                0
            )

    for enemy in enemies:
        coords = canvas.coords(enemy["body"])

        if coords and coords[3] >= HEIGHT - 95:
            end_game()
            return


# -----------------------------
# ENEMY SHOOTING
# -----------------------------

def enemy_shoot():
    if not enemies:
        return

    enemy = random.choice(enemies)

    coords = canvas.coords(enemy["body"])

    if not coords:
        return

    x1, y1, x2, y2 = coords

    center_x = (x1 + x2) / 2

    bullet = canvas.create_oval(
        center_x - 5,
        y2,
        center_x + 5,
        y2 + 12,
        fill="#FF3131",
        outline=""
    )

    enemy_bullets.append(bullet)


def move_enemy_bullets():
    for bullet in enemy_bullets[:]:

        canvas.move(
            bullet,
            0,
            ENEMY_BULLET_SPEED + level * 0.4
        )

        coords = canvas.coords(bullet)

        if not coords or coords[1] > HEIGHT:
            remove_enemy_bullet(bullet)


def remove_enemy_bullet(bullet):
    if bullet in enemy_bullets:
        enemy_bullets.remove(bullet)

    canvas.delete(bullet)


# -----------------------------
# COLLISIONS
# -----------------------------

def touching(box1, box2):
    if not box1 or not box2:
        return False

    return (
        box1[0] < box2[2]
        and box1[2] > box2[0]
        and box1[1] < box2[3]
        and box1[3] > box2[1]
    )


def check_collisions():
    global score
    global lives

    # Player bullets hitting enemies
    for bullet in bullets[:]:

        bullet_box = canvas.bbox(bullet)

        for enemy in enemies[:]:

            enemy_box = canvas.bbox(enemy["body"])

            if touching(bullet_box, enemy_box):

                remove_bullet(bullet)
                delete_enemy(enemy)

                score += 10
                update_hud()

                break

    # Enemy bullets hitting player
    player_box = canvas.bbox(player)

    for bullet in enemy_bullets[:]:

        bullet_box = canvas.bbox(bullet)

        if touching(bullet_box, player_box):

            remove_enemy_bullet(bullet)

            lives -= 1
            update_hud()

            if lives <= 0:
                end_game()
                return

            # Clear enemy bullets after a hit
            for other_bullet in enemy_bullets[:]:
                remove_enemy_bullet(other_bullet)

            break


# -----------------------------
# USER INTERFACE
# -----------------------------

def create_hud():
    canvas.create_text(
        20, 25,
        text="",
        anchor="w",
        fill="white",
        font=("Arial", 17, "bold"),
        tags="score_text"
    )

    canvas.create_text(
        WIDTH // 2, 25,
        text="",
        fill="white",
        font=("Arial", 17, "bold"),
        tags="level_text"
    )

    canvas.create_text(
        WIDTH - 20, 25,
        text="",
        anchor="e",
        fill="white",
        font=("Arial", 17, "bold"),
        tags="lives_text"
    )

    canvas.create_line(
        0, 50,
        WIDTH, 50,
        fill="#434765",
        width=2
    )

    update_hud()


def update_hud():
    canvas.itemconfig(
        "score_text",
        text=f"SCORE: {score}"
    )

    canvas.itemconfig(
        "level_text",
        text=f"LEVEL: {level}"
    )

    canvas.itemconfig(
        "lives_text",
        text=f"LIVES: {lives}"
    )


# -----------------------------
# GAME OVER
# -----------------------------

def end_game():
    global game_running
    global game_over

    if not game_running:
        return

    game_running = False
    game_over = True

    canvas.create_rectangle(
        150, 185,
        650, 420,
        fill="#15182B",
        outline="#FF4D6D",
        width=3,
        tags="overlay"
    )

    canvas.create_text(
        WIDTH // 2,
        240,
        text="GAME OVER",
        fill="#FF4D6D",
        font=("Arial", 38, "bold"),
        tags="overlay"
    )

    canvas.create_text(
        WIDTH // 2,
        310,
        text=f"FINAL SCORE: {score}",
        fill="white",
        font=("Arial", 23, "bold"),
        tags="overlay"
    )

    canvas.create_text(
        WIDTH // 2,
        370,
        text="PRESS R TO RESTART",
        fill="#00E5FF",
        font=("Arial", 17, "bold"),
        tags="overlay"
    )


# -----------------------------
# RESTART GAME
# -----------------------------

def start_game():
    global player
    global score
    global lives
    global level
    global game_running
    global game_over
    global shoot_cooldown
    global enemy_shoot_timer

    canvas.delete("all")

    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    keys_pressed.clear()

    score = 0
    lives = STARTING_LIVES
    level = 1

    shoot_cooldown = 0
    enemy_shoot_timer = 0

    game_running = True
    game_over = False

    create_hud()
    create_player()
    create_wave()


# -----------------------------
# KEYBOARD CONTROLS
# -----------------------------

def key_down(event):
    key = event.keysym

    keys_pressed.add(key)

    if key == "space" and game_running:
        shoot()

    if key.lower() == "r" and game_over:
        start_game()


def key_up(event):
    keys_pressed.discard(event.keysym)


window.bind("<KeyPress>", key_down)
window.bind("<KeyRelease>", key_up)


# -----------------------------
# MAIN GAME LOOP
# -----------------------------

def game_loop():
    global shoot_cooldown
    global enemy_shoot_timer
    global level

    if game_running:

        move_player()

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if "space" in keys_pressed:
            shoot()

        move_bullets()
        move_enemies()

        if game_running:

            move_enemy_bullets()
            check_collisions()

        if game_running:

            enemy_shoot_timer += 1

            shoot_interval = max(
                25,
                100 - level * 8
            )

            if enemy_shoot_timer >= shoot_interval:

                enemy_shoot()
                enemy_shoot_timer = 0

            # Start next wave
            if not enemies:

                level += 1
                update_hud()
                create_wave()

    # Run approximately 60 times per second
    window.after(16, game_loop)


# -----------------------------
# START
# -----------------------------

start_game()
game_loop()

window.mainloop()
