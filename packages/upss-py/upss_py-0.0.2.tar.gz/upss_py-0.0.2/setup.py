from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='upss-py',
    version='0.0.2',
    author='kosinak',
    author_email='dargas020@gmail.com',
    description='Library for UPSS',
    license="MIT-License",
    license_files=["LICENSE"],
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['cryptography>=46.0.3'],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent'
    ],
    keywords='upss protocol ',
    project_urls={
        'GitHub': 'https://github.com/Dargas020/upss-python'
    },
    python_requires='>=3.9'
)
