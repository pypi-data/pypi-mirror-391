from setuptools import setup, find_packages

setup(
    name="easynotify-sachin",
    version="0.1.1",
    author="Sachin Rendla",
    author_email="sachin@nci.com",
    description="A simple notification helper for AWS SNS or email.",
    packages=find_packages(),
    install_requires=[
        "boto3",
    ],
    python_requires=">=3.6",
)

