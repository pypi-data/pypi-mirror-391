import bimb
import numpy as np
import torch
import torchvision
import torchvision.transforms as transforms
import time

print("=" * 60)
print("EAGER FULL DATASET LOAD COMPARISON")
print("=" * 60)

# ============= BIMB =============
semver = "v0.1.4"
print("\n bimb " + semver + " - [f32]")
_, _, _, _ = bimb.load_images_raw("./data/cifar-10-jpg") #heat cache
print("\n cache hot, starting timer")
start = time.time()
buffer_f32, shape,labels,class_map = bimb.load_images_raw("./data/cifar-10-jpg")
numpy_array = buffer_f32.reshape(shape)
rust_time_raw = time.time() - start
print(f"✓ Bimb loaded {shape[0]} images (f32, HWC): {rust_time_raw:.3f}s")
print(f"✓ Data received: {len(labels)} labels, {len(class_map)} classes.")
print(f"✓ Class map: {class_map}")

# Transform to NCHW (same as PyTorch output)
print("\n bimb " + semver + " - [f32] + transform to NCHW")
_, _, _, _ = bimb.load_images_raw("./data/cifar-10-jpg") #heat cache
print("\n cache hot, starting timer")
start = time.time()
buffer_f32, shape, labels, class_map= bimb.load_images_raw("./data/cifar-10-jpg")
numpy_array = buffer_f32.reshape(shape)
# Transpose NHWC -> NCHW
tensor = torch.from_numpy(numpy_array).permute(0, 3, 1, 2)
rust_time_converted = time.time() - start
print(f"✓ Bimb loaded + permuted {shape[0]} images (float32, CHW): {rust_time_converted:.3f}s")

# ============= PYTORCH LOADER =============
print("\n[PYTORCH STANDARD LOADER]")
transform = transforms.Compose([transforms.ToTensor()])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=False, transform=transform)
testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=False, transform=transform)

full_dataset = torch.utils.data.ConcatDataset([trainset, testset])
loader = torch.utils.data.DataLoader(
    full_dataset,
    batch_size=512,
    shuffle=False,
    num_workers=8,
    pin_memory=False,
    persistent_workers=False,
)

start = time.time()
count = 0
for batch, _ in loader:
    count += batch.size(0)
pytorch_time = time.time() - start
print(f"✓ PyTorch loaded {count} images (float32, CHW): {pytorch_time:.3f}s")

# ============= COMPARISON =============
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"bimb {semver} (f32 normalized, raw):     {rust_time_raw:.3f}s  ({shape[0]/rust_time_raw:.0f} img/s)")
print(f"bimb {semver} (f32 normalized, NCHW):    {rust_time_converted:.3f}s  ({shape[0]/rust_time_converted:.0f} img/s)")
print(f"PyTorch (standard):             {pytorch_time:.3f}s  ({count/pytorch_time:.0f} img/s)")

speedup_raw = pytorch_time / rust_time_raw
speedup_fair = pytorch_time / rust_time_converted

print(f"\nSpeedup (NHWC): {speedup_raw:.2f}x")
print(f"Speedup (NCHW): {speedup_fair:.2f}x")
print("=" * 60)
