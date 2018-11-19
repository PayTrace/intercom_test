# Copyright 2018 PayTrace, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='intercom_test',
    version='1.0dev',
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    use_2to3=False,
    description='Inter-component testing support code for "Interface By Example"',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Richard T. Weeks',
    author_email='rtweeks21@gmail.com',
    license='Apache License 2.0',
    install_requires=[
        'PyYAML >=3.11, <4',
        'pyasn1 >=0.4.2, <1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Other Audience",
        "Topic :: Software Development :: Testing",
    ],
)
