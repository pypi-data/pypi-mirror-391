from setuptools import setup

setup(
    name="spritemaker",
    version="1.0.0",
    py_modules=["spritemaker"],
    install_requires=["Pillow"],
    author="Your Name",
    author_email="youremail@example.com",
    description="Advanced single-file Python sprite library",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/spritemaker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
