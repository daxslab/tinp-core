#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py
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

import sys
from itertools import chain

def join_dicts(*args):
    """
    join multiple dictionaries
    :param args: dictionaries
    :return: a dictionarie composed for the union of *dictionaries
    """
    iters = []
    for dictionary in args:
        if sys.version >= '3':
            iters.append(dictionary.items())
        else:
            iters.append(dictionary.iteritems())
    return dict(chain(*iters))

# a = {'si':'1', 'as':'3'}
# # a = {}
# b = {'si':2, 'aso':3, 'ds':9}
# print join_dicts(a,b)