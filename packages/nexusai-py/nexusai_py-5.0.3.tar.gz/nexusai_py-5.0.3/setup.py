from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nexusai-py",
    version="5.0.3",
    author="Nexus API",
    author_email="drezus.nexus@gmail.com",
    description="A comprehensive Python wrapper for the Nexus AI API - Image Generation, Text Generation, and Akinator Game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://nexus.drexus.xyz",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/nexusai-py/issues",
        "Documentation": "https://nexus.drexus.xyz/docs",
        "Source Code": "https://github.com/yourusername/nexusai-py",
        "Discord": "https://discord.gg/qdgkMkQbnt",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
        "examples": [
            "Pillow>=8.0",
        ],
    },
    keywords="ai api nexus image-generation text-generation gemini gpt-4 llama akinator artificial-intelligence machine-learning",
    include_package_data=True,
    zip_safe=False,
)
