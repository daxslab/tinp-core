#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tinp-cli.py
#
# Copyright 2014 Carlos Cesar Caballero Diaz <ccesar@linuxmail.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from __future__ import absolute_import, print_function
import sys
import os

import contrib.spia.internationalizator as internationalizator
from contrib.spia.internationalizator import _
if sys.version < '3':
    from urllib import quote
else:
    from urllib.parse import quote


LOCALE_DIR = os.path.join(sys.path[0], "locale")
internationalizator.load_locale_chains(LOCALE_DIR)


def add(repo_path, package_names, sources, recommends, suggests, arch):
    """
        add package option handler
    """
    from parsers import get_repositories
    from repository import SourceRepository, TinpRepository
    from parsers import get_repositories
    from utils import join_dicts

    repos = get_repositories(sources)
    rep = SourceRepository(repos, arch=arch)
    print (_("Loading packages..."))
    rep.load_packages()
    print (_("Finding dependencies..."))
    packages = {}
    for package in package_names.split(' '):
        packages = join_dicts(packages, 
            rep.get_package_tree(package, recommends=recommends, suggests=suggests))
    print (_("Loading repository..."))
    tinp = TinpRepository(repo_path, arch=arch)
    print (_("Adding new packages..."))
    for p in packages:
        tinp.add_package(packages[p])
    print (_("Building package index..."))
    tinp.rebuild_repo_index()
    print ("----------------------------------------")
    print (_('Completed. You can use the repository adding next line to your "sources.list":'))
    print ('    deb file:%s tinp main' % quote(repo_path, safe="%/:=&?~#+!$,;'@()*[]"))

def add_section(repo_path, section_name, sources, recommends, suggests, arch):
    """
        add_section option handler
    """
    from parsers import get_repositories
    from repository import SourceRepository, TinpRepository
    from parsers import get_repositories
    from utils import join_dicts
    repos = get_repositories(sources)
    rep = SourceRepository(repos, arch=arch)
    print (_("Loading packages..."))
    rep.load_packages()
    print (_("Finding dependencies..."))
    packages = {}
    for package_name in rep.packages:
        if rep.packages[package_name]['Section'] == section_name:
            packages = join_dicts(packages, 
                rep.get_package_tree(package_name, recommends=recommends, suggests=suggests))
    tinp = TinpRepository(repo_path, arch=arch)
    print (_("Adding new packages..."))
    for p in packages:
        tinp.add_package(packages[p])
    print (_("Building package index..."))
    tinp.rebuild_repo_index()
    print ("----------------------------------------")
    print (_('Completed. You can use the repository adding next line to your "sources.list":'))
    print ('    deb file:%s tinp main' % quote(repo_path, safe="%/:=&?~#+!$,;'@()*[]"))


def upgrade(repo_path, sources, arch):
    """
        upgrade package option handler
    """
    from parsers import get_repositories
    from repository import SourceRepository, TinpRepository

    repos = get_repositories(sources)
    rep = SourceRepository(repos, arch=arch)
    print (_("Loading packages..."))
    rep.load_packages()
    tinp = TinpRepository(repo_path, arch=arch)
    print (_("Updating packages..."))
    for p in tinp.packages:
        tinp.add_package(rep.packages[p])
    print (_("Building package index..."))
    tinp.rebuild_repo_index()


def remove(repo_path, package_names, arch):
    """
        remove package option handler
    """
    from repository import TinpRepository

    print (_("Loading repository..."))
    tinp = TinpRepository(repo_path, arch=arch)
    print (_("removing package(s)..."))
    for package in package_names.split(' '):
        tinp.remove_package(package)
    print (_("Building package index..."))
    tinp.rebuild_repo_index()
    print (_('Completed'))

def define_locale(locale):
    internationalizator.force(locale)

def start(repo_path, options):
    """Run the requested actions from CLI"""
    if options.define_locale:
        define_locale(options.define_locale)
    if options.add:
        add(repo_path, options.add, options.sources, 
            options.add_recommends, options.add_suggests, options.arch)
    if options.add_section:
        add_section(repo_path, options.add_section, options.sources, 
            options.add_recommends, options.add_suggests, options.arch)
    if options.remove:
        remove(repo_path, options.remove, options.arch)
    if options.upgrade:
        upgrade(repo_path, options.sources, options.arch)

lookup = {
    'usage: ': _('Usage: '),
    'optional arguments': _('Options'),
    'positional arguments': _('Arguments'),
    'too few arguments':_('too few arguments'),
    'show this help message and exit':_('show this help message and exit')
    }


def gettext(s):
    return lookup.get(s, s)

def main():
    """Main CLI program entry point"""
    # import optparse

    # usage = _('%(prog)s path/to/repo/ option "argument[s]"')
    # # usage = '%prog path/to/repo/ option "argument[s]"'    
    prog = 'tinp-cli'
    version = '%(prog)s 0.2.1'
    description = _('This program creates and manage a customized debian-based repository.')
    epilog = version+' - (C) 2014 Carlos Cesar Caballero Díaz'
    # parser = optparse.OptionParser(usage=usage, description=description,
    #   version=version)
    # parser.set_usage('Uso: pepe')
    # parser.usage('Uso'.decode('utf-8'))
    # parser.usage = 'Uso'
    import argparse
    argparse._ = gettext

    parser = argparse.ArgumentParser(
      prog=prog,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description=description,
      epilog=epilog)

    parser.add_argument('custom_repository', metavar=_('path'),
                   help=_('path to custom repository'))

    parser.add_argument('--version', action='version', version=version, 
      help=_('show program\'s version number and exit'))
    parser.add_argument('-a', '--add', action='store', default=False, dest='add',
      metavar=_('package[s]'), 
      help=_('adds packages and all their dependencies to the custom repository (ex: "apache2 scite")'))
    parser.add_argument('-d', '--add-section', action='store', default=False, dest='add_section',
      metavar=_('section[s]'), 
      help=_('adds all packages from a section and all their dependencies to the custom repository (ex: "utils admin")'))
    parser.add_argument('-c', '--arch', action='store', default='binary-i386', 
      metavar=_('arch'), help=_('define architecture (default "binary-i386")'))
    parser.add_argument('-s', '--sources', action='store', default='/etc/apt/sources.list', 
      metavar=_('sources_file'), 
      help=_('origin repository source file (/etc/apt/sources.list by default)'))
    parser.add_argument('-e', '--add-recommends', action='store_true', default=False, 
      help=_('add recomended packages'))
    parser.add_argument('-g', '--add-suggests', action='store_true', default=False, 
      help=_('add sugested packages'))
    parser.add_argument('-r', '--remove', action='store', default=False,
      dest='remove', metavar=_('package[s]'), help=_('removes packages from the repo (ex: "apache2 scite") not remove dependencies'))
    parser.add_argument('-u', '--upgrade', action='store_true', default=False,
      dest='upgrade', help=_('upgrades the repository, find new versions of the actual custom repository packages, and replace them'))
    parser.add_argument('-l', '--define-locale', action='store', default=False,
      dest='define_locale', metavar=_('locale'), help=_('define output languaje based on locale'))
    
    args = parser.parse_args()
    if not args.custom_repository:
        parser.error(_('You need to specify the working path, run again with the --help option'))
    else:
        if not args.add and not args.add_section and not args.remove and not args.upgrade:
            parser.error(_('Arguments error, run again with the --help option'))

    start(args.custom_repository, args)


if __name__ == '__main__':
    main()