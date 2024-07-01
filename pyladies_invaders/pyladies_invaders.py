import pygame
import sys
import random
import enum


SCREEN_WIDTH = 700
SCREEN_HEIGHT = 497

FPS = 60

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_IMG = "img/player.png"
SHOT_PLAYER_IMG = "img/shot_player.png"

INVADER_WIDTH = 25
INVADER_HEIGHT = 18
INVADER_IMG = "img/invader.png"
SHOT_INVADER_IMG = "img/shot_invader.png"

LIFE_WIDTH = 30
LIFE_HEIGHT = 22
LIFE_IMG = "img/life.png"
LIFE_QTD = 3

SHOT_WIDTH = 3
SHOT_HEIGHT = 5

SHOT_PLAYER_SPEED = 10
SHOT_INVADER_SPEED = 3
INVADER_X_SPEED = 10
INVADER_Y_SPEED = 5

HIT_INVADER_SOUND = "sounds/hit_invader.ogg"
HIT_PLAYER_SOUND = "sounds/hit_player.ogg"
EXPLOSION_SOUND = "sounds/explosion.ogg"
VICTORY_SOUND = "sounds/victory.ogg"
GAME_START_SOUND = "sounds/game_start.ogg"
GAME_OVER_SOUND = "sounds/game_over.ogg"
GAME_RUN_SOUND = "sounds/game_run.ogg"

FONT = "fonts/RobotoMono-Bold.ttf"

INVADER_TIME_X = 500
INVADER_TIME_Y = 1000
INVADER_TIME_SHOOT = 300

MOVE_INVADERS_X = pygame.USEREVENT + 1
MOVE_INVADERS_Y = pygame.USEREVENT + 2
INVADERS_SHOOT = pygame.USEREVENT + 3

PYLADIES_LOGO = "img/pyladies_logo.png"
PYLADIES_LOGO_WIDTH = 70
PYLADIES_LOGO_HEIGHT = 30

GAME_START_IMG = "img/game_start.png"
GAME_OVER_IMG = "img/game_over.png"


class Direction(enum.Enum):
    LEFT = "left"
    RIGHT = "right"


class Object:
    def __init__(self, image_path, width, height, x=0, y=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.image.load(image_path)

    def move(self, x, y):
        self.x = x
        self.y = y

    def show(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def collision(self, other):
        return pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
            pygame.Rect(other.x, other.y, other.width, other.height)
        )


class Sound:
    def __init__(self, sound_path, channel_number, volume=0.3):
        self.sound = pygame.mixer.Sound(sound_path)
        self.channel = pygame.mixer.Channel(channel_number)
        self.channel.set_volume(volume)

    def play(self, loops=0):
        self.channel.play(self.sound, loops=loops)

    def stop(self):
        self.channel.stop()


class Player(Object):
    def __init__(self, image=PLAYER_IMG):
        x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
        y = SCREEN_HEIGHT - PLAYER_HEIGHT

        super().__init__(image, PLAYER_WIDTH, PLAYER_HEIGHT, x, y)

    def move(self, x):
        self.x = x if x >= 0 and x <= SCREEN_WIDTH - self.width else self.x


class ShotPlayer(Object):
    def __init__(self, x, image=SHOT_PLAYER_IMG):
        y = SCREEN_HEIGHT - PLAYER_HEIGHT - SHOT_HEIGHT

        super().__init__(image, SHOT_WIDTH, SHOT_HEIGHT, x, y)

    def move(self, y):
        self.y = max(0, y)


class Invader(Object):
    def __init__(self, x, y, image=INVADER_IMG):
        super().__init__(image, INVADER_WIDTH, INVADER_HEIGHT, x, y)


class ShotInvader(Object):
    def __init__(self, x, y, image=SHOT_INVADER_IMG):
        super().__init__(image, SHOT_WIDTH, SHOT_HEIGHT, x, y)

    def move(self, y):
        self.y = min(SCREEN_HEIGHT, y)


class Life(Object):
    def __init__(self, x, y, image=LIFE_IMG):
        super().__init__(image, LIFE_WIDTH, LIFE_HEIGHT, x, y)


class Text:
    def __init__(self, screen, font_size=25):
        self.font = pygame.font.Font(FONT, font_size)
        self.screen = screen

    def write(self, text_to_write, x, y, color=(255, 255, 255)):
        text = self.font.render(text_to_write, True, color)
        self.screen.blit(text, (x, y))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PyLadies Invaders")

        self.pyladies_logo = Object(
            PYLADIES_LOGO,
            PYLADIES_LOGO_WIDTH,
            PYLADIES_LOGO_HEIGHT,
            SCREEN_WIDTH - PYLADIES_LOGO_WIDTH - 300,
            10,
        )

        pygame.time.set_timer(MOVE_INVADERS_X, 500)
        pygame.time.set_timer(MOVE_INVADERS_Y, 2000)
        pygame.time.set_timer(INVADERS_SHOOT, 1000)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.player = Player()
        self.shot_player = None

        self.invaders = [
            Invader(x * INVADER_WIDTH * 2 + 100, y * 50 + 50)
            for x in range((SCREEN_WIDTH - 150) // 50)
            for y in range(5)
        ]
        self.shots_invaders = []

        self.lifes = [
            Life(x * LIFE_WIDTH + SCREEN_WIDTH - LIFE_WIDTH * LIFE_QTD - 30, 10)
            for x in range(LIFE_QTD)
        ]

        self.direction = Direction.LEFT

        self.sound_hit_invader = Sound(HIT_INVADER_SOUND, 0)
        self.sound_hit_player = Sound(HIT_PLAYER_SOUND, 1)
        self.sound_explosion = Sound(EXPLOSION_SOUND, 2)
        self.sound_victory = Sound(VICTORY_SOUND, 3)
        self.sound_game_start = Sound(GAME_START_SOUND, 4)
        self.sound_game_over = Sound(GAME_OVER_SOUND, 5)
        self.sound_game_run = Sound(GAME_RUN_SOUND, 6, 0.1)

        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == MOVE_INVADERS_X:
                self.move_invaders_x()

            if event.type == MOVE_INVADERS_Y:
                self.move_invaders_y()

            if event.type == INVADERS_SHOOT:
                self.invader_shoot()

    def handle_input(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT]:
            self.player.move(self.player.x - 5)
        if pressed_keys[pygame.K_RIGHT]:
            self.player.move(self.player.x + 5)
        if pressed_keys[pygame.K_SPACE]:
            self.shot_player = ShotPlayer(self.player.x + PLAYER_WIDTH // 2)
        if pressed_keys[pygame.K_ESCAPE]:
            sys.exit()

    def check_collision(self):
        for shot_invader in self.shots_invaders:
            if self.player.collision(shot_invader):
                self.shots_invaders.remove(shot_invader)
                self.sound_hit_player.play()
                self.lifes.pop()

        for invader in self.invaders:
            if invader.collision(self.player):
                self.invaders.remove(invader)
                self.lifes.pop()

                self.sound_hit_invader.play()

            if self.shot_player and invader.collision(self.shot_player):
                self.invaders.remove(invader)
                self.sound_hit_invader.play()
                self.shot_player = None
                self.score += 1

    def check_game_over(self):
        if not self.lifes:
            self.sound_explosion.play()
            self.game_over()

        if not self.invaders:
            self.sound_victory.play()
            self.game_over()

    def move_invaders_y(self):
        for invader in self.invaders:
            invader.move(invader.x, invader.y + INVADER_Y_SPEED)

        if invader.y >= SCREEN_HEIGHT + INVADER_HEIGHT:
            self.invaders.remove(invader)

    def move_invaders_x(self):
        for invader in self.invaders:
            if self.direction == Direction.LEFT:
                invader.move(invader.x - INVADER_X_SPEED, invader.y)
            elif self.direction == Direction.RIGHT:
                invader.move(invader.x + INVADER_X_SPEED, invader.y)

        if self.invaders:
            if self.invaders[-1].x >= SCREEN_WIDTH - INVADER_WIDTH:
                self.direction = Direction.LEFT
            elif self.invaders[0].x <= 0:
                self.direction = Direction.RIGHT

    def invader_shoot(self):
        invader_to_shoot = random.choice(self.invaders)
        self.shots_invaders.append(
            ShotInvader(
                invader_to_shoot.x + INVADER_WIDTH // 2,
                invader_to_shoot.y + INVADER_HEIGHT,
            )
        )

    def move_shots(self):
        if self.shot_player:
            self.shot_player.move(self.shot_player.y - SHOT_PLAYER_SPEED)
            if self.shot_player.y <= 0:
                self.shot_player = None

        for shot_invader in self.shots_invaders:
            shot_invader.move(shot_invader.y + SHOT_INVADER_SPEED)
            if shot_invader.y >= SCREEN_HEIGHT:
                self.shots_invaders.remove(shot_invader)

    def draw(self):
        self.screen.fill((0, 0, 0))

        text = Text(self.screen, 15)
        text.write(f"Pontuação: {self.score}", 30, 10)
        text.write("Vidas:", SCREEN_WIDTH - 180, 10)

        self.pyladies_logo.show(self.screen)

        self.player.show(self.screen)

        for life in self.lifes:
            life.show(self.screen)

        for invader in self.invaders:
            invader.show(self.screen)

        for shot_invader in self.shots_invaders:
            shot_invader.show(self.screen)

        if self.shot_player:
            self.shot_player.show(self.screen)

        pygame.display.flip()

    def run(self):
        self.game_start()
        self.sound_game_run.play(-1)

        while True:
            self.handle_events()
            self.handle_input()
            self.move_shots()
            self.check_collision()
            self.draw()
            self.check_game_over()  # needs to be checked after draw
            self.clock.tick(FPS)

    def game_start(self):
        game_start_image = pygame.image.load(GAME_START_IMG)
        self.screen.blit(game_start_image, (0, 0))
        pygame.display.flip()

        self.sound_game_start.play(-1)

        start = False
        while not start:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                        start = True
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
        if start:
            self.sound_game_start.stop()
            pygame.time.delay(300)
            return

    def game_over(self):
        pygame.time.wait(5000)

        game_over_image = pygame.image.load(GAME_OVER_IMG)
        self.screen.blit(game_over_image, (0, 0))
        Text(self.screen, 50).write(str(self.score), 470, 232)
        pygame.display.flip()

        self.sound_game_run.stop()
        self.sound_game_over.play(-1)

        restart = False
        while not restart:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                        restart = True
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
        if restart:
            self.sound_game_over.stop()
            pygame.time.delay(300)
            self.__init__()
            self.run()


Game().run()
