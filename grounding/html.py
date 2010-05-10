def make_html():
    plotdata = get_plotdata()
    plotvalues = plotdata.values()
    plotvalues.sort(key=lambda x: x['hsv'][0])
    with open('colors_%s.html' % DATA_NAME, 'w') as out:
        print >> out, """<!doctype html>
<html><head><title>xkcd Color Values</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
</head>
<body>
<div style="float:right; border: 2px solid blue; padding: 1em; margin: 1em;"><a href="color_wheel.png"><img src="tiny_colorwheel.png"/></a></div>
<p>For each color name that people gave a sufficient number of times, the color
we show here is the one closest to the <i>median</i> of all colors that people
gave that name. That makes them not just synthetic average colors: at least
one person gave that name to that actual color.</p>
"""
        print >> out, '<table style="clear: left;"><tr valign="top"><td>'
        count = 0
        halfway = (len(plotvalues)+1)/2
        print len(plotvalues)
        for v in plotvalues:
            hue, sat, val = v['hsv']
            count += 1
            hex = "#%02x%02x%02x" % tuple(v['rgb'] * 255)
            size = np.log(v['freq']-1)/np.log(2)
            textcolor = 'white'
            if val > 0.5: textcolor='black'
            bar = ('<table><tr><td style="width: %2.2fem; background-color: %s; color: %s;">%s</td><td>%s (%d)</td></tr></table>' % ((size+4), hex, textcolor, hex, v['colorname'], v['freq']))
            print >> out, bar
            if count == halfway:
                print >> out, '</td><td>'
        print >> out, "</td></tr></table>"
        print >> out, "</html>"


