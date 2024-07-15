from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="specialeffects",
    version="0.1",
    description="Package for orchestrating light, sound, and custom special effects.",
    long_description=readme(),
    keywords="lights sounds effects",
    author="Cody VanZandt",
    author_email="cody.a.vanzandt@gmail.com",
    license="CC0",
    packages=["specialeffects"],
    install_requires=["playsound3", "python-kasa"],
    include_package_data=True,
    zip_safe=False,
)
