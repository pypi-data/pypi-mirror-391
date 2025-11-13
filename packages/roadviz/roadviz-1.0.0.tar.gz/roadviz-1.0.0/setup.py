from setuptools import setup, find_packages

setup(
    name='roadviz',
    version='1.0.0',
    author='Anubhav Shukla',
    author_email='anubhavshukla870@gmail.com',
    description='A Plotly-based visualization library for road accident data analysis.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'plotly',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
