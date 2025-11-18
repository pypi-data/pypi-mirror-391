from PIL import Image

class CropHealthAnalyzer:
    def analyze_image(self, image_path: str):
        img = Image.open(image_path).convert("L")
        pixels = img.getdata()
        avg = sum(pixels) / len(pixels)
        if avg < 90:
            return {"status": "DISEASED", "score": 0.25}
        elif avg > 170:
            return {"status": "HEALTHY", "score": 0.92}
        return {"status": "OBSERVE", "score": 0.60}
