##install dependencies
pip install setuptools wheel twine

##build package
python setup.py sdist bdist_wheel

##upload to pypi
twine upload dist/*