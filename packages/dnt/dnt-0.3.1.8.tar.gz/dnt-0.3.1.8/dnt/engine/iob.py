import numpy as np

def iob(box_a:np.ndarray, box_b:np.ndarray)->tuple:
    """
    Calculate the Intersection over Box (IoB) between two bounding boxes.

    Parameters:
        box_a -- numpy arrays of shape (4,) containing [l, t, w, h]
        box_b -- numpy arrays of shape (4,) containing [l, t, w, h], target bounding box

    Returns:
    iob, iob -- float, the IoB values for box_a and box_b
    """
    # Determine the (x, y)-coordinates of the intersection rectangle
    x_l = max(box_a[0], box_b[0])
    y_t = max(box_a[1], box_b[1])
    x_r = min(box_a[0]+box_a[2], box_b[0]+box_b[2])
    y_b = min(box_a[1]+box_a[3], box_b[1]+box_b[3])
    
    # Compute the area of intersection rectangle
    inter_width = max(0, x_r - x_l)
    inter_height = max(0, y_b - y_t)
    inter_area = inter_width * inter_height
    
    # Compute the area of both the prediction and ground-truth rectangles
    box_a_area = box_a[2] * box_a[3]
    box_b_area = box_b[2] * box_b[3]
    
    # Compute the intersection over union by taking the intersection area and dividing it by the sum of prediction + ground-truth areas - the intersection area
    iob_a = inter_area / box_a_area if box_a_area != 0 else 0.0
    iob_b = inter_area / box_b_area if box_b_area != 0 else 0.0
    
    return iob_a, iob_b

def iobs(alrbs:np.ndarray, blrbs:np.ndarray)->np.ndarray:
    """
    Calculate the IoU matrix for multiple bounding boxes.

    Parameters:
    boxes -- numpy array of shape (N, 4), where N is the number of boxes, and each row is [x1, y1, x2, y2]

    Returns:
    iou_matrix -- numpy array of shape (N, N), where iou_matrix[i, j] is the IoU between boxes[i] and boxes[j]
    """
    num_a = alrbs.shape[0]
    num_b = blrbs.shape[0]
    iobs_a = np.zeros((num_a, num_b))
    iobs_b = np.zeros((num_a, num_b))

    for i in range(num_a):
        for j in range(num_b):
            iobs_a[i, j], iobs_b[i, j] = iob(alrbs[i,:], blrbs[j,:])
            
    return iobs_a, iobs_b

if __name__ == '__main__':
    # Example usage
    boxes = np.array([
        [0, 0, 1, 1],
        [0.5, 0.5, 1.5, 1.5],
        [1, 1, 2, 2]
    ])

    matrix_a, matrix_b = iobs(boxes, boxes)
    print(matrix_a)
    print(matrix_b)