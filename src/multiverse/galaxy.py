import random
import sys

import pygame
from multiverse.constants import BLACK, COLORS, WHITE

# Constants
SCALE_FACTOR = 2
WINDOW_WIDTH, WINDOW_HEIGHT = 300, 300
GRID_SIZE = 16
MIN_CIRCLE_RADIUS = 2
MAX_CIRCLE_RADIUS = WINDOW_WIDTH // GRID_SIZE // 2 - 1
CIRCLE_PROBABILITY = 0.1  # chance of a circle appearing in a grid cell
SPEED = 5


class Star:
    def __init__(self, seed1, seed2):
        self.seed1 = seed1
        self.seed2 = seed2

        random.seed((seed1 & 0xFFFF) << 16 | (seed2 & 0xFFFF))
        self.exists = random.randint(1, 20) == 1
        if not self.exists:
            return

        self.color = random.choice(COLORS)
        self.radius = random.randint(MIN_CIRCLE_RADIUS, MAX_CIRCLE_RADIUS)
        self.has_life = random.randint(1, 1_000) == 1


class Galaxy:
    def __init__(self):
        self.user_x, self.user_y = 0, 0
        self.speed = 5.0
        self.grid_size = 16

        pygame.init()
        self.win = pygame.display.set_mode((WINDOW_WIDTH * SCALE_FACTOR, WINDOW_HEIGHT * SCALE_FACTOR))
        self.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Multiverse")
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Handle key events
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.user_x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.user_x += self.speed
            if keys[pygame.K_UP]:
                self.user_y -= self.speed
            if keys[pygame.K_DOWN]:
                self.user_y += self.speed

            # Clear the screen
            self.screen.fill(BLACK)

            nx = self.screen.get_width() // self.grid_size
            ny = self.screen.get_height() // self.grid_size
            for iy in range(ny):
                for ix in range(nx):
                    seed1 = int(self.user_x // self.grid_size) + ix
                    seed2 = int(self.user_y // self.grid_size) + iy
                    star = Star(seed1, seed2)
                    if star.exists:
                        x = ix * self.grid_size + self.grid_size // 2
                        y = iy * self.grid_size + self.grid_size // 2
                        pygame.draw.circle(self.screen, star.color, (x, y), star.radius)
                        if star.has_life:
                            pygame.draw.circle(self.screen, "#00FF00", (x, y), 2 * star.radius, width=1)

            font = pygame.font.SysFont("Mono", 15)
            location = font.render(
                f"x={self.user_x:.0f}\n"
                f"y={-self.user_y:.0f}\n"
                f"sector=({self.user_x // self.screen.get_width():.0f},{-self.user_y // self.screen.get_height():.0f})",
                True,
                WHITE,
            )
            self.screen.blit(location, (10, 10))

            # Update the display
            self.win.blit(pygame.transform.scale(self.screen, self.win.get_rect().size), (0, 0))
            pygame.display.update()

        pygame.quit()
        sys.exit()
