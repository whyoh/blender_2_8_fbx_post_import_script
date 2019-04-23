import bpy, bmesh, time, warnings, os
from collections import defaultdict
from mathutils import Vector


# showme() updates all available 3dviews
# Its purpose is allow me as a learning obbtuse brat 
# to understand just what the heck the code is doing to the mesh
def showme(apply):
  if not apply:
    return
  time.sleep(.35)
  for window in bpy.context.window_manager.windows:
    screen = window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
          #print("found a 3d view window")
          with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# vertex_as_tuple() returns a given vertex s coordinates as a touple
def vertex_as_tuple(v):
    return tuple(v.co)

# median_get() calculates the median point of an edge given as a set of verts
def median_get(verts_sel):
  Vco_sel= [v.co for v in verts_sel]
  return sum(Vco_sel, Vector()) / len(Vco_sel)

# Some helpful console level messages
_warnMsg = [
  "Select one iten and one item only before running this script you have selected ",
  "Selected object is not a Mesh",
  "Ready to start",
  "This object has %s! Polygons",
  "This Bmesh object has %s! Faces",   #4
  "The mesh has no Normals Split Data"
]

# define if showme(_apply) will run at all
_apply = False

# define if we should try merging again
_mergeAgain = True

# define the edge merger
def edgeMerger():
  # Lets start gathering the stuff we will use later
  ob=bpy.context.selected_objects[0]
  obData = ob.data
  print( _warnMsg[3] % str(len(obData.polygons)) )
  _mergeAgain = False
  # Lets just make sure we are in edit mode before we begin
  if(ob.mode !='EDIT'):
    bpy.ops.object.mode_set(mode='EDIT' , toggle=False)
  showme(_apply)
  
  # clean slate, deselect anything and show everything
  bpy.ops.mesh.reveal()
  bpy.ops.mesh.select_all(action='DESELECT')
  showme(_apply)

  # We are ready to begin the actual mesh editing
  # Documentation recomends that for any nitty gritty operations
  # We use Bmesh
  bm = bmesh.new()
  bm = bmesh.from_edit_mesh(obData)
  print ( _warnMsg[4] % str(len(bm.faces)))
  showme(_apply)

  # Store a verts dict for referece
  edge_medians={}

  # Loop over edges 
  for edg_pos,edge in enumerate(bm.edges):
    print("Edge %s in pos: %s" % (str(edge.index), str(edg_pos)))
    this_edge_median = median_get(edge.verts)
    edge_medians[str(edge.index)] = this_edge_median
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    
    # Try to find identical edge medians from different edges
    for i,em in edge_medians.items():
      #print([em, i, this_edge_median] )
      
      # If this Edge's Median is equal to any other Median except itself
      if em == this_edge_median and (str(i) != str(edge.index)):
        print("Edge %s matches %s " % (str(i) ,str(edge.index)))
        
        # These lists will hold the welding params
        vert_keeper = []
        vert_welder = []

        # Loop over verts in the matched edge
        for vert in edge.verts:
          print(["Vert co:      ",edge.index,vert.index ,vert.co])
          print(["Vert no:      ",edge.index,vert.index, vert.normal])
          if vert not in vert_welder:
            vert_welder.append(vert)
        
        # Loop over verts in the matching edge
        # TODO: Is there a reason to maybe revert matching and matched?
        for vert in bm.edges[int(i)].verts:
          print(["VertMatch co: ",i,vert.index ,vert.co])
          print(["VertMatch no: ",i,vert.index, vert.normal])
          if vert not in vert_welder:
            vert_welder.append(vert)
          if vert not in vert_keeper:
            vert_keeper.append(vert)
        
        # Trying to look at weld options here
        # bmesh.ops.find_doubles(bm, verts, keep_verts, dist)
        # Build a tracemap of verts to merge thru weld
        findingDoubles = bmesh.ops.find_doubles(bm, verts=vert_welder, keep_verts=vert_keeper, dist=0.0001)
        
        # Define if the resulting edge after weld should be hard or smooth

        # Use core operator weld_verts, cause all the cool kids use it
        bmesh.ops.weld_verts(bm , targetmap = findingDoubles["targetmap"])
      
      #print(["Edge Median: ", this_edge_median])
      #print(["Edge Tag: ", edge.tag])

      # return all changes to the actual mesh
      #bmesh.update_edit_mesh(obData,True)
      bmesh.update_edit_mesh(ob.data, loop_triangles=True, destructive=True)
      obData.calc_loop_triangles()
      showme(_apply)
      
      # Clear the screen after an iteration
      os.system("cls")
      
      # free Bmesh
      #bm.free()

      # call thyself
      _mergeAgain = True
      #bpy.ops.object.mode_set(mode='OBJECT' , toggle=False)
      #edgeMerger()
    # Visually marked an edge as processed (for use with showme() mostly)
    #edge.select = True
# End edgeMerger()


# Lets avoid trying to do anything if we have more than one object selected
if len(bpy.context.selected_objects) != 1:
  print(_warnMsg[0] + str(len(bpy.context.selected_objects))) 

# Also, let's avoid doing anything if we dont have a mesh object selected
elif bpy.context.selected_objects[0].type !="MESH":
  print(_warnMsg[1])    

# Make sure we have custom split normals to deal with
elif not bpy.context.selected_objects[0].data.has_custom_normals:
    print( _warnMsg[5])

# Otherwise we are ready to start
else:
  print(_warnMsg[2])
  
  # call the iterative function that will call itself after it has finished mergin an edge

  while _mergeAgain:
    edgeMerger()
  
'''

Edge1
['vert co: ', 0, Vector((-0.04274683818221092, 1.6370863914489746, -0.044565267860889435))]
['vert no: ', 0, Vector((-0.7777091264724731, -0.13971489667892456, -0.612901508808136))]
['vert co: ', 2, Vector((-0.04317079111933708, 1.6509138345718384, -0.04676194116473198))]
['vert no: ', 2, Vector((-0.6971747875213623, -0.10606074333190918, -0.7090122103691101))]
['edge Median: ', Vector((-0.042958814650774, 1.6440000534057617, -0.04566360265016556))]

Edge6
['vert co: ', 0, Vector((-0.04274683818221092, 1.6370863914489746, -0.044565267860889435))]
['vert no: ', 0, Vector((-0.7777091264724731, -0.13971489667892456, -0.612901508808136))]
['vert co: ', 4, Vector((-0.04317079111933708, 1.6509138345718384, -0.04676194116473198))]
['vert no: ', 4, Vector((-0.8149774670600891, -0.11520981043577194, -0.5679246783256531))]
['edge Median: ', Vector((-0.042958814650774, 1.6440000534057617, -0.04566360265016556))]



Edge5
['vert co', 4, Vector((-0.04317079111933708, 1.6509138345718384, -0.04676194116473198))]
['vert no', 4, Vector((-0.8149774670600891, -0.11520981043577194, -0.5679246783256531))]
['vert co', 5, Vector((-0.05244690179824829, 1.6519113779067993, -0.03365299478173256))]
['vert no', 5, Vector((-0.8300769925117493, -0.14721477031707764, -0.5378661751747131))]

Edge25
['vert co', 13, Vector((-0.04317079111933708, 1.6509138345718384, -0.04676194116473198))]
['vert no', 13, Vector((-0.789111316204071, -0.22680334746837616, -0.5708444714546204))]
['vert co', 14, Vector((-0.05244690179824829, 1.6519113779067993, -0.03365299478173256))]
['vert no', 14, Vector((-0.85653156042099, -0.23453369736671448, -0.45972558856010437))]

https://blender.stackexchange.com/questions/134798/finding-a-specific-face-vertex-edge-based-on-position-value-not-indices-value

'''
