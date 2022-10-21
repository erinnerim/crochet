import bpy
import bmesh
import math
import numpy as np

def parametric_surface(u_range, v_range, stitch_aspect):

    #construct parametric surface
    r = 3

    bpy.ops.mesh.primitive_xyz_function_surface(
        x_eq="(3+1.5*cos(u))*cos(v)",
        y_eq="(3+1.5*cos(u))*sin(v)",
        z_eq="1.5*sin(u)",
        range_u_max=2*math.pi,
        range_v_max=2*math.pi,
        range_u_step=u_range,
        range_v_step=v_range)

    #define bmesh
    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    bpy.ops.mesh.select_all(action='DESELECT')

    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    #separate edge loops from surface mesh
    for i in range(0, u_range):
        indices = [i,u_range+i]
        for e in bm.edges:
            if e.verts[0].index in indices and e.verts[1].index in indices:
                e.select = True
                break
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.separate(type = 'SELECTED')

    #back to object mode
    bmesh.update_edit_mesh(me,True)
    bpy.ops.object.editmode_toggle()

    ob = bpy.context.selected_objects[0]
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.object.delete(use_global=False, confirm=False)

    bpy.ops.object.select_by_type(type='MESH')
    active_ob = bpy.context.selected_objects[0]


    bpy.context.view_layer.objects.active = active_ob
    bpy.ops.object.convert(target = 'CURVE')

    obj_list = bpy.context.selected_objects
    for ob in obj_list:
        bpy.ops.object.select_all(action='DESELECT')
        #bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, enter_editmode=False, location=(0, 0, 0))
        #bpy.ops.mesh.primitive_cube_add(size=0.5, enter_editmode=False, location=(0, 0, 0))
        bpy.ops.mesh.primitive_vert_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.modifier_add(type='ARRAY')
        bpy.context.object.modifiers["Array"].use_constant_offset = True
        bpy.context.object.modifiers["Array"].use_relative_offset = False
        bpy.context.object.modifiers["Array"].constant_offset_displace[2]=stitch_aspect
        bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
        bpy.context.object.modifiers["Array"].curve = ob
        bpy.ops.object.modifier_add(type='CURVE')
        bpy.context.object.modifiers["Curve"].object = ob
        bpy.context.object.modifiers["Curve"].deform_axis = 'POS_Z'
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Array")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Curve")

    #delete the extraneous curves
    bpy.ops.object.select_by_type(extend=False, type='CURVE')
    bpy.ops.object.delete(use_global=False)

    #add all vert objects into a collection MyShape
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.collection.create(name='MyShape')
    bpy.ops.object.select_all(action='DESELECT')

    #iterate through the collection MyShape, adding vertices to their own respective groups
    counter = 0
    for obj in bpy.data.collections['MyShape'].objects:
    #obj = bpy.data.collections['MyShape'].objects[0]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        Verts_these = [i.index for i in bpy.context.active_object.data.vertices]
        VGroup_new = bpy.context.active_object.vertex_groups.new(name=f'Set.{counter:03}')
        VGroup_new.add(Verts_these, 1.0, 'ADD')
        counter+=1

    #join everything into a single mesh so we can go into edit mode
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()


#creates a randomized object consisting of a given number of vertices partitioned into two groups
def generate_bipartite_verts(num_verts):

    #define vertices
    vertices = []
    for x in range(0,num_verts//2):
        vertices.append([2*np.random.random()-1,0,0])
    for x in range(0,num_verts//2):
        vertices.append([2*np.random.random()-1,1,0])

    #make mesh
    bipartite_mesh = bpy.data.meshes.new('Bipartite_Mesh')
    bipartite_mesh.from_pydata(vertices,[],[])
    bipartite_mesh.update()

    #make object from mesh
    bipartite_object = bpy.data.objects.new('Bipartite_Object', bipartite_mesh)

    #make collection
    new_collection = bpy.data.collections.new('New_Collection')
    bpy.context.scene.collection.children.link(new_collection)

    #add object to scene collection
    new_collection.objects.link(bipartite_object)

    #selects and activates the newly created object
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bipartite_object

#assigns vertices of a bipartite object to two vertex groups based on their indices
def bipartite_vertex_group_separate(obj, num_verts):

    VGroup0_data = range(0,num_verts//2,1)
    VGroup1_data = range(num_verts//2,num_verts+1,1)
    VGroup0 = bpy.context.active_object.vertex_groups.new(name='Group_0')
    VGroup0.add(VGroup0_data, 1.0, 'ADD')
    VGroup1 = bpy.context.active_object.vertex_groups.new(name='Group_1')
    VGroup1.add(VGroup1_data, 1.0, 'ADD')

#returns a list of vertices of an object in a given vertex group
def group_lookup(obj, vg_idx):

    vs = [ v for v in obj.data.vertices if vg_idx in [ vg.group for vg in v.groups ] ]
    return vs

#returns a list of vertices of a bmesh in a given vertex group
def bm_group_lookup(bm, vg_idx):

    bm.verts.ensure_lookup_table()
    layer_deform = bm.verts.layers.deform.active
    return [v for v in bm.verts if vg_idx == v[layer_deform].items()[0][0]]

#given a vertex of an object, finds the closest vertex in a vertex group by Euclidean distance
def find_shortest_edge(obj, vert_from, vg_to_idx):

    return min(group_lookup(obj, vg_to_idx), 
    key = lambda vert_to: np.linalg.norm(vert_from.co-vert_to.co))

#given a vertex of a bmesh, finds the closest vertex in a vertex group by Euclidean distance
def bm_find_shortest_edge(bm, vert_from, vg_to_idx):

    return [vert_from, min(bm_group_lookup(bm,vg_to_idx),
    key = lambda vert_to: np.linalg.norm(vert_from.co-vert_to.co))]

#finds and adds the shortest edge from a given bmesh vertex to a bmesh vertex in a vertex group
def add_shortest_edge(obj, bm, vert_from, to_idx):  

    layer_deform = bm.verts.layers.deform.active

    shortest_edge = bm_find_shortest_edge(bm, vert_from, to_idx) 

    coords = [[e.verts[0].index, e.verts[1].index] for e in bm.edges]
    if all(set([shortest_edge[0].index, shortest_edge[1].index]) != set(c) for c in coords):
        bm.edges.new(shortest_edge)
        bmesh.update_edit_mesh(obj.data)

#iterates through a vertex group of an object to add all the shortest edges to another vertex group
def bridge_edges(obj, from_idx, to_idx):

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()



    from_verts = bm_group_lookup(bm, from_idx)
    for v in from_verts:
        add_shortest_edge(obj, bm, v, to_idx)

    bm.free()
    bpy.ops.object.mode_set(mode='OBJECT')

#iterates through a vertex group to join vertices with consecutive indices 
def make_edge_loop(bm, vg_idx):

    vg_verts = bm_group_lookup(bm, vg_idx)

    for i in range(0,len(vg_verts)-1):
        bm.edges.new([vg_verts[i], vg_verts[i+1]])

#iterates through an object's vertex groups to add a spanning index-based edge loop
def make_edge_loops(obj, vg_idxs):

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    for vg_idx in vg_idxs:
        make_edge_loop(bm, vg_idx)

    bm.free
    bpy.ops.object.mode_set(mode='OBJECT')

def main():
    u_range = 17
    v_range = 34
    stitch_aspect = 0.5

    parametric_surface(u_range, v_range, stitch_aspect)
    obj = bpy.context.object
    make_edge_loops(obj, range(0, u_range))


    obj = bpy.context.object
    for i in range(0, u_range):
        bridge_edges(obj, i, (i+1)%u_range)

main()
