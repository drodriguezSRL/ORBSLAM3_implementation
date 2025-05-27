import numpy as np
import cv2

def stereo_rectification_to_orbslam_yaml_format(K1, D1, K2, D2, R, T, image_size):
    """
    K1, K2: Intrinsic matrices (3x3)
    D1, D2: Distortion coefficients (1x5 or 1x8)
    R, T: Rotation and translation from left to right camera
    image_size: (width, height)
    """
    width, height = image_size

    # Stereo rectification
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
        K1, D1, K2, D2, (width, height), R, T,
        flags=cv2.CALIB_ZERO_DISPARITY, alpha=0
    )

    def format_matrix_cv_yaml(name, M, dtype='d'):
        flat = M.flatten()
        return f"""{name}: !!opencv-matrix
   rows: {M.shape[0]}
   cols: {M.shape[1]}
   dt: {dtype}
   data: [{', '.join(f"{v:.15g}" for v in flat)}]
"""

    # Format output
    output = ""
    output += format_matrix_cv_yaml("LEFT.R", R1)
    output += format_matrix_cv_yaml("LEFT.P", P1)
    output += format_matrix_cv_yaml("RIGHT.R", R2)
    output += format_matrix_cv_yaml("RIGHT.P", P2)
    return output

# --- inputs (replace with your calibration) ---
K1 = np.array([[262.28277587890625, 0, 327.2907409667969],
               [0, 262.28277587890625, 177.83383178710938],
               [0, 0, 1]])
D1 = np.array([-0.28340811, 0.07395907, 0.00019359, 1.76187114e-05, 0.0])

K2 = np.array([[262.28277587890625, 0, 327.2907409667969],
               [0, 262.28277587890625, 177.83383178710938],
               [0, 0, 1]])
D2 = np.array([-0.28368365, 0.07451284, -0.00010473, -3.555907e-05, 0.0]) # lens distortion coefficients

R = np.array([[1.00, 0.00, 0.00],
              [0.00, 1.0, 0.00],
              [0.00, 0.00, 1.0]]) # rotation matrix 

T = np.array([-0.12, 0.0, 0.0])  # 12cm baseline

image_size = (640, 360)  # width, height

# --- Run ---
yaml_output = stereo_rectification_to_orbslam_yaml_format(K1, D1, K2, D2, R, T, image_size)
print(yaml_output)
