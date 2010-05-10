from __future__ import with_statement
import numpy as np
from matplotlib.colors import rgb_to_hsv
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import cPickle as pickle

def get_plotdata(data_name):
    colordata = pickle.load('data/xkcd/%s' % data_name)
    plotdata = {}
    for key, data in colordata.items():
        if key.find('nigger') > -1: continue
        if data['freq'] >= 3 and len(key) >= 3 and data['freq'] * len(key) * len(key) >= 100:
            rgb = data['rgb'] / 255.0
            hsv_array = rgb_to_hsv(rgb[np.newaxis, np.newaxis, :])
            hsv = hsv_array[0,0]
            plotdata[key] = {
                'colorname': key,
                'rgb': rgb,
                'hsv': hsv,
                'freq': data['freq'],
            }
            print key, hsv
    return plotdata

def make_miniplot():
    plt.figure(figsize=(10, 10), dpi=100)
    plt.grid(False)
    polar = plt.subplot(111, polar=True, axisbg=(0.5, 0.5, 0.5))
    polar.minorticks_off()
    polar.set_xticklabels('        ', visible=False)
    polar.set_yticklabels('        ', visible=False)
    plotdata = get_plotdata()
    plotvalues = plotdata.values()
    plotvalues.sort(key=lambda x: -(x['freq']))

    sizes = np.log([v['freq']-1 for v in plotvalues])/np.log(2)
    texts = [v['colorname'] for v in plotvalues]
    hsv = np.array([v['hsv'] for v in plotvalues])
    rs = hsv[:,1]
    thetas = (0.25 - hsv[:,0]) * np.pi * 2
    rgb = np.array([v['rgb'] for v in plotvalues])
    #rgba = np.zeros( (rgb.shape[0], rgb.shape[1]+1) )
    #rgba[:,0:3] = rgb
    #rgba[:,3] = 0.8
    polar.scatter(thetas, rs, s=sizes*2, c=rgb, edgecolors='none')
    polar.set_ylim(ymin=0.0, ymax=1.1)
    
    plt.savefig('mini_colorwheel.png', dpi=100)

def make_plot(data_name):
    plt.figure(figsize=(15, 15), dpi=100)
    plt.grid(False)
    polar = plt.subplot(111, polar=True, axisbg=(0.5, 0.5, 0.5))
    polar.minorticks_off()
    #polar.set_axis_off()
    polar.set_xticklabels('        ', visible=False)
    polar.set_yticklabels('        ', visible=False)
    plotdata = get_plotdata()
    plotvalues = plotdata.values()
    plotvalues.sort(key=lambda x: -(x['freq']))

    sizes = np.log([v['freq']-1 for v in plotvalues])/np.log(2)
    texts = [v['colorname'] for v in plotvalues]
    hsv = np.array([v['hsv'] for v in plotvalues])
    rs = hsv[:,1]
    thetas = (0.25 - hsv[:,0]) * np.pi * 2
    rgb = np.array([v['rgb'] for v in plotvalues])
    #rgba = np.zeros( (rgb.shape[0], rgb.shape[1]+1) )
    #rgba[:,0:3] = rgb
    #rgba[:,3] = 0.8
    polar.scatter(thetas, rs, s=sizes*4, c=rgb, edgecolors='none')
    polar.set_ylim(ymin=0.0, ymax=1.1)
    
    for r, theta, text, size, color in zip(rs, thetas, texts, sizes, rgb):
        if np.sum(color) > 1.5: textcolor='black'
        else: textcolor='white'
        #print text
        plt.text(theta, r, text.decode('utf-8'), size=size/2.0, color=textcolor)
    
    plt.savefig('colorwheel_%s.png' % data_name, dpi=500)

if __name__ == '__main__':
    make_plot('median_colors')
