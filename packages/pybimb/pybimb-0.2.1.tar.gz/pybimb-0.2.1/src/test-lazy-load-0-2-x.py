import time

import bimb
import numpy as np
import torch
import torchvision
import torchvision.transforms as transforms

print("=" * 60)
print("LAZY DATALOADER ITERATION COMPARISON")
print("=" * 60)

BATCH_SIZE = 512
DATA_PATH = "./data/cifar-10-jpg"
PYTORCH_ROOT = "./data"
SEMVER = "v0.2.1"

# ============= BIMB LAZY (NCHW) =============
print(f"\n[BIMB {SEMVER} (Rust) - f32, NCHW]")
try:
    # 1. Initialization
    bimb_loader_nchw = bimb.BimbLoader(DATA_PATH)
    bimb_loader_nchw.shuffle()
    print(f"✓ BimbLoader initialized. Found {len(bimb_loader_nchw)} images.")

    # 2. Iteration (This is the part we time)
    print(f"Starting lazy iteration (batch_size={BATCH_SIZE})...")
    start = time.time()
    count_nchw = 0
    while True:
        batch_data = bimb_loader_nchw.get_next_batch(BATCH_SIZE)
        if batch_data is None:
            break  # Epoch finished

        numpy_array, labels = batch_data

        # This is the "fair" comparison, adding the permute cost
        if numpy_array.shape[0] > 0:
            tensor = torch.from_numpy(numpy_array)

        count_nchw += numpy_array.shape[0]

    bimb_lazy_time_nchw = time.time() - start
    print(
        f"✓ Bimb loaded {count_nchw} images (float32, CHW): {bimb_lazy_time_nchw:.3f}s"
    )

except Exception as e:
    print(f"ERROR: Bimb NCHW test failed: {e}")
    bimb_lazy_time_nchw = 0
    count_nchw = 0


# ============= PYTORCH LOADER =============
print("\n[PYTORCH STANDARD LOADER]")
transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ]
)

try:
    trainset = torchvision.datasets.CIFAR10(
        root=PYTORCH_ROOT, train=True, download=True, transform=transform
    )
    testset = torchvision.datasets.CIFAR10(
        root=PYTORCH_ROOT, train=False, download=True, transform=transform
    )

    full_dataset = torch.utils.data.ConcatDataset([trainset, testset])
    loader = torch.utils.data.DataLoader(
        full_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,  # Fair comparison to our .shuffle()
        num_workers=8,
        pin_memory=False,
        persistent_workers=True,
    )

    print(
        f"Starting PyTorch lazy iteration (num_workers=8, batch_size={BATCH_SIZE})..."
    )
    start = time.time()
    count_torch = 0
    for batch, _ in loader:
        count_torch += batch.size(0)
    pytorch_time = time.time() - start
    print(f"✓ PyTorch loaded {count_torch} images (float32, CHW): {pytorch_time:.3f}s")

except Exception as e:
    print(f"ERROR: PyTorch test failed: {e}")
    pytorch_time = 0
    count_torch = 0


# ============= COMPARISON =============
print("\n" + "=" * 60)
print("LAZY ITERATION RESULTS")
print("=" * 60)
if count_nchw > 0:
    print(
        f"bimb {SEMVER} (f32, NCHW):       {bimb_lazy_time_nchw:.3f}s ({count_nchw / bimb_lazy_time_nchw:.0f} img/s)"
    )
if count_torch > 0:
    print(
        f"PyTorch (NCHW):  {pytorch_time:.3f}s ({count_torch / pytorch_time:.0f} img/s)"
    )

if bimb_lazy_time_nchw > 0 and pytorch_time > 0:
    speedup_fair = pytorch_time / bimb_lazy_time_nchw
    print(f"\nSpeedup (bimb NCHW / PyTorch): {speedup_fair:.2f}x")
print("=" * 60)
