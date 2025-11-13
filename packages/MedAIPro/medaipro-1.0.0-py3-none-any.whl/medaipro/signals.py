import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def analyze_ecg(file_path):
    """自動分析心電圖"""
    data = pd.read_csv(file_path)
    peaks, _ = find_peaks(data['heart_rate'], distance=50)
    avg_hr = np.mean(data['heart_rate'])
    arrhythmia = np.sum(data['heart_rate'] > 120)
    return {"平均心率": round(avg_hr, 2), "R峰數": len(peaks), "異常心律次數": int(arrhythmia)}

def analyze_eeg(file_path):
    """腦電波分析"""
    data = pd.read_csv(file_path)
    return {
        "Delta": float(data['delta'].mean()),
        "Alpha": float(data['alpha'].mean()),
        "Beta": float(data['beta'].mean())
    }
