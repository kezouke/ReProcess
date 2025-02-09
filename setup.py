from setuptools import setup, find_packages

setup(name='reprocess',
      version='0.3',
      description='A tool for processing code repositories.',
      author='Advanced Engineering School',
      author_email='eliwhatthe@gmail.com',
      packages=find_packages(),
      package_data={
          'data': ['path.json'],
      },
      url='https://github.com/kezouke/ReProcess',
      license='MIT',
      keywords='dependency-graph code-analysis',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
      ],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown')