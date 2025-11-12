from setuptools import setup, find_packages

setup(
    name="textron-logging",
    version="1.0.2",
    description="Minimal uniform logging for Textron apps (console + optional Azure Monitor)",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],  # stdlib only; Azure is optional
    extras_require={
        "azure": [
            "opentelemetry-sdk>=1.24.0",
            "azure-monitor-opentelemetry-exporter>=1.0.0"
        ]
    },
)
