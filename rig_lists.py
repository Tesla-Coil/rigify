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
import bpy

from . import utils


def get_rig_list(path, mode='relative'):
    """ Recursively searches for rig types, and returns a list.

    :param path
    :type path:str
    :param mode: path is absolute or relative?
    :type mode: str
    """

    if mode == 'relative':
        base_path = ''
        MODULE_DIR = os.path.dirname(__file__)
        RIG_DIR_ABS = os.path.join(MODULE_DIR, utils.RIG_DIR)
        SEARCH_DIR_ABS = os.path.join(RIG_DIR_ABS, path)
    elif mode == 'absolute':
        base_path = path
        SEARCH_DIR_ABS = path
    else:
        return

    rigs_dict = dict()
    rigs = []
    impl_rigs = []

    files = os.listdir(SEARCH_DIR_ABS)
    files.sort()

    for f in files:
        is_dir = os.path.isdir(os.path.join(SEARCH_DIR_ABS, f))  # Whether the file is a directory

        # Stop cases
        if f[0] in [".", "_"]:
            continue
        if f.count(".") >= 2 or (is_dir and "." in f):
            print("Warning: %r, filename contains a '.', skipping" % os.path.join(SEARCH_DIR_ABS, f))
            continue

        if is_dir:
            # Check directories
            if mode == 'relative':
                module_name = os.path.join(path, f).replace(os.sep, ".")
                rig = utils.get_resource(module_name, base_path=base_path)
            else:
                module_name = "__init__"
                rig = utils.get_resource(module_name, base_path=os.path.join(module_name, f, ''))
            # Check if it's a rig itself
            if hasattr(rig, "Rig"):
                rigs += [f]
            else:
                # Check for sub-rigs
                sub_dict = get_rig_list(os.path.join(path, f, ""), mode=mode)  # "" adds a final slash
                rigs.extend(["%s.%s" % (f, l) for l in sub_dict['rig_list']])
                impl_rigs.extend(["%s.%s" % (f, l) for l in sub_dict['implementation_rigs']])
        elif f.endswith(".py"):
            # Check straight-up python files
            t = f[:-3]
            if mode == 'relative':
                module_name = os.path.join(path, t).replace(os.sep, ".")
                rig = utils.get_resource(module_name, base_path=base_path)
            else:
                custom_folder = bpy.context.user_preferences.addons['rigify'].preferences.custom_folder
                custom_rigs_folder = os.path.join(custom_folder, utils.RIG_DIR, '')
                module_name = os.path.join(path, t).replace(custom_rigs_folder, '').replace(os.sep, ".")
                rig = utils.get_resource(module_name, base_path=custom_rigs_folder)
            if hasattr(rig, "Rig"):
                rigs += [t]
            if hasattr(rig, 'IMPLEMENTATION') and rig.IMPLEMENTATION:
                impl_rigs += [t]
    rigs.sort()

    rigs_dict['rig_list'] = rigs
    rigs_dict['implementation_rigs'] = impl_rigs

    return rigs_dict


def get_collection_list(rig_list):
    collection_list = []
    for r in rig_list:
        a = r.split(".")
        if len(a) >= 2 and a[0] not in collection_list:
            collection_list += [a[0]]
    return collection_list


# Public variables
rigs_dict = get_rig_list("")
rig_list = rigs_dict['rig_list']
implementation_rigs = rigs_dict['implementation_rigs']
collection_list = get_collection_list(rig_list)
col_enum_list = [("All", "All", ""), ("None", "None", "")] + [(c, c, "") for c in collection_list]


def get_external_rigs(custom_rigs_folder):
    if custom_rigs_folder:
        external_rigs_dict = get_rig_list(custom_rigs_folder, mode='absolute')
        rigs_dict['external'] = external_rigs_dict
