#-------------------------- MESH SYNC --------------------------#
#-------------------------(basic version)-----------------------#
#                                                               #
#                      Alessandro Zomparelli                    #
#                             (2019)                            #
#                                                               #
# http://www.alessandrozomparelli.com/                          #
#                                                               #
# Creative Commons                                              #
# CC BY-SA 3.0                                                  #
# http://creativecommons.org/licenses/by-sa/3.0/                #

bl_info = {
    "name": "Mesh Sync",
    "author": "Alessandro Zomparelli (Co-de-iT)",
    "version": (1, 0, 0),
    "blender": (4, 0, 2),
    "location": "",
    "description": "Save/read mesh data to external files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://www.alessandrozomparelli.com/",
    "category": "Mesh"}

import bpy, re, bmesh
from mathutils import Vector
import numpy as np

def convert_object_to_mesh(ob, apply_modifiers=True, preserve_status=True):
    if not ob.name: return None
    if ob.type != 'MESH':
        if not apply_modifiers:
            mod_visibility = [m.show_viewport for m in ob.modifiers]
            for m in ob.modifiers: m.show_viewport = False
        me = simple_to_mesh(ob)
        new_ob = bpy.data.objects.new(ob.data.name, me)
        new_ob.location, new_ob.matrix_world = ob.location, ob.matrix_world
        if not apply_modifiers:
            for m,vis in zip(ob.modifiers,mod_visibility): m.show_viewport = vis
    else:
        if apply_modifiers:
            new_ob = ob.copy()
            new_ob.data = simple_to_mesh(ob)
        else:
            new_ob = ob.copy()
            new_ob.data = ob.data.copy()
            new_ob.modifiers.clear()
    bpy.context.collection.objects.link(new_ob)
    if preserve_status:
        new_ob.select_set(False)
    else:
        for o in bpy.context.view_layer.objects: o.select_set(False)
        new_ob.select_set(True)
        bpy.context.view_layer.objects.active = new_ob
    return new_ob

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
        row.prop(ob, 'sync_v_neighbors')
        row.prop(ob, 'sync_f_neighbors')
        row = col.row(align=True)
        #row.label(text="File Path:")

        if ob.sync_out_auto: simple_export(ob, ob.sync_out_path)
        #if ob.prop_read: simple_import(ob, ob.sync_in_path)


def simple_export(ob, rec_path):
    dg = bpy.context.evaluated_depsgraph_get()
    ob_eval = ob.evaluated_get(dg) if ob.sync_out_modifiers else ob
    mesh = bpy.data.meshes.new_from_object(ob_eval, preserve_all_data_layers=True, depsgraph=dg)

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

    # save EDGES
    ob_text = open(rec_path + '_edges.txt', 'w+')
    for e in mesh.edges:
        line = '{} {}\n'.format(e.vertices[0], e.vertices[1])
        ob_text.write(line)
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

    # save NEIGHBORS
    if ob.sync_v_neighbors:
        n_edges = len(mesh.edges)
        verts = np.zeros(n_edges*2)
        mesh.edges.foreach_get('vertices',verts)
        verts = verts.reshape((n_edges,2))
        verts = verts.astype(int)
        neigh = [[] for v in mesh.vertices]
        ob_text = open(rec_path + '_verts_neighbors.txt', 'w+')
        for e in verts:
            neigh[e[0]].append(e[1])
            neigh[e[1]].append(e[0])
        for v0 in neigh:
            line = ""
            for v1 in v0:
                line += '{},'.format(v1)
            line = line[:-1] + '\n'
            ob_text.write(line)
        ob_text.close()

    if ob.sync_f_neighbors:
        bm = bmesh.new()   # create an empty BMesh
        bm.from_mesh(mesh)   # fill it in from a Mesh
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        ob_text = open(rec_path + '_face_neighbors.txt', 'w+')
        for f in bm.faces:
            line = ""
            for e in f.edges:
                for lf in e.link_faces:
                    if lf != f: line += '{},'.format(lf.index)
            line = line[:-1] + '\n'
            ob_text.write(line)
        ob_text.close()

    bpy.data.meshes.remove(mesh)

def simple_import(ob, read_path):
    separators = ("," , ";" , "Q", "T", "{", "}", "(", ")", "[", "]")
    read_path = bpy.path.abspath(read_path)
    suffix = ("_vertices","_faces","_weight",".txt")
    for s in suffix:
        read_path = read_path.replace(s,"")

    # read vertices
    vertices = []
    with open(read_path + "_vertices.txt") as f:
        data = f.readlines()
        for line in data:
            for s in separators: line = line.replace(s," ")
            co = line.split()
            co = tuple(float(n) for n in co)
            if len(co) == 3: vertices.append(Vector(co))
    # read faces
    faces = []
    try:
        with open(read_path + "_faces.txt") as f:
            data = f.readlines()
            for line in data:
                for s in separators: line = line.replace(s," ")
                verts = line.split()
                verts = tuple(int(n) for n in verts)
                if len(verts) > 2: faces.append(verts)
    except: pass

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
                for s in separators: line = line.replace(s," ")
                weight = line.split()
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

    @classmethod
    def poll(cls, context):
        try: return context.mode == 'OBJECT'
        except: return False

    def execute(self, context):
        ob = bpy.context.object
        simple_import(ob, ob.sync_in_path)
        return {'FINISHED'}

class import_export_all(bpy.types.Operator):
    bl_idname = "object.import_export_all"
    bl_label = "Sync All"
    bl_description = ("Import and export all meshes")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try: return context.mode == 'OBJECT'
        except: return False

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

    @classmethod
    def poll(cls, context):
        try: return context.mode == 'OBJECT'
        except: return False

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
    bpy.types.Object.sync_out_auto = bpy.props.BoolProperty(
        name = "Real-time",
        description = "Active realtime recording (While this panel is visible)",
        default = False
        )
    bpy.types.Object.sync_out_modifiers = bpy.props.BoolProperty(
        name = "Use Modifiers", description = "Apply Modifiers", default = False
        )
    bpy.types.Object.sync_out_weight = bpy.props.BoolProperty(
        name = "Vertex Groups", description = "Export Active Weight",
        default = False
        )
    bpy.types.Object.sync_out_path = bpy.props.StringProperty(
        name="", description="Recording Folder", subtype='FILE_PATH'
        )
    bpy.types.Object.sync_smooth = bpy.props.BoolProperty(
        name = "Smooth", description = "Add Smooth Shading", default = False
        )
    bpy.types.Object.sync_in_path = bpy.props.StringProperty(
        name="", description="Reading Folder", subtype='FILE_PATH'
        )
    bpy.types.Object.sync_f_neighbors = bpy.props.BoolProperty(
        name = "Face Neighbors",
        description = "Export indexes of face's neighbors", default = False
        )
    bpy.types.Object.sync_v_neighbors = bpy.props.BoolProperty(
        name = "Vertex Neighbors",
        description = "Export indexes of vertex' neighbors", default = False
        )

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        bpy.utils.unregister_class(cls)
