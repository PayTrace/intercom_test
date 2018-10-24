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

from numbers import Number
from pyasn1.codec.der import encoder as der_encoder
from pyasn1.type import univ
from .types import JSONValue, JSONObject, KeyValuePair

def kvp(k, v):
    result = KeyValuePair()
    result['key'] = k
    result['value'] = asn1(v)
    return result

def asn1(value):
    visited_objs = set()
    
    def step(value):
        if id(value) in visited_objs:
            raise ValueError("Cannot convert cyclical object graph")
        
        result = JSONValue()
        if isinstance(value, str):
            result['strval'] = value
        elif isinstance(value, Number):
            result['numval'] = value
        elif value is None:
            result['nullval'] = None
        elif isinstance(value, bool):
            result['boolval'] = value
        elif isinstance(value, JSONObject):
            visited_objs.add(id(value))
            result['objval'] = value
        elif callable(getattr(value, 'items', None)):
            visited_objs.add(id(value))
            result['objval'] = JSONObject()
            result['objval'].extend(
                kvp(k, v)
                for k, v
                in value.items()
            )
        elif isinstance(value, (list, tuple)):
            if isinstance(value, list):
                visited_objs.add(id(value))
            result['arrval'] = univ.SequenceOf()
            result['arrval'].extend(step(item) for item in value)
          
        return result
    
    return step(value)

def asn1_der(value):
    return der_encoder.encode(asn1(value))
