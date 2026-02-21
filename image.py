# image.py
from pathlib import Path
import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0

image_model = efficientnet_b0(pretrained=True)
image_model.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def scan_image(path: Path) -> dict:
    try:
        img = Image.open(path).convert("RGB")
        x = transform(img).unsqueeze(0)
    except Exception:
        return {"penalty":0,"flags":[],"evidence":[],"summary":{}}

    with torch.no_grad():
        out = image_model(x)
        prob = torch.nn.functional.softmax(out, dim=1)
        score = float(prob[0][1].item() if prob.shape[1]>1 else 0.5)

    penalty = int(score*50)
    flags = []
    evidence = []

    if score >= 0.75:
        flags.append("image:gan_fingerprint")
        flags.append("image:noise_anomaly")
        evidence.append({"pipeline":"image","type":"ai_image_detection","severity":4,"details":{"score":score},"timestamps":[]})
    elif score >= 0.5:
        flags.append("image:gan_fingerprint")
        evidence.append({"pipeline":"image","type":"ai_image_detection","severity":3,"details":{"score":score},"timestamps":[]})

    return {"penalty":min(penalty,50),"flags":flags,"evidence":evidence,"summary":{"score":score}}
