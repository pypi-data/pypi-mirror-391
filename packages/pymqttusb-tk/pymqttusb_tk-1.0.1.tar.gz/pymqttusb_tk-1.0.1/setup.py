import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymqttusb_tk",
    version="1.0.1",
    author="Didier Orlandi",
    author_email="didier.orlandi06@gmail.com",
    description="Connexion USB <-> MQTT (SSL ou WSS) avec interface Tkinter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/didierorlandi/pymqttusb_tk",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications",
        "Intended Audience :: Education",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Environment :: X11 Applications :: GTK",
    ],
    python_requires=">=3.6",
    install_requires=[
        "paho-mqtt<2.0.0",
        "pyserial>=3.5",
    ],
)
