from setuptools import setup, find_packages

setup(
    name="django_unfold_conf",
    version="0.71.5",
    packages=find_packages(where="django-unfold/src"),
    package_dir={"": "django-unfold/src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    description="This is a package forked from https://unfoldadmin.com/ that I make some adjustments, early I fully credit the original author.",
)