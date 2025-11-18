from setuptools import setup, find_packages

setup(
    name = 'infinite_context',
    version = '2.0.6',
    author = 'OPENSAPI',
    packages=find_packages(),
    install_requires=[
        'perpetual-context',
        'certifi',
        'requests',
        'lxml',
        'pandas',
        'pillow',
        'numpy',
        'paddlepaddle',
        'paddleocr',
        'opencv-python',
        'moviepy',
        'SpeechRecognition',
        'ffmpeg-python',
        'pydub',
        'docx2txt',
        'youtube-transcript-extractor'
    ],
    url = 'https://github.com/sapiens-technology/InfiniteContext',
    license = 'Proprietary Software'
)
