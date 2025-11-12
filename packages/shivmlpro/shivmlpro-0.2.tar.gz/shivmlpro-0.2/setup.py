from setuptools import setup, find_packages

setup(
    name='shivmlpro',
    version='0.2',
    author='Shivam Vinod Chaudhari',
    author_email='shivam7744998850@gmail.com',
    description='An all-in-one ML automation library for supervised, unsupervised, and reinforcement learning.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shivchaudhari-ai/shivmlpro',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'matplotlib',
        'xgboost'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
