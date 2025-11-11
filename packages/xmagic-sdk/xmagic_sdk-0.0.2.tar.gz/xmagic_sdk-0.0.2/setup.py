import setuptools

install_requires = [
   "setuptools",
   "pydantic",
   "numpy",
   "requests",
   "python-dotenv",
   "click",
   "bson",
   "fastapi",
   "uvicorn",
   "httpx",
]

setuptools.setup(
   name='xmagic-sdk',
   version="0.0.2",
   author='Marcos Rivera Martínez, Glenn Ko, Subhash G N, Jatin Sarda',
   author_email='marcos.rm@stochastic.ai, glenn@stochastic.ai, subhash.gn@stochastic.ai',
   description='',
   long_description_content_type="text/markdown",
   url="",
   classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent"
   ],
   package_dir={"": "src"},
   packages=setuptools.find_packages(where="src"),
   python_requires=">=3.9",
   install_requires=install_requires,
   entry_points={
        "console_scripts": [
            "xmagic = xmagic_sdk.cli:xmagic"
        ]
   }  
)