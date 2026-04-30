import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image

# Simple lightweight pretrained model (binary classifier placeholder)
# You can replace later with a real deepfake model

class SimpleDeepfakeDetector:
    def __init__(self):
        self.model = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(224*224*3, 2)
        )
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def predict(self, frame):
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            output = self.model(tensor)
            probs = torch.softmax(output, dim=1)

        fake_score = probs[0][1].item()
        return fake_score


detector = SimpleDeepfakeDetector()