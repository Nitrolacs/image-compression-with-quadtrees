from PIL import Image, ImageDraw

from tree import QuadTree, MAX_DEPTH


def create_image(quadtree: QuadTree, level: int, borders: bool) -> Image:
    # Создаём пустой холст изображения
    image = Image.new('RGB', (quadtree.width, quadtree.height))

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, quadtree.width, quadtree.height), (0, 0, 0))
    leaf_nodes = quadtree.get_leaf_nodes(level)

    for node in leaf_nodes:
        if borders:
            draw.rectangle(node.border_box, node.average_color,
                           outline=(0, 0, 0))
        else:
            draw.rectangle(node.border_box, node.average_color)

    return image


def compression_start(file: str, level: int, borders: bool) -> None:
    original_image = Image.open(file)
    quadtree = QuadTree(original_image)

    file_name = file[:-4]
    file_extension = file[len(file) - 3::]

    result_image = create_image(quadtree, level, borders)
    result_image.save(f"{file_name}_quadtree.{file_extension}")
