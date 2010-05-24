from __future__ import with_statement
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import cPickle as pickle

from color_data import component_median, make_lab_color_data, lab_to_rgb, luv_to_rgb

def get_plotdata():
    colordata = make_lab_color_data()
    plotdata = {}
    for key, colors in colordata.items():
        if len(colors) > 4:
            lab = component_median(colors)
            rgb = [x/255.0 for x in lab_to_rgb(lab)]
            if key == 'rise': colorname = 'rose'
            else: colorname = key
            plotdata[key] = {
                'colorname': colorname,
                'rgb': rgb,
                'lab': lab,
                'freq': len(colors)
            }
            print key, lab
    return plotdata

def make_plot():
    plt.figure(figsize=(15, 12), dpi=100)
    plt.grid(False)
    axes = plt.subplot(111, axisbg=(1,1,1))
    axes.minorticks_off()
    plotdata = get_plotdata()
    plotvalues = plotdata.values()
    plotvalues.sort(key=lambda x: -(x['freq']))

    sizes = np.sqrt(np.sqrt([v['freq']-1 for v in plotvalues]))*2
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
    plt.xlim(xmin=-100, xmax=100)
    plt.ylim(ymin=-100, ymax=100)
    plt.xlabel('a')
    plt.ylabel('b')
    
    for L, a, b, text, size, color in zip(L_components, a_components, b_components, texts, sizes, rgb):
        textcolor='black'
        #print text
        if a > -70 and a < 85 and b > -70 and b < 85:
            plt.text(a, b, text.decode('utf-8'), size=size/2.0, color=textcolor)
    plt.savefig('concept_colors2.png', dpi=1000)

if __name__ == '__main__':
    make_plot()

