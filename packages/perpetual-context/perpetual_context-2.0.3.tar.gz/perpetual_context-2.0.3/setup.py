from setuptools import setup, find_packages

setup(
    name = 'perpetual_context',
    version = '2.0.3',
    author = 'OPENSAPI',
    packages=find_packages(),
    install_requires=[
        'count-tokens',
        'requests',
        'numpy',
        'openpyxl',
        'pandas',
        'statistics',
        'certifi',
        'tabulate',
        'PyPDF2',
        'PyMuPDF',
        'python-docx',
        'python-pptx',
        'beautifulsoup4',
        'youtube-search-python',
        'youtube-transcript-api',
        'pillow',
        'easyocr',
        'torch',
        'torchvision',
        'webcolors==1.13',
        'scikit-learn',
        'pydub',
       ' SpeechRecognition'
    ],
    url = 'https://github.com/sapiens-technology/PerpetualContext',
    license = 'Proprietary Software'
)
