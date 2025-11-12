import bimb # :)
import numpy as np
import torch
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# The path to your CIFAR-10 data
DATA_PATH = "/home/dnp/7karni/bimb/data/cifar-10-jpg/"

print("Calling Rust...")
start = time.time()

# 1. Call your Rust function
#    This runs your *entire* parallel pipeline
raw_data, shape = bimb.load_images_raw(DATA_PATH)

end = time.time()
print(f"Rust loading, decoding, and conversion took: {end - start:.4f}s")
print(f"Received shape: {shape}")

# 2. Wrap the raw buffer in NumPy (zero-copy)
#    np.frombuffer is the magic glue
numpy_array = np.frombuffer(raw_data, dtype=np.uint8).reshape(shape).copy()

# 3. Convert to PyTorch (zero-copy)
tensor = torch.from_numpy(numpy_array)

print(f"PyTorch tensor shape: {tensor.shape}")

# --- Victory Lap ---
print("Displaying first image from the tensor...")
# Select the first image
first_image_tensor = tensor[0]

# Convert tensor (H, W, C) to a NumPy array for matplotlib
plt.imshow(first_image_tensor.numpy())
plt.title("From Rust to Python to this here PNG!")
plt.savefig('rust-python-disk.png')
print("image saved")
plt.show()
