import random
import matplotlib.pyplot as plt
import numpy as np
random.seed(0)

def has_overlap(box1, box2):
    (x1, y1), (w1, h1) = box1
    (x2, y2), (w2, h2) = box2

    # Check if one rectangle is to the left of the other
    if x1 + w1*1.3 <= x2 or x2 + w2*1.3 <= x1:
        return False

    # Check if one rectangle is above the other
    if y1 + h1*1.3 <= y2 or y2 + h2*1.3 <= y1:
        return False

    # If both conditions are false, the rectangles overlap
    return True


def generate_box_inside(field, box_dims):
    output = tuple(zip(*(
        [random.randint(low, high-box_dim), box_dim]
        for low, high, box_dim in zip(*field, box_dims)
    )))
    return output


def generate_box(field, box_dims_list):
    non_overlapping_boxes = []
    for box_dims in box_dims_list:
        for _ in range(100):  # Make 100 attempts before giving up
            box = generate_box_inside(field, box_dims)
            if all(not has_overlap(box, prev_box) for prev_box in non_overlapping_boxes):
                non_overlapping_boxes.append(box)
                break
            print("box", box, "Overlapped detected in bounding boxes! Retrying...")

    if len(non_overlapping_boxes) < len(box_dims_list):
        print("Couldn't generate all non-overlapping boxes.")
        return None

    return non_overlapping_boxes


def plot_rectangles(image, rectangles):
    fig, ax = plt.subplots()
    ax.imshow(image)

    for rect in rectangles:
        (x, y), (w, h) = rect
        ax.add_patch(plt.Rectangle((x, y), w, h, edgecolor='r', fill=False))

    plt.show()



if __name__ == '__main__':
    # Example usage
    field = ((0, 0), (100, 200))
    box_dims_list = [(10, 50), (20, 30), (40, 20)]  # Each tuple represents (width, height) for a box

    # Generating rectangles (you need to implement generate_box function)
    rectangles = generate_box(field, box_dims_list)

    # Sample image (replace with your image)
    image = np.ones((200, 100, 3), dtype=np.uint8) * 255  # White image, you should replace this with your image

    plot_rectangles(image, rectangles)