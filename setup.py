from distutils.core import setup


github_url = 'https://github.com/gistart/prometheus-push-client'


setup(
    name="prometheus_push_client",
    version="0.0.1",
    author="gistart",
    author_email="gistart@yandex.ru",
    description="TODO",
    long_description="TODO",
    long_description_content_type="text/markdown",
    url=github_url,
    license="MIT",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    python_requires=">=3.6",
    packages=[
        "prometheus_push_client"
    ],
    install_requires=[
        "prometheus_client",
    ],
    extras_require={
        "aiohttp": [
            "aiohttp"
        ],
        "test": [
            "pytest",
            "pytest-asyncio",
            "aiohttp",
            "requests",
        ],
    }
)