# -*- coding: utf-8 -*-
"""classification using VGG16.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14hQVfFN8lh7z_m96qAhLb36khuvpUei0
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.models import vgg16
from torch.utils.data import DataLoader
from torchsummary import summary

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
])

train_dataset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=2)

model = vgg16(weights='IMAGENET1K_V1')
model.classifier[6] = nn.Linear(4096, 10)  # Change the last layer to 10 classes for CIFAR-10
model = model.to(device)

summary(model, (3, 224, 224))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 10
for epoch in range(num_epochs):
    model.train()  # Set model to training mode
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)  # Move data to GPU/CPU

        optimizer.zero_grad()  # Reset gradients for each batch
        outputs = model(images)  # Forward pass
        loss = criterion(outputs, labels)  # Calculate loss

        loss.backward()  # Backpropagation
        optimizer.step()  # Update weights

        running_loss += loss.item()  # Accumulate loss

        # Calculate accuracy
        _, predicted = torch.max(outputs, 1)  # Get predictions
        total += labels.size(0)  # Update total number of labels
        correct += (predicted == labels).sum().item()  # Update correct predictions

    epoch_loss = running_loss / len(train_loader)
    epoch_accuracy = 100 * correct / total  # Calculate accuracy

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.2f}%")

model.eval()  # Set model to evaluation mode
correct = 0
total = 0

with torch.no_grad():  # Disable gradient computation for evaluation
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f"Test Accuracy: {100 * correct / total:.2f}%")

import matplotlib.pyplot as plt
from PIL import Image
import torch
from torchvision import transforms

# Define the image preprocessing steps
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
])

# Load and preprocess the image
img_path = '/content/h-2.jpg'  # Path to the image
img = Image.open(img_path)  # Load the image
img_t = preprocess(img)  # Preprocess the image
batch_t = torch.unsqueeze(img_t, 0)  # Add a batch dimension
batch_t = batch_t.to(device)  # Move input to the same device as the model

# Perform inference
with torch.no_grad():  # Disable gradient calculation
    output = model(batch_t)  # Forward pass

# Get the predicted class
_, predicted = torch.max(output, 1)
class_idx = predicted.item()

# CIFAR-10 class names
classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
predicted_class = classes[class_idx]

# Display the image with the predicted class
plt.figure(figsize=(6, 6))
plt.imshow(img)  # Show the original image
plt.title(f'Predicted class: {predicted_class}', fontsize=16)
plt.axis('off')  # Hide axes
plt.show()