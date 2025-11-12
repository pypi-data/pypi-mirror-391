import bimb
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision
import torchvision.transforms as transforms
import matplotlib
matplotlib.use('Agg') # No $DISPLAY needed
import matplotlib.pyplot as plt
import time
# PIL is no longer needed for the Bimb pipeline
# from PIL import Image

# ============= PART 1: Simple CNN Classifier =============
# (Unchanged)
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2), nn.Dropout2d(0.25),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2), nn.Dropout2d(0.25),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 512), nn.ReLU(inplace=True), # Adjusted for 32x32 -> 8x8
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# ============= PART 2: Bimb Loader Adapter =============
# This new class makes our BimbLoader "look like" a PyTorch DataLoader
# by implementing the __iter__ and __len__ methods.

class BimbWrapper:
    def __init__(self, bimb_loader, batch_size, device='cpu', shuffle=False):
        self.loader = bimb_loader
        self.batch_size = batch_size
        self.device = device
        self.shuffle = shuffle

    def __len__(self):
        # Return the number of batches
        return (len(self.loader) + self.batch_size - 1) // self.batch_size

    def __iter__(self):
        # This is the "generator" that the training loop will call

        # 1. Shuffle at the start of each epoch (if requested)
        if self.shuffle:
            self.loader.shuffle()
        else: self.loader.reset()

        # 2. Start the batch-yielding loop
        while True:
            # 3. Call our Rust function
            batch_data = self.loader.get_next_batch(self.batch_size)

            # 4. Check for end of epoch
            if batch_data is None:
                break # StopIteration

            numpy_array, labels = batch_data

            # 5. Skip empty batches (if any images failed to load)
            if numpy_array.shape[0] == 0:
                continue

            # 6. Perform the final transformations
            #    .permute() is the zero-copy HWC -> CHW transpose
            tensor = torch.from_numpy(numpy_array).permute(0, 3, 1, 2).to(self.device)
            labels = torch.tensor(labels, dtype=torch.long).to(self.device)

            # 7. Yield the batch to the training loop
            yield tensor, labels

# ============= PART 3: Training Function (Reforged) =============
# (Unchanged - it's already perfect)
def train_model(model, train_loader, test_loader, num_epochs=5, device='cpu'):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(f"Starting training for {num_epochs} epochs on {device}...")

    for epoch in range(num_epochs):
        # --- Training Phase ---
        model.train()
        start_time = time.time()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        # This loop now works perfectly with our BimbWrapper
        for i, (images, labels) in enumerate(train_loader):
            # The .to(device) calls are now handled *inside* the wrapper,
            # but we leave them here for compatibility with the PyTorch loader.
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted_train = outputs.max(1)
            total_train += labels.size(0)
            correct_train += predicted_train.eq(labels).sum().item()

        epoch_time = time.time() - start_time
        epoch_train_loss = running_loss / len(train_loader)
        epoch_train_acc = 100. * correct_train / total_train

        # --- Testing Phase (The Inspection) ---
        model.eval()
        correct_test = 0
        total_test = 0
        with torch.no_grad():
            for images_test, labels_test in test_loader:
                images_test, labels_test = images_test.to(device), labels_test.to(device)
                outputs_test = model(images_test)
                _, predicted_test = outputs_test.max(1)
                total_test += labels_test.size(0)
                correct_test += predicted_test.eq(labels_test).sum().item()

        epoch_test_acc = 100. * correct_test / total_test

        print(f'  Epoch [{epoch+1}/{num_epochs}] completed in {epoch_time:.2f}s')
        print(f'    Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.2f}%')
        print(f'    Test Acc: {epoch_test_acc:.2f}%')

    print("Training finished.")
    return

# ============= PART 4: Main Benchmark Script =============

if __name__ == "__main__":
    # --- Setup ---
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    batch_size = 256
    num_epochs = 5
    num_workers = 8 # Workers for PyTorch

    # We now point to the root of the train/test splits
    BIMB_TRAIN_PATH = "./data/cifar-10-jpg/train"
    BIMB_TEST_PATH = "./data/cifar-10-jpg/test"
    PYTORCH_DATA_ROOT = './data'

    # --- Data transforms (FOR PYTORCH ONLY) ---
    transform_pytorch = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    # ======================================================
    # --- CAMPAIGN 1: Bimb (Rust) Training ---
    # ======================================================
    print("\n" + "=" * 60)
    print("BENCHMARK 1: Training with BIMB (Rust) Loader")
    print("=" * 60)

    # This is now a true end-to-end time, just like PyTorch's
    start_total_bimb = time.time()

    # 1. Initialization (Cheap - just scans paths)
    print(f"Bimb: Initializing lazy loaders...")
    bimb_train_loader_rust = bimb.BimbLoader(BIMB_TRAIN_PATH)
    bimb_test_loader_rust = bimb.BimbLoader(BIMB_TEST_PATH)
    print(f"  Train: {len(bimb_train_loader_rust)} samples. Test: {len(bimb_test_loader_rust)} samples.")
    print(f"  Class map: {bimb_train_loader_rust.class_map}")

    # 2. Create Python Adapters
    bimb_train_wrapper = BimbWrapper(bimb_train_loader_rust, batch_size, device, shuffle=True)
    bimb_test_wrapper = BimbWrapper(bimb_test_loader_rust, batch_size, device, shuffle=False)

    # 3. Create Model
    model_bimb = SimpleCNN(num_classes=len(bimb_train_loader_rust.class_map)).to(device)

    # 4. Train (All the real work happens here)
    print("Bimb: Starting training cycle...")
    train_model(model_bimb, bimb_train_wrapper, bimb_test_wrapper, num_epochs=num_epochs, device=device)

    end_total_bimb = time.time()
    total_time_bimb = end_total_bimb - start_total_bimb

    print(f"\n--- Bimb Results ---")
    print(f"✓ TOTAL BIMB TIME (Lazy Init + Train): {total_time_bimb:.4f}s")


    # ======================================================
    # --- CAMPAIGN 2: PyTorch (torchvision) Training ---
    # ======================================================
    print("\n" + "=" * 60)
    print(f"BENCHMARK 2: Training with PyTorch Loader ({num_workers} workers)")
    print("=" * 60)

    start_total_pytorch = time.time()

    # 1. Create PyTorch Dataset (lazy)
    print(f"PyTorch: Initializing lazy dataset from {PYTORCH_DATA_ROOT}...")
    pytorch_trainset = torchvision.datasets.CIFAR10(root=PYTORCH_DATA_ROOT, train=True,
                                                    download=True, transform=transform_pytorch)
    pytorch_testset = torchvision.datasets.CIFAR10(root=PYTORCH_DATA_ROOT, train=False,
                                                   download=True, transform=transform_pytorch)

    # 2. Create DataLoaders
    pytorch_train_loader = DataLoader(pytorch_trainset, batch_size=batch_size, shuffle=True,
                                      num_workers=num_workers, persistent_workers=True)
    pytorch_test_loader = DataLoader(pytorch_testset, batch_size=batch_size, shuffle=False,
                                     num_workers=num_workers, persistent_workers=True)

    # 3. Create Model
    model_pytorch = SimpleCNN(num_classes=10).to(device)

    # 4. Train
    print(f"PyTorch: Starting training cycle (num_workers={num_workers})...")
    train_model(model_pytorch, pytorch_train_loader, pytorch_test_loader, num_epochs=num_epochs, device=device)

    end_total_pytorch = time.time()
    total_time_pytorch = end_total_pytorch - start_total_pytorch

    print(f"\n--- PyTorch Results ---")
    print(f"✓ TOTAL PYTORCH TIME (Lazy Init + Train): {total_time_pytorch:.4f}s")

    # ======================================================
    # --- FINAL COMPARISON ---
    # ======================================================
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total Bimb Time (Lazy):     {total_time_bimb:.4f}s")
    print(f"Total PyTorch Time (Lazy):  {total_time_pytorch:.4f}s")

    speedup = total_time_pytorch / total_time_bimb
    print(f"\n🚀 Bimb's end-to-end process is {speedup:.2f}x {'FASTER' if speedup > 1 else 'SLOWER'} than PyTorch's.")
