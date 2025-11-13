##install dependencies
pip install setuptools wheel twine

##build package
python setup.py sdist bdist_wheel

##upload to pypi
twine upload -u __token__ -p pypi-AgEIcHlwaS5vcmcCJGVhYTdkZGIyLTRhNzktNDJlOS05OGI2LTVkMzU5YWM5MDI2NwACKlszLCJhMTE2MWM3Ny1mODZmLTRkY2MtOWJhNy0wMDUxNGQ5NmM2MDAiXQAABiAbwTTCEJCfXPbH4v9kd2PXLoaxsDgYzQuIl3KBeIxiYA dist/*

##install sdk
pip install -U -i https://pypi.org/simple/ ising-sdk