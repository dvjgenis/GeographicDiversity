# GeographicDiversity_Package/Solar_Package/setup.py

from setuptools import setup, find_packages

setup(
    name='solar_geographic_diversity',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'requests',
        'haversine',
        'matplotlib',
        'seaborn',
        'folium',
        'plotly',
        'fpdf',
        'openpyxl'
        # Add more if needed
    ],
    author='Dulf Vincent Genis',
    author_email='e1818585@ameren.com',
    description='Solar Geographic Diversity Analysis',
    url='https://github.ameren.com/iCenter/NREL_Diversity_Performance_Analysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)