import pygame


class Window:
    def __init__(self, width: int, height: int, title: str):
        self.__width = width
        self.__height = height
        self.__title = title
        self.__screen = pygame.display.set_mode(
            (
                self.__width,
                self.__height,
            ),
        )
        pygame.display.set_caption(self.__title)

    def append_title(self, string: str) -> None:
        pygame.display.set_caption(f"{self.__title} - {string}")

    def reset_title(self) -> None:
        pygame.display.set_caption(self.__title)

    def get_screen(self) -> pygame.display:
        return self.__screen

    def flip(self) -> None:
        pygame.display.flip()

    def update(self) -> None:
        pygame.display.update()

    def capture_to_string(self) -> str:
        return pygame.image.tostring(self.__screen, "RGBA")

    def fill(self, colour: tuple) -> None:
        self.__screen.fill(colour)
