from setuptools import setup

setup(
    name='unrobot',
    version='0.1.0',    
    description='unrobot is a simple robot descriptor loader and toolkit for robotics applications.',
    url='https://github.com/Churros98/unrobot',
    author='Sofiane',
    author_email='Churros98@example.com',
    license='MIT',
    packages=['unrobot'],
    install_requires=['pydantic==2.12.4'],
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
