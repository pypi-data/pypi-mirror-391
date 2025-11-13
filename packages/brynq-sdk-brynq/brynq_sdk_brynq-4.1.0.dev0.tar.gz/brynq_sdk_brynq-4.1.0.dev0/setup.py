from setuptools import find_namespace_packages, setup

setup(
    name='brynq_sdk_brynq',
    version='4.1.0.dev0',
    description='BrynQ SDK for the BrynQ.com platform',
    long_description='BrynQ SDK for the BrynQ.com platform',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'requests>=2,<=3',
        'pandera>=0.26.0,<=1.0.0'
    ],
    zip_safe=False,
)
