class Point:
    """Класс точки."""
    def __init__(self, x, y):
        """Конструктор класса точки."""
        self.x = x
        self.y = y
        
    def __repr__(self):
        """Строковое представление экземпляра класса"""
        return f"Точка: ({self.x}, {self.y})"

class QuadTree:
    """Класс квадродерева."""
    pass