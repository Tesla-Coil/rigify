#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

import os
import sys
import bpy

from . import utils


def get_rigs(base_path, path, feature_set='rigify'):
    """ Recursively searches for rig types, and returns a list.

    :param base_path: base dir where rigs are stored
    :type path:str
    :param path:      rig path inside the base dir
    :type path:str
    """

    rigs = {}
    impl_rigs = {}

    files = os.listdir(os.path.join(base_path, path))
    files.sort()

    for f in files:
        is_dir = os.path.isdir(os.path.join(base_path, path, f))  # Whether the file is a directory

        # Stop cases
        if f[0] in [".", "_"]:
            continue
        if f.count(".") >= 2 or (is_dir and "." in f):
            print("Warning: %r, filename contains a '.', skipping" % os.path.join(path, f))
            continue

        if is_dir:
            # Check directories
            module_name = os.path.join(path, "__init__").replace(os.sep, ".")
            # rig_module = utils.get_resource(module_name, base_path=base_path, resource_type='RIG')
            # Check if it's a rig itself
            # if hasattr(rig_module, "Rig"):
            # if False:
            #     rigs[f] = {"module": rig_module,
            #                "feature_set": feature_set}
            # else:
            # Check for sub-rigs
            sub_rigs, sub_impls = get_rigs(base_path, os.path.join(path, f, ""), feature_set)  # "" adds a final slash
            rigs.update({"%s.%s" % (f, l): sub_rigs[l] for l in sub_rigs})
            impl_rigs.update({"%s.%s" % (f, l): sub_rigs[l] for l in sub_impls})
        elif f.endswith(".py"):
            # Check straight-up python files
            f = f[:-3]
            module_name = os.path.join(path, f).replace(os.sep, ".")
            rig_module = utils.get_resource(module_name, base_path=base_path, resource_type='RIG')
            if hasattr(rig_module, "Rig"):
                rigs[f] = {"module": rig_module,
                           "feature_set": feature_set}
            if hasattr(rig_module, 'IMPLEMENTATION') and rig_module.IMPLEMENTATION:
                impl_rigs[f] = rig_module

    return rigs, impl_rigs


# def get_collection_list(rigs):
#     collection_list = []
#     for r in rigs:
#         a = r.split(".")
#         if len(a) >= 2 and a[0] not in collection_list:
#             collection_list += [a[0]]
#     return collection_list


# Public variables
MODULE_DIR = os.path.dirname(os.path.dirname(__file__))
if MODULE_DIR not in sys.path:
    sys.path.append(MODULE_DIR)

rigs, implementation_rigs = get_rigs(MODULE_DIR, os.path.join(os.path.basename(os.path.dirname(__file__)), utils.RIG_DIR, ''))
# collection_list = get_collection_list(sorted(rigs.keys()))
# col_enum_list = [("All", "All", ""), ("None", "None", "")] + [(c, c, "") for c in collection_list]


def get_external_rigs(feature_sets_path):
    # Clear and fill rigify rigs and implementation rigs public variables
    for rig in rigs.keys():
        if rigs[rig]["feature_set"] != "rigify":
            rigs.pop(rig)
            if rig in implementation_rigs:
                implementation_rigs.pop(rig)
    # rigs.clear()
    # implementation_rigs.clear()
    # new_rigs, new_implementation_rigs = get_rigs(
    #     MODULE_DIR,
    #     os.path.join(
    #         os.path.basename(os.path.dirname(__file__)), utils.RIG_DIR, ''
    #     )
    # )
    # rigs.update(new_rigs)
    # implementation_rigs.update(new_implementation_rigs)

    # Get external rigs
    for feature_set in os.listdir(feature_sets_path):
        if feature_set:
            feature_set_path = os.path.join(feature_sets_path, feature_set)
            if feature_set_path not in sys.path:
                sys.path.append(feature_set_path)

            utils.get_resource('__init__', base_path=feature_set_path, resource_type='RIG')
            external_rigs, external_impl_rigs = get_rigs(feature_set_path, utils.RIG_DIR, feature_set)
            rigs.update(external_rigs)
            implementation_rigs.update(external_impl_rigs)
