from setuptools import setup, find_packages

setup(
    name="psd-covariance",
    version='0.1.0',
    description='Computes several covariance matrix estimators that ensure positive semi-definiteness (PSD).',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Jesper Cremers',
    author_email='Jesper.Cremers@vub.be',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'joblib',
        'scikit-learn',
        'pandas',
    ],
    python_requires='>=3.7',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)