'''
Copyright (C) 2021 Conjuur

Created by Matt Myers

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


bl_info = {
    "name": "Conjuur - Image Voodoo",
    "author": "Matt Myers",
    "version": (1, 1),
    "blender": (2, 91, 0),
    "location": "View3D",
    "description": "Adds scaled reference images into respective views",
    "warning": "",
    "wiki_url": "",
    "category": "View3D",
}

import bpy
import os
from os import listdir
from bpy_extras.io_utils import ImportHelper
from bpy.types import (Panel, Operator, PropertyGroup)
from bpy.props import (StringProperty,
                       FloatProperty,
                       PointerProperty,
                       BoolProperty
                       )


# Global Inputs #########################


class VoodooInputs(PropertyGroup):
    load_directory: StringProperty(
        name="", description="Directory where images are stored.",
        default="Please pick directory below", maxlen=1024)

    length_dim: FloatProperty(
        name="Length", description="", default=1.0, min=0.01, max=1000.0)

    width_dim: FloatProperty(
        name="Width", description="", default=1.0, min=0.01, max=1000.0)

    height_dim: FloatProperty(
        name="Height", description="", default=1.0, min=0.01, max=1000.0)

    meas_length_dim: FloatProperty(
        name="Length", description="", default=1.0, min=0.01, max=1000.0)

    meas_width_dim: FloatProperty(
        name="Width", description="", default=1.0, min=0.01, max=1000.0)

    meas_height_dim: FloatProperty(
        name="Height", description="", default=1.0, min=0.01, max=1000.0)

    image_alpha: FloatProperty(
        name="Transparency", description="", default=1.0, min=0.0, max=1.0)


# Operators ################################

class ImageAlpha(Operator):
    bl_idname = "op.im_alpha"
    bl_label = "Apply Image Transparency"

    def execute(self, context):
        scene = context.scene
        vprops = scene.voodooprops

        # Set transparency for all visible images
        for im in bpy.data.objects:
            if im.type == "EMPTY" and im.visible_get():
                bpy.context.view_layer.objects.active = im
                obj = bpy.context.active_object
                obj.use_empty_image_alpha = True
                bpy.context.object.color[3] = vprops.image_alpha

        return{'FINISHED'}


class ScaleSelectedImage(Operator):
    bl_idname = "op.scale_selected"
    bl_label = "Scale Image"

    def execute(self, context):
        scene = context.scene
        vprops = scene.voodooprops

        obj = bpy.context.active_object

        # Need to rewrite
        if 'top' in obj.name.lower() or 'bottom' in obj.name.lower():
            obj.scale[0] = (obj.scale[0] *
                            vprops.length_dim/vprops.meas_length_dim)
            obj.scale[1] = (obj.scale[1] *
                            vprops.width_dim/vprops.meas_width_dim)
        elif 'front' in obj.name.lower() or 'back' in obj.name.lower():
            obj.scale[0] = (obj.scale[0] *
                            vprops.length_dim/vprops.meas_length_dim)
            obj.scale[1] = (obj.scale[1] *
                            vprops.height_dim/vprops.meas_height_dim)
        elif 'right' in obj.name.lower() or 'left' in obj.name.lower():
            obj.scale[0] = (obj.scale[0] *
                            vprops.width_dim/vprops.meas_width_dim)
            obj.scale[1] = (obj.scale[1] *
                            vprops.height_dim/vprops.meas_height_dim)
        else:
            print("Scale your custom image manually")

        return{'FINISHED'}


class SelectDir(Operator, ImportHelper):
    bl_idname = "op.select_dir"
    bl_label = "Import File Directory"

    filter_glob = StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'})
    auto_spacing = BoolProperty(
        name='Auto Spacing', description='Check to auto separate images',
        default=False)

    def execute(self, context):
        scene = context.scene
        vprops = scene.voodooprops

        def open_graphics_files(acceptable_files, dir_path):
            files_to_open = iter(acceptable_files)
            done_looping = False
            while not done_looping:
                try:
                    file = next(files_to_open)
                    set_view(file)
                    bpy.ops.object.load_reference_image(filepath=str(dir_path)
                                                        + '\\' + file[0])

                    # Correct translation in these views
                    if file[1] == 'back':
                        bpy.ops.transform.rotate(value=3.14159,
                                                 orient_axis='Y')
                    elif file[1] == 'left':
                        bpy.ops.transform.rotate(value=3.14159,
                                                 orient_axis='X')

                    # Name the blender image object
                    obj = bpy.context.active_object
                    blender_name = file[0]
                    obj.name = blender_name

                except StopIteration:
                    done_looping = True
            return

        def set_view(file_name):
            view_matrix = {'top':
                           [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                            [0, 0, 0, 1]],
                           'front':
                           [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0],
                            [0, 0, 0, 1]],
                           'right':
                           [[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0],
                            [0, 0, 0, 1]],
                           'bottom':
                           [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0],
                            [0, 0, 0, 1]],
                           'back':
                           [[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0],
                            [0, 0, 0, 1]],
                           'left':
                           [[0, 0, -1, 0], [1, 0, 0, 0], [0, -1, 0, 0],
                            [0, 0, 0, 1]]
                           }

            orient_view = view_matrix[file_name[1]]
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area_vw = area.spaces[0].region_3d
                    if area_vw is not None:
                        area_vw.view_perspective = 'ORTHO'
                        area_vw.view_matrix = orient_view
            return

        def image_separate(images):
            print('separating...')
            print(images)

            # Shift numbers are defined separately because there can be
            # multiple images for each view
            shift = {'top': 3, 'front': 3, 'right': 3, 'bottom': 3,
                     'back': 3, 'left': 3}

            # Rewrite this loop !
            for ob in bpy.data.objects:
                if 'top' in ob.name.lower() and ob.type == 'EMPTY':
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.transform.translate(value=(0, 0, shift['top']))
                    bpy.ops.object.select_all(action='DESELECT')
                    shift['top'] += 3
                if 'front' in ob.name.lower() and ob.type == 'EMPTY':
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.transform.translate(value=(0, -shift['front'], 0))
                    bpy.ops.object.select_all(action='DESELECT')
                    shift['front'] += 3
                if 'right' in ob.name.lower() and ob.type == 'EMPTY':
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.transform.translate(value=(shift['right'], 0, 0))
                    bpy.ops.object.select_all(action='DESELECT')
                    shift['right'] + 3
                if 'bottom' in ob.name.lower() and ob.type == 'EMPTY':
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.transform.translate(value=(0, 0, -shift['bottom']))
                    bpy.ops.object.select_all(action='DESELECT')
                    shift['bottom'] += 3
                if 'back' in ob.name.lower() and ob.type == 'EMPTY':
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.transform.translate(value=(0, shift['back'], 0))
                    bpy.ops.object.select_all(action='DESELECT')
                    shift['back'] += 3
                if 'left' in ob.name.lower() and ob.type == 'EMPTY':
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.transform.translate(value=(-shift['left'], 0, 0))
                    bpy.ops.object.select_all(action='DESELECT')
                    shift['left'] += 3

            return

        # Main ##########################################################

        # Define the filepath from which the reference images will be pulled
        filename, extension = os.path.splitext(self.filepath)
        dir = self.filepath.split("\\")
        vprops.load_directory = dir[-2]    # Folder to be display in UI
        loading_directory = '\\'.join(dir[:-1])

        # Allowable file types
        endings = ['png', 'bmp', 'jpg', 'jpeg', 'tif', 'tiff']
        view_names = ['top', 'front', 'right', 'bottom', 'back', 'left']

        # Pull out only graphics files that have proper view names in them
        files = [
                file
                for file in listdir(loading_directory)
                if file.endswith(tuple(endings))
                and any(name in file.lower() for name in view_names)
            ]
        # Need to rewrite in a better way!!
        view_name = []
        for f in files:
            if 'top' in f.lower():
                view_name.append('top')
            elif 'front' in f.lower():
                view_name.append('front')
            elif 'right' in f.lower():
                view_name.append('right')
            elif 'bottom' in f.lower():
                view_name.append('bottom')
            elif 'back' in f.lower():
                view_name.append('back')
            elif 'left' in f.lower():
                view_name.append('left')

        combined = list((zip(files, view_name)))
        open_graphics_files(combined, loading_directory)
        bpy.ops.object.select_all(action='DESELECT')

        if self.auto_spacing:
            image_separate(combined)

        return {'FINISHED'}


# Menu Panels  ##############################

class ObjectPtVoodooPanel(Panel):
    bl_idname = "object.voodoo_panel"
    bl_label = "Conjuur - Image Voodoo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Image Vodoo"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vprops = scene.voodooprops

        layout.prop(vprops, "load_directory", icon="IMAGE_DATA")
        layout.operator("op.select_dir",  icon="FILEBROWSER")

        layout.label(text="Final Scaled Dimensions")

        split = layout.split()

        col = split.row()
        col.label(text="", icon="ARROW_LEFTRIGHT")
        col.prop(vprops, "length_dim")
        col.prop(vprops, "width_dim")
        col.prop(vprops, "height_dim")

        layout.label(text="Screen Measured Dimensions")

        split = layout.split()

        col = split.row()
        col.label(text="", icon="ARROW_LEFTRIGHT")
        col.prop(vprops, "meas_length_dim")
        col.prop(vprops, "meas_width_dim")
        col.prop(vprops, "meas_height_dim")

        layout.operator("op.scale_selected",  icon="FULLSCREEN_ENTER")

        layout.prop(vprops, "image_alpha", icon="IMAGE_DATA")
        layout.operator("op.im_alpha",  icon="IMAGE_RGB_ALPHA")


# Registration #################################

classes = (VoodooInputs,
           ObjectPtVoodooPanel,
           SelectDir,
           ScaleSelectedImage,
           ImageAlpha)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.voodooprops = PointerProperty(type=VoodooInputs)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
