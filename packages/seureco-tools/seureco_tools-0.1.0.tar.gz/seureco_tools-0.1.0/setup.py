from setuptools import setup, find_packages

setup(
    name="seureco_tools",
    version="0.1.0",
    author="Hajar",
    author_email="hajar.sriri@etu.univ-paris1.fr",
    description="IODE package for data preprocessing",
    packages=find_packages(),  # trouve automatiquement le dossier seureco_tools
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy"
    ],
    python_requires=">=3.8",
)
