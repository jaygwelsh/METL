from setuptools import setup, find_packages

setup(
    name='metl',
    version='0.1.0',
    description='Metadata Embedding and Tracking Ledger',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'cryptography==41.0.3',
        'pikepdf==8.7.0',
        'Pillow>=10.0.1',
        'python-docx==0.8.11',
        'click==8.1.7',
        'PyQt5==5.15.9',
        'pyyaml==6.0',
        'pytest==7.4.0',
        'pytest-cov==4.1.0'
    ],
    entry_points={
        'console_scripts': [
            'metl=interfaces.cli:cli'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
