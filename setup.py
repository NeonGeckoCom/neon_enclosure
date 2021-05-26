# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
from os import getenv, path


def get_requirements(requirements_filename: str):
    requirements_file = path.join(path.abspath(path.dirname(__file__)), "requirements", requirements_filename)
    with open(requirements_file, 'r', encoding='utf-8') as r:
        requirements = r.readlines()
    requirements = [r.lower().strip() for r in requirements if r.lower().strip() and not r.strip().startswith("#")]
    print(requirements)
    if getenv("GITHUB_TOKEN"):
        for i in range(0, len(requirements)):
            r = requirements[i]
            if "github.com" in r:
                requirements[i] = r.replace("github.com", f"{getenv('GITHUB_TOKEN')}@github.com")
    return requirements


with open("README.md", "r") as f:
    long_description = f.read()

with open("./version.py", "r", encoding="utf-8") as v:
    for line in v.readlines():
        if line.startswith("__version__"):
            if '"' in line:
                version = line.split('"')[1]
            else:
                version = line.split("'")[1]

setup(
    name='neon-enclosure',
    version=version,
    packages=find_packages(),
    url='https://github.com/NeonGeckoCom/neon-enclosure',
    license='NeonAI License v1.0',
    install_requires=get_requirements("requirements.txt"),
    author='Neongecko',
    author_email='developers@neon.ai',
    description=long_description,
    entry_points={
        'console_scripts': [
            'neon_enclosure_client=neon_enclosure.client.enclosure.__main__:main'
        ]
    }
)
