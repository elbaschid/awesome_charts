#! /usr/bin/env python
# -*- coding: utf-8 -*-
import math
import argparse
import itertools

from svgplotlib import Base
from svgplotlib import getFont
from svgplotlib.Pie import Pie
import svgplotlib.Config as Config
from svgplotlib.SVG import SVG, show

from colourlovers import ColourLovers

#import kuler as kulerapi
#KULER_API_KEY = '1CE8EF1EA94657BA43864B9287974119'

class AwesomeBar(Base):
   
    def __init__(self, title, values, labels, colors=None, **kwargs):
        # smaller default font
        if not 'fontSize' in kwargs:
            kwargs['fontSize'] = 12 

        super(AwesomeBar, self).__init__(**kwargs)

        titleScale = kwargs.get('titleScale', 2.2)
        titleColor = kwargs.get('titleColor', 'black')
        labelColor = kwargs.get('labelColor', 'black')

        spacing = kwargs.get('spacing', 0)

        if colors is None or len(colors) == 0:
           colors = self.COLORS
        
        style = self.style = {
            'stroke'        : 'black',
            'stroke-width'  : '1',
            'fill'          : 'black',
        }
        
        textStyle = self.textStyle = {
            'stroke'        : 'none',
        }
 
        main_group = self.Group(**style)

        # plot area size
        self.plotWidth = WIDTH = kwargs.get('size', 1000)
        self.plotHeight = kwargs.get('size', 90)
        
        HEIGHT = self.plotHeight - 2 * self.PAD

        dy = self.PAD
        dx = self.PAD 

        self.set('width', WIDTH)
        self.set('height',  self.plotHeight)

        titleSize = self.textSize(unicode(title))
        title_y = dy + (self.plotHeight / 2) + self.PAD
        title_y -= (titleScale * (titleSize.height + titleSize.descent) / 2)

        text = main_group.EText(
            self.font, 
            title, 
            x=dx, 
            y=title_y, 
            scale=titleScale,
            **{'stroke': 'none'}
        ) 

        plot_x = dx + 200
        plot_y = dy

        colouriter = itertools.cycle(colors)
        plot_area = main_group.Group(transform="translate(%g,%g)" % (plot_x, plot_y), **style)

        bar_width = WIDTH - plot_x - (spacing * (len(values)-1))

        label_style = {
            'stroke': 'none', 
            'fill':'black'
        }

        bar_x = bar_y = 0
        for value, label in zip(values, labels):

            ## rectangle width is percentage of bar width
            rect_width = int((float(value) / 100.0) * bar_width)

            hex_colour = colouriter.next()

            plot_area.Rect(
                x=bar_x,
                y=bar_y,
                width=rect_width,
                height=HEIGHT,
                stroke=hex_colour,
                fill=hex_colour
            )

            label_size = self.textSize(unicode(label))

            text_y = (bar_y + (HEIGHT / 2)) - (self.textSize(unicode(label))[1] / 2)
            text = plot_area.EText(
                self.font, 
                label, 
                x=bar_x+10, 
                y=text_y, 
                **label_style
            ) 

            bar_x = bar_x + rect_width + spacing

def get_labels_values(args_list):
    labels = []
    values = []
    for raw_value in args_list:
        try:
            label, value = raw_value.rsplit(':', 1)
            labels.append(label)
            values.append(value)
        except ValueError:
            parser.error(
                "cannot determine 'label:value' from '%s'" % raw_value
            )
    return labels, values

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-a', '--awesomeness', nargs='*', default=[],
        help="awesomeness as list of 'label:value' with value in %"
    )
    parser.add_argument(
        '-i', '--input', default=None,
        help='input file defining an awesome bar in each line'
    )
    parser.add_argument(
        '-p', '--palette', default='random',
        help='define how to search for a palette on ColourLovers',
    )
    parser.add_argument(
        '-t', '--title',
        help='text used as title for the awesome bar'
    )
    parser.add_argument(
        '-o', '--output', 
        help='filename the SVG should be saved to' 
    )

    args = parser.parse_args()

    batch_list = []
    if len(args.awesomeness) > 0:
        batch_list.append(args)

    elif args.input:
        with open(args.input, 'r') as input_file:
            for line in input_file:

                if len(line.strip()) == 0:
                    continue

                args_list = [x.strip() for x in line.strip().split(';')]
                batch_list.append(
                    parser.parse_args([
                        '-t', args_list[0], 
                        '-p', args_list[1],
                        '-o', args_list[2],
                        '-a'
                    ] + args_list[3:])
                )
                
    cl_api = ColourLovers()
    #kuler = kulerapi.Kuler(KULER_API_KEY)

    for args in batch_list:
        labels, values = get_labels_values(args.awesomeness)
        print labels, values

        try:
            palettes = cl_api.get_palette(args.palette)
        except:
            print "Could not get palette from ColourLovers. Using default."
            palettes = []

        colours = []
        ##extract list of hex values from palette
        if len(palettes) > 0:
            for hex_code in palettes[0].colours:
                colours.append(hex_code)

        print colours

        awesome_bar = AwesomeBar(
            args.title,
            values,  
            labels=labels,
            colors=colours,
            fontFamily='Ubuntu', 
            fontStyle='Regular',
        )

        if args.output:
            with open(args.output, 'w') as out_fh:
                awesome_bar.write(out_fh)
        else:
            show(awesome_bar, awesome_bar.width, awesome_bar.height)

if __name__ == "__main__":
    main()
