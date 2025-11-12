"""Setup script for sheep-herding-rl package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='sheep-herding-rl',
    version='1.0.3',
    author='ferip',
    description='A reinforcement learning environment for sheep herding simulation with PPO, SAC, and TD3 algorithms',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/dzijo/ferit-hackathon',  # Update if needed
    packages=find_packages(exclude=['tests', 'tests.*', 'images', '__pycache__']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'pygame',
        'numpy',
        'pillow',
        'scipy',
        'pyyaml',
        'matplotlib',
        'torch>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov',
            'black',
            'flake8',
            'mypy',
        ],
    },
    # No console scripts defined yet
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.yml', '*.json'],
    },
    keywords='reinforcement-learning, simulation, ppo, sac, td3, sheep-herding',
    project_urls={
        'Bug Reports': 'https://github.com/dzijo/ferit-hackathon/issues',
        'Source': 'https://github.com/dzijo/ferit-hackathon',
    },
)
