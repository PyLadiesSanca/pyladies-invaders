import pygame
import sys
import random
import enum


SCREEN_WIDTH = 700
SCREEN_HEIGHT = 497

FPS = 60

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50

SHOT_WIDTH = 3
SHOT_HEIGHT = 5

SHOT_PLAYER_SPEED = 10
SHOT_INVADER_SPEED = 3

INVADER_WIDTH = 25
INVADER_HEIGHT = 18

INVADER_TIME_X = 500
INVADER_TIME_Y = 1000
INVADER_TIME_SHOOT = 300

MOVE_INVADERS_X = pygame.USEREVENT + 1
MOVE_INVADERS_Y = pygame.USEREVENT + 2
INVADERS_SHOOT = pygame.USEREVENT + 3


class Direction(enum.Enum):
    LEFT = 0
    RIGHT = 1


class Object():
    def __init__(self, image, width, height, x=0, y=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

    def move(self, x, y):
        self.x = x = x
        self.y = y

    def show(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def collision(self, other):
        return pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
            pygame.Rect(other.x, other.y, other.width, other.height))


class Player(Object):
    def __init__(self):
        x = (SCREEN_WIDTH + PLAYER_WIDTH) // 2
        y = SCREEN_HEIGHT - PLAYER_HEIGHT
        image = pygame.image.load('img/player.png')

        super().__init__(image, PLAYER_WIDTH, PLAYER_HEIGHT, x, y)

    def move(self, x):
        self.x = x if x >= 0 and x <= SCREEN_WIDTH - self.width else self.x


class ShotPlayer(Object):
    def __init__(self, x):
        y = SCREEN_HEIGHT - PLAYER_HEIGHT - SHOT_HEIGHT
        image = pygame.image.load('img/shot_player.png')

        super().__init__(image, SHOT_WIDTH, SHOT_HEIGHT, x, y)

    def move(self, y):
        self.y = max(0, y)


class Invader(Object):
    def __init__(self, x, y):
        image = pygame.image.load('img/invader.png')

        super().__init__(image, INVADER_WIDTH, INVADER_HEIGHT, x, y)


class ShotInvader(Object):
    def __init__(self, x, y):
        image = pygame.image.load('img/shot_invader.png')

        super().__init__(image, SHOT_WIDTH, SHOT_HEIGHT, x, y)

    def move(self, y):
        self.y = min(SCREEN_HEIGHT, y)


class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('PyLadies Invaders')

        pygame.time.set_timer(MOVE_INVADERS_X, 500)
        pygame.time.set_timer(MOVE_INVADERS_Y, 2000)
        pygame.time.set_timer(INVADERS_SHOOT, 1000)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.player = Player()
        self.shot_player = None

        self.invaders = [Invader(x * 50 + 100, y * 50) for x in range((SCREEN_WIDTH - 200) // 50) for y in range(5)]
        self.shots_invaders = []

        self.direction = Direction.LEFT

        self.sound_hit_invader = pygame.mixer.Sound('sounds/hit_invader.wav')
        self.sound_hit_invader.set_volume(0.1)

        self.sound_hit_player = pygame.mixer.Sound('sounds/hit_player.wav')
        self.sound_hit_player.set_volume(0.1)

        self.sound_victory = pygame.mixer.Sound('sounds/victory.wav')
        self.sound_victory.set_volume(0.1)

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
        for invader in self.invaders:
            if self.shot_player and invader.collision(self.shot_player):
                self.sound_hit_invader.play()
                self.invaders.remove(invader)
                self.shot_player = None
                self.score += 1

        if not self.invaders:
            self.sound_victory.play()
            self.game_over()

        for shot_invader in self.shots_invaders:
            if self.player.collision(shot_invader):
                self.sound_hit_player.play()
                self.game_over()

    def move_invaders_y(self):
        for invader in self.invaders:
            invader.move(invader.x, invader.y + SHOT_INVADER_SPEED)

        if invader.y >= SCREEN_HEIGHT + INVADER_HEIGHT:
            self.invaders.remove(invader)

    def move_invaders_x(self):
        for invader in self.invaders:
            if self.direction == Direction.LEFT:
                invader.move(invader.x - SHOT_INVADER_SPEED, invader.y)
            elif self.direction == Direction.RIGHT:
                invader.move(invader.x + SHOT_INVADER_SPEED, invader.y)

        if self.invaders:
            if self.invaders[-1].x >= SCREEN_WIDTH - INVADER_WIDTH:
                self.direction = Direction.LEFT
            elif self.invaders[0].x <= 0:
                self.direction = Direction.RIGHT

    def invader_shoot(self):
        invader_to_shoot = random.choice(self.invaders)
        self.shots_invaders.append(
            ShotInvader(invader_to_shoot.x + INVADER_WIDTH // 2, invader_to_shoot.y + INVADER_HEIGHT)
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

        self.player.show(self.screen)

        for invader in self.invaders:
            invader.show(self.screen)

        for shot_invader in self.shots_invaders:
            shot_invader.show(self.screen)

        if self.shot_player:
            self.shot_player.show(self.screen)

        pygame.display.flip()

    def run(self):
        self.game_start()

        while True:
            self.handle_events()
            self.handle_input()
            self.check_collision()
            self.move_shots()
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

    def game_start(self):
        game_start_image = pygame.image.load('img/game_start.png')
        self.screen.blit(game_start_image, (0, 0))

        pygame.display.flip()

        start = False

        while not start:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                        start = True
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
        return

    def game_over(self):
        game_over_image = pygame.image.load('img/game_over.png')
        self.screen.blit(game_over_image, (0, 0))

        font = pygame.font.Font('fonts/RobotoMono-Bold.ttf', 50)
        score = font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(score, (470, 232))

        pygame.display.flip()

        restart = False

        while not restart:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                        restart = True
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
        if restart:
            self.__init__()
            self.run()


Game().run()
