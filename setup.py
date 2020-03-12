from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(name='bcore',
      version='0.0.1',
      description='Train subjects in tasks',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/balajisriram/BCore',
      author='Balaji Sriram',
      author_email='balajisriram@gmail.com',
      license='NA',
      packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*"]),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        ],
      zip_safe=False)