import pygame
from PIL import Image
import numpy as np

SIZE = 10
WIDTH, HEIGHT = (80, 60)
FPS = 60


class Recorder:
    def __init__(self, filename, extension="gif", fps=60):
        self.__extension = extension
        self.__filename = filename
        self.__duration = 1 / fps * 1000  # ms
        self.__fname = f"{self.__filename}.{self.__extension}"
        self.__images = list()

    def capture(self, img, size):
        self.__images.append(Image.frombytes("RGBA", size, img))

    def store(self):
        if len(self.__images) == 0:
            return
        self.__images[0].save(
            self.__fname,
            save_all=True,
            append_images=self.__images[1:],
            duration=self.__duration,
            loop=0,
        )


class Colour:
    BACKGROUND = (10, 10, 10)
    GRID = (40, 40, 40)
    DIE_NEXT = (170, 170, 170)
    ALIVE_NEXT = (255, 255, 255)


class ConwayGameOfLife:
    def __init__(self, width, height, size, fps=60):
        self.__fps = fps
        self.__width = width
        self.__height = height
        self.__size = size
        self.__cells = np.zeros((self.__height, self.__width))

        self.width = self.__width * self.__size
        self.height = self.__height * self.__size

        self.initialize()

    def initialize(self):
        pygame.init()
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode(
            (
                self.width,
                self.height,
            )
        )
        self.__screen.fill(Colour.GRID)
        self.update()

    def run(self, recorder=None):
        pygame.display.flip()
        pygame.display.update()

        running = False
        record = False

        while True:
            self.__clock.tick(self.__fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if recorder:
                        recorder.store()
                    pygame.quit()
                    return

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running = not running
                        self.update()
                        pygame.display.update()
                    elif event.key == pygame.K_r:
                        if recorder:
                            record = not record

                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.__cells[y // self.__size, x // self.__size] = 1
                    self.update()
                    pygame.display.update()

            self.__screen.fill(Colour.GRID)

            if running:
                self.__cells = self.update(with_progress=True)
                pygame.display.update()
                if record and recorder:
                    array2d = pygame.image.tostring(self.__screen, "RGBA")
                    recorder.capture(array2d, (self.width, self.height))

    def update(self, with_progress=False):
        updated_cells = np.zeros(self.__cells.shape)

        for row, col in np.ndindex(self.__cells.shape):
            alive = (
                np.sum(self.__cells[row - 1 : row + 2, col - 1 : col + 2])
                - self.__cells[row, col]
            )
            colour = (
                Colour.BACKGROUND if self.__cells[row, col] == 0 else Colour.ALIVE_NEXT
            )

            if self.__cells[row, col] == 1:
                if alive < 2 or alive > 3:
                    if with_progress:
                        colour = Colour.DIE_NEXT
                elif 2 <= alive <= 3:
                    updated_cells[row, col] = 1
                    if with_progress:
                        colour = Colour.ALIVE_NEXT
            else:
                if alive == 3:
                    updated_cells[row, col] = 1
                    if with_progress:
                        colour = Colour.ALIVE_NEXT

            pygame.draw.rect(
                self.__screen,
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
        "ConwayGameOfLife",
        extension="gif",
        fps=FPS,
    )
    game.run(recorder=recorder)


if __name__ == "__main__":
    main()
