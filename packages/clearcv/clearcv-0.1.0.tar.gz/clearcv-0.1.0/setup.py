from setuptools import setup, find_packages


setup(
name="clearcv",
version="0.1.0",
description="ClearCV — a lightweight, NumPy-based computer vision toolkit built in Python.",
long_description=open('README.md', encoding='utf-8').read(),
long_description_content_type='text/markdown',
author='Your Name',
author_email='you@example.com',
packages=find_packages(exclude=('tests',)),
install_requires=['numpy'],
extras_require={
'extras': ['imageio', 'matplotlib']
},
python_requires='>=3.8',
include_package_data=True,
license='MIT',
)