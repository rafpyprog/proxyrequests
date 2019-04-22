from setuptools import setup


requires = [
    "beautifulsoup4>=4.7.1",
    "dateparser>=0.7.1",
    "lxml>=4.3.3",
    "requests>=2.21.0",
]

setup(
    name="proxyrequests",
    version="0.0.1",
    install_requires=requires,
    packages=["proxyrequests"],
)
