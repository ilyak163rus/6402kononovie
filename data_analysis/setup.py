from setuptools import setup, find_packages

setup(
    name="analysis",
    version="0.1",
    author="Ilya Kononov",
    author_email="ilyakononovv@mail,ru",
    packages=['analysis'],
    install_requires=[
        'pytrends',
        'pandas',
        'matplotlib',
        'scipy',
        'statsmodels',
        'openpyxl',
        'jupyter'
    ],
)