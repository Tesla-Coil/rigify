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

# <pep8 compliant>

bl_info = {
    "name": "Rigify",
    "version": (0, 4),
    "author": "Nathan Vegdahl",
    "blender": (2, 66, 0),
    "description": "Automatic rigging from building-block components",
    "location": "Armature properties, Bone properties, View3d tools panel, Armature Add menu",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/Rigging/Rigify",
    "tracker_url": "http://github.com/cessen/rigify/issues",
    "category": "Rigging"}


if "bpy" in locals():
    import importlib
    importlib.reload(generate)
    importlib.reload(ui)
    importlib.reload(utils)
    importlib.reload(metarig_menu)
    importlib.reload(rig_lists)
else:
    from . import utils, rig_lists, generate, ui, metarig_menu

import bpy
import sys
import os
from bpy.types import AddonPreferences
from bpy.props import BoolProperty


class RigifyPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    def update_legacy(self, context):
        if self.legacy_mode:

            sys.path.append("C:\\Program Files\\Blender Foundation\\blender-2.77-windows64 DEV\\2.77\\scripts\\"
                            "addons\\rigify")

            unregister()

            globals().pop('utils')
            globals().pop('rig_lists')
            globals().pop('generate')
            globals().pop('ui')
            globals().pop('metarig_menu')

            import legacy.utils
            import legacy.rig_lists
            import legacy.generate
            import legacy.ui
            import legacy.metarig_menu

            print("ENTERING RIGIFY LEGACY\r\n")

            globals()['utils'] = legacy.utils
            globals()['rig_lists'] = legacy.rig_lists
            globals()['generate'] = legacy.generate
            globals()['ui'] = legacy.ui
            globals()['metarig_menu'] = legacy.metarig_menu

            register()

        else:

            for i, p in enumerate(sys.path):
                if p == "C:\\Program Files\\Blender Foundation\\blender-2.77-windows64 DEV\\2.77\\scripts\\addons\\rigify":
                    sys.path.pop(i)

            unregister()

            globals().pop('utils')
            globals().pop('rig_lists')
            globals().pop('generate')
            globals().pop('ui')
            globals().pop('metarig_menu')

            from . import utils
            from . import rig_lists
            from . import generate
            from . import ui
            from . import metarig_menu

            print("ENTERING RIGIFY LEGACY\r\n")

            globals()['utils'] = utils
            globals()['rig_lists'] = rig_lists
            globals()['generate'] = generate
            globals()['ui'] = ui
            globals()['metarig_menu'] = metarig_menu

            register()

    legacy_mode = BoolProperty(
        name='Rigify Legacy Mode',
        description='Select if you want to use Rigify in legacy mode',
        default=False,
        update=update_legacy
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='Select if you want to use Rigify in legacy mode ')
        layout.prop(self, 'legacy_mode')


class RigifyName(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()


class RigifyParameters(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()


class RigifyArmatureLayer(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Layer Name", default=" ")
    row = bpy.props.IntProperty(name="Layer Row", default=1, min=1, max=32)


##### REGISTER #####

def register():
    ui.register()
    metarig_menu.register()

    bpy.utils.register_class(RigifyName)
    bpy.utils.register_class(RigifyParameters)
    bpy.utils.register_class(RigifyArmatureLayer)
    bpy.utils.register_class(RigifyPreferences)

    bpy.types.PoseBone.rigify_type = bpy.props.StringProperty(name="Rigify Type", description="Rig type for this bone")
    bpy.types.PoseBone.rigify_parameters = bpy.props.PointerProperty(type=RigifyParameters)

    bpy.types.Armature.rigify_layers = bpy.props.CollectionProperty(type=RigifyArmatureLayer)

    IDStore = bpy.types.WindowManager
    IDStore.rigify_collection = bpy.props.EnumProperty(items=rig_lists.col_enum_list, default="All", name="Rigify Active Collection", description="The selected rig collection")
    IDStore.rigify_types = bpy.props.CollectionProperty(type=RigifyName)
    IDStore.rigify_active_type = bpy.props.IntProperty(name="Rigify Active Type", description="The selected rig type")

    # Add rig parameters
    for rig in rig_lists.rig_list:
        r = utils.get_rig_type(rig)
        try:
            r.add_parameters(RigifyParameters)
        except AttributeError:
            pass


def unregister():
    del bpy.types.PoseBone.rigify_type
    del bpy.types.PoseBone.rigify_parameters

    IDStore = bpy.types.WindowManager
    del IDStore.rigify_collection
    del IDStore.rigify_types
    del IDStore.rigify_active_type

    bpy.utils.unregister_class(RigifyName)
    bpy.utils.unregister_class(RigifyParameters)
    bpy.utils.unregister_class(RigifyArmatureLayer)
    bpy.utils.unregister_class(RigifyPreferences)

    metarig_menu.unregister()
    ui.unregister()
