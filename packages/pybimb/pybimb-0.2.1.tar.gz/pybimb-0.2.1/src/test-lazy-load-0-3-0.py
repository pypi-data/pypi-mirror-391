#!/usr/bin/env python3
import time
from itertools import islice

import bimb
import torch
import torchvision
import torchvision.transforms as transforms

# ============================================
# LAZY DATALOADER PREFETCHING BENCHMARK
# ============================================

print("=" * 60)
print("LAZY DATALOADER (PREFETCHING) ITERATION COMPARISON")
print("=" * 60)

if __name__ == "__main__":
    # --- Parameters ---
    BATCH_SIZE = 512
    DATA_PATH = "./data/cifar-10-jpg"  # path to all 60k CIFAR-10 images (train+test)
    PYTORCH_ROOT = "./data"
    SEMVER = "v0.3.1"
    PREFETCH_DEPTHS = [1, 2, 4, 6, 8, 10, 12]
    NUM_WORKERS = 8

    results = {}

    # ======================================================
    # BIMB TESTS
    # ======================================================
    for depth in PREFETCH_DEPTHS:
        print("\n" + "=" * 60)
        print(f"[BIMB {SEMVER}] Prefetch depth = {depth}")
        print("=" * 60)
        try:
            print(f"Initializing BimbLoader(prefetch_depth={depth})...")
            bimb_loader = bimb.BimbLoader(DATA_PATH, prefetch_depth=depth)
            total_images = len(bimb_loader)
            num_batches = (total_images + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"✓ Found {total_images} images ({num_batches} batches)")

            start = time.time()
            count = 0
            for _ in range(num_batches):
                batch_data = bimb_loader.get_next_batch(BATCH_SIZE)
                if batch_data is None:
                    break
                numpy_array, labels = batch_data
                if numpy_array.shape[0] == 0:
                    continue
                tensor = torch.from_numpy(numpy_array)  # NCHW already
                count += tensor.size(0)
            total_time = time.time() - start

            if count == 0:
                raise RuntimeError("No images loaded from BimbLoader")

            throughput = count / total_time
            print(
                f"✓ BIMB (depth={depth}) loaded {count} images in {total_time:.3f}s "
                f"→ {throughput:.0f} img/s"
            )
            results[f"Bimb (depth={depth})"] = (total_time, throughput)

        except Exception as e:
            print(f"❌ ERROR for BIMB prefetch_depth={depth}: {e}")
            results[f"Bimb (depth={depth})"] = (0.0, 0.0)
        finally:
            if "bimb_loader" in locals():
                del bimb_loader
                time.sleep(0.2)  # allow thread cleanup

    # ======================================================
    # PYTORCH BASELINE
    # ======================================================
    print("\n" + "=" * 60)
    print(f"[PYTORCH] Standard DataLoader (num_workers={NUM_WORKERS})")
    print("=" * 60)

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
        total_images = len(full_dataset)
        num_batches = (total_images + BATCH_SIZE - 1) // BATCH_SIZE

        loader = torch.utils.data.DataLoader(
            full_dataset,
            batch_size=BATCH_SIZE,
            shuffle=True,
            num_workers=NUM_WORKERS,
            pin_memory=True,
            persistent_workers=True,
        )

        start = time.time()
        count_torch = 0
        for batch, _ in islice(loader, num_batches):
            count_torch += batch.size(0)
        pytorch_time = time.time() - start

        throughput_torch = count_torch / pytorch_time
        print(
            f"✓ PyTorch loaded {count_torch} images in {pytorch_time:.3f}s "
            f"→ {throughput_torch:.0f} img/s"
        )
        results["PyTorch"] = (pytorch_time, throughput_torch)

    except Exception as e:
        print(f"❌ ERROR in PyTorch loader: {e}")
        results["PyTorch"] = (0.0, 0.0)

    # ======================================================
    # FINAL SUMMARY
    # ======================================================
    print("\n" + "=" * 60)
    print("FINAL ITERATION RESULTS")
    print("=" * 60)
    print(f"{'Loader':<20} | {'Time (s)':<10} | {'Img/s':<10}")
    print("-" * 45)

    for name, (t, rate) in results.items():
        if t > 0:
            print(f"{name:<20} | {t:<10.3f} | {rate:<10.0f}")
        else:
            print(f"{name:<20} | {'FAILED':<10} | {'-':<10}")

    print("=" * 60)

    # Speedup comparisons (if valid)
    if "PyTorch" in results and results["PyTorch"][0] > 0:
        pyt_time = results["PyTorch"][0]
        for name in [n for n in results if "Bimb" in n]:
            t = results[name][0]
            if t > 0:
                speedup = pyt_time / t
                print(f"{name:<20}: {speedup:.2f}× faster than PyTorch")
    print("=" * 60)
