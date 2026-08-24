import pygame
import random
import math
import cv2
import mediapipe as mp

pygame.init()

# ============================================================
# WINDOW
# ============================================================

WIDTH = 1000
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HAND DRIVE RACING")
clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GREEN = (30, 120, 45)
DARK_GREEN = (20, 90, 35)
ROAD = (50, 50, 55)
ROAD_LINE = (240, 240, 240)

RED = (220, 40, 40)
BLUE = (35, 120, 245)
YELLOW = (255, 215, 30)
ORANGE = (255, 120, 20)
CYAN = (40, 220, 255)
PURPLE = (170, 50, 200)

# ============================================================
# ROAD
# ============================================================

ROAD_LEFT = 170
ROAD_RIGHT = 830
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH // 3

# ============================================================
# PLAYER
# ============================================================

CAR_WIDTH = 60
CAR_HEIGHT = 105

player_x = WIDTH // 2 - CAR_WIDTH // 2
player_y = HEIGHT - 155

# ============================================================
# SPEED
# ============================================================

speed = 8.0

MIN_SPEED = 0
NORMAL_MAX_SPEED = 22
NITRO_MAX_SPEED = 35

ACCELERATION = 0.30
BRAKE_POWER = 0.80
FRICTION = 0.04

# Fast steering
STEERING_SPEED = 0.65

# ============================================================
# GAME VARIABLES
# ============================================================

score = 0
distance = 0
nitro = 100

game_over = False

road_offset = 0

enemy_timer = 0
coin_timer = 0

nitro_active = False

# ============================================================
# HAND STATUS
# ============================================================

hand_mode = "NO HANDS"

hand_accelerating = False
hand_braking = False
hand_nitro = False

hand_count = 0

# ============================================================
# FONTS
# ============================================================

font = pygame.font.SysFont(
    "Arial",
    25,
    bold=True
)

small_font = pygame.font.SysFont(
    "Arial",
    17,
    bold=True
)

big_font = pygame.font.SysFont(
    "Arial",
    70,
    bold=True
)

speed_font = pygame.font.SysFont(
    "Arial",
    32,
    bold=True
)

# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("WARNING: Camera could not be opened.")

    camera = None

# Camera preview size
CAMERA_WIDTH = 240
CAMERA_HEIGHT = 180

# ============================================================
# OBJECTS
# ============================================================

enemies = []
coins = []

# ============================================================
# DRAW CAR
# ============================================================

def draw_car(x, y, color):

    x = int(x)
    y = int(y)

    # Shadow
    pygame.draw.ellipse(
        screen,
        BLACK,
        (
            x - 4,
            y + CAR_HEIGHT - 10,
            CAR_WIDTH + 8,
            18
        )
    )

    # Body
    pygame.draw.rect(
        screen,
        color,
        (
            x,
            y,
            CAR_WIDTH,
            CAR_HEIGHT
        )
    )

    # Windows
    pygame.draw.rect(
        screen,
        (20, 30, 40),
        (
            x + 10,
            y + 14,
            CAR_WIDTH - 20,
            28
        )
    )

    pygame.draw.rect(
        screen,
        (20, 30, 40),
        (
            x + 10,
            y + 55,
            CAR_WIDTH - 20,
            20
        )
    )

    # Headlights
    pygame.draw.rect(
        screen,
        WHITE,
        (
            x + 7,
            y + 5,
            13,
            8
        )
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (
            x + CAR_WIDTH - 20,
            y + 5,
            13,
            8
        )
    )

    # Wheels
    wheels = [
        (x - 6, y + 18),
        (x + CAR_WIDTH - 2, y + 18),
        (x - 6, y + 70),
        (x + CAR_WIDTH - 2, y + 70)
    ]

    for wx, wy in wheels:

        pygame.draw.rect(
            screen,
            BLACK,
            (
                wx,
                wy,
                9,
                25
            )
        )

# ============================================================
# NITRO FLAME
# ============================================================

def draw_nitro_flame(x, y):

    flame_x = int(
        x + CAR_WIDTH / 2
    )

    pygame.draw.polygon(
        screen,
        ORANGE,
        [
            (
                flame_x - 14,
                y + CAR_HEIGHT
            ),
            (
                flame_x + 14,
                y + CAR_HEIGHT
            ),
            (
                flame_x,
                y + CAR_HEIGHT
                + random.randint(20, 40)
            )
        ]
    )

    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (
                flame_x - 7,
                y + CAR_HEIGHT
            ),
            (
                flame_x + 7,
                y + CAR_HEIGHT
            ),
            (
                flame_x,
                y + CAR_HEIGHT
                + random.randint(12, 28)
            )
        ]
    )

# ============================================================
# ROAD
# ============================================================

def draw_road():

    global road_offset

    screen.fill(GREEN)

    # Grass details
    for y in range(-50, HEIGHT + 50, 70):

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (
                40,
                y,
                8,
                30
            )
        )

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (
                WIDTH - 48,
                y,
                8,
                30
            )
        )

    # Road
    pygame.draw.rect(
        screen,
        ROAD,
        (
            ROAD_LEFT,
            0,
            ROAD_WIDTH,
            HEIGHT
        )
    )

    # Road edges
    pygame.draw.rect(
        screen,
        WHITE,
        (
            ROAD_LEFT,
            0,
            6,
            HEIGHT
        )
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (
            ROAD_RIGHT - 6,
            0,
            6,
            HEIGHT
        )
    )

    # Lane markings
    road_offset = (
        road_offset + speed
    ) % 100

    for lane in range(1, 3):

        x = (
            ROAD_LEFT
            + lane * LANE_WIDTH
        )

        for y in range(
            -100,
            HEIGHT + 100,
            100
        ):

            pygame.draw.rect(
                screen,
                ROAD_LINE,
                (
                    x - 4,
                    y + road_offset,
                    8,
                    50
                )
            )

# ============================================================
# CREATE ENEMY
# ============================================================

def create_enemy():

    lane = random.randint(0, 2)

    x = (
        ROAD_LEFT
        + lane * LANE_WIDTH
        + LANE_WIDTH // 2
        - CAR_WIDTH // 2
    )

    return {
        "x": x,
        "y": -130,
        "speed": random.uniform(4, 9),
        "color": random.choice(
            [
                RED,
                ORANGE,
                PURPLE,
                BLUE
            ]
        )
    }

# ============================================================
# CREATE COIN
# ============================================================

def create_coin():

    lane = random.randint(0, 2)

    x = (
        ROAD_LEFT
        + lane * LANE_WIDTH
        + LANE_WIDTH // 2
    )

    return {
        "x": x,
        "y": -30
    }

# ============================================================
# COLLISION
# ============================================================

def collision(
    x1,
    y1,
    w1,
    h1,
    x2,
    y2,
    w2,
    h2
):

    return (
        x1 < x2 + w2
        and
        x1 + w1 > x2
        and
        y1 < y2 + h2
        and
        y1 + h1 > y2
    )

# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    global player_x
    global speed
    global score
    global distance
    global nitro
    global game_over

    player_x = (
        WIDTH // 2
        - CAR_WIDTH // 2
    )

    speed = 8.0
    score = 0
    distance = 0
    nitro = 100

    enemies.clear()
    coins.clear()

    game_over = False

# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    clock.tick(FPS)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            if (
                game_over
                and event.key == pygame.K_r
            ):

                reset_game()

    # ========================================================
    # RESET HAND ACTIONS
    # ========================================================

    hand_accelerating = False
    hand_braking = False
    hand_nitro = False

    # ========================================================
    # CAMERA FRAME
    # ========================================================

    camera_surface = None

    if camera is not None:

        ret, frame = camera.read()

        if ret:

            frame = cv2.flip(
                frame,
                1
            )

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = hands.process(
                rgb
            )

            hand_data = []

            if results.multi_hand_landmarks:

                for hand_landmarks in results.multi_hand_landmarks:

                    wrist = hand_landmarks.landmark[
                        mp_hands.HandLandmark.WRIST
                    ]

                    thumb_tip = hand_landmarks.landmark[
                        mp_hands.HandLandmark.THUMB_TIP
                    ]

                    index_tip = hand_landmarks.landmark[
                        mp_hands.HandLandmark.INDEX_FINGER_TIP
                    ]

                    middle_tip = hand_landmarks.landmark[
                        mp_hands.HandLandmark.MIDDLE_FINGER_TIP
                    ]

                    hand_data.append(
                        {
                            "x": wrist.x,
                            "y": wrist.y,
                            "thumb_y": thumb_tip.y,
                            "index_y": index_tip.y,
                            "middle_y": middle_tip.y
                        }
                    )

                    # Draw landmarks
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

            hand_count = len(
                hand_data
            )

            # =================================================
            # TWO HAND CONTROL
            # =================================================

            if hand_count >= 2:

                # Average hand position
                avg_x = (
                    hand_data[0]["x"]
                    +
                    hand_data[1]["x"]
                ) / 2

                avg_y = (
                    hand_data[0]["y"]
                    +
                    hand_data[1]["y"]
                ) / 2

                # ------------------------------------------------
                # FAST STEERING
                # ------------------------------------------------

                target_x = (
                    ROAD_LEFT
                    +
                    avg_x * ROAD_WIDTH
                    -
                    CAR_WIDTH / 2
                )

                target_x = max(
                    ROAD_LEFT + 12,
                    min(
                        target_x,
                        ROAD_RIGHT
                        - CAR_WIDTH
                        - 12
                    )
                )

                steering_error = (
                    target_x
                    -
                    player_x
                )

                player_x += (
                    steering_error
                    * STEERING_SPEED
                )

                # ------------------------------------------------
                # ACCELERATION
                # ------------------------------------------------

                if avg_y < 0.38:

                    hand_accelerating = True
                    hand_mode = "ACCELERATE"

                # ------------------------------------------------
                # BRAKE
                # ------------------------------------------------

                elif avg_y > 0.62:

                    hand_braking = True
                    hand_mode = "BRAKE"

                else:

                    hand_mode = "CRUISE"

                # ------------------------------------------------
                # THUMBS UP NITRO
                # ------------------------------------------------

                thumbs_up = False

                for hand in hand_data:

                    if (
                        hand["thumb_y"]
                        <
                        hand["index_y"] - 0.08
                        and
                        hand["thumb_y"]
                        <
                        hand["middle_y"] - 0.08
                    ):

                        thumbs_up = True

                if thumbs_up:

                    hand_nitro = True

            else:

                hand_mode = "NO HANDS"

            # =================================================
            # CAMERA LABEL
            # =================================================

            cv2.putText(
                frame,
                f"HANDS: {hand_count}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                hand_mode,
                (10, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

            if hand_nitro:

                cv2.putText(
                    frame,
                    "NITRO!",
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 200, 255),
                    2
                )

            # =================================================
            # CONVERT CAMERA TO PYGAME
            # =================================================

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frame = cv2.resize(
                frame,
                (
                    CAMERA_WIDTH,
                    CAMERA_HEIGHT
                )
            )

            camera_surface = pygame.surfarray.make_surface(
                frame.swapaxes(0, 1)
            )

    # ========================================================
    # GAME UPDATE
    # ========================================================

    if not game_over:

        keys = pygame.key.get_pressed()

        # ====================================================
        # KEYBOARD BACKUP STEERING
        # ====================================================

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:

            player_x -= 12

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

            player_x += 12

        # ====================================================
        # ACCELERATION
        # ====================================================

        accelerating = (
            keys[pygame.K_UP]
            or
            keys[pygame.K_w]
            or
            hand_accelerating
        )

        # ====================================================
        # BRAKE
        # ====================================================

        braking = (
            keys[pygame.K_DOWN]
            or
            keys[pygame.K_s]
            or
            hand_braking
        )

        # ====================================================
        # NITRO
        # ====================================================

        nitro_requested = (
            keys[pygame.K_SPACE]
            or
            hand_nitro
        )

        # ====================================================
        # ACCELERATE
        # ====================================================

        if accelerating:

            speed += ACCELERATION

        else:

            speed -= FRICTION

        # ====================================================
        # BRAKE
        # ====================================================

        if braking:

            speed -= BRAKE_POWER

        # ====================================================
        # NITRO
        # ====================================================

        nitro_active = False

        if (
            nitro_requested
            and
            nitro > 0
            and
            not braking
        ):

            nitro_active = True

            speed += 0.50

            nitro -= 1.0

        else:

            nitro += 0.30

        # ====================================================
        # SPEED LIMIT
        # ====================================================

        nitro = max(
            0,
            min(
                100,
                nitro
            )
        )

        if nitro_active:

            speed = min(
                speed,
                NITRO_MAX_SPEED
            )

        else:

            speed = min(
                speed,
                NORMAL_MAX_SPEED
            )

        speed = max(
            MIN_SPEED,
            speed
        )

        # ====================================================
        # ROAD LIMIT
        # ====================================================

        player_x = max(
            ROAD_LEFT + 12,
            min(
                player_x,
                ROAD_RIGHT
                - CAR_WIDTH
                - 12
            )
        )

        # ====================================================
        # SCORE
        # ====================================================

        distance += (
            speed * 0.05
        )

        score += int(
            speed * 0.03
        )

        # ====================================================
        # ENEMY SPAWN
        # ====================================================

        enemy_timer += 1

        spawn_rate = max(
            22,
            65 - int(speed * 1.5)
        )

        if enemy_timer >= spawn_rate:

            enemies.append(
                create_enemy()
            )

            enemy_timer = 0

        # ====================================================
        # MOVE ENEMIES
        # ====================================================

        for enemy in enemies[:]:

            enemy["y"] += (
                speed
                +
                enemy["speed"]
            )

            if collision(
                player_x,
                player_y,
                CAR_WIDTH,
                CAR_HEIGHT,
                enemy["x"],
                enemy["y"],
                CAR_WIDTH,
                CAR_HEIGHT
            ):

                game_over = True

            if enemy["y"] > HEIGHT + 150:

                enemies.remove(
                    enemy
                )

        # ====================================================
        # COINS
        # ====================================================

        coin_timer += 1

        if coin_timer >= 75:

            coins.append(
                create_coin()
            )

            coin_timer = 0

        for coin in coins[:]:

            coin["y"] += speed

            d = math.hypot(
                player_x
                + CAR_WIDTH / 2
                - coin["x"],

                player_y
                + CAR_HEIGHT / 2
                - coin["y"]
            )

            if d < 48:

                score += 150

                nitro = min(
                    100,
                    nitro + 20
                )

                coins.remove(
                    coin
                )

            elif coin["y"] > HEIGHT:

                coins.remove(
                    coin
                )

    # ========================================================
    # DRAW GAME
    # ========================================================

    draw_road()

    # ========================================================
    # DRAW COINS
    # ========================================================

    for coin in coins:

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                int(coin["x"]),
                int(coin["y"])
            ),
            13
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            (
                int(coin["x"]),
                int(coin["y"])
            ),
            8,
            3
        )

    # ========================================================
    # DRAW ENEMIES
    # ========================================================

    for enemy in enemies:

        draw_car(
            enemy["x"],
            enemy["y"],
            enemy["color"]
        )

    # ========================================================
    # DRAW PLAYER
    # ========================================================

    if not game_over:

        if nitro_active:

            draw_nitro_flame(
                player_x,
                player_y
            )

        draw_car(
            player_x,
            player_y,
            BLUE
        )

    # ========================================================
    # HUD
    # ========================================================

    screen.blit(
        font.render(
            f"SCORE: {score}",
            True,
            WHITE
        ),
        (20, 15)
    )

    screen.blit(
        font.render(
            f"DISTANCE: {int(distance)}",
            True,
            WHITE
        ),
        (20, 48)
    )

    # ========================================================
    # SPEED
    # ========================================================

    current_speed = int(
        speed * 10
    )

    screen.blit(
        speed_font.render(
            str(current_speed),
            True,
            WHITE
        ),
        (
            WIDTH - 150,
            15
        )
    )

    screen.blit(
        small_font.render(
            "KM/H",
            True,
            WHITE
        ),
        (
            WIDTH - 145,
            53
        )
    )

    # ========================================================
    # NITRO BAR
    # ========================================================

    pygame.draw.rect(
        screen,
        BLACK,
        (
            20,
            85,
            220,
            22
        )
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            20,
            85,
            int(
                220
                * nitro
                / 100
            ),
            22
        )
    )

    screen.blit(
        small_font.render(
            "NITRO",
            True,
            WHITE
        ),
        (
            20,
            110
        )
    )

    # ========================================================
    # CAMERA PANEL
    # ========================================================

    camera_x = WIDTH - CAMERA_WIDTH - 20
    camera_y = 150

    pygame.draw.rect(
        screen,
        BLACK,
        (
            camera_x - 4,
            camera_y - 4,
            CAMERA_WIDTH + 8,
            CAMERA_HEIGHT + 8
        )
    )

    if camera_surface is not None:

        screen.blit(
            camera_surface,
            (
                camera_x,
                camera_y
            )
        )

    else:

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (
                camera_x,
                camera_y,
                CAMERA_WIDTH,
                CAMERA_HEIGHT
            )
        )

        no_camera = small_font.render(
            "CAMERA OFF",
            True,
            RED
        )

        screen.blit(
            no_camera,
            (
                camera_x + 65,
                camera_y + 80
            )
        )

    camera_label = small_font.render(
        "HAND CAMERA",
        True,
        WHITE
    )

    screen.blit(
        camera_label,
        (
            camera_x,
            camera_y + CAMERA_HEIGHT + 8
        )
    )

    # ========================================================
    # HAND STATUS
    # ========================================================

    if hand_count >= 2:

        status_color = (
            50,
            255,
            50
        )

        status = "HAND CONTROL: ON"

    else:

        status_color = RED

        status = "SHOW BOTH HANDS"

    status_text = font.render(
        status,
        True,
        status_color
    )

    screen.blit(
        status_text,
        (
            WIDTH // 2
            - status_text.get_width() // 2,
            15
        )
    )

    # ========================================================
    # HAND MODE
    # ========================================================

    if hand_mode == "ACCELERATE":

        mode_color = (
            50,
            255,
            50
        )

    elif hand_mode == "BRAKE":

        mode_color = RED

    elif hand_mode == "CRUISE":

        mode_color = YELLOW

    else:

        mode_color = WHITE

    mode_text = small_font.render(
        f"MODE: {hand_mode}",
        True,
        mode_color
    )

    screen.blit(
        mode_text,
        (
            WIDTH // 2
            - mode_text.get_width() // 2,
            50
        )
    )

    # ========================================================
    # BOTTOM CONTROLS
    # ========================================================

    controls = small_font.render(
        "✋ STEER   ↑ HIGH: ACCEL   ↓ LOW: BRAKE   👍 NITRO",
        True,
        WHITE
    )

    screen.blit(
        controls,
        (
            WIDTH // 2
            - controls.get_width() // 2,
            HEIGHT - 42
        )
    )

    backup = small_font.render(
        "Keyboard: A/D  W/S  SPACE",
        True,
        WHITE
    )

    screen.blit(
        backup,
        (
            WIDTH // 2
            - backup.get_width() // 2,
            HEIGHT - 20
        )
    )

    # ========================================================
    # GAME OVER
    # ========================================================

    if game_over:

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 185)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        crash = big_font.render(
            "CRASH!",
            True,
            RED
        )

        final_score = font.render(
            f"FINAL SCORE: {score}",
            True,
            WHITE
        )

        restart = font.render(
            "PRESS R TO RACE AGAIN",
            True,
            YELLOW
        )

        screen.blit(
            crash,
            (
                WIDTH // 2
                - crash.get_width() // 2,
                HEIGHT // 2 - 120
            )
        )

        screen.blit(
            final_score,
            (
                WIDTH // 2
                - final_score.get_width() // 2,
                HEIGHT // 2 - 20
            )
        )

        screen.blit(
            restart,
            (
                WIDTH // 2
                - restart.get_width() // 2,
                HEIGHT // 2 + 50
            )
        )

    # ========================================================
    # UPDATE
    # ========================================================

    pygame.display.flip()

# ============================================================
# CLEANUP
# ============================================================

if camera is not None:

    camera.release()

hands.close()

pygame.quit()