from setuptools import setup

setup(
    name="agenda-entrenos",
    version="0.1.0",
    description="Una agenda para entrenamientos.",
    author=["Cristian Ruiz", "Alejandro Mata", "Unai Alvarez", "Eleder Martin"],
    author_email=["cristian.ruiz@alumni.mondragon.edu", "alejandro.mata@alumni.mondragon.edu", "unai.alvarez@alumni.mondragon.edu", "eleder.martin@alumni.mondragon.edu"],
    py_modules=["core", "excepciones", "queries", "utils", "test"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    url="https://test.pypi.org/project/agenda-entrenos/",
    long_description=open("README.md", encoding="utf-8").read() if __import__('os').path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    license="MIT",
)
