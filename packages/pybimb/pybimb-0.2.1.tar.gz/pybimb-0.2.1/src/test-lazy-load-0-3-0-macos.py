import time
from itertools import islice  # Used for a fair comparison

import bimb
import numpy as np
import torch
import torchvision
import torchvision.transforms as transforms

# ============================================
# ALL DEFINITIONS GO HERE (at the top level)
# ============================================

print("=" * 60)
print("LAZY DATALOADER (PREFETCHING) ITERATION COMPARISON")
print("=" * 60)

# ============================================
# ALL EXECUTION CODE MUST GO INSIDE THIS BLOCK
# (This is CRITICAL for macOS/Windows multiprocessing)
# ============================================

if __name__ == "__main__":
    # --- Benchmark Parameters ---
    BATCH_SIZE = 512
    DATA_PATH = "./data/cifar-10-jpg"  # Path to all 60k images
    PYTORCH_ROOT = "./data"
    SEMVER = "v0.3.0-prefetch"
    PREFETCH_FACTOR = 16  # How many batches for Rust to pre-load
    NUM_WORKERS = 8  # Workers for PyTorch

    # ============= BIMB LAZY (NCHW) =============
    # We will only test the "fair" NCHW case now
    print(f"\n[BIMB {SEMVER} (Rust) - f32, NCHW]")
    try:
        # 1. Initialization
        # This now takes all parameters and spawns the background thread
        print(
            f"Initializing BimbLoader(prefetch_factor={PREFETCH_FACTOR}, batch_size={BATCH_SIZE})..."
        )
        bimb_loader = bimb.BimbLoader(
            DATA_PATH,
            batch_size=BATCH_SIZE,
            prefetch_factor=PREFETCH_FACTOR,
            shuffle=True,
        )
        print(f"✓ BimbLoader initialized. Found {len(bimb_loader)} images.")
        print(f"  Class map: {bimb_loader.class_map}")

        # 2. Iteration (This is the part we time)
        print(f"Starting lazy iteration + permute...")
        start = time.time()
        count_nchw = 0

        # We must calculate how many batches to pull for one epoch
        num_batches = (len(bimb_loader) + BATCH_SIZE - 1) // BATCH_SIZE

        # We now loop `num_batches` times and pull from the prefetch queue
        for _ in range(num_batches):
            # The new get_next_batch() takes no arguments
            # It just pulls a pre-made batch from the "bucket"
            batch_data = bimb_loader.get_next_batch()

            if batch_data is None:
                print(
                    "WARNING: BimbLoader stopped early. Did the producer thread panic?"
                )
                break  # Epoch finished early

            numpy_array, labels = batch_data

            # This is the "fair" comparison, adding the permute cost
            if numpy_array.shape[0] > 0:
                tensor = torch.from_numpy(numpy_array).permute(0, 3, 1, 2)

            count_nchw += numpy_array.shape[0]

        bimb_lazy_time_nchw = time.time() - start
        print(
            f"✓ Bimb loaded + permuted {count_nchw} images (float32, CHW): {bimb_lazy_time_nchw:.3f}s"
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
            shuffle=True,
            num_workers=NUM_WORKERS,
            persistent_workers=True,
        )

        print(
            f"Starting PyTorch lazy iteration (num_workers={NUM_WORKERS}, batch_size={BATCH_SIZE})..."
        )
        start = time.time()
        count_torch = 0
        # We use islice to ensure we iterate the same number of batches
        for batch, _ in islice(loader, num_batches):
            count_torch += batch.size(0)
        pytorch_time = time.time() - start
        print(
            f"✓ PyTorch loaded {count_torch} images (float32, CHW): {pytorch_time:.3f}s"
        )

    except Exception as e:
        print(f"ERROR: PyTorch test failed: {e}")
        pytorch_time = 0
        count_torch = 0

    # ============= COMPARISON =============
    print("\n" + "=" * 60)
    print("LAZY (PREFETCHING) ITERATION RESULTS")
    print("=" * 60)
    if count_nchw > 0:
        print(
            f"bimb {SEMVER} (f32, NCHW): {bimb_lazy_time_nchw:.3f}s ({count_nchw / bimb_lazy_time_nchw:.0f} img/s)"
        )
    if count_torch > 0:
        print(
            f"PyTorch (standard, NCHW):  {pytorch_time:.3f}s ({count_torch / pytorch_time:.0f} img/s)"
        )

    if bimb_lazy_time_nchw > 0 and pytorch_time > 0:
        speedup_fair = pytorch_time / bimb_lazy_time_nchw
        print(f"\nSpeedup (bimb NCHW / PyTorch): {speedup_fair:.2f}x")
    print("=" * 60)
