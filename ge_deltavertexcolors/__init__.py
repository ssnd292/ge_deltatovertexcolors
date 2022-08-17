# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Positiona Delta to Vertex Color",
    "author" : "Fuxna, Redphoenix",
    "description" : "This addon creates a position delta and bakes it into vertex color based on keyshapes. Used for Farming Sim 2022 roof snow meshes.",
    "blender" : (2, 93, 0),
    "version" : (0, 0, 3),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import bmesh
from mathutils import Vector
from bpy.utils import register_class, unregister_class

def delta_to_vcolor(self, context):
    obj = context.active_object
    mesh = obj.data
    
    deltas = []

    bm = bmesh.new()
    bm.from_mesh(mesh)

    if (len(bm.verts.layers.shape) == 0):
        #print('No Basis Vector -- Aborting')
        self.report({'ERROR'},'No Basis Shapekey Found -- Aborting')
        return

    if (bm.verts.layers.shape.get("Delta Shapekey") == None):
        #val = bm.verts.layers.shape.new("Delta Shapekey")
        obj.shape_key_add(from_mix=False)
        obj.active_shape_key_index = 1
        bpy.data.shape_keys[0].key_blocks[1].name = "Delta Shapekey" 
        bm = bmesh.new()
        bm.from_mesh(mesh)        
        val = bm.verts.layers.shape[1]
        #print('No Delta Key -- Created --')
        self.report({'INFO'}, 'No Delta Shapekey Found -- Created New One --')        
    else:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        val = bm.verts.layers.shape[1]
    
    
    if (bm.loops.layers.color.get("Delta Vector Colors") == None):
        color_layer = bm.loops.layers.color.new("Delta Vector Colors")
        self.report({'INFO'}, 'No Delta Vector Colors Found -- Created New One --')   
    else:
        color_layer = bm.loops.layers.color.get("Delta Vector Colors")
        
    print(val)
    
    bm.verts.ensure_lookup_table()
    
    for i in range(len(bm.verts)):
        v = bm.verts[i]
        delta = v[val] - v.co
        delta[0] = min(max(delta[0], -1), 1)
        delta[1] = min(max(delta[1], -1), 1)
        delta[2] = min(max(delta[2], -1), 1)
        
        try:
            delta = (delta @ Vector((0.5, 0.5, 0.5))) + Vector((0.5, 0.5, 0.5))
        except:
            print("@ did not work trying *")
        
        try:
            delta = (delta * Vector((0.5, 0.5, 0.5))) + Vector((0.5, 0.5, 0.5))
        except:
            print("* did not work")

        x = delta[0] 
        y = 1.0 - delta[1]
        z = delta[2]   
        delta = Vector((x, z, y, 1.0))
        deltas.append(delta)
        
           
    for face in bm.faces:
        for loop in face.loops:
            loop[color_layer] = deltas[loop.vert.index]
                      
    bm.to_mesh(mesh)
    obj.data.update()
    print("Done.")


class deltatovcolor(bpy.types.Operator):
    bl_idname = "mesh.deltatovcolor"
    bl_label = "Bake Delta Positions"
    bl_description = "Bakes Delta Between to Shape Keys to Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        delta_to_vcolor(self, context)
        return {'FINISHED'}

class ge_deltavertexcolors_PT_scenepanel(bpy.types.Panel):
    bl_label = "Bake Position Delta to Vertex Color"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True # 
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)

        row = flow.row(align=True)
        row.operator('mesh.deltatovcolor', icon='ORIENTATION_GLOBAL', text='Bake Deltas to Vertex Colors')

def register():
    register_class(deltatovcolor)
    register_class(ge_deltavertexcolors_PT_scenepanel)


def unregister(): 
    unregister_class(deltatovcolor)
    unregister_class(ge_deltavertexcolors_PT_scenepanel)