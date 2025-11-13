import numpy as np
import cv2
import tensorflow as tf

def load_image(path):
    """讀取醫學影像（CT/MRI/X-ray）"""
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

def segment_tumor(image, model_path="models/segmentation_model.h5"):
    """使用 AI 模型分割腫瘤區域"""
    model = tf.keras.models.load_model(model_path)
    img = cv2.resize(image, (256, 256)) / 255.0
    pred = model.predict(img[np.newaxis, ..., np.newaxis])
    mask = (pred[0, ..., 0] > 0.5).astype(np.uint8)
    return cv2.resize(mask, (image.shape[1], image.shape[0]))

def extract_features(image):
    """提取影像特徵"""
    edges = cv2.Canny(image, 100, 200)
    return {
        "平均亮度": float(np.mean(image)),
        "標準差": float(np.std(image)),
        "邊緣密度": float(np.mean(edges) / 255)
    }
