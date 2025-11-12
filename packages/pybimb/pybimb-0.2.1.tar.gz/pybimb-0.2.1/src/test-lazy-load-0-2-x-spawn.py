#!/usr/bin/env python3
"""
Cross-platform (macOS-safe) version of the lazy iteration benchmark.
Ensures torch DataLoader workers use "spawn" without crashing PyO3 modules.
"""

import multiprocessing as mp
import time

import bimb
import torch
import torchvision
import torchvision.transforms as transforms

print("=" * 60)
print("LAZY DATALOADER ITERATION COMPARISON (spawn)")
print("=" * 60)


def main():
    # --- Parameters ---
    BATCH_SIZE = 512
    DATA_PATH = "./data/cifar-10-jpg"
    PYTORCH_ROOT = "./data"
    SEMVER = "v0.2.1"
    NUM_WORKERS = 8

    # =====================================================
    # BIMB LAZY (Rust, NCHW)
    # =====================================================
    print(f"\n[BIMB {SEMVER} (Rust) - f32, NCHW]")
    try:
        bimb_loader_nchw = bimb.BimbLoader(DATA_PATH)
        bimb_loader_nchw.shuffle()
        print(f"✓ BimbLoader initialized. Found {len(bimb_loader_nchw)} images.")

        print(f"Starting lazy iteration (batch_size={BATCH_SIZE})...")
        start = time.time()
        count_nchw = 0

        while True:
            batch_data = bimb_loader_nchw.get_next_batch(BATCH_SIZE)
            if batch_data is None:
                break  # End of epoch
            numpy_array, labels = batch_data
            if numpy_array.shape[0] == 0:
                continue
            tensor = torch.from_numpy(numpy_array)  # already NCHW
            count_nchw += tensor.size(0)

        bimb_lazy_time = time.time() - start
        print(f"✓ BIMB loaded {count_nchw} images in {bimb_lazy_time:.3f}s")

    except Exception as e:
        print(f"ERROR: BIMB test failed: {e}")
        bimb_lazy_time = 0.0
        count_nchw = 0

    # =====================================================
    # PYTORCH STANDARD LOADER
    # =====================================================
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
            pin_memory=False,
            persistent_workers=True,
        )

        print(f"Starting PyTorch lazy iteration (spawn mode, workers={NUM_WORKERS})...")
        start = time.time()
        count_torch = 0
        for batch, _ in loader:
            count_torch += batch.size(0)
        pytorch_time = time.time() - start
        print(f"✓ PyTorch loaded {count_torch} images in {pytorch_time:.3f}s")
        del loader

    except Exception as e:
        print(f"ERROR: PyTorch test failed: {e}")
        pytorch_time = 0.0
        count_torch = 0

    # =====================================================
    # COMPARISON
    # =====================================================
    print("\n" + "=" * 60)
    print("LAZY ITERATION RESULTS (spawn)")
    print("=" * 60)
    if count_nchw > 0:
        print(
            f"bimb {SEMVER} (NCHW): {bimb_lazy_time:.3f}s "
            f"({count_nchw / bimb_lazy_time:.0f} img/s)"
        )
    if count_torch > 0:
        print(
            f"PyTorch (NCHW):     {pytorch_time:.3f}s "
            f"({count_torch / pytorch_time:.0f} img/s)"
        )
    if bimb_lazy_time > 0 and pytorch_time > 0:
        speedup = pytorch_time / bimb_lazy_time
        print(f"\nSpeedup (bimb / PyTorch): {speedup:.2f}×")
    print("=" * 60)


if __name__ == "__main__":
    # --- IMPORTANT for macOS / Windows ---
    # use "spawn" explicitly; PyTorch sets this by default on macOS.
    mp.set_start_method("spawn", force=True)
    main()
