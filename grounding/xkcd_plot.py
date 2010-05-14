from __future__ import with_statement
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import cPickle as pickle

from color_data import component_median, make_lab_color_data, make_luv_color_data, lab_to_rgb, luv_to_rgb

def get_plotdata():
    colordata = make_lab_color_data()
    plotdata = {}
    for key, colors in colordata.items():
        if len(colors) > 4:
            lab = component_median(colors)
            rgb = [x/255.0 for x in lab_to_rgb(lab)]
            plotdata[key] = {
                'colorname': key,
                'rgb': rgb,
                'lab': lab,
                'freq': len(colors)
            }
            print key, lab
    return plotdata

def make_plot():
    plt.figure(figsize=(15, 15), dpi=100)
    plt.grid(False)
    axes = plt.subplot(111, axisbg=(0.5, 0.5, 0.5))
    axes.minorticks_off()
    plotdata = get_plotdata()
    plotvalues = plotdata.values()
    plotvalues.sort(key=lambda x: -(x['freq']))

    sizes = np.log([v['freq']-1 for v in plotvalues])/np.log(2)
    texts = [v['colorname'] for v in plotvalues]
    lab = np.array([v['lab'] for v in plotvalues])
    L_components = lab[:,0]
    a_components = lab[:,1]
    b_components = lab[:,2]
    rgb = np.array([v['rgb'] for v in plotvalues])
    #rgba = np.zeros( (rgb.shape[0], rgb.shape[1]+1) )
    #rgba[:,0:3] = rgb
    #rgba[:,3] = 0.8
    axes.scatter(a_components, b_components, s=sizes*2, c=rgb, edgecolors='none')
    
    for L, a, b, text, size, color in zip(L_components, a_components, b_components, texts, sizes, rgb):
        if L >= 50: textcolor='black'
        else: textcolor='white'
        #print text
        plt.text(a, b, text.decode('utf-8'), size=size/2.0, color=textcolor)
    plt.savefig('concept_colors2.png', dpi=500)

if __name__ == '__main__':
    make_plot()

