#
# Copyright (c) SAS Institute Inc.
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
#


"""
Module for parsing patches.xml from the repository metadata.
"""

__all__ = ('PatchesXml', )

# import stable api
from rpath_xmllib import api1 as xmllib

from patchxml import PatchXml
from xmlcommon import XmlStreamedParser, SlotNode
from errors import UnknownElementError

class _Patches(SlotNode):
    """
    Python representation of patches.xml from the repository metadata.
    """
    __slots__ = ()

class _PatchElement(SlotNode):
    """
    Parser for patch element of patches.xml.
    """

    WillYield = True
    __slots__ = ('id', 'checksum', 'checksumType', 'location', '_parser',
        'parseChildren')

    # All attributes are defined in __init__ by iterating over __slots__,
    # this confuses pylint.
    # W0201 - Attribute $foo defined outside __init__
    # pylint: disable-msg=W0201

    def addChild(self, child):
        """
        Parse children of patch element.
        """

        if child.getName() == 'checksum':
            self.checksum = child.finalize()
            self.checksumType = child.getAttribute('type')
        elif child.getName() == 'location':
            self.location = child.getAttribute('href')
        else:
            raise UnknownElementError(child)

    def finalize(self):
        self._parser = PatchXml(None, self.location)
        self.parseChildren = self._parser.parse
        return self

class PatchesXml(XmlStreamedParser):
    """
    Handle registering all types for parsing patches.xml.
    """

    def _registerTypes(self):
        """
        Setup databinder to parse xml.
        """

        self._databinder.registerType(_Patches, name='patches')
        self._databinder.registerType(_PatchElement, name='patch')
        self._databinder.registerType(xmllib.StringNode, name='checksum')
