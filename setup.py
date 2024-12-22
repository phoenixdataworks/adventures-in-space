from setuptools import setup, find_packages

setup(
    name="adventures-in-space",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0",
        "asyncio>=3.4.3",
    ],
    entry_points={
        "console_scripts": [
            "adventures-in-space=main:asyncio.run(main())",
        ],
    },
)
