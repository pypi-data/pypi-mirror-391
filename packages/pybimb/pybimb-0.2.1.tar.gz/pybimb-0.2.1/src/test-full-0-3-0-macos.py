import time

import matplotlib
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

matplotlib.use("Agg")
import bimb
import matplotlib.pyplot as plt
import numpy as np

# ======================================================
#  PART 1: Simple CNN
# ======================================================


class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


# ======================================================
#  PART 2: Bimb Wrapper (turns Rust loader into iterable)
# ======================================================


class BimbWrapper:
    def __init__(self, bimb_loader, batch_size, device="cpu", shuffle=False):
        self.loader = bimb_loader
        self.batch_size = batch_size
        self.device = device
        self.shuffle = shuffle

    def __len__(self):
        return (len(self.loader) + self.batch_size - 1) // self.batch_size

    def __iter__(self):
        if self.shuffle:
            self.loader.shuffle()
        else:
            self.loader.reset()

        while True:
            batch_data = self.loader.get_next_batch(self.batch_size)
            if batch_data is None:
                break

            numpy_array, labels = batch_data
            if numpy_array.shape[0] == 0:
                continue

            # Rust already gives NCHW layout
            tensor = torch.from_numpy(numpy_array).to(self.device)
            labels = torch.tensor(labels, dtype=torch.long).to(self.device)
            yield tensor, labels


# ======================================================
#  PART 3: Training Function
# ======================================================


def train_model(model, train_loader, test_loader, num_epochs=5, device="cpu"):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(num_epochs):
        model.train()
        start_time = time.time()
        running_loss = 0.0
        correct_train, total_train = 0, 0

        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total_train += labels.size(0)
            correct_train += predicted.eq(labels).sum().item()

        epoch_train_acc = 100.0 * correct_train / total_train
        epoch_loss = running_loss / len(train_loader)
        print(
            f"  Epoch [{epoch + 1}/{num_epochs}] - Loss: {epoch_loss:.4f} | Acc: {epoch_train_acc:.2f}% | Time: {time.time() - start_time:.2f}s"
        )

        # --- Quick test ---
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = outputs.max(1)
                total += labels.size(0)
                correct += preds.eq(labels).sum().item()
        print(f"    Test Acc: {100.0 * correct / total:.2f}%")


# ======================================================
#  PART 4: Benchmarks
# ======================================================

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch_size = 256
    num_epochs = 3  # shorter for benchmarking
    num_workers = 8

    BIMB_TRAIN_PATH = "./data/cifar-10-jpg/train"
    BIMB_TEST_PATH = "./data/cifar-10-jpg/test"
    PYTORCH_DATA_ROOT = "./data"

    transform_pytorch = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ]
    )

    results = {}

    # --------------------------------------------------
    # 1. Bimb (prefetch_depth = 1)
    # --------------------------------------------------
    print("\n" + "=" * 60)
    print("BENCHMARK 1: BimbLoader (prefetch_depth = 1)")
    print("=" * 60)

    bimb_train_loader_1 = bimb.BimbLoader(BIMB_TRAIN_PATH, prefetch_depth=1)
    bimb_test_loader_1 = bimb.BimbLoader(BIMB_TEST_PATH, prefetch_depth=1)

    train_wrapper_1 = BimbWrapper(bimb_train_loader_1, batch_size, device, shuffle=True)
    test_wrapper_1 = BimbWrapper(bimb_test_loader_1, batch_size, device, shuffle=False)

    model_1 = SimpleCNN(num_classes=len(bimb_train_loader_1.class_map)).to(device)

    start_1 = time.time()
    train_model(model_1, train_wrapper_1, test_wrapper_1, num_epochs, device)
    total_1 = time.time() - start_1
    results["Bimb (1)"] = total_1

    # --------------------------------------------------
    # 2. Bimb (prefetch_depth = 10)
    # --------------------------------------------------
    print("\n" + "=" * 60)
    print("BENCHMARK 2: BimbLoader (prefetch_depth = 10)")
    print("=" * 60)

    bimb_train_loader_10 = bimb.BimbLoader(BIMB_TRAIN_PATH, prefetch_depth=10)
    bimb_test_loader_10 = bimb.BimbLoader(BIMB_TEST_PATH, prefetch_depth=10)

    train_wrapper_10 = BimbWrapper(
        bimb_train_loader_10, batch_size, device, shuffle=True
    )
    test_wrapper_10 = BimbWrapper(
        bimb_test_loader_10, batch_size, device, shuffle=False
    )

    model_10 = SimpleCNN(num_classes=len(bimb_train_loader_10.class_map)).to(device)

    start_10 = time.time()
    train_model(model_10, train_wrapper_10, test_wrapper_10, num_epochs, device)
    total_10 = time.time() - start_10
    results["Bimb (10)"] = total_10

    # --------------------------------------------------
    # 3. PyTorch built-in DataLoader
    # --------------------------------------------------
    print("\n" + "=" * 60)
    print("BENCHMARK 3: PyTorch DataLoader")
    print("=" * 60)

    trainset = torchvision.datasets.CIFAR10(
        root=PYTORCH_DATA_ROOT, train=True, download=True, transform=transform_pytorch
    )
    testset = torchvision.datasets.CIFAR10(
        root=PYTORCH_DATA_ROOT, train=False, download=True, transform=transform_pytorch
    )

    pytorch_train_loader = DataLoader(
        trainset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        persistent_workers=True,
    )
    pytorch_test_loader = DataLoader(
        testset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        persistent_workers=True,
    )

    model_pt = SimpleCNN(num_classes=10).to(device)

    start_pt = time.time()
    train_model(model_pt, pytorch_train_loader, pytorch_test_loader, num_epochs, device)
    total_pt = time.time() - start_pt
    results["PyTorch"] = total_pt

    # --------------------------------------------------
    # 4. Results
    # --------------------------------------------------
    print("\n" + "=" * 60)
    print("FINAL TRAINING TIME RESULTS")
    print("=" * 60)
    print(f"{'Loader':<20} | {'Time (s)':<10}")
    print("-" * 35)

    for name, t in results.items():
        print(f"{name:<20} | {t:<10.2f}")

    print("=" * 60)
    best = min(results, key=results.get)
    print(f"Fastest loader: {best} ({results[best]:.2f}s)\n")
