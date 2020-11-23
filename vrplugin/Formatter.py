# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import traceback


# Converts an array into a Vector3 that can be read in by Unity
# @staticmethod
def array_to_vec3(arr):
    myList = []
    for elm in arr:
        myList.append({"x": elm[0], "y": elm[1], "z": elm[2]})
    return myList


# @staticmethod
def dict_to_json(dict):
    return str(dict).replace("'", "\"")

