#-------------------------- MESH SYNC --------------------------#
#-------------------------(basic version)-----------------------#
#                                                               #
#                      Alessandro Zomparelli                    #
#                             (2019)                            #
#                                                               #
# http://sketchesofcode.wordpress.com/                          #
#                                                               #
# Creative Commons                                              #
# CC BY-SA 3.0                                                  #
# http://creativecommons.org/licenses/by-sa/3.0/                #

bl_info = {
    "name": "Mesh Sync",
    "author": "Alessandro Zomparelli (Co-de-iT)",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Save/read mesh data to external files",
    "warning": "",
    "wiki_url": "https://wiki.blender.org/index.php/Extensions:2.6/"
                "Py/Scripts/Mesh/Tissue",
    "tracker_url": "https://plus.google.com/u/0/+AlessandroZomparelli/",
    "category": "Mesh"}

import bpy, re
from mathutils import Vector

class OBJECT_PT_mesh_sync(bpy.types.Panel):
    bl_idname = "OBJECT_PT_mesh_sync"
    bl_label = "Mesh Sync"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            return ob.type == 'MESH'
        except: return False

    def draw(self, context):
        layout = self.layout
        ob = context.object


        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('object.import_all', icon='IMPORT')
        row.operator('object.export_all', icon='EXPORT')
        row = col.row(align=True)
        row.operator('object.import_export_all', icon='FILE_REFRESH')
        row = col.row(align=True)
        row.label(text="Import:")
        row = col.row(align=True)
        col.prop(ob, 'sync_in_path', icon='FILE_FOLDER')
        col.separator()
        col.operator('object.import_mesh_data', icon='IMPORT')
        col.separator()
        row = col.row(align=True)
        row.label(text="Export:")
        row = col.row(align=True)
        row.prop(ob, 'sync_out_auto')
        col.prop(ob, 'sync_out_path', icon='FILE_FOLDER')
        col.separator()
        col.operator('object.export_mesh_data', icon='EXPORT')
        row = col.row(align=True)
        row.prop(ob, 'sync_out_modifiers')
        row.prop(ob, 'sync_out_weight')
        row = col.row(align=True)
        #row.label(text="File Path:")

        if ob.sync_out_auto: simple_export(ob, ob.sync_out_path)
        #if ob.prop_read: simple_import(ob, ob.sync_in_path)


def simple_export(ob, rec_path):
    mesh = ob.to_mesh(bpy.context.depsgraph, ob.sync_out_modifiers)
    
    # save VERTICES
    v_list = []
    for v in mesh.vertices:
        v_list.append(v.co)

    lines = []
    rec_path = bpy.path.abspath(rec_path)
    ob_text = open(rec_path + '_vertices.txt', 'w+')

    #lines.append(str(len(v_list)) + '\n')
    for i in range(len(v_list)):
        #open mesh
        co_1 = str(v_list[i][0])
        co_2 = str(v_list[i][1])
        co_3 = str(v_list[i][2])
        co = co_1 + ', ' + co_2 + ', ' + co_3 + '\n'
        lines.append(co)

    ob_text.writelines(lines)
    ob_text.close()

    # save FACES
    ob_text = open(rec_path + '_faces.txt', 'w+')
    #ob_text.write(str(len(mesh.polygons)) + '\n')
    for f in mesh.polygons:
        for i in range(0,len(f.vertices)):
            a=str(f.vertices[i])
            if i != len(f.vertices) - 1:
                a += ' '
            ob_text.write(a)
        ob_text.write('\n')
    ob_text.close()

    # save WEIGHT
    if ob.sync_out_weight:# and ob.vertex_groups.active:
        ob_text = open(rec_path + '_weight.txt', 'w+')
        for v in mesh.vertices:
            first = True
            for vg in ob.vertex_groups:
                #ob_text.write(str(len(mesh.vertices)) + '\n')
                if first: first = False
                else: ob_text.write(' ')
                weight = 0
                for w in v.groups:
                    if w.group == vg.index:
                        weight = w.weight
                ob_text.write(str(weight))
            ob_text.write('\n')
        ob_text.close()
    bpy.data.meshes.remove(mesh)

def simple_import(ob, read_path):

    read_path = bpy.path.abspath(read_path)

    # read vertices
    vertices = []
    with open(read_path + "_vertices.txt") as f:
        data = f.readlines()
        for line in data:
            co = line.replace(';',' ').replace(',',' ').replace('}',' ').replace('{',' ').split()
            co = tuple(float(n) for n in co)
            if len(co) == 3: vertices.append(Vector(co))

    # read faces
    faces = []
    with open(read_path + "_faces.txt") as f:
        data = f.readlines()
        for line in data:
            verts = line.replace(';',' ').replace(',',' ').replace('Q{',' ').replace('}',' ').split()
            verts = tuple(int(n) for n in verts)
            if len(verts) > 2: faces.append(verts)

    new_me = bpy.data.meshes.new("imported")
    new_me.from_pydata(vertices, [], faces)
    new_me.update(calc_edges=True)
    old_me = ob.data
    ob.data = new_me
    bpy.data.meshes.remove(old_me)

    # vertex groups
    try:
        with open(read_path + "_weight.txt") as f:
            for vg in ob.vertex_groups: ob.vertex_groups.remove(vg)
            data = f.readlines()
            first = True
            count = 0
            for line in data:
                weight = line.replace(';',' ').replace(',',' ').split()
                weight = tuple(float(n) for n in weight)
                if first:
                    for i in range(len(weight)):
                        ob.vertex_groups.new(name='Imported_' + str(i))
                    first = False
                for i in range(len(weight)):
                    ob.vertex_groups[i].add([count], weight[i], 'REPLACE')
                count += 1
    except: pass

class export_mesh_data(bpy.types.Operator):
    bl_idname = "object.export_mesh_data"
    bl_label = "Export Mesh Data"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = bpy.context.object
        simple_export(ob, ob.sync_out_path)
        return {'FINISHED'}

class import_mesh_data(bpy.types.Operator):
    bl_idname = "object.import_mesh_data"
    bl_label = "Import Mesh Data"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = bpy.context.object
        simple_import(ob, ob.sync_in_path)
        return {'FINISHED'}

class import_export_all(bpy.types.Operator):
    bl_idname = "object.import_export_all"
    bl_label = "Sync All"
    bl_description = ("Import and export all meshes")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if o.sync_out_path != "":
                    try: simple_export(o, o.sync_out_path)
                    except: pass
                if o.sync_in_path != "":
                    try: simple_import(o, o.sync_in_path)
                    except: pass
        return {'FINISHED'}

class import_all(bpy.types.Operator):
    bl_idname = "object.import_all"
    bl_label = "Import All"
    bl_description = ("Import all meshes")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if o.sync_in_path != "":
                    try: simple_import(o, o.sync_in_path)
                    except: pass
        return {'FINISHED'}

class export_all(bpy.types.Operator):
    bl_idname = "object.export_all"
    bl_label = "Export All"
    bl_description = ("Export all meshes")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if o.sync_out_path != "":
                    try: simple_export(o, o.sync_out_path)
                    except: pass
        return {'FINISHED'}

classes = (
    OBJECT_PT_mesh_sync,
    export_mesh_data,
    import_mesh_data,
    import_all,
    export_all,
    import_export_all
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.sync_out_auto = bpy.props.BoolProperty(name = "Real-time", description = "Active realtime recording (While this panel is visible)", default = False)
    bpy.types.Object.sync_out_modifiers = bpy.props.BoolProperty(name = "Use Modifiers", description = "Apply Modifiers", default = False)
    bpy.types.Object.sync_out_weight = bpy.props.BoolProperty(name = "Vertex Groups", description = "Export Active Weight", default = False)
    bpy.types.Object.sync_out_path = bpy.props.StringProperty(name="", description="Recording Folder", subtype='FILE_PATH')
    #bpy.types.Object.prop_read = bpy.props.BoolProperty(name = "Real-time Import", description = "Active realtime import", default = False)
    bpy.types.Object.sync_in_path = bpy.props.StringProperty(name="", description="Reading Folder", subtype='FILE_PATH')

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        bpy.utils.unregister_class(cls)
