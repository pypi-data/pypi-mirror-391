from setuptools import setup, find_packages

setup(
    name="qualityvision",
    version="0.1.1",
    author="Rahul Patekar",
    author_email="ngrahulpatekar@gmail.com",
    description="A simple Blur Detection module using numpy and OpenCV",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ngrahulp/qualityvision",
    packages=find_packages(),
    install_requires=[
        "mediapipe>=0.10.0",
        "opencv-python>=4.5.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
