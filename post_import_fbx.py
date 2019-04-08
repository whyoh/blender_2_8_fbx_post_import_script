import bpy, bmesh, time
from collections import defaultdict
#select linked
# bpy.ops.mesh.select_linked(delimit=set())

# select boundary loop
# bpy.ops.mesh.region_to_loop()

# remove doubles
# bpy.ops.mesh.remove_doubles()

# make a given object variable (ob) the selected object
# bpy.context.view_layer.objects.active = ob

# bmash from object
# bm = bmesh.from_edit_mesh(mesh)
# select mode
# bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT', action='TOGGLE')
# ['VERT', 'EDGE', 'FACE']
#trying stuff out

# showme() updates all available 3dviews
# Its purpose is allow me as a learning obbtuse brat 
# to understand just what the heck the code is doing to the mesh
def showme(apply):
  if !apply:
    return
  time.sleep(.5)
  for window in bpy.context.window_manager.windows:
    screen = window.screen

    for area in screen.areas:
        if area.type == 'VIEW_3D':
          print("found a 3d view window")
          bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# vertex_as_tuple() returns a given vertex s coordinates as a touple
def vertex_as_tuple(v):
    return tuple(v.co)

# Some helpful console level messages
_warnMsg = [
  "Select one iten and one item only before running this script you have selected ",
  "Selected object is not a Mesh",
  "Ready to start",
  "This object has %s! Polygons",
  "This Bmesh object has %s! Faces"   #4
]

# define if showme() will run at all
_apply = False

# Lets avoid trying to do anything if we have more than one object selected
if len(bpy.context.selected_objects) != 1:
  print(_warnMsg[0] + str(len(bpy.context.selected_objects))) 

# Also, let's avoid doing anything if we dont have a mesh object selected
elif bpy.context.selected_objects[0].type !="MESH":
  print(_warnMsg[1])    

# Otherwise we are ready to start
else:
  print(_warnMsg[2])
  
  # Lets start gathering the stuff we will use later
  ob=bpy.context.selected_objects[0]
  obData = ob.data
  print( _warnMsg[3] % str(len(obData.polygons)) )
  
  # Lets just make sure we are in edit mode before we begin
  if(ob.mode !='EDIT'):
    bpy.ops.object.mode_set(mode='EDIT' , toggle=False)
  showme(_apply)
  
  # clean slate, deselect anything and show everything
  bpy.ops.mesh.reveal()
  showme(_apply)
  bpy.ops.mesh.select_all(action='DESELECT')
  showme(_apply)
  
  # We are ready to begin the actual mesh editing
  # Documentation recomends that for any nitty gritty operations
  # We use Bmesh

  bm = bmesh.from_edit_mesh(obData)
  print ( _warnMsg[4] % str(len(bm.faces)))
  # Loops, fruty or not
  #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT', action='TOGGLE')
  #showme()
  #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
  #showme()
  #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE', action='TOGGLE')
  
  bm.faces[0].select = True
  bmesh.update_edit_mesh(obData,True)
  
  bpy.ops.mesh.select_linked( delimit = set())
  bpy.ops.mesh.region_to_loop()
  
  #showme()
    