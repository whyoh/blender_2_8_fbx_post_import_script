import bpy, bmesh
from collections import defaultdict


def vertex_as_tuple(v):
    return tuple(v.co)


mesh_data = bpy.context.object.data

mesh = bmesh.new()
mesh.from_mesh(mesh_data)

# for each polygon
# for each edge in the loop of that polygon
# see if there's another polygon which shares that edge
# only keep the edges with 1 polygon - that's the perimeter of an island.

edge_lookup = defaultdict(list)
for p in mesh.faces:
    for e in p.edges:
        edge_lookup[e].append(p)

edge_lookup = dict((k, v[0]) for k, v in edge_lookup.items() if len(v) == 1)

print(len(edge_lookup))

# for each edge which doesn't have another polygon
# see if there's a perimeter edge whose vertices are the same as this edge

# let's have a dictionary of vertex pairs to edges (for perimeter edges)
vertex_lookup = defaultdict(list)
for e, p in edge_lookup.items():
    a, b = [vertex_as_tuple(v) for v in e.verts]
    key = tuple(sorted((a, b)))
    vertex_lookup[key].append((p, e))

vertex_lookup = dict((k, v) for k, v in vertex_lookup.items() if len(v) == 2)

print(len(vertex_lookup))

# for those pairs of polygons
# join the polygons (into two polygons sharing a common edge, not one polygon)
# check the angle between normals
# if it's > 60 degrees then mark the edge as hard

verts_to_delete = []
for e1, e2 in vertex_lookup.values():
    # each of e1 and e2 are a (BMFace, BMEdge) pair
    edge1, edge2 = [e[1] for e in (e1, e2)]
    poly1, poly2 = [e[0] for e in (e1, e2)]
    # just change the poly of e2 to use the edge e1
    verts_to_delete.append(edge2.verts[0])
    verts_to_delete.append(edge2.verts[1])
    edge2.copy_from(edge1)

for v in verts_to_delete:
    mesh.verts.remove(v)

mesh.to_mesh(mesh_data)
    

# DONE!
