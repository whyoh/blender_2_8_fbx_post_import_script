import bpy
from collections import defaultdict


def vertex_as_tuple(v):
    return tuple(mesh.vertices[v].undeformed_co)


mesh = bpy.context.object.data

# for each polygon
# for each edge in the loop of that polygon
# see if there's another polygon which shares that edge
# only keep the edges with 1 polygon - that's the perimeter of an island.

edge_lookup = defaultdict(list)
for p in mesh.polygons:
    for l in p.loop_indices:
        e = mesh.loops[l].edge_index
        edge_lookup[e].append(p)

edge_lookup = dict((k, v[0]) for k, v in edge_lookup.items() if len(v) == 1)

print(len(edge_lookup))

# for each edge which doesn't have another polygon
# see if there's a perimeter edge whose vertices are the same as this edge

# let's have a dictionary of vertex pairs to edges (for perimeter edges)
vertex_lookup = defaultdict(list)
for e, p in edge_lookup.items():
    a, b = [vertex_as_tuple(v) for v in mesh.edges[e].vertices]
    key = tuple(sorted((a, b)))
    vertex_lookup[key].append((p, e))

vertex_lookup = dict((k, v) for k, v in vertex_lookup.items() if len(v) == 2)

print(len(vertex_lookup))

# for those pairs of polygons
# join the polygons (into two polygons sharing a common edge, not one polygon)
# check the angle between normals
# if it's > 60 degrees then mark the edge as hard

edges_to_delete = []
for e1, e2 in vertex_lookup.values():
    # each of e1 and e2 are a (polygon, edge index) pair
    edge1, edge2 = [mesh.edges[e[1]] for e in (e1, e2)]
    poly1, poly2 = [e[0] for e in (e1, e2)]
    # just change the poly of e2 to use the edge e1
    try:
        loop2 = mesh.loops[[l for l in poly2.loop_indices if mesh.loops[l].edge_index == edge2.index][0]]
    except:
        #print(len([l for l in poly2.loop_indices if mesh.loops[l].edge_index == edge2.index]))
        print(poly2.index, edge2.index, [l for l in poly2.loop_indices])
        raise
    verts1 = [vertex_as_tuple(v) for v in edge1.vertices]
    vert2 = vertex_as_tuple(loop2.vertex_index)
    #loop2.edge_index, loop2.vertex_index = edge1.index, edge1.vertices[verts1.index(vert2)]  # joined!
    
    #if poly1.normal.dot(poly2.normal) > 0.5:
    #    edge1.use_edge_sharp = True

    # tidy up (or attempt to)
    ## this doesn't work and neither does edges.remove() etc
    #del mesh.vertices[edge2.vertices[0]]
    #del mesh.vertices[edge2.vertices[1]]
    #del edge2
    
    edges_to_delete.append(edge2)
    
## sigh!
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for edge2 in edges_to_delete:
    mesh.vertices[edge2.vertices[0]].select = True
    mesh.vertices[edge2.vertices[1]].select = True
bpy.ops.object.mode_set(mode='EDIT')
#bpy.ops.mesh.delete(type='VERT')
#for edge2 in edges_to_delete:
 #   edge2.select = True
#bpy.ops.mesh.delete(type='EDGE')
#bpy.ops.object.mode_set(mode='OBJECT')
    

# DONE!
