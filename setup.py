from setuptools import setup, find_packages


setup(
    name="tasks",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "annotated-types==0.7.0",
        "click==8.1.7",
        "colorama==0.4.6",
        "pydantic==2.10.2",
        "pydantic_core==2.27.1",
        "typing_extensions==4.12.2",
        "pytest==8.3.3",
    ],
    entry_points={
        "console_scripts": [
            "tasks=src.main:app",
        ],
    },
    description="CLI-приложение для управления задачами",
    python_requires='>=3.10',
)
