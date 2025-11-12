from setuptools import setup

setup(
    name="textron-logging",
    version="1.0.6",
    description="Minimal uniform logging for Textron apps (console + optional Azure Monitor)",
    author="Your Name",
    packages=["textron_logging"],   # ✅ FORCE include the module
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "azure": [
            "opentelemetry-sdk>=1.24.0",
            "azure-monitor-opentelemetry-exporter>=1.0.0"
        ]
    },
)
