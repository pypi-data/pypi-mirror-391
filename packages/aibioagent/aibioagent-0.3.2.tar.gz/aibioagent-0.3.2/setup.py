"""
Setup configuration for AI Scientist for Bioimaging package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text(encoding="utf-8")

setup(
    name="aibioagent",
    version="0.3.2",
    author="Chen Li",
    author_email="chenli970701@gmail.com",  
    description="A multi-agent AI system for biomedical imaging research with RAG, image analysis, and paper review",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chenli-git/AI_scientist_for_bioimaging",
    project_urls={
        "Bug Tracker": "https://github.com/chenli-git/AI_scientist_for_bioimaging/issues",
        "Documentation": "https://github.com/chenli-git/AI_scientist_for_bioimaging#readme",
        "Source Code": "https://github.com/chenli-git/AI_scientist_for_bioimaging",
    },
    packages=find_packages(exclude=["tests", "tests.*", "data.papers", "data.uploads", "test_images"]),
    py_modules=["aibioagent"],  # Include the single-file module
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: LangChain",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Core LLM and LangChain
        "openai>=1.43.0,<2.0.0",
        "langchain>=0.3.0,<2.0.0",
        "langchain-core>=0.3.0,<2.0.0",
        "langchain-community>=0.3.0,<1.0.0",
        "langchain-openai>=0.1.0,<2.0.0",
        "langchain-text-splitters>=0.3.0,<2.0.0",
        # Vector Store
        "chromadb>=0.5.3,<2.0.0",
        # PDF and Document Processing
        "pypdf>=4.2.0,<7.0.0",
        "docling>=2.50.0,<3.0.0",
        "tiktoken>=0.7.0,<1.0.0",
        # Image Processing
        "scikit-image>=0.24.0,<1.0.0",
        "tifffile>=2025.1.10",
        "pillow>=10.0.0,<12.0.0",
        "opencv-python>=4.8.0,<5.0.0",
        # Data Processing
        "numpy>=1.26.0,<3.0.0",
        "pandas>=2.2.0,<3.0.0",
        # Web Scraping
        "beautifulsoup4>=4.14.0,<5.0.0",
        "playwright>=1.50.0,<2.0.0",
        "requests>=2.32.0,<3.0.0",
        # UI
        "gradio>=4.44.0,<6.0.0",
        # Config & Utilities
        "python-dotenv>=1.0.1,<2.0.0",
        "rich>=13.7.0,<14.0.0",
        "tenacity>=8.3.0,<9.0.0",
        "pydantic>=2.0.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0,<9.0.0",
            "pytest-mock>=3.14.0,<4.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-scientist=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "artificial-intelligence",
        "biomedical-imaging",
        "multi-agent-systems",
        "rag",
        "langchain",
        "image-analysis",
        "paper-review",
        "microscopy",
        "computer-vision",
        "research-assistant",
    ],
)
