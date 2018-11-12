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

"""Intercomponent Testing (Interface by Example)
***************************************************

The main functionality of this package is accessible through
:class:`.InterfaceCaseProvider`.  :class:`.CaseAugmenter` and it's predefined
subclasses, typically necessary for testing *service provider* code, are also
available from this module.  These classes come from :mod:`.framework` but are
imported into the base namespace of this package for ease of use.

For cross-language compatibility, the ASN1 source for encoding JSON values is
available from this module as :const:`JSON_ASN1_SOURCE`.
"""

from .framework import (
    InterfaceCaseProvider,
    CaseAugmenter,
    HTTPCaseAugmenter,
    RPCCaseAugmenter,
)
from .json_asn1.types import ASN1_SOURCE as JSON_ASN1_SOURCE
