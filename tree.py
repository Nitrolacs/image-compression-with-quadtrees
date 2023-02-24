import threading

from PIL import Image
from typing import Optional

MAX_DEPTH = 8
ERROR_THRESHOLD = 13


class Point:
    """Класс точки."""

    def __init__(self, x, y) -> None:
        """Конструктор класса точки."""
        self.x = x
        self.y = y

    def __eq__(self, another: "Point") -> bool:
        return self.x == another.y and self.y == another.y

    def __repr__(self) -> str:
        """Строковое представление экземпляра класса"""
        return f"Точка: ({self.x}, {self.y})"


def weighted_average(hist):
    """Возвращает взвешенное среднее значение цвета и
    ошибку из гистограммы пикселей."""
    total = sum(hist)
    value, error = 0, 0
    if total > 0:
        value = sum(i * x for i, x in enumerate(hist)) / total
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
        error = error ** 0.5
    return value, error


def color_from_histogram(hist):
    """Возвращает средний цвет RGB из заданной гистограммы количества цветов пикселей."""
    r, re = weighted_average(hist[:256])
    g, ge = weighted_average(hist[256:512])
    b, be = weighted_average(hist[512:768])
    e = re * 0.2989 + ge * 0.5870 + be * 0.1140
    return (int(r), int(g), int(b)), e


class QuadtreeNode:
    """
    Узел квадродерева, который содержит секцию изображения и информацию о ней.
    """

    def __init__(self, image: Image, border_box: tuple[int],
                 depth: int) -> None:
        self.__border_box = border_box  # регион копирования
        self.__depth = depth
        self.__childrens = None  # top left, top right, bottom left, bottom right
        self.__is_leaf = False

        # Обрезка части изображения по координатам
        image = image.crop(border_box)
        hist = image.histogram()
        self.__average_color, self.__error = color_from_histogram(
            hist)  # (r, g, b), error

    @property
    def depth(self) -> int:
        """Возврат глубины."""
        return self.__depth

    @property
    def error(self) -> float:
        return self.__error

    @property
    def average_color(self) -> tuple[int, int, int]:
        return self.__average_color

    @property
    def childrens(self) -> Optional[list]:
        """Возвращение дочерних узлов."""
        return self.__childrens

    @property
    def border_box(self) -> tuple[int]:
        """Возврат граничных точек."""
        return self.__border_box

    @property
    def is_leaf(self) -> bool:
        """Является ли квадрант листом или нет."""
        return self.__is_leaf

    @is_leaf.setter
    def is_leaf(self, value: bool) -> None:
        """Квадрант становится листом."""
        self.__is_leaf = value

    def split(self, image: Image) -> None:
        """Разбивает данную секцию изображения на четыре равных блока."""
        left, top, right, bottom = self.__border_box

        left_right = left + (right - left) / 2
        top_bottom = top + (bottom - top) / 2

        top_left = QuadtreeNode(image, (left, top, left_right, top_bottom),
                                self.__depth + 1)
        top_right = QuadtreeNode(image, (left_right, top, right, top_bottom),
                                 self.__depth + 1)
        bottom_left = QuadtreeNode(image,
                                   (left, top_bottom, left_right, bottom),
                                   self.__depth + 1)
        bottom_right = QuadtreeNode(image,
                                    (left_right, top_bottom, right, bottom),
                                    self.__depth + 1)

        self.__childrens = [top_left, top_right, bottom_left, bottom_right]


class QuadTree:
    """Класс квадродерева."""

    def __init__(self, image: Image) -> None:
        self.__width, self.__height = image.size
        self.__root = QuadtreeNode(image, image.getbbox(), 0)

        # keep track of max depth achieved by recursion
        self.__max_depth = 0
        self.__build_tree(image, self.__root)


    @property
    def width(self) -> int:

        return self.__width

    @property
    def height(self) -> int:

        return self.__height

    def __build_tree(self, image: Image, node: QuadtreeNode) -> None:
        """
        Рекурсивно добавляет узлы, пока не будет достигнута максимальная глубина
        """
        if (node.depth >= MAX_DEPTH) or (node.error <= ERROR_THRESHOLD):
            if node.depth > self.__max_depth:
                self.__max_depth = node.depth
            node.is_leaf = True
            return

        node.split(image)

        threads = []
        for child in node.childrens:
            thread = threading.Thread(target=self.__build_tree,
                                      args=(image, child))

            thread.start()
            threads.append(thread)

        for process in threads:
            process.join()

        return None

    def get_leaf_nodes(self, depth: int) -> list:
        if depth > self.__max_depth:
            raise ValueError('Дана глубина больше, чем высота деревьев')

        leaf_nodes = []

        # рекурсивный поиск по квадродереву
        self.get_leaf_nodes_recursion(self.__root, depth, leaf_nodes)

        return leaf_nodes

    def get_leaf_nodes_recursion(self, node: QuadtreeNode, depth: int,
                                 leaf_nodes: list):
        """
        Рекурсивно получает листовые узлы в зависимости от того,
        является ли узел листом или достигнута заданная глубина.
        """
        if node.is_leaf is True or node.depth == depth:
            leaf_nodes.append(node)
        elif node.childrens is not None:
            for child in node.childrens:
                self.get_leaf_nodes_recursion(child, depth, leaf_nodes)


