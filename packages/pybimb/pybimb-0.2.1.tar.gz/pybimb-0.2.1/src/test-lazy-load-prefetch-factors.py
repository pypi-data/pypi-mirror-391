import time

import bimb
import numpy as np
import torch

# --- Parameters ---
BATCH_SIZE = 256
DATA_PATH = "./data/cifar-10-jpg"  # Path to all 60k images
SEMVER = "v0.3.0-prefetch"
PREFETCH_DEPTHS = range(1, 21, 2)

print("=" * 60)
print(f"BIMB {SEMVER} PREFETCH DEPTH BENCHMARK")
print("=" * 60)

results = {}

if __name__ == "__main__":
    # =================== WARM-UP ===================
    print("Warming up OS page cache (1 run)...")
    try:
        warmup_loader = bimb.BimbLoader(DATA_PATH, prefetch_depth=1)
        total_batches = (len(warmup_loader) + BATCH_SIZE - 1) // BATCH_SIZE
        for _ in range(total_batches):
            batch = warmup_loader.get_next_batch(BATCH_SIZE)
            if batch is None:
                break
        del warmup_loader
        print("✓ Cache warmed up.")
    except Exception as e:
        print(f"ERROR: Warm-up failed: {e}")
        exit(1)

    # =================== MAIN LOOP ===================
    for depth in PREFETCH_DEPTHS:
        print("\n" + "-" * 60)
        print(f"TESTING: prefetch_depth = {depth}")
        print("-" * 60)

        try:
            loader = bimb.BimbLoader(DATA_PATH, prefetch_depth=depth)
            num_batches = (len(loader) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"Starting benchmark... ({num_batches} batches)")

            start = time.time()
            total_images = 0

            for i in range(num_batches):
                batch = loader.get_next_batch(BATCH_SIZE)
                if batch is None:
                    print(f"Reached end at batch {i + 1}")
                    break

                numpy_array, labels = batch
                # The Rust loader already gives NCHW order
                tensor = torch.from_numpy(numpy_array)
                total_images += tensor.shape[0]

            duration = time.time() - start
            print(f"✓ Loaded {total_images} images in {duration:.3f}s")
            results[depth] = duration

        except Exception as e:
            print(f"ERROR during run with prefetch_depth={depth}: {e}")
            results[depth] = 0.0
        finally:
            # Explicit cleanup (ensures producer thread shuts down)
            if "loader" in locals():
                del loader
                time.sleep(0.2)

    # =================== RESULTS ===================
    print("\n" + "=" * 60)
    print("PREFETCH DEPTH RESULTS (60,000 images)")
    print("=" * 60)
    print(f"{'Prefetch Depth':<18} | {'Total Time (s)':<15} | {'Images/s':<10}")
    print("-" * 45)

    if not results:
        print("No results recorded.")
    else:
        for depth in sorted(results.keys()):
            t = results[depth]
            if t > 0:
                ips = 60000 / t
                print(f"{depth:<18} | {t:<15.3f} | {ips:<10.0f}")
            else:
                print(f"{depth:<18} | {'FAILED':<15} | {'N/A':<10}")

    print("=" * 60)
