"""Реализация квадродерева"""

import threading

from PIL import Image
from typing import Optional, Union

MAX_DEPTH = 8  # Максимальная глубина узла
ERROR_THRESHOLD = 13  # Порог значения

class Point:
    """Класс точки."""

    def __init__(self, x: int, y: int) -> None:
        """
        Конструктор класса точки.
        :param x: Координата x
        :param y: Координата y
        :return: None
        """
        self.x = x
        self.y = y

    def __eq__(self, another: "Point") -> bool:
        """
        Сравнение двух точек.
        :param another: Точка для сравнения
        :return: Результат сравнения
        """
        return self.x == another.y and self.y == another.y

    def __repr__(self) -> str:
        """
        Строковое представление точки.
        :return: строковое представление точки
        """
        return f"Точка: ({self.x}, {self.y})"


def weighted_average(hist: list[int]) -> Union[int, float]:
    """
    Возвращает взвешенное среднее значение цвета и
    ошибку из гистограммы пикселей.
    :param hist: список количества пикселей для каждого диапазона.
    :return: взвешенное среднее значение цвета и ошибку
    """
    total = sum(hist)
    value, error = 0, 0
    if total > 0:
        value = sum(i * x for i, x in enumerate(hist)) / total
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
        error = error ** 0.5
    return value, error


def color_from_histogram(hist: list[int]) -> Union[tuple[int], float]:
    """
    Возвращает средний цвет RGB из заданной гистограммы количества цветов пикселей.
    :param hist: список количества пикселей для каждого диапазона.
    :return: средний цвет и ошибку.
    """
    red, red_error = weighted_average(hist[:256])
    green, green_error = weighted_average(hist[256:512])
    blue, blue_error = weighted_average(hist[512:768])
    error = red_error * 0.2989 + green_error * 0.5870 + blue_error * 0.1140
    return (int(red), int(green), int(blue)), error


class QuadtreeNode:
    """
    Класс, отвечающий за узел квадродерева, 
    который содержит секцию изображения и информацию о ней.
    """

    def __init__(self, image: Image, border_box: tuple[int],
                 depth: int) -> None:
        """
        Конструктор класса.
        :param image: изображение
        :param border_box: координатная область
        :param depth: глубина
        :return: None
        """
        self.__border_box = border_box  # регион копирования
        self.__depth = depth
        self.__childrens = None  # top left, top right, bottom left, bottom right
        self.__is_leaf = False
        self.__node_points = []

        left_right = self.__border_box[0] + (self.__border_box[2] - self.__border_box[0]) / 2
        top_bottom = self.__border_box[1] + (self.__border_box[3] - self.__border_box[1]) / 2

        self.__node_center_point = Point(left_right, top_bottom)

        # Обрезка части изображения по координатам
        image = image.crop(border_box)
        # Метод histogram возвращает список количества пикселей
        # для каждого диапазона, присутствующего на изображении.
        # В списке будут объединены все подсчеты для каждого диапазона.
        # Для RGB изображения для каждого цвета будет возвращен
        # список количества пикселей, суммарно 768.
        # Другими словами, метод дает информацию о том, сколько красных,
        # зелёных и синих пикселей присутствует в изображении для каждых
        # 256 типо красного, 256 типов зеленого и 256 синего.
        hist = image.histogram()
        self.__average_color, self.__error = color_from_histogram(
            hist)  # (r, g, b), error

    @property
    def depth(self) -> int:
        """
        Возвращает значение глубины.
        :return: глубина.
        """
        return self.__depth
    
    @property
    def node_center_point(self) -> int:
        """
        Возвращает координаты центральной точки узла.
        :return: глубина.
        """
        return self.__node_center_point
    
    @property
    def node_points(self) -> list[Point]:
        """
        Возвращает список точек узла.
        :return: глубина.
        """
        return self.__node_points

    @property
    def error(self) -> float:
        """
        Возвращает значения ошибки
        :return: значение ошибки
        """
        return self.__error

    @property
    def average_color(self) -> tuple[int, int, int]:
        """
        Возвращает значения цвета
        :return: значение цвета
        """
        return self.__average_color

    @property
    def childrens(self) -> Optional[list]:
        """Возвращение дочерних узлов."""
        return self.__childrens

    @property
    def border_box(self) -> tuple[int]:
        """Возвращает граничные точек."""
        return self.__border_box

    @property
    def is_leaf(self) -> bool:
        """Является ли узел листом или нет."""
        return self.__is_leaf

    @is_leaf.setter
    def is_leaf(self, value: bool) -> None:
        """Квадрант становится листом."""
        self.__is_leaf = value

    def split(self, image: Image) -> None:
        """
        Разбивает данную секцию изображения на четыре равных блока.
        :param image: изображение
        :return: None
        """
        
        left, top, right, bottom = self.__border_box

        top_left = QuadtreeNode(image, (left, top, self.__node_center_point.x, self.__node_center_point.y),
                                self.__depth + 1)
        top_right = QuadtreeNode(image, (self.__node_center_point.x, top, right, self.__node_center_point.y),
                                 self.__depth + 1)
        bottom_left = QuadtreeNode(image,
                                   (left, self.__node_center_point.y, self.__node_center_point.x, bottom),
                                   self.__depth + 1)
        bottom_right = QuadtreeNode(image,
                                    (self.__node_center_point.x, self.__node_center_point.y, right, bottom),
                                    self.__depth + 1)

        self.__childrens = [top_left, top_right, bottom_left, bottom_right]

    def insert_point_into_node() -> None:
        """
        Вставка точки в узел
        """


class QuadTree:
    """Класс квадродерева."""

    def __init__(self, image: Image) -> None:
        self.__width, self.__height = image.size
        self.__root = QuadtreeNode(image, image.getbbox(), 0)

        # остлеживает максимальную глубину, достигнутую рекурсией
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


