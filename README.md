# blender_2_8_fbx_post_import_script
Attempt to understand what is missing in imported hard edges

Context 

Steps the script should implement
1: get the edge boundary loop of all mesh islands, store vertecii info, 
2: get the result of what remove doubles does right before creating faces. 
3: get borders of diferent mesh islends that would be joined by remove doubles 
4: store those edges relations in radians 
5: apply remove doubles 
6: for compared radians above a threshold mark the edge as hard
