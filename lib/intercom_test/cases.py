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

from base64 import b64encode
from codecs import ascii_decode
import hashlib
import itertools
import yaml
from .exceptions import DataParseError
from .json_asn1.convert import asn1_der
from .utils import def_enum
from .yaml_tools import value_from_event_stream as _value_from_events

def hash_from_fields(test_case):
    """Compute a string hash from any acyclic, JSON-ic :class:`dict`
    
    :param dict test_case: test case data to be hashed
    :returns: a repeatably generatable hash of *test_case*
    :rtype: str
    
    The hash is computed by encoding *test_case* in ASN1 DER (see
    :const:`.json_asn1.types.ASN1_SOURCE` for the ASN1 syntax of the data
    format), then hashing with SHA-256, and finally Base64 encoding to get the
    result.
    
    Note that this function hashes **all** key/value pairs of *test_case*.
    """
    key = test_case if isinstance(test_case, dict) else dict(test_case)
    key = asn1_der(key)
    key = hashlib.sha256(key).digest()
    key = ascii_decode(b64encode(key))[0]
    return key

class IdentificationListReader:
    """Utility class to read case ID and associated events from a YAML event stream
    
    This class is used internally to identify test cases when correlating the
    test case with existing augmentation data for editing.  In that case, both
    the Python-native representation of the test case (for
    :func:`hash_from_fields`) and the YAML event stream for the key/value pairs
    (to preserve as much format from the source file) are needed.
    """
    @def_enum
    def State():
        return "header content tail"
    
    def __init__(self, key_fields):
        super().__init__()
        self._key_fields = frozenset(key_fields)
        self._state = self.State.header
    
    def read(self, event):
        self._event = event
        return getattr(self, '_read_from_' + self._state.name)(event)
    
    def _read_from_header(self, event):
        if not isinstance(event, yaml.NodeEvent):
            pass
        else:
            self._expect(yaml.SequenceStartEvent)
            self._state = self.State.content
            self._depth = 0
            self._ignoring_entry = 0
    
    def _read_from_content(self, event):
        emit = False
        if isinstance(event, yaml.CollectionStartEvent):
            if self._depth == 0:
                self._accumulated_events = []
                self._accumulating_mapping = isinstance(event, yaml.MappingStartEvent)
                self._reading_assoc_value = False
            self._depth += 1
        elif isinstance(event, yaml.CollectionEndEvent):
            self._depth -= 1
            if self._depth == 0:
                emit = True
        
        if self._depth < 0:
            self._state = self.State.tail
        elif self._ignoring_entry:
            if self._depth == 1:
                self._ignoring_entry -= 1
        elif (
            self._depth == 1
            and not self._reading_assoc_value
            and isinstance(event, yaml.ScalarEvent)
            and self._accumulating_mapping
        ):
            if event.value in self._key_fields:
                self._accumulated_events.append(event)
                self._reading_assoc_value = True
            else:
                self._ignoring_entry = 1
                # and don't append event to self._accumulated_events
        elif (
            self._depth == 2
            and not self._reading_assoc_value
            and isinstance(event, yaml.CollectionStartEvent)
            and self._accumulating_mapping
        ):
            self._ignoring_entry = 2 # we have to wait for self._depth to drop back to 1 *twice* to ignore this key and its corresponding value
            # and don't append event to self._accumulated_events
        else:
            self._accumulated_events.append(event)
            self._reading_assoc_value = False
        
        if emit:
            events = self._accumulated_events
            del self._accumulated_events
            return (self._key_from_events(events), events[1:-1])
    
    def _read_from_tail(self, event):
        pass
    
    def _key_from_events(self, events):
        given_values = _value_from_events(events)
        return hash_from_fields(dict(
            entry for entry in given_values.items()
            if entry[0] in self._key_fields
        ))
    
    def _expect(self, event_type):
        if isinstance(self._event, event_type):
            return
        raise DataParseError(
            "{} where {} expected"
            " in line {} while reading {}".format(
                type(self._event).__name__,
                event_type.__name__,
                self._event.start_mark.line,
                self._state.name.replace('_', ' '),
            )
        )
