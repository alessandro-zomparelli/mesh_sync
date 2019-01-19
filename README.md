# Mesh Sync
Synchronize mesh object exporting or importing data.
Destination folder and a base name must be set (eg. "//myMesh") and two txt files will be created:

//myMesh_vertices.txt

Containing the informations about Vertices (eg. "0.0, 0.0, 0.0")

//myMesh_faces.txt 

Containing the informations about Faces (eg. "1 2 3 4")

Optionally a third file can be created:

//myMesh_weight.txt

Containing on each line (for each Vertex) one value for each Vertex Group. (eg. "0.25 0.75")
