from setuptools import find_packages, setup

setup(
    name="lazy-crow-nest",
    version="1.0.0",
    url="https://gitea.livelace.ru/livelace/lazy-crow-nest.git",
    author="Oleg Popov",
    author_email="o.popov@livelace.ru",
    license="BSD",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "lazy-crow-nest=lcn.__main__:main"
        ],
    }
)