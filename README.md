# MeshSync

## Blender

### Exporting
Synchronize mesh object exporting or importing data as txt files. Chose a folder and a prefix name (eg. "//MyMesh_") and manually pres "Export".

![GitHub Logo](/Blender_Import.jpg)

According to the chosen settings the following files can be created:

myMesh_vertices.txt
Containing the informations about Vertices (eg. "0.0, 0.0, 0.0")

myMesh_edges.txt 
Containing the informations about Edges (eg. "1 2")

myMesh_faces.txt 
Containing the informations about Faces (eg. "1 2 3 4")

Additionally other files can be generated:

myMesh_weight.txt
Containing on each line (for each Vertex) one value for each Vertex Group. (eg. "0.25 0.75")

myMesh_verts_neighbors.txt
Indexes of neighbors vertices (eg. "0 1 2 3")

myMesh_face_neighbors.txt
Indexes of neighbors faces (eg. "0 1 2 3")

![GitHub Logo](/Blender_Import.jpg)

![GitHub Logo](https://raw.githubusercontent.com/alessandro-zomparelli/mesh_sync/master/Blender_Import.jpg)
