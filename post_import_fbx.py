import bpy, bmesh, time, warnings, os, time
from collections import defaultdict
from mathutils import Vector




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
_mergeAgainCount = 0

# define a treshold for making edges hard
_hardAfter = 0.261799 # or 45 degrees

# measure execution time
_startTime = time.time()
_endTime = 0
def edgeTagger():
  # Lets start gathering the stuff we will use later
  ob=bpy.context.selected_objects[0]
  obData = ob.data
  global _hardAfter
  print("edgeTagger")
  print( _warnMsg[3] % str(len(obData.polygons)) )
  # Lets just make sure we are in edit mode before we begin
  if(ob.mode !='EDIT'):
    bpy.ops.object.mode_set(mode='EDIT' , toggle=False)
  showme(_apply)

  # We are ready to begin the actual mesh editing
  # Documentation recomends that for any nitty gritty operations
  # We use Bmesh
  bm = bmesh.new()
  bm = bmesh.from_edit_mesh(obData)
  for e in bm.edges:
    if e.select:
      print(e)
      if e.calc_face_angle_signed(0) > _hardAfter or e.calc_face_angle_signed(0) < (_hardAfter * -1):
        e.smooth = False
      else:
        e.smooth = True
  print ( _warnMsg[4] % str(len(bm.faces)))
  # return all changes to the actual mesh
  bmesh.update_edit_mesh(ob.data, loop_triangles=True, destructive=True)
  obData.calc_loop_triangles()

  bpy.ops.object.mode_set(mode='OBJECT' , toggle=False)
  showme(_apply)

# define the edge merger
def edgeMerger():

  # Lets start gathering the stuff we will use later
  ob=bpy.context.selected_objects[0]
  obData = ob.data
  print( _warnMsg[3] % str(len(obData.polygons)) )
  global _mergeAgain, _mergeAgainCount
  _mergeAgain = False
  
  # Lets just make sure we are in edit mode before we begin
  if(ob.mode !='EDIT'):
    bpy.ops.object.mode_set(mode='EDIT' , toggle=False)
    showme(_apply)
  
  # Runs only the first time the script start
  if _mergeAgainCount == 0:
    # clean slate, deselect anything and show everything
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    showme(_apply)
  _mergeAgainCount += 1
  
  # We are ready to begin the actual mesh editing
  # Documentation recomends that for any nitty gritty operations
  # We use Bmesh
  bm = bmesh.new()
  bm = bmesh.from_edit_mesh(obData)
  print ( _warnMsg[4] % str(len(bm.faces)))
  showme(_apply)
  findingDoubles = []
  
  # Store a verts dict for referece
  edge_medians={}

  # Loop over edges 
  #for edg_pos,edge in enumerate(bm.edges):
  for edg_pos,edge in enumerate(bm.edges):
    #print("Edge %s in pos: %s" % (str(edge.index), str(edg_pos)))
    this_edge_median = median_get(edge.verts)
    edge_medians[str(edge.index)] = this_edge_median
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    
    # Try to find identical edge medians from different edges
    for i,em in edge_medians.items():
      #print([em, i, this_edge_median] )
      
      # If this Edge's Median is equal to any other Median except itself
      if em == this_edge_median and (str(i) != str(edge.index)):
        #print("Edge %s matches %s " % (str(i) ,str(edge.index)))
        edge.select = True

        # TODO: Include some math from the custom normals to help decide if welded edges
        # should be smooth[True False]
        # Lets get some math on the normals
        # having two edges, treat common vertex as individual
        # option 1
        # ((e1v1 + e1v2)/2)-e1 
        # option 2
        # e1v1.angle(e1v2) + e2v1.angle(e2v2)
        '''
        print ([
        edge.verts[0].normal.angle(Vector([0,0,1])),edge.verts[1].normal.angle(Vector([0,0,1])),
        bm.edges[int(i)].verts[0].normal.angle(Vector([0,0,1])),bm.edges[int(i)].verts[1].normal.angle(Vector([0,0,1]))
        ])
        '''

        # These lists will hold the welding params
        vert_keeper = []
        vert_welder = []

        # Loop over verts in the matched edge
        for vert in edge.verts:
          if vert not in vert_welder:
            vert_welder.append(vert)
        
        # Loop over verts in the matching edge
        # TODO: Is there a reason to maybe revert matching and matched?
        # bottom edge being in matched in matcher allows edge welding stacks
        for vert in bm.edges[int(i)].verts:
          if vert not in vert_welder:
            vert_welder.append(vert)
          if vert not in vert_keeper:
            vert_keeper.append(vert)
             
        # Build a tracemap list of verts to merge thru weld
        findingDoubles.append(bmesh.ops.find_doubles(bm, verts=vert_welder, keep_verts=vert_keeper, dist=0.0001))
  
  # Use core operator weld_verts, cause all the cool kids use it
  if len(findingDoubles):
    for fd in findingDoubles:
      for fd_vm,fd_vk in fd["targetmap"].items():
        if fd_vm.is_valid and fd_vk.is_valid:
          bmesh.ops.weld_verts(bm , targetmap = {fd_vm:fd_vk}) 
        # Dead vertices in targetmap mean a merge didn't take place, set to try again
        else:
          _mergeAgain = True
  
  # return all changes to the actual mesh
  bmesh.update_edit_mesh(ob.data, loop_triangles=True, destructive=True)
  ob.data.calc_loop_triangles()
  showme(_apply)
  return
# End edgeMerger()

## Helper functions below

# showme() updates all available 3dviews
# Its purpose is allow me as a learning obbtuse brat 
# to understand just what the heck the code is doing to the mesh
def showme(apply):
  if not apply:
    return
  #time.sleep(.35)
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

## Actual runtime starts here

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
  edgeTagger()
_endTime = time.time()
_totalTime= _endTime - _startTime

print("END OF PROGRAM \nTotal Time: %s" % str(_totalTime))
 