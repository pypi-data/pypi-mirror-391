from setuptools import setup, find_packages

setup(
    name="django_unfold_conf",
    version="0.71.3",
    packages=find_packages(where="django-unfold/src"),
    package_dir={"": "django-unfold/src"},
    install_requires=[],
    description="This is a package forked from https://unfoldadmin.com/ that I make some adjustments, earby I fully credit the original author.",
)
