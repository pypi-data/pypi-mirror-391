from setuptools import setup, find_packages

# --- NEW: Read the README.md file ---
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
# --- END NEW ---

setup(
    name="iloko-cli",
    version="1.5.1",  # <-- IMPORTANT: Change this version number!
    description="A command-line interpreter for the ILOKO esolang.",
    
    # --- NEW: Add the long description from README ---
    long_description=long_description,
    long_description_content_type="text/markdown",
    # --- END NEW ---
    
    author="Christian Andrei",
    packages=find_packages(),
    # This is the most important part!
    # It tells pip to create a command named 'iloko'
    # that runs the 'main' function inside 'iloko_cli/cli.py'
    entry_points={
        'console_scripts': [
            'iloko = iloko_cli.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
