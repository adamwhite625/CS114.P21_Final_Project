# -*- coding: utf-8 -*-
"""Untitled33 _271095_271101.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZgBzIsTs6qk5-75Ptko-fB2s6MrqrMaJ

##Collect data
"""

!pip install pyheif

github_list = '''https://github.com/GwLewis369/Hand-written-digit-classification-data.git
https://github.com/gbaonr/CS114_handwritten_digits_data
https://github.com/adamwhite625/CS114_hand_written_digit.git
https://github.com/theRaven1312/CS114.P21
https://github.com/Khoiisme1905/CS114.git
https://github.com/ProjectHT1/machinelearning
https://github.com/Searching96/hand-written-digit.git
https://github.com/Salmon1605/CS114
https://github.com/anhtuann1224/hand_written_digit
https://github.com/NATuanAN/Hand_written_digit_classification_data.git
https://github.com/huapogba/may-hoc
https://github.com/hieutran890j2/CS114.git
https://github.com/votanhoang483/CS114.P21-Hand_written_digit_classification
https://github.com/DHPh/CS114_hand_written_digit/
https://github.com/thaituanUIT/ReminiScenceAI
https://github.com/anngyn/CS114-Hand-Written-Digit
https://github.com/lngphgthao/cs114-hand-written-digit-classification/tree/main/hand_written_digit
https://github.com/Toan02Ky-UIT/CS114
https://github.com/Lochke/CS114_Handwritten_Digit_Classification.git
https://github.com/NThong325/CS114/tree/cfd654a14dd471f5272387139d586ddcbf9cdf7e/hand_written_digit
https://github.com/toanlamdata/digit-recognition-group
https://github.com/Nohenshin/CS114.P21-2025-
https://github.com/hmcslearning/ML1142025
https://github.com/lngphgthao/cs114-hand-written-digit-classification
https://github.com/huapogba/may-hoc
https://github.com/NThong325/CS114/tree/main/hand_written_digit
https://github.com/23520276/Hand-written-digit-classification/
https://github.com/NThong325/CS114
'''

from google.colab import drive
drive.mount('/gdrive')
data_dir = '/gdrive/MyDrive/project1/handwritten_digit_classification/DATA'

from urllib.parse import urlparse
import os

for i in github_list.split():
    if not i.startswith("https://github.com/"):
        print(f"Skipping invalid URL: {i}")
        continue

    path = urlparse(i).path.strip("/")
    dir_name = path.replace("/", "_").replace(".git", "")
    clone_path = f'/tmp/{dir_name}'
    target_path = f'{data_dir}/{dir_name}'

    if os.path.exists(target_path):
        print(f"Directory {target_path} already exists, skipping clone for {i}")
        continue

    # Nếu thư mục tạm đã tồn tại, xóa nó trước khi clone
    if os.path.exists(clone_path):
        !rm -rf {clone_path}

    !git clone {i} {clone_path} || rm -rf {clone_path}

    if os.path.exists(clone_path):
        !mv {clone_path} {target_path}
    else:
        print(f"Failed to clone {i}")

"""##Thống kê số lượng"""

import os
import glob
# import path
a = glob.glob(f'{data_dir}/*/hand_written_digit/??52????')
print(a)

table =  []

for folder in a:
  mssv = os.path.basename(folder)
  table.append([mssv])
  for num in range(10):
    li = glob.glob(f'{folder}/{num}_*')
    table[-1].append(len(li))
  table[-1].append(sum(table[-1][1:]))

from tabulate import tabulate
tab  = tabulate(table, headers=['mssv', *range(10), 'sum'])
print(tab)

"""##Prepare dataset"""

import os
import glob

image_lists = []
for folder in glob.glob(f'{data_dir}/*/hand_written_digit/??52????'):
    for num in range(10):
        for img_path in glob.glob(f'{folder}/{num}_*'):
            image_lists.append((img_path, num))

print("Sample of image_lists:")
for item in image_lists[:5]:
    print(item, type(item), len(item))

from torch.utils.data import Dataset
from PIL import Image
import torch
import pyheif
import io

class custom_image_dataset(Dataset):
    def __init__(self, image_list, transform=None):
        self.image_list = image_list
        self.transform = transform

    def __len__(self):
        return len(self.image_list)

    def __getitem__(self, idx):
        img_path, label = self.image_list[idx]
        ext = os.path.splitext(img_path)[1].lower()

        try:
            if ext == '.heic':
                heif_file = pyheif.read(img_path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
                image = image.convert('RGB')
            else:
                image = Image.open(img_path).convert('RGB')

            if self.transform:
                image = self.transform(image)
            return image, torch.tensor(label), img_path
        except Exception as e:
            print(f"Error reading image {img_path}: {e}")
            raise ValueError(f"Cannot read image: {img_path}")

from concurrent.futures import ThreadPoolExecutor
import os
from PIL import Image
import pyheif
import io

def is_valid_image(item):
    path, label = item
    if not os.path.isfile(path):
        print(f"Invalid file (does not exist): {path}")
        return None

    ext = os.path.splitext(path)[1].lower()

    supported_extensions = ['.jpg', '.jpeg', '.png', '.heic']

    if ext not in supported_extensions:
        print(f"Invalid image (unsupported extension): {path}")
        return None

    try:
        if ext == '.heic':
            heif_file = pyheif.read(path)
            if heif_file:
                return (path, label)
            else:
                print(f"Invalid HEIC image: {path}")
                return None
        else:
            with Image.open(path) as img:
                img.verify()
            return (path, label)
    except Exception as e:
        print(f"Error validating image {path}: {e}")
        return None

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(is_valid_image, image_lists))

valid_image_lists = [r for r in results if r is not None]
print(f"Total valid images: {len(valid_image_lists)}")

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset
import numpy as np

train_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((200, 200)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(10),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((200, 200)),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

split = int(0.8 * len(valid_image_lists))
train_dataset = custom_image_dataset(valid_image_lists[:split], train_transform)
test_dataset = custom_image_dataset(valid_image_lists[split:], test_transform)

train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)
test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)

class_counts = np.zeros(10)
for _, label in valid_image_lists[:split]:
    class_counts[label] += 1
class_weights = 1.0 / (class_counts + 1e-5)
class_weights = class_weights / class_weights.sum() * 10
class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)

for inputs, labels, paths in train_dataloader:
    print(f"Batch size: {len(labels)}")
    print(f"Input shape: {inputs.shape}")
    print(f"Label type: {type(labels)}")
    print(f"Labels: {labels}")
    break

"""###Build Model"""

import torch.nn as nn
import torch.nn.functional as F

class ConvNeuralNetwork(nn.Module):
    def __init__(self):
        super(ConvNeuralNetwork, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 5)
        self.conv3 = nn.Conv2d(32, 64, 5)
        self.fc1 = nn.Linear(64 * 21 * 21, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 64 * 21 * 21)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = ConvNeuralNetwork().to(device)
print(model)

"""###Training"""

import torch.optim as optim
import matplotlib.pyplot as plt

criterion = nn.CrossEntropyLoss(weight=class_weights)
optimizer = optim.Adam(model.parameters(), lr=0.001)

def train_loop(dataloader, model, criterion, optimizer):
    model.train()
    running_loss = 0.0
    for i, (inputs, labels, _) in enumerate(dataloader):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if i % 20 == 19:
            print(f'[Batch {i + 1}] loss: {running_loss / 20:.3f}')
            running_loss = 0.0
    return running_loss / len(dataloader)

def test_loop(dataloader, model, criterion):
    model.eval()
    total = 0
    correct = 0
    test_loss = 0.0
    with torch.no_grad():
        for inputs, labels, _ in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            test_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    test_loss /= len(dataloader)
    accuracy = 100 * correct / total
    print(f'Test Error: \n Accuracy: {accuracy:.1f}%, Avg loss: {test_loss:.3f} \n')
    return test_loss, accuracy

train_losses = []
test_losses = []
test_accuracies = []
best_loss = float('inf')
epochs_no_improve = 0
best_model_path = f'{data_dir}/best_model.pth'
epochs = 20
patience = 5

for epoch in range(epochs):
    print(f'Epoch {epoch + 1}\n-------------------------------')
    train_loss = train_loop(train_dataloader, model, criterion, optimizer)
    test_loss, test_accuracy = test_loop(test_dataloader, model, criterion)

    train_losses.append(train_loss)
    test_losses.append(test_loss)
    test_accuracies.append(test_accuracy)

    if test_loss < best_loss:
        best_loss = test_loss
        epochs_no_improve = 0
        torch.save(model.state_dict(), best_model_path)
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= patience:
            print(f'Early stopping at epoch {epoch + 1}')
            break

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Train Loss')
plt.plot(test_losses, label='Test Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Test Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(test_accuracies, label='Test Accuracy', color='green')
plt.xlabel('Epoch')
plt.ylabel('Accuracy (%)')
plt.title('Test Accuracy')
plt.legend()

plt.tight_layout()
plt.show()

print('Finished Training!')
model.load_state_dict(torch.load(best_model_path))

!pip install pillow_heif

"""##Dự đoán"""

import os
from google.colab import drive
import imghdr
import pillow_heif
from PIL import Image

# Kết nối Google Drive
drive.mount('/gdrive')

# Đường dẫn đến thư mục chứa dữ liệu giải nén
extract_dir = '/gdrive/MyDrive/project1/handwritten_digit_classification/cs114_hwdr'

# Lấy danh sách tất cả các file ảnh hợp lệ trong thư mục giải nén
test_image_paths = []
for root, _, files in os.walk(extract_dir):
    for file in files:
        file_path = os.path.join(root, file)
        # Kiểm tra xem file có phải là ảnh hợp lệ không
        try:
            if file.lower().endswith('.heic'):
                heif_file = pillow_heif.read_heif(file_path)
                test_image_paths.append(file_path)
            else:
                img = Image.open(file_path)
                img.close()
                test_image_paths.append(file_path)
        except Exception as e:
            print(f"Bỏ qua file không phải ảnh hoặc lỗi: {file_path} ({str(e)})")

print(f"Tìm thấy {len(test_image_paths)} file ảnh hợp lệ trong bộ dữ liệu kiểm tra.")
print("Ví dụ 5 file đầu tiên:", test_image_paths[:5])

from torch.utils.data import Dataset
from PIL import Image
import torch
import pillow_heif

class TestImageDataset(Dataset):
    def __init__(self, image_paths, transform=None):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            if img_path.lower().endswith('.heic'):
                heif_file = pillow_heif.read_heif(img_path)
                image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data)
            else:
                image = Image.open(img_path)
            image = image.convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, img_path
        except Exception as e:
            print(f"Lỗi khi đọc file {img_path}: {str(e)}")
            # Trả về ảnh rỗng và đường dẫn để không làm gián đoạn DataLoader
            return torch.zeros((3, 28, 28)), img_path

import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as F


transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

test_dataset = TestImageDataset(test_image_paths, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)

# Tải mô hình đã huấn luyện
model_path = '/gdrive/MyDrive/project1/handwritten_digit_classification/best_model.pth'

class ConvNeuralNetwork(nn.Module):
    def __init__(self):
        super(ConvNeuralNetwork, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 5)
        self.conv3 = nn.Conv2d(32, 64, 5)

        self.fc1 = nn.Linear(64 * 21 * 21, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = ConvNeuralNetwork()

state_dict = torch.load(model_path, map_location=torch.device('cpu'))
model.load_state_dict(state_dict)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()  # Chuyển sang chế độ đánh giá
print("Mô hình đã được tải và sẵn sàng dự đoán!")

import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as F
import pillow_heif

transform = transforms.Compose([
    transforms.Resize((200, 200)), # Thay đổi kích thước resize
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

class TestImageDataset(Dataset):
    def __init__(self, image_paths, transform=None):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            if img_path.lower().endswith('.heic'):
                heif_file = pillow_heif.read_heif(img_path)
                # Pass mode and stride explicitly if necessary, though frombytes often infers
                image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data)
            else:
                image = Image.open(img_path)
            image = image.convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, img_path
        except Exception as e:
            print(f"Lỗi khi đọc file {img_path}: {str(e)}")
            return torch.zeros((3, 200, 200)), img_path

test_dataset = TestImageDataset(test_image_paths, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)

# Tải mô hình đã huấn luyện
model_path = '/gdrive/MyDrive/project1/handwritten_digit_classification/DATA/best_model.pth'


class ConvNeuralNetwork(nn.Module):
    def __init__(self):
        super(ConvNeuralNetwork, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 5)
        self.conv3 = nn.Conv2d(32, 64, 5)
        self.fc1 = nn.Linear(64 * 21 * 21, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Tạo một instance (thể hiện) của lớp mô hình
model = ConvNeuralNetwork()

# Tải state_dict (các tham số đã học) vào instance mô hình vừa tạo
state_dict = torch.load(model_path, map_location=torch.device('cpu'))
model.load_state_dict(state_dict)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()  # Chuyển sang chế độ đánh giá
print("Mô hình đã được tải và sẵn sàng dự đoán!")

import os
import torch

predictions = []

with torch.no_grad():  # Tắt gradient để tăng tốc độ
    for batch_idx, (images, img_paths) in enumerate(test_loader):
        images = images.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)  # Lấy nhãn dự đoán
        for img_path, pred in zip(img_paths, predicted):
            filename = os.path.basename(img_path)
            predictions.append((filename, pred.item()))
        #print(f"Đã xử lý batch {batch_idx + 1}/{len(test_loader)}")

print(f"Đã dự đoán xong cho {len(predictions)} ảnh.")

import csv

# Đường dẫn file CSV đầu ra
output_csv = '/gdrive/MyDrive/project1/handwritten_digit_classification/DATA/predictions.csv'

# Ghi kết quả vào file CSV
with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for filename, label in predictions:
        writer.writerow([filename, label])

print(f"Kết quả đã được lưu vào {output_csv}")

"""##Đánh giá Model"""

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

true_labels = []
predicted_labels = []

model.eval()

with torch.no_grad():
    for images, labels, _ in test_dataloader:
        images = images.to(device)
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        true_labels.extend(labels.cpu().numpy())
        predicted_labels.extend(preds.cpu().numpy())

accuracy = accuracy_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels, average='weighted')
precision = precision_score(true_labels, predicted_labels, average='weighted')
recall = recall_score(true_labels, predicted_labels, average='weighted')
conf_matrix = confusion_matrix(true_labels, predicted_labels)

metrics_data = {'Metric': ['Accuracy', 'F1-score', 'Precision', 'Recall'],
                'Score': [accuracy, f1, precision, recall]}
metrics_df = pd.DataFrame(metrics_data)
print("Evaluation Metrics:")
display(metrics_df)

# Visualize confusion matrix
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.show()