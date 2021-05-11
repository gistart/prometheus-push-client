import setuptools


# version
with open("./prometheus_push_client/version.py") as fd:
    exec(fd.read())


# description
github_url = 'https://github.com/gistart/prometheus-push-client'

readme_lines = []
with open('README.md') as fd:
    readme_lines = filter(None, fd.read().splitlines())
readme_lines = list(readme_lines)[:10]
readme_lines.append('Read more at [github page](%s).' % github_url)
readme = '\n\n'.join(readme_lines)


# requirements
extras_require = {}
extras_require["http"] = [
    "aiohttp<4",
    "requests<3",
]
extras_require["test"] = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-mock",
    *extras_require["http"]
]
extras_require["dev"] = [
    "ipython",
    "setuptools",
    "wheel",
    "twine",
    *extras_require["test"]
]


# setup
setuptools.setup(
    name="prometheus_push_client",
    version=__version__,
    author="gistart",
    author_email="gistart@yandex.ru",
    description="Push Prometheus metrics to VictoriaMetrics or other exporters",
    long_description=readme,
    long_description_content_type="text/markdown",
    url=github_url,
    packages=setuptools.find_packages(include=["prometheus_push_client*"]),
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "prometheus_client>=0.4.0",
    ],
    extras_require=extras_require,
)