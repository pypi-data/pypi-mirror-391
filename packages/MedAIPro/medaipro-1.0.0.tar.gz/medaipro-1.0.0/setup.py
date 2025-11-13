from setuptools import setup, find_packages

setup(
    name="MedAIPro",
    version="1.0.0",
    author="BSP",
    author_email="your@email.com",
    description="世界最先進的醫療人工智慧模組",
    packages=find_packages(),
    install_requires=[
        "numpy", "pandas", "opencv-python", "tensorflow", 
        "scikit-learn", "scipy", "fpdf2", "joblib"
    ],
    python_requires=">=3.8",
)
