from setuptools import setup, find_packages

setup(
    name='event_listener',
    version='0.1',
    packages=find_packages(),
    author='Aniket Tiratkar',
    author_email='atiratkar@gmail.com',
    description='A kafka event listener to make action dispatching easier',
    url='https://github.com/aniketpt/event_listener',
    install_requires=open('requirements.txt').read().split()
)
