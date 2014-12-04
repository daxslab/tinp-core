#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# repository.py
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

import os
from contrib.unwrapt import Download
from contrib.unwrapt.utils import to_url
from parsers import get_packages, create_section
from io import open


class Repository:

    def __init__(self, packages = [], arch='binary-i386'):
        """
        main repository instance
        """
        self.packages = packages
        self.arch = arch

    def get_package(self, package_name):
        """
        Return a package object
        :param package_name: Name of package to return
        :return: Package object
        """
        return self.packages[package_name]


class TinpRepository(Repository):

    def __init__(self, path, packages={}, arch='binary-i386'):
        """
        Creates a new tinP repository instance
        :param packages: Dictionary of package objects following a deb822 instance
        :param path: Path of the tinP repository
        :param arch: repository architecture
        """
        Repository.__init__(self, packages, arch)
        self.path = path
        self.repository = 'deb file:%s tinp main' % self.path
        self.repository = create_section(self.repository)
        self.packages_index_path = to_url(self.repository[0], self.arch, 'Packages')
        if self.packages_index_path.startswith('file:'):
            self.packages_index_path = self.packages_index_path.replace('file:', '', 1)
        self.load_packages()
        # self.packages_index_path = os.path.join(self.path, 'dists', 'tinp', 'main', self.arch, 'Packages')

    def load_packages(self):
        """
        load packages from package index
        """
        try:
            self.packages = get_packages(self.repository, arch=self.arch, packages_index_filename='Packages')
        except:
            pass

    def remove_package(self, package_name):
        """
        Remove a package from repository
        :param package_name: Name of package to remove
        TODO: remove unused dependencies
        """
        package_path = os.path.join(self.path, self.packages[package_name]['Filename'])
        try:
            os.remove(package_path)
            path_directory, filename = os.path.split(package_path)
            os.removedirs(path_directory)
        except IOError:
            pass
        del self.packages[package_name]

    def add_package(self, package):
        """
        Add a new package to repository
        :param package: Package object
        :param package_file: path (url or local) to package file
        """
        package_file = os.path.join(package.base_url, package['Filename'])
        download_package = False
        new_package_name = package['Package']
        if not new_package_name in self.packages:
            self.packages[new_package_name] = package
            download_package = True
        else:
            if package['Version'] > self.packages[new_package_name]['Version']:
                self.remove_package(new_package_name)
                self.add_package(package, package_file)
                # self.packages[new_package_name] = package
                # download_package = True
        if download_package:
            package_path = os.path.join(self.path, self.packages[new_package_name]['Filename'])
            package_dir, package_filename = os.path.split(package_path)
            try:
                os.makedirs(package_dir)
            except:
                pass
            Download.download(package_file, package_path)

    def rebuild_repo_index(self):
        """
        Rebuild the packages index file
        """
        packages_index_dir, packages_index_filename = os.path.split(self.packages_index_path)
        if packages_index_dir.startswith('file:'):
            packages_index_dir = packages_index_dir.replace('file:', '', 1)
        try:
            os.makedirs(packages_index_dir)
        except:
            pass
        # write packages text file
        packages_index_file = open(self.packages_index_path, 'wb')        
        for pack_key in self.packages:
            self.packages[pack_key].dump(fd=packages_index_file)
            packages_index_file.write('\n'.encode('utf-8'))
        packages_index_file.close()
        # create gziped file
        import gzip
        f_in = open(self.packages_index_path, 'rb')
        f_out = gzip.open(self.packages_index_path+'.gz', 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()


class SourceRepository(Repository):

    def __init__(self, sources, packages=[], arch='binary-i386'):
        """
        Creates a new source (origin) repository instance
        :param sources: Source repositories
        :param packages: Dictionary of package objects following a deb822 instance
        :param arch: repository architecture
        """
        Repository.__init__(self, packages, arch)
        self.sources = sources

    def load_packages(self):
        """
        load packages from packages indexs
        """
        self.packages = get_packages(self.sources, arch=self.arch)

    def get_package_tree(self, package_name, recommends=False, suggests=False, packages_dict = {}):
        """
        get a complete package dependency tree
        :param package_name: packege head
        :param recommends: search for recommended packages too
        :return: packages list
        """

        if not package_name in self.packages:
            return packages_dict
        head_package = self.packages[package_name]
        if not package_name in packages_dict:
            packages_dict[package_name] = head_package
            rels = head_package.relations
            relations = rels['depends']
            if recommends:
                relations = relations + rels['recommends']
            if suggests:
                relations = relations + rels['suggests']
            for deps in relations:
                news = self.get_package_tree(deps[0]['name'], packages_dict=packages_dict)
                # packages_dict = join_dicts(packages_dict,
                #                            self.get_package_tree(deps[0]['name'], packages_dict=packages_dict))
                for key in news:
                    if not key in packages_dict:
                        packages_dict[key] = news[key]
        return packages_dict



# from parsers import get_repositories
# repos = get_repositories("/etc/apt/sources.list")
# rep = SourceRepository(repos)
# rep.load_packages()
# packages = rep.get_package_tree('apache2', recommends=True, suggests=True)


# tinp = TinpRepository('/home/cccaballero/Escritorio/repotest')
# for p in packages:
#     tinp.add_package(packages[p])
# tinp.rebuild_repo_index()