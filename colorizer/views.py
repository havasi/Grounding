from django.shortcuts import render_to_response
from django.http import HttpResponse
from grounding.colorizer import make_colorizer
from csc.nl import get_nl
import re
en_nl = get_nl('en')
import nltk.data

sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
colorizer = make_colorizer()

tokenizers = []
paragraphpattern = re.compile('''\s*\n(\s*\n)+''')
tokenizers.append(lambda x: paragraphpattern.split(x))
tokenizers.append(lambda x: sent_tokenizer.tokenize(x,realign_boundaries=True))
tokenizers.append(lambda x: x.split())
names = ['paragraphs','sentences','words','characters']
#tokenizers is an array of 2-tuples of the form ('name of tokens', tokenizer)
#output is a dictionary of form {'name of tokens':[tokens], 'color':color} and so is each token except for word.

def HTMLColor(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def RGBColor(hex_string):
    """ convert #RRGGBB to an (R, G, B) tuple """
    hex_string = hex_string.strip()
    if hex_string[0] == '#': hex_string = hex_string[1:]
    if len(hex_string) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = hex_string[:2], hex_string[2:4], hex_string[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


#kind of arbitrary weightings, but make the range (0, 1)
def linearizeColorfulness(howcolorful):
    if howcolorful < 0:
        return 0
    if howcolorful > 1:
        return 1
    return howcolorful

def mergeColors(color1, color2, weight1):
    return tuple(color1[i]*weight1 + color2[i]*(1-weight1) for i in range(3))

def deepColorTokenize(text, maxdepth):
    return deepColorTokenizeHelper(text.strip(), tokenizers, names, maxdepth, (255,255,255))

def deepColorTokenizeHelper(text, tokenizers, names, maxdepth, bgcolor):
    rgba = colorizer.color_for_text(text)
    color = tuple(rgba[:3])
    alpha = rgba[3]
    try:
        howcolorful = linearizeColorfulness(alpha)
    except KeyError:
        if (color == (128,128,128)):
            howcolorful = 0
        else:
            howcolorful = 0.5
    transcolor = mergeColors(color, bgcolor, howcolorful)
    if transcolor[0] + transcolor[1] + transcolor[2] > 384:
        fontcolor = "#000000"
    else:
        fontcolor = "#ffffff"
    if maxdepth == 0:
        stopword = en_nl.is_stopword(text.strip("""'"().?!;: \t\n\r"""))
        return {'color':HTMLColor(transcolor), 'colored':(not stopword), 'bordercolor': HTMLColor(color), names[0]:[text], 'fontcolor':fontcolor}
    else:
        textcolor = {}
        textcolor['color'] = HTMLColor(transcolor)
        textcolor['fontcolor'] = fontcolor
        textcolor['bordercolor'] = HTMLColor(color)
        textcolor['colored'] = not en_nl.is_stopword(text.strip("""''""().?!;: \t\n\r"""))
        textcolor[names[0]] = [deepColorTokenizeHelper(token, tokenizers[1:], names[1:], maxdepth-1, color) for token in tokenizers[0](text) if token.strip() != '']
        return textcolor;

def splitparagraphs(text):
    return None

def startpage(request):
    if 'text' in request.POST and request.POST['text'].strip()!='':
        text = request.POST['text']
        colordepth = 3
        if request.POST['colordepth']:
            if request.POST['colordepth'] == 'wholetext':
                colordepth = 0
            elif request.POST['colordepth'] == 'paragraph':
                colordepth = 1
            elif request.POST['colordepth'] == 'sentence':
                colordepth = 2
        colorized = deepColorTokenize(text,colordepth)
        return render_to_response('colorizer/index.html', {'coloredtext':colorized, 'originaltext':text})
    else:
        return render_to_response('colorizer/index.html')
def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    for k,v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k,v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))
