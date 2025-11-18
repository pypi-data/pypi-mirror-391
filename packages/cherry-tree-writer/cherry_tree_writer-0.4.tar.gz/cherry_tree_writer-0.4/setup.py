from setuptools import find_packages, setup

with open("README.md", "r") as readme:
      description = readme.read()

setup(name='cherry_tree_writer',
      version='0.4',
      description='Minimalist Python library for writting cherrytree document',
      author='Guilhem RIOUX',
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      long_description=description,
      long_description_content_type="text/markdown"
     )
