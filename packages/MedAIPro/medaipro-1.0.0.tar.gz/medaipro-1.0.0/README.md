# 🧬 MedAIPro
**世界最先進的醫療人工智慧模組**

---

## 🚀 功能
- 醫學影像 AI 分析（CT/MRI/X-ray）
- ECG/EEG 生理信號自動分析
- 藥物交互風險偵測
- 疾病風險預測模型
- 臨床統計分析與報告生成

---

## 🧠 使用範例
```python
from medaipro import analyze_ecg, check_interaction, predict_disease

print(analyze_ecg("data/ecg.csv"))
print(check_interaction("Aspirin", "Warfarin"))
print(predict_disease([0.7, 1.3, 0.9, 0.1]))
