import pygame
import numpy as np
from tools.recorder import Recorder
from tools.window import Window
from tools.colour import Colour

SIZE = 10
WIDTH, HEIGHT = (80, 60)
FPS = 60

ALIVE_NEXT = Colour.WHITE
DIE_NEXT = Colour.LIGHT_GRAY
GRID = Colour.GRAY
BACKGROUND = Colour.DARK_GRAY


class ConwayGameOfLife:
    def __init__(self, width, height, size, fps=60):
        self.__fps = fps
        self.__width = width
        self.__height = height
        self.__size = size
        self.__cells = np.zeros((self.__height, self.__width))

        self.__width = self.__width * self.__size
        self.__height = self.__height * self.__size

        self.initialize()

    def initialize(self):
        pygame.init()
        title = self.get_title()
        self.__window = Window(self.__width, self.__height, title)
        self.__window.fill(GRID)
        self.update()

    def get_title(self):
        return self.__class__.__qualname__

    def run(self, recorder=None):
        self.__window.flip()
        self.__window.update()

        clock = pygame.time.Clock()

        running = False
        record = False

        while True:
            clock.tick(self.__fps)
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
                        self.update()
                        self.__window.update()
                    elif event.key == pygame.K_r:
                        if recorder:
                            record = not record

                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.__cells[y // self.__size, x // self.__size] = 1
                    self.update()
                    self.__window.update()

            self.__window.fill(GRID)

            if running:
                self.__cells = self.update(with_progress=True)
                self.__window.update()
                if record and recorder:
                    array2d = self.__window.capture_to_string()
                    recorder.capture(array2d, (self.__width, self.__height))

    def update(self, with_progress=False):
        updated_cells = np.zeros(self.__cells.shape)

        for row, col in np.ndindex(self.__cells.shape):
            alive = (
                np.sum(self.__cells[row - 1 : row + 2, col - 1 : col + 2])
                - self.__cells[row, col]
            )
            colour = BACKGROUND if self.__cells[row, col] == 0 else ALIVE_NEXT

            if self.__cells[row, col] == 1:
                if alive < 2 or alive > 3:
                    if with_progress:
                        colour = DIE_NEXT
                elif 2 <= alive <= 3:
                    updated_cells[row, col] = 1
                    if with_progress:
                        colour = ALIVE_NEXT
            else:
                if alive == 3:
                    updated_cells[row, col] = 1
                    if with_progress:
                        colour = ALIVE_NEXT

            pygame.draw.rect(
                self.__window.get_screen(),
                colour,
                (
                    col * self.__size,
                    row * self.__size,
                    self.__size - 1,
                    self.__size - 1,
                ),
            )

        return updated_cells


def main():
    game = ConwayGameOfLife(WIDTH, HEIGHT, SIZE)
    recorder = Recorder(
        game.get_title(),
        extension="gif",
        fps=FPS,
    )
    game.run(recorder=recorder)


if __name__ == "__main__":
    main()
