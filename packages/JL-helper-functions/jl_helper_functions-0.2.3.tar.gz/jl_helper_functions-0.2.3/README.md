This package contains 2 functions:



-make\_vprint(verbose): returns a print function that only prints if verbose = True; useful for creating optinal print statements in long pipelines



-is\_normalized(adata, layer, verbose): checks if the matrix in layer has already been normalized for an AnnData object from scanpy





Numpy is required for the is\_normalized function to work. Scanpy is not directly required by the function, but it assumes adata is an AnnData object so the function is useless without scanpy installed. 

