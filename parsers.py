#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# parsers.py
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

__author__ = 'cccaballero'

from contrib.debian import deb822
from contrib.unwrapt.utils import url_join, to_url
from contrib.unwrapt.Download import download
import tempfile

def get_packages(repositories, arch='binary-i386', packages_index_filename='Packages.gz'):
    """
    Return packages information from a repository package file
    :param packages_file: debian repository packages file
    :return: packages dictionary
    """
    packages = {}
    # packages = []
    for section in repositories:
        package_sources_path = to_url(section, arch, packages_index_filename)
        tmp_file = tempfile.mkdtemp()
        download(package_sources_path, tmp_file+"/tmp000")
        # packages.append(deb822.Packages.iter_paragraphs(open(tmp_file+"/tmp000")))
        for pkg in deb822.Packages.iter_paragraphs(open(tmp_file+"/tmp000")):
            pkg.base_url = section["surl"]
            if pkg['Package'] in packages:
                if pkg['Version'] > packages[pkg['Package']]['Version']:
                    packages[pkg['Package']] = pkg
            else:
                packages[pkg['Package']] = pkg
    return packages

class InvalidRepository(Exception):
    """
        A repository string was passed that is invalid or not supported
    """
    pass


def _read_sources_file(sources_file):
    sources_lines = []
    sources_file = open(sources_file, "rb")
    for f in sources_file:
        if f != "\n":
            clean_line = f.strip()
            if not clean_line or clean_line.decode('UTF-8').startswith('#') or len(clean_line.split()) < 4:
                pass
            else:
                if not f in sources_lines:
                    sources_lines.append(f.decode('UTF-8').split('#')[0]) # remove inline comments and append
    sources_file.close()
    return sources_lines


def create_section(line):
    repository_sections = []
    try:
        rtype, url, dist, sections = line.split(None, 3)
    except:
        raise InvalidRepository("Repository is either invalid or not supported: %s" % line)
    for section in sections.split():
                r = {}
                r["rtype"] = rtype
                r["surl"] = url
                r["dist"] = dist
                r["section"] = section
                r["url"] = url_join(url, "dists", dist, section)
                repository_sections.append(r)
    return repository_sections


def get_repositories(sources_file):
    repositories = []
    sources_lines = _read_sources_file(sources_file)

    for repo in sources_lines:
        repositories = repositories + create_section(repo)
    return repositories


# file = open('/home/cccaballero/Escritorio/Packages', 'wb')
# for pack in deb822.Packages.iter_paragraphs(open("/media/cccaballero/Cesar2/repo/ru1404/mirror/ubuntu.uci.cu/ubuntu/dists/trusty/main/binary-i386/Packages.gz")):
#     pack.dump(fd=file)
#     file.write('\n')


# pack = deb822.Packages.iter_paragraphs(open("/media/cccaballero/Cesar2/repo/ru1404/mirror/ubuntu.uci.cu/ubuntu/dists/trusty/main/binary-i386/Packages.gz"))
# print pack
# file = open('/home/cccaballero/Escritorio/Packages', 'wb')
# file.write(pack.__str__())
# file.close()

# for pack in deb822.Packages.iter_paragraphs(open("/media/cccaballero/Cesar2/repo/ru1404/mirror/ubuntu.uci.cu/ubuntu/dists/trusty/main/binary-i386/Packages.gz")):
#     # print pack
#     for key in pack:
#         print key+": "+pack[key]
#     break

# print get_repositories("/etc/apt/sources.list")

# f = open('/home/cccaballero/Escritorio/sources.list')
# for stanza in deb822.Sources.iter_paragraphs(f):
#
#         print stanza
# f.close()

# print to_url(get_repositories("/etc/apt/sources.list")[0], 'binary-i386', 'Packages.gz')
# print create_section("deb file:/pepe/lolo psc main")

# print get_packages(get_repositories("/etc/apt/sources.list"))
# a = get_packages(get_repositories("/etc/apt/sources.list"))
# print len(a)
# for p in a:
#     print p