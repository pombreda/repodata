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
Module for parsing patch-*.xml files from the repository metadata.
"""

__all__ = ('PatchXml', )

from rpath_xmllib import api1 as xmllib

from xmlcommon import XmlFileParser, SlotNode
from packagexml import PackageXmlMixIn
from errors import UnknownElementError

class _Patch(SlotNode):
    """
    Python representation of patch-*.xml from the repository metadata.
    """

    # R0902 - Too many instance attributes
    # pylint: disable-msg=R0902

    __slots__ = ('name', 'summary', 'description', 'version',
                 'release', 'requires', 'recommends', 'rebootNeeded',
                 'licenseToConfirm', 'packageManager', 'category',
                 'packages', 'provides', 'supplements', 'conflicts',
                 'obsoletes')

    # All attributes are defined in __init__ by iterating over __slots__,
    # this confuses pylint.
    # W0201 - Attribute $foo defined outside __init__
    # pylint: disable-msg=W0201

    def addChild(self, child):
        """
        Parse children of patch element.
        """

        # R0912 - Too many branches
        # pylint: disable-msg=R0912

        n = child.getName()
        if n == 'yum:name':
            self.name = child.finalize()
        elif n == 'summary':
            if child.getAttribute('lang') == 'en':
                self.summary = child.finalize()
        elif n == 'description':
            if child.getAttribute('lang') == 'en':
                self.description = child.finalize()
        elif n == 'yum:version':
            self.version = child.getAttribute('ver')
            self.release = child.getAttribute('rel')
        elif n == 'rpm:requires':
            self.requires = child.getChildren('entry', namespace='rpm')
        elif n == 'rpm:provides':
            self.provides = child.getChildren('entry', namespace='rpm')
        elif n == 'rpm:supplements':
            self.supplements = child.getChildren('entry', namespace='rpm')
        elif n == 'rpm:recommends':
            self.recommends = child.getChildren('entry', namespace='rpm')
        elif n == 'rpm:obsoletes':
            self.obsoletes = child.getChildren('entry', namespace='rpm')
        elif n == 'rpm:conflicts':
            self.conflicts = child.getChildren('entry', namespace='rpm')
        elif n == 'reboot-needed':
            self.rebootNeeded = True
        elif n == 'license-to-confirm':
            self.licenseToConfirm = child.finalize()
        elif n == 'package-manager':
            self.packageManager = True
        elif n == 'category':
            self.category = child.finalize()
        elif n == 'atoms':
            self.packages = child.getChildren('package')
        else:
            raise UnknownElementError(child)

    def __cmp__(self, other):
        vercmp = cmp(self.version, other.version)
        if vercmp != 0:
            return vercmp

        relcmp = cmp(self.release, other.release)
        if relcmp != 0:
            return relcmp

        sumcmp = cmp(self.summary, other.summary)
        if sumcmp != 0:
            return sumcmp

        desccmp = cmp(self.description, other.description)
        if desccmp != 0:
            return desccmp

        for pkg in other.packages:
            if pkg not in self.packages:
                self.packages.append(pkg)

        return 0

    def __hash__(self):
        return hash((self.name, self.version, self.release, self.summary,
                     self.description))


class _Atoms(SlotNode):
    """
    Parser for the atoms element of a path-*.xml file.
    """

    __slots__ = ()

    def addChild(self, child):
        """
        Parse children of atoms element.
        """

        n = child.getName()
        if n == 'package':
            child.type = child.getAttribute('type')
            SlotNode.addChild(self, child)
        elif n == 'message':
            pass
        elif n == 'script':
            pass
        else:
            raise UnknownElementError(child)


class PatchXml(XmlFileParser, PackageXmlMixIn):
    """
    Handle registering all types for parsing patch-*.xml files.
    """

    def _registerTypes(self):
        """
        Setup databinder to parse xml.
        """

        class _Package(self.PackageFactory):
            # The base package has no type
            __slots__ = ('type', )


        PackageXmlMixIn._registerTypes(self)
        self._databinder.registerType(_Package, name='package')
        self._databinder.registerType(_Patch, name='patch')
        self._databinder.registerType(xmllib.StringNode, name='name',
                                      namespace='yum')
        self._databinder.registerType(xmllib.StringNode, name='category')
        self._databinder.registerType(_Atoms, name='atoms')
        self._databinder.registerType(xmllib.StringNode,
                                      name='license-to-confirm')
