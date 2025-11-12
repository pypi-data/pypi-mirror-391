from dfttoolkit.visualise import VisualiseAims
import matplotlib as mpl

mpl.use("qtagg")

vis = VisualiseAims("aims.out")
vis.convergence(forces=True, ks_eigenvalues=True, fig_size=(28, 7)).savefig("test.png")
