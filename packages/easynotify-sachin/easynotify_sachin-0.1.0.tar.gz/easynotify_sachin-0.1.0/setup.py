from setuptools import setup, find_packages

setup(
    name="easynotify-sachin",
    version="0.1.0",
    author="Sachin Rendla",
    author_email="youremail@example.com",
    description="A simple notification helper for AWS SNS or email.",
    packages=find_packages(),
    install_requires=[
        "boto3",
    ],
    python_requires=">=3.6",
)

