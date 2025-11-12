import matplotlib.pyplot as plt
import matplotlib as mpl

fig, ax = plt.subplots(figsize=(1,6), layout='constrained')

colorlist=["#983604", "#CE3202","#E53602","#FE6501","#FDFC0A","#98CC05","#037F03","#3663FE","#0301CE","#300397","#010263","#030153","#020330","#000000"]
cmap = mpl.colors.LinearSegmentedColormap.from_list("dummy",colorlist)
norm = mpl.colors.Normalize(vmin=0, vmax=15)
m=mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

fig.colorbar(m, cax=ax, orientation='vertical', label='Some Units')

print(m.to_rgba(5))

plt.show()