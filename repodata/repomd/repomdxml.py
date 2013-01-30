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
Module for parsing repomd.xml files from the repository metadata.
"""

__all__ = ('RepoMdXml', )

# use stable api
from rpath_xmllib import api1 as xmllib

from packagexml import _Package
from primaryxml import PrimaryXml
from patchesxml import PatchesXml
from filelistsxml import FileListsXml
from updateinfoxml import UpdateInfoXml
from xmlcommon import XmlFileParser, SlotNode
from errors import UnknownElementError

class _RepoMd(SlotNode):
    """
    Python representation of repomd.xml from the repository metadata.
    """

    __slots__ = ('revision', )
    class Package(_Package):
        pass
    PackageFactory = Package

    def addChild(self, child):
        """
        Parse children of repomd element.
        """

        # W0212 - Access to a protected member _parser of a client class
        # pylint: disable-msg=W0212

        name = child.getName()
        if name == 'revision':
            self.revision = child.finalize()
        elif name == 'data':
            child.type = child.getAttribute('type')
            if child.type == 'patches':
                child._parser = PatchesXml(None, child.location)
                child.iterSubnodes = child._parser.parse
            elif child.type == 'primary':
                child._parser = PrimaryXml(None, child.location)
                child._parser.PackageFactory = self.PackageFactory
                child._parser._registerTypes()
                child.iterSubnodes = child._parser.parse
            elif child.type == 'filelists':
                child._parser = FileListsXml(None, child.location)
                child._parser.PackageFactory = self.PackageFactory
                child._parser._registerTypes()
                child.iterSubnodes = child._parser.parse
            elif child.type == 'updateinfo':
                child._parser = UpdateInfoXml(None, child.location)
                child.iterSubnodes = child._parser.parse
            SlotNode.addChild(self, child)
        elif name == 'tags':
            # I know this tag exists, but don't care about it for now. - AG
            pass
        else:
            # raise UnknownElementError(child)
            # I don't want this to fail. - AG
            pass

    def getRepoData(self, name=None):
        """
        Get data elements of repomd xml file.
        @param name: filter by type of node
        @type name: string
        @return list of nodes
        @return single node
        @return None
        """

        if not name:
            return self.getChildren('data')

        for node in self.getChildren('data'):
            if node.type == name:
                return node

        return None


class _RepoMdDataElement(SlotNode):
    """
    Parser for repomd.xml data elements.
    """
    __slots__ = ('location', 'checksum', 'checksumType', 'timestamp',
                 'openChecksum', 'openChecksumType', 'databaseVersion',
                 'size', 'openSize', 'type', '_parser', 'iterSubnodes', )

    # All attributes are defined in __init__ by iterating over __slots__,
    # this confuses pylint.
    # W0201 - Attribute $foo defined outside __init__
    # pylint: disable-msg=W0201

    def addChild(self, child):
        """
        Parse children of data element.
        """

        name = child.getName()
        if name == 'location':
            self.location = child.getAttribute('href')
        elif name == 'checksum':
            self.checksum = child.finalize()
            self.checksumType = child.getAttribute('type')
        elif name == 'timestamp':
            self.timestamp = child.finalize()
        elif name == 'open-checksum':
            self.openChecksum = child.finalize()
            self.openChecksumType = child.getAttribute('type')
        elif name == 'database_version':
            self.databaseVersion = child.finalize()
        elif name == 'size':
            self.size = child.finalize()
        elif name == 'open-size':
            self.openSize = child.finalize()
        else:
            raise UnknownElementError(child)


class RepoMdXml(XmlFileParser):
    """
    Handle registering all types for parsing repomd.xml file.
    """
    RepoMdFactory = _RepoMd

    def _registerTypes(self):
        """
        Setup databinder to parse xml.
        """

        self._databinder.registerType(self.RepoMdFactory, name='repomd')
        self._databinder.registerType(_RepoMdDataElement, name='data')
        self._databinder.registerType(xmllib.StringNode, name='revision')
        self._databinder.registerType(xmllib.StringNode, name='checksum')
        self._databinder.registerType(xmllib.IntegerNode, name='timestamp')
        self._databinder.registerType(xmllib.StringNode, name='open-checksum')
        self._databinder.registerType(xmllib.StringNode, name='database_version')
