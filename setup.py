from setuptools import setup, find_packages

setup(name='re_process',
      version='0.1',
      description=
      'A tool for generating dependency graphs from code repositories.',
      author='Advanced Engineering School',
      author_email='eliwhatthe@gmail.com',
      packages=find_packages(),
      package_data={
          'data': ['path.json'],
      },
      url='https://github.com/kezouke/TestGena',
      license='MIT',
      keywords='dependency-graph code-analysis',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
      ],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown')
