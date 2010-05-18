#
# Copyright (c) 2008-2010 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

"""
Module for parsing patches.xml from the repository metadata.
"""

__all__ = ('PatchesXml', )

# import stable api
from rpath_xmllib import api1 as xmllib

from patchxml import PatchXml
from xmlcommon import XmlFileParser, SlotNode
from errors import UnknownElementError

class _Patches(SlotNode):
    """
    Python representation of patches.xml from the repository metadata.
    """

    __slots__ = ()

    def addChild(self, child):
        """
        Parse children of patches element.
        """

        # W0212 - Access to a protected member _parser of a client class
        # pylint: disable-msg=W0212

        if child.getName() != 'patch':
            raise UnknownElementError(child)
        child.id = child.getAttribute('id')
        child._parser = PatchXml(None, child.location)
        child.parseChildren = child._parser.parse
        SlotNode.addChild(self, child)

    def getPatches(self):
        """
        Get a list of all patches in the repository.
        @return list of _PatchElement instances
        """

        return self.getChildren('patch')


class _PatchElement(SlotNode):
    """
    Parser for patch element of patches.xml.
    """

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

class PatchesXml(XmlFileParser):
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
