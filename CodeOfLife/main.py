import pygame
import numpy as np
from tools.colour import Colour
from tools.window import Window
from tools.recorder import Recorder
from threading import Thread, Lock

SIZE = 5
WIDTH, HEIGHT = 800, 600
BACKGROUND = Colour.BLACK
FPS = 60
dt = 2


def generate_pos(n):
    init_x_pos = np.random.randint(0, WIDTH, (n))
    init_y_pos = np.random.randint(0, HEIGHT, (n))
    return zip(init_x_pos, init_y_pos)


class Particle:
    def __init__(
        self,
        pos=(0, 0),
        vel=(0, 0),
        colour=Colour.WHITE,
        size=SIZE,
        mass=1,
        max_v=np.inf,
    ):
        self.__x, self.__y = pos
        self.__vx, self.__vy = vel
        self.__colour = colour
        self.__size = size
        self.__mass = mass
        self.__max_v = max_v
        self.__lock = Lock()
        self.__fx = 0
        self.__fy = 0

    def __str__(self):
        return (
            f"Particle(pos=({self.__x}, {self.__y}), m={self.__mass}, s={self.__size})"
        )

    def __repr__(self):
        return self.__str__()

    def get_mass(self):
        return self.__mass

    def get_pos(self):
        return (self.__x, self.__y)

    def get_vel(self):
        return (self.__vx, self.__vy)

    def draw(self, screen: pygame.display, with_size=False) -> None:
        x = int(self.__x)
        y = int(self.__y)

        if not with_size:
            screen.set_at((x, y), self.__colour)
            return

        pygame.draw.circle(
            screen,
            self.__colour,
            (x, y),
            self.__size,
        )

    def distance_components(self, particle) -> tuple:
        px, py = particle.get_pos()
        dx = self.__x - px
        dy = self.__y - py
        return dx, dy

    def update_force(self, force=(0, 0)) -> None:
        fx, fy = force
        with self.__lock:
            self.__fx += fx
            self.__fy += fy

    def update_vel(self) -> None:
        self.__vx += self.__fx * dt / self.__mass
        self.__vy += self.__fy * dt / self.__mass
        self.__fx, self.__fy = 0, 0

    def update_pos(self):
        self.__vx *= 0.5
        self.__vy *= 0.5

        if any([abs(self.__vx) > self.__max_v, abs(self.__vy) > self.__max_v]):
            v = np.linalg.norm([self.__vx, self.__vy])
            if v > self.__max_v:
                self.__vx *= self.__max_v / v
                self.__vy *= self.__max_v / v

        self.__x += self.__vx * dt
        self.__y += self.__vy * dt

        if self.__x < 0:
            self.__x *= -1
            self.__vx *= -1
        elif self.__x > WIDTH:
            self.__x = 2 * WIDTH - self.__x
            self.__vx *= -1
        if self.__y < 0:
            self.__y *= -1
            self.__vy *= -1
        elif self.__y > HEIGHT:
            self.__y = 2 * HEIGHT - self.__y
            self.__vy *= -1


def iterations(particle1: Particle, particles2: list, g: float) -> None:
    influence = 80
    fx, fy = 0, 0
    for particle2 in particles2:
        if particle1 == particle2:
            continue
        dx, dy = particle1.distance_components(particle2)
        if abs(dx) > influence or abs(dy) > influence:
            continue
        d = np.linalg.norm((dx, dy))
        if d > influence:
            continue
        F = g * particle1.get_mass() * particle2.get_mass() / d
        fx += F * dx
        fy += F * dy
    particle1.update_force((fx, fy))


def rule(particles1: list, particles2: list, g=-1.0) -> None:
    rule_threads = []
    for particle1 in particles1:
        thread = Thread(
            target=iterations,
            args=(particle1, particles2, g),
        )
        rule_threads.append(thread)
        thread.start()

    for thread in rule_threads:
        thread.join()


def create_particles(n, **kwargs):
    return [Particle(pos=(x, y), **kwargs) for x, y in generate_pos(n)]


class CodeOfLife:
    def __init__(
        self,
        width=WIDTH,
        height=HEIGHT,
    ):
        self.__width = WIDTH
        self.__height = HEIGHT
        self.__particles = dict()
        self.initialise()
        self.__policies = list()

    def add_particles(self, name, particle_list: list) -> None:
        self.__particles[name] = particle_list

    def initialise(self):
        pygame.init()
        title = self.get_title()
        self.__window = Window(self.__width, self.__height, title)

    def get_title(self):
        return self.__class__.__qualname__

    def add_policy(self, policy, set1Name, set2Name, g=-1):
        set1 = self.__particles[set1Name]
        set2 = self.__particles[set2Name]
        self.__policies.append({"target": policy, "args": (set1, set2, g)})

    def update(self):
        policy_threads = list()
        for policy in self.__policies:
            thread = Thread(**policy)
            policy_threads.append(thread)
            thread.start()

        for thread in policy_threads:
            thread.join()

    def run(self, recorder=None):
        self.__window.flip()
        self.__window.update()

        clock = pygame.time.Clock()

        running = False
        record = False

        particles = list()
        for val in self.__particles.values():
            particles += list(val)

        while True:
            clock.tick(FPS)

            if record and recorder:
                self.__window.append_title("Recording")
            else:
                self.__window.reset_title()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if recorder:
                        self.__window.append_title("Saving... Please wait...")
                        recorder.store()
                    pygame.quit()
                    return

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running = not running

                    elif event.key == pygame.K_r:
                        if recorder:
                            record = not record

                # if pygame.mouse.get_pressed()[0]:
                #     x, y = pygame.mouse.get_pos()
                #     self.__cells[y // self.__size, x // self.__size] = 1
                #     self.update()
                #     self.__window.update()

            self.__window.fill(BACKGROUND)

            if running:
                self.update()

                for particle in particles:
                    particle.update_vel()
                    particle.update_pos()
                    particle.draw(self.__window.get_screen(), with_size=True)

                self.__window.update()
                if record and recorder:
                    array2d = self.__window.capture_to_string()
                    recorder.capture(array2d, (self.__width, self.__height))


def main() -> None:
    game = CodeOfLife(width=WIDTH, height=HEIGHT)
    recorder = Recorder(
        game.get_title(),
        extension="gif",
        fps=FPS,
    )

    game.add_particles("yellow", create_particles(100, colour=Colour.YELLOW))
    game.add_particles("red", create_particles(50, colour=Colour.RED))
    game.add_particles("green", create_particles(50, colour=Colour.GREEN))

    m = 5
    game.add_policy(rule, "green", "green", -0.3 * m)
    game.add_policy(rule, "green", "red", -0.17 * m)
    game.add_policy(rule, "green", "yellow", 0.3 * m)
    game.add_policy(rule, "red", "red", -0.1 * m)
    game.add_policy(rule, "red", "green", -0.3 * m)
    game.add_policy(rule, "yellow", "yellow", 0.15 * m)
    game.add_policy(rule, "yellow", "green", -0.2 * m)
    # game.add_policy(rule, "yellow", "yellow", -0.15 * m)
    # game.add_policy(rule, "red", "yellow", -0.2 * m)
    # game.add_policy(rule, "yellow", "red", 0.2 * m)

    game.run(recorder=recorder)


if __name__ == "__main__":
    main()
