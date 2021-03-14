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
    "version": (2, 0),
    "blender": (2, 91, 0),
    "location": "View3D",
    "description": "Adds scaled reference images into respective views",
    "warning": "",
    "wiki_url": "",
    "category": "View3D",
}

import bpy
from subprocess import check_call
import os
from os import listdir

try:
    import cv2 as cv
except ImportError:
    pybin = bpy.app.binary_path_python
    check_call([pybin,'-m', 'pip', 'install', 'opencv-python'])
    import cv2 as cv

try:
    import numpy as np
except ImportError:
    pybin = bpy.app.binary_path_python
    check_call([pybin, '-m', 'pip', 'install', 'numpy'])
    import numpy as np

try:
    from PIL import Image
except ImportError:
    pybin = bpy.app.binary_path_python
    check_call([pybin, '-m', 'pip', 'install', 'Pillow'])
    from PIL import Image

import random as rng
import math
import csv
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.types import (Panel, Operator, PropertyGroup)
from bpy.props import (StringProperty,
                       FloatProperty,
                       PointerProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty,
                       FloatVectorProperty
                       )

rng.seed(12345)

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

    canny_filter1: IntProperty(
        name="Canny Edge Filter 1", description="Canny Edge Filter 1",
        default=30, min=1, max=500)

    canny_filter2: IntProperty(
        name="Canny Edge Filter 2", description="Canny Edge Filter 2",
        default=200, min=1, max=500)


# Operators ################################


class CannyEdges(Operator):
    bl_idname = "op.canny_edges"
    bl_label = "Canny Edge and Contour Generator"

    def execute(self, context):
        scene = context.scene
        vprops = scene.voodooprops

        # Check to make sure an object is selected
        if bpy.context.selected_objects == []:
            print("No object selected.")
        else:
            obj = bpy.context.selected_objects[0]
            im = bpy.data.images[obj.name]

            # Delete existing canny and Contours
            im_names = [obj.name + '-canny', obj.name + '-contours']
            for pics in bpy.data.images:
                if pics.name in im_names:
                    bpy.data.images.remove(pics)

            # Canny Edge
            img = cv.imread(bpy.data.images[obj.name].filepath_from_user())
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            gray_filtered = cv.bilateralFilter(gray, 7, vprops.canny_filter1*2,
                                               vprops.canny_filter2*2)
            edges = cv.Canny(gray_filtered, vprops.canny_filter1,
                             vprops.canny_filter2)

            # Find contours
            contours, hierarchy = cv.findContours(edges, cv.RETR_TREE,
                                                  cv.CHAIN_APPROX_SIMPLE)
            # Draw contours
            cont_colors = []
            drawing = np.zeros((edges.shape[0],
                                edges.shape[1], 3), dtype=np.uint8)
            for i in range(len(contours)):
                color = (rng.randint(0, 256), rng.randint(0, 256),
                         rng.randint(0, 256))
                cv.drawContours(drawing, contours, i, color, 1,
                                cv.LINE_8, hierarchy, 0)
                cont_colors.append(color)

            # Store path
            fp = bpy.data.filepath
            fp_sp = fp.split('\\')
            store_dir = '\\'.join(fp_sp[:-1]) + '\\'

            cv.imwrite(store_dir + obj.name + "-canny.jpg", edges)
            cv.imwrite(store_dir + obj.name + "-contours.jpg", drawing)

            # Internalize Edge and Contour Images
            bpy.ops.image.new(name=obj.name + '-canny', width=im.size[0],
                              height=im.size[1])
            bpy.data.images[obj.name + '-canny'].source = 'FILE'
            bpy.data.images[obj.name + '-canny'].filepath = store_dir + \
                obj.name + "-canny.jpg"
            bpy.data.images[obj.name + '-canny'].use_fake_user = True
            bpy.ops.file.pack_all()

            bpy.ops.image.new(name=obj.name + '-contours', width=im.size[0],
                              height=im.size[1])
            bpy.data.images[obj.name + '-contours'].source = 'FILE'
            bpy.data.images[obj.name + '-contours'].filepath = store_dir + \
                obj.name + "-contours.jpg"
            bpy.data.images[obj.name + '-contours'].use_fake_user = True
            bpy.ops.file.pack_all()

            os.remove(store_dir + obj.name + "-canny.jpg")
            os.remove(store_dir + obj.name + "-contours.jpg")

        return{'FINISHED'}


class ImagetoCSV(Operator):
    bl_idname = "op.im_createcsv"
    bl_label = "Create CSV point file"

    def execute(self, context):
        scene = context.scene
        vprops = scene.voodooprops

        # Need to eventually rewrite so I don't need these variables
        counter = 0
        x_coord = []
        y_coord = []
        step = []
        coords = []

        # Store path
        fp = bpy.data.filepath
        fp_sp = fp.split('\\')
        store_dir = '\\'.join(fp_sp[:-1]) + '\\' + vprops.load_directory
        print("image will be stored here {}".format(store_dir))

        # find the corresponding canny image to the selected view
        ob = bpy.context.selected_objects[0]
        for im in bpy.data.images:
            if im.name == ob.name + '-canny':
                image_for_pts = im

        # get pixels in each dimension
        width, height = image_for_pts.size

        # need to temporarily save out canny file and then remove it afterward
        image_for_pts.save_render(store_dir + '\\' + 'temp-canny.jpg')

        canny_image = Image.open(store_dir + '\\' + 'temp-canny.jpg', 'r')
        pix_val = list(canny_image.getdata())
        pixel = pix_val[0: width * height]

        for i in range(0, width * height):
            if pixel[i][0] >= 128:
                print('found one at pixel number: ', counter)
                x_coord.append([(counter) % width])
                if counter == 0:
                    y_coord.append([math.ceil(counter + 1 / width)])
                else:
                    y_coord.append([math.ceil(counter / width) *
                                    (-1) + height])
            counter += 1

        z_coord = np.ones((len(x_coord), 1))

        for i in range(0, len(x_coord)):
            step = np.append(x_coord[i], y_coord[i])
            coords.append(step)

        coords = np.hstack((coords, z_coord))

        with open(store_dir + '\\' + ob.name + '-pts.txt', 'w',
                  newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(coords)

        csv_file.close()

        # Remove temp canny file
        os.remove(store_dir + '\\' + 'temp-canny.jpg')

        return{'FINISHED'}


class ImportPixels(Operator):
    bl_idname = "op.im_importcsv"
    bl_label = "Import Edge Pixels"

    # generic transform props   ----> without this I was getting the mesh
    # to build but getting a location error
    align_items = (
            ('WORLD', "World", "Align the new object to the world"),
            ('VIEW', "View", "Align the new object to the view"),
            ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object")
    )
    align: EnumProperty(
            name="Align",
            items=align_items,
            default='WORLD',
            update=AddObjectHelper.align_update_callback,
            )
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )

    def execute(self, context):
        scene = context.scene
        vprops = scene.voodooprops

        v = []

        # Open file csv related to selected view and append verts
        def open_csv(filename):
            with open(filename) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    x_coord = float(row[0])
                    y_coord = float(row[1])
                    z_coord = float(row[2])
                    v.append((x_coord, y_coord, z_coord))
            return v

        # Determine the upper left of the selected image position in space
        def find_upper_left(obj):
            if bpy.context.scene.unit_settings.system == 'METRIC':
                if bpy.context.scene.unit_settings.length_unit == 'METERS':
                    unit_sc = 1
                elif bpy.context.scene.unit_settings.length_unit == \
                        'CENTIMETERS':
                    unit_sc = 100
                elif bpy.context.scene.unit_settings.length_unit == \
                        'MILLIIMETERS':
                    unit_sc = 100
                else:
                    print("Select a different metric unit.")
            elif bpy.context.scene.unit_settings.system == 'IMPERIAL':
                if bpy.context.scene.unit_settings.length_unit == 'INCHES':
                    unit_sc = 1/.0254
                elif bpy.context.scene.unit_settings.length_unit == 'FEET':
                    unit_sc = (1/0.0254)/12

            if obj is not None and obj.type == 'EMPTY':
                x_loc = bpy.context.object.location[0] * unit_sc
                y_loc = bpy.context.object.location[1] * unit_sc
                z_loc = bpy.context.object.location[2] * unit_sc

                x_scale = bpy.context.object.scale[0]
                y_scale = bpy.context.object.scale[1]
                z_scale = bpy.context.object.scale[2]

                x_pixels = bpy.data.images[obj.name + '-canny'].size[0]
                y_pixels = bpy.data.images[obj.name + '-canny'].size[1]

                # print("Pixels in x: ", x_pixels)
                # print("Pixels in y: ", y_pixels)

                # account for which side of the image is the longest side
                if x_pixels >= y_pixels:
                    x_sz = (bpy.context.object.empty_display_size)
                    # this always gives a number in meters
                else:
                    x_sz = (bpy.context.object.empty_display_size) * \
                            x_pixels/y_pixels

                # The x_sz = 5 is used because blender uses 5m as the
                # default size for ref images

                # ===> Need to set up loop to use differen x_loc, y_loc
                #       or z_loc depending on which view it is
                # Top:     -x, y
                # Front:   -x, z
                # Right:   -y, z
                # Bottom:  -x, -y
                # Back:     x, z
                # Left:     y, z

                if obj.name.startswith("top"):
                    h_coord = (x_loc - x_sz * x_scale/2 * unit_sc)
                    v_coord = (x_sz / (x_pixels/y_pixels)) * y_scale/2 * \
                        unit_sc + y_loc
                elif obj.name.startswith("front"):
                    h_coord = (x_loc - x_sz * x_scale/2 * unit_sc)
                    v_coord = (x_sz / (x_pixels/y_pixels)) * y_scale/2 * \
                        unit_sc + z_loc
                elif obj.name.startswith("right"):
                    h_coord = (y_loc - x_sz * x_scale/2 * unit_sc)
                    v_coord = (x_sz / (x_pixels/y_pixels)) * y_scale/2 * \
                        unit_sc + z_loc
                elif obj.name.startswith("back"):
                    h_coord = (x_loc + x_sz * x_scale/2 * unit_sc)
                    v_coord = (x_sz / (x_pixels/y_pixels)) * y_scale/2 * \
                        unit_sc + z_loc
                elif obj.name.startswith("bottom"):
                    h_coord = (x_loc - x_sz * x_scale/2 * unit_sc)
                    v_coord = -1 * (x_sz / (x_pixels/y_pixels)) * y_scale/2 * \
                        unit_sc + y_loc
                elif obj.name.startswith("left"):
                    h_coord = (y_loc + x_sz * x_scale/2 * unit_sc)
                    v_coord = (x_sz / (x_pixels/y_pixels)) * y_scale/2 * \
                        unit_sc + z_loc

            else:
                print("Selected an invalid object.")
                h_coord, v_coord = None, None
                x_pixels, y_pixels = None, None
                return h_coord, v_coord, x_pixels, y_pixels

            im_width = 2 * (x_sz * x_scale/2 * unit_sc)
            im_height = 2 * (x_sz/(x_pixels/y_pixels)) * y_scale/2 * unit_sc

            im_horiz_scfactor = x_pixels/im_width
            im_vert_scfactor = y_pixels/im_height

            return h_coord, v_coord, im_horiz_scfactor, im_vert_scfactor, \
                im_height, unit_sc, x_loc, y_loc, z_loc

        # Augment verts with respect to the position of the image in space
        def augmented_verts(obj, h_co, v_co, raw_vert_list, horiz_scfactor,
                            vert_scfactor, im_height, unit_sc):
            aug_v = []

            # need to correct since the origin of the pic in blender is at
            # the bottom left corner

            # correct for unit scale
            unit_sc = 1/unit_sc

            if obj.startswith("front"):
                v_co = v_co - im_height
                for vert in raw_vert_list:
                    aug_v.append([(vert[0]/horiz_scfactor + h_co) * unit_sc,
                                  0, (vert[1]/vert_scfactor + v_co) * unit_sc])
            elif obj.startswith("top"):
                v_co = v_co - im_height
                for vert in raw_vert_list:
                    aug_v.append([(vert[0]/horiz_scfactor + h_co) * unit_sc,
                                 (vert[1]/vert_scfactor + v_co) * unit_sc, 0])
            elif obj.startswith("right"):
                v_co = v_co - im_height
                for vert in raw_vert_list:
                    aug_v.append([0, (vert[0]/horiz_scfactor + h_co) * unit_sc,
                                 (vert[1]/vert_scfactor + v_co) * unit_sc])
            elif obj.startswith("left"):
                v_co = v_co - im_height
                for vert in raw_vert_list:
                    aug_v.append([0, (-vert[0]/horiz_scfactor + h_co) *
                                 unit_sc,
                                 (vert[1]/vert_scfactor + v_co) * unit_sc])
            elif obj.startswith("bottom"):
                v_co = v_co + im_height
                for vert in raw_vert_list:
                    aug_v.append([(vert[0]/horiz_scfactor + h_co) * unit_sc,
                                 (-vert[1]/vert_scfactor + v_co) * unit_sc, 0])
            elif obj.startswith("back"):
                v_co = v_co - im_height
                for vert in raw_vert_list:
                    aug_v.append([(-vert[0]/horiz_scfactor + h_co) * unit_sc,
                                  0, (vert[1]/vert_scfactor + v_co) * unit_sc])

            return aug_v

        # Create mesh with augmented verts
        def canny_mesh(aug_v, obj):
            verts = aug_v
            edges = []
            # faces = [[0, 1, 2, 3]]
            faces = []
            mesh = bpy.data.meshes.new(name=ob.capitalize() + " Mesh")
            mesh.from_pydata(verts, edges, faces)
            object_data_add(context, mesh, operator=self)

            return

        def apply_rotations(obj, im, x_loc, y_loc, z_loc, unit_sc):
            print("The rotation center is about: ", x_loc, y_loc, z_loc)
            x_rot = im.rotation_euler[0]
            y_rot = im.rotation_euler[1]
            z_rot = im.rotation_euler[2]
            bpy.ops.object.editmode_toggle()
            bpy.context.scene.cursor.location[0] = x_loc / unit_sc
            bpy.context.scene.cursor.location[1] = y_loc / unit_sc
            bpy.context.scene.cursor.location[2] = z_loc / unit_sc

            bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'

            if obj.startswith("top"):
                bpy.ops.transform.rotate(value=-z_rot, orient_axis='Z')
            elif obj.startswith("back"):
                bpy.ops.transform.rotate(value=-math.pi-y_rot, orient_axis='Y')
            elif obj.startswith("left"):
                bpy.ops.transform.rotate(value=math.pi+y_rot, orient_axis='X')
            elif obj.startswith("front"):
                bpy.ops.transform.rotate(value=-y_rot, orient_axis='Y')
            elif obj.startswith("right"):  # wip
                bpy.ops.transform.rotate(value=y_rot, orient_axis='X')
            elif obj.startswith("bottom"):
                bpy.ops.transform.rotate(value=-z_rot, orient_axis='Z')

            bpy.ops.object.editmode_toggle()

            # set cursor back to zero
            bpy.context.scene.cursor.location[0] = 0
            bpy.context.scene.cursor.location[1] = 0
            bpy.context.scene.cursor.location[2] = 0
            bpy.context.scene.tool_settings.transform_pivot_point = \
                'MEDIAN_POINT'

            return

        # Main #####################

        ob = None

        try:
            # Get the filepath and drop the file name off the end
            fp = bpy.data.filepath
            fp_split = fp.split('\\')
            separator = '\\'
            fp = (separator.join(fp_split[:-1]))

            # only do one image at a time
            my_im = bpy.context.selected_objects[0]
            ob = bpy.context.selected_objects[0].name
            full_name = fp + '\\' + vprops.load_directory + '\\' + ob + \
                '-pts.txt'

            # call open csv function if files exists
            if os.path.exists(full_name):
                csv_verts = open_csv(full_name)
            else:
                print("The CSV file hasn't been created yet.")

            # call find upper left function
            horiz_coord, vert_coord, hor_sc, vert_sc, image_height, \
                unit_scale, x_center, y_center, z_center = \
                find_upper_left(bpy.context.selected_objects[0])

            # call augmented verts to reorient the vert csv file with
            # respect to the image
            augmented_vertices = augmented_verts(ob, horiz_coord, vert_coord,
                                                 v, hor_sc, vert_sc,
                                                 image_height, unit_scale)

            # create mesh
            canny_mesh(augmented_vertices, ob)

            # apply any rotation done on image after adding it to the view
            # this isn't working correctly
            apply_rotations(ob, my_im, x_center, y_center,
                            z_center, unit_scale)

        except:
            print("No object selected.")

        return{'FINISHED'}


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
                    bpy.data.images[obj.name].use_fake_user = True

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

class ObjectMtVoodooMenu(bpy.types.Menu):
    bl_idname = "object.voodoo_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout


class ObjectPtVoodooPanel(Panel):
    bl_idname = "object.voodoo_panel"
    bl_label = "Conjuur - Image Voodoo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Image Vodoo v2.1 Now With Contours"
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


class ObjectMtVoodooMenu2(bpy.types.Menu):
    bl_idname = "object.voodoo_menu2"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout


class ObjectPtVoodooPanel2(Panel):
    bl_idname = "object.voodoo_panel2"
    bl_label = "Conjuur - Edge Processing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Image Vodoo v2.1 Now With Contours"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vprops = scene.voodooprops

        layout.operator("op.canny_edges",  icon="EDGESEL")

        split = layout.split()
        col = split.row()
        col.label(text="", icon="ALIGN_FLUSH")
        col.prop(vprops, "canny_filter1")
        col.prop(vprops, "canny_filter2")

        # layout.prop(vprops, "image_toggle", text="", icon="IMAGE_RGB_ALPHA")
        # layout.operator("op.im_switchtypes")  # ,  icon="")
        layout.operator("op.im_createcsv",  icon="STICKY_UVS_DISABLE")
        layout.operator("op.im_importcsv",  icon="STICKY_UVS_LOC")


# Registration #################################

classes = (VoodooInputs,
           ObjectPtVoodooPanel,
           ObjectPtVoodooPanel2,
           SelectDir,
           ScaleSelectedImage,
           ImageAlpha,
           ImportPixels,
           ImagetoCSV,
           CannyEdges,
           ObjectMtVoodooMenu,
           ObjectMtVoodooMenu2
           )


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
