# from distutils.core import setup
#
# setup(
#     name='qualityvision',
#     packages=['qualityvision'],
#     version='0.1',
#     license='MIT',
#     description='Computer Vision Helping Library',
#     author='Rahul Patekar',
#     author_email='ngrahulpatekar@gmail.com',
#     url='https://github.com/ngrahulp/summary_generation_code.git',
#     keywords=['ComputerVision', 'HandTracking', 'FaceTracking', 'ImageQuality'],
#     install_requires=[
#         'opencv-python',
#         "mediapipe",
#         'numpy'
#     ],
#     python_requires='>=3.12',  # Requires any version >= 3.12
#
#     classifiers=[
#         'Development Status :: 3 - Alpha',
#         # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
#         'Intended Audience :: Developers',
#         'Topic :: Software Development :: Build Tools',
#         'License :: OSI Approved :: MIT License',
#         'Programming Language :: Python :: 3.12',  # Specify which pyhton versions that you want to support
#     ],
# )




from setuptools import setup, find_packages

setup(
    name="qualityvision",
    version="0.1.0",
    author="Rahul Patekar",
    author_email="ngrahulpatekar@gmail.com",
    description="A simple Face and Hand tracking module using Mediapipe and OpenCV",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ngrahulp/summary_generation_code",
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
