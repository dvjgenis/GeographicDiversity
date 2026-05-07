# GeographicDiversity_Package/Wind_Package/setup.py

from setuptools import setup, find_packages

setup(
    name='wind_geographic_diversity',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'meteostat',
        'matplotlib',
        'folium',
        'plotly',
        'haversine',
        'fpdf',
        'seaborn',
        'requests',
        'openpyxl'
        # Add more if needed
    ],
    author='Dulf Vincent Genis',
    author_email='e1818585@ameren.com',
    description='Wind Geographic Diversity Analysis',
    url='https://github.ameren.com/iCenter/GeographicDiversity',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # or your chosen license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)