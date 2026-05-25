import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image


class SimpleDeepfakeDetector:
    """
    Prototype deepfake detector.
    This is a placeholder model for pipeline integration only.
    Replace later with a pretrained MesoNet/Xception model.
    """

    def __init__(self):
        self.model = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(224 * 224 * 3, 2)
        )
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def predict_frame(self, frame):
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            output = self.model(tensor)
            probs = torch.softmax(output, dim=1)

        fake_score = float(probs[0][1].item())
        return fake_score

    def analyze_image(self, image_path: str):
        frame = cv2.imread(image_path)

        if frame is None:
            return {
                "deepfake_score": None,
                "deepfake_risk": "unknown",
                "deepfake_reason": "Could not read image for deepfake analysis."
            }

        score = self.predict_frame(frame)

        if score >= 0.75:
            risk = "high"
        elif score >= 0.50:
            risk = "medium"
        else:
            risk = "low"

        return {
            "deepfake_score": round(score, 3),
            "deepfake_risk": risk,
            "deepfake_reason": "Prototype visual manipulation detector produced a deepfake risk score."
        }

    def analyze_video(self, video_path: str, max_frames: int = 10):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return {
                "deepfake_score": None,
                "deepfake_risk": "unknown",
                "deepfake_reason": "Could not open video for deepfake analysis."
            }

        scores = []
        frame_count = 0

        while frame_count < max_frames:
            ret, frame = cap.read()

            if not ret:
                break

            score = self.predict_frame(frame)
            scores.append(score)
            frame_count += 1

        cap.release()

        if not scores:
            return {
                "deepfake_score": None,
                "deepfake_risk": "unknown",
                "deepfake_reason": "No readable frames found for deepfake analysis."
            }

        avg_score = sum(scores) / len(scores)

        if avg_score >= 0.75:
            risk = "high"
        elif avg_score >= 0.50:
            risk = "medium"
        else:
            risk = "low"

        return {
            "deepfake_score": round(float(avg_score), 3),
            "deepfake_risk": risk,
            "deepfake_reason": f"Prototype visual manipulation detector analyzed {len(scores)} frame(s)."
        }


detector = SimpleDeepfakeDetector()