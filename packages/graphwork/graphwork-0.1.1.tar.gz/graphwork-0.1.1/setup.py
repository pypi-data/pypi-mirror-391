from setuptools import setup, find_packages

setup(
    name="graphwork",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={"my_package": ["templates/*.html"]},
    description="A simple package with HTML files included.",
    author="schz",
    python_requires=">=3.8",
    install_requires = [
        "opencv-python",
        "pillow",
        "numpy",
        "librosa",
        "matplotlib",
        "pandas",
        "scikit-learn",
        "networkx",
        "scipy"
    ]

)
