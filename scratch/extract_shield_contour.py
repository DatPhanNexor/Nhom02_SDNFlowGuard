from PIL import Image
import numpy as np

img = Image.open(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\sdnflowguard-logo.png").convert("RGBA")
arr = np.array(img)
alpha = arr[:, :, 3]

# Find contour of alpha > 128
h, w = alpha.shape
print(f"Canvas size: {w}x{h}")

# Find top point
top_y = np.where(alpha > 128)[0][0]
top_xs = np.where(alpha[top_y, :] > 128)[0]
top_x = int(np.mean(top_xs))
print(f"Top crest: ({top_x}, {top_y})")

# Find bottom tip
bottom_y = np.where(alpha > 128)[0][-1]
bottom_xs = np.where(alpha[bottom_y, :] > 128)[0]
bottom_x = int(np.mean(bottom_xs))
print(f"Bottom tip: ({bottom_x}, {bottom_y})")

# Find left and right corners
left_x = np.where(alpha > 128)[1][0]
left_ys = np.where(alpha[:, left_x] > 128)[0]
left_y = int(np.mean(left_ys))
print(f"Left corner: ({left_x}, {left_y})")

right_x = np.where(alpha > 128)[1][-1]
right_ys = np.where(alpha[:, right_x] > 128)[0]
right_y = int(np.mean(right_ys))
print(f"Right corner: ({right_x}, {right_y})")

# Let's check the outline at intervals of y
print("\nShield outline profile (y, min_x, max_x, width):")
for y in range(top_y, bottom_y + 1, 30):
    xs = np.where(alpha[y, :] > 128)[0]
    if len(xs) > 0:
        print(f"  y={y:3d}: x=[{xs[0]:3d}, {xs[-1]:3d}], w={xs[-1]-xs[0]:3d}, center={(xs[0]+xs[-1])/2:.1f}")
