import random
import string
import sys
import platform

import multiverse.constants as c
import pygame


class Body:
    """A star or planet in the galaxy. Each body is uniquely identified by a pair of seeds.
    The first seed represents the x-coordinate of the body, and the second seed represents the y-coordinate.
    The seeds are used to determine if the body exists, its color, its radius, and if it has life."""
    def __init__(self, seed1, seed2):
        self.seed1 = seed1
        self.seed2 = seed2

        architecture = platform.architecture()[0]
        if architecture == "64bit":
            seed = (seed1 & 0xFFFFFFFF) << 32 | (seed2 & 0xFFFFFFFF)
        elif architecture == "32bit":
            seed = (seed1 & 0xFFFF) << 16 | (seed2 & 0xFFFF)
        else:
            raise Exception(f"Unsupported architecture: {architecture}")
        random.seed(seed)

        self.exists = random.random() <= c.DENSITY
        if not self.exists:
            return

        self.color = random.choice(c.COLORS)
        self.radius = random.randint(c.MIN_RADIUS, c.MAX_RADIUS)
        self.has_life = self.exists * (random.random() <= c.LIFE_PROB)
        self.name = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


class Galaxy:
    """The galaxy is a grid of stars and planets. The user can move around the galaxy using the arrow keys.
    The galaxy is quite large (order of 2^64 or 10^19 in each direction), but only a small portion of it is visible
    at any given time. The galaxy is divided into sectors, and each sector is a square of side length equal to the
    height of the screen. The user can see the coordinates of the sector they are currently in."""
    def __init__(self):
        self.user_x, self.user_y = 0, 0
        self.speed = c.SPEED
        self.grid_size = c.GRID_SIZE
        pygame.init()
        self.win = pygame.display.set_mode((c.WINDOW_WIDTH * c.SCALE_FACTOR, c.WINDOW_HEIGHT * c.SCALE_FACTOR))
        self.screen = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        pygame.display.set_caption("Multiverse")
        self.clock = pygame.time.Clock()
        self.fonts = {
            "Mono-small": pygame.font.SysFont("Mono", 10),
            "Mono-medium": pygame.font.SysFont("Mono", 15),
            "Mono-large": pygame.font.SysFont("Mono", 20),
        }

    def handle_keys(self):
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

    def add_location_text(self):
        location = self.fonts["Mono-medium"].render(
            f"x={self.user_x:.0f}\n"
            f"y={-self.user_y:.0f}\n"
            f"sector=({self.user_x // self.screen.get_width():.0f},{-self.user_y // self.screen.get_height():.0f})",
            True,
            c.WHITE,
        )
        self.screen.blit(location, (10, 10))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_keys()

            # Clear the screen
            self.screen.fill(c.BLACK)

            # get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x /= c.SCALE_FACTOR
            mouse_y /= c.SCALE_FACTOR

            nx = self.screen.get_width() // self.grid_size
            ny = self.screen.get_height() // self.grid_size
            for iy in range(ny):
                for ix in range(nx):
                    seed1 = int(self.user_x // self.grid_size) + ix
                    seed2 = int(self.user_y // self.grid_size) + iy
                    body = Body(seed1, seed2)
                    if body.exists:
                        x = ix * self.grid_size + self.grid_size // 2
                        y = iy * self.grid_size + self.grid_size // 2
                        pygame.draw.circle(self.screen, body.color, (x, y), body.radius)
                        if body.has_life:
                            pygame.draw.circle(self.screen, c.GREEN, (x, y), body.radius + self.grid_size / 3, width=1)
                        if (mouse_x - x) ** 2 + (mouse_y - y) ** 2 <= (max(body.radius, 3 * c.MIN_RADIUS)) ** 2:
                            star_name = self.fonts["Mono-medium"].render(body.name, True, c.WHITE)
                            self.screen.blit(star_name, (x, y - body.radius - self.grid_size))

            self.add_location_text()

            # Update the display
            self.win.blit(pygame.transform.scale(self.screen, self.win.get_rect().size), (0, 0))
            pygame.display.update()

        pygame.quit()
        sys.exit()
