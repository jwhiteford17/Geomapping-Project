import pandas as pd
import pandas_bokeh
from bokeh.io import output_file, show
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, LogColorMapper, ColorBar, LogTicker, TapTool, MapPlot
import xyzservices.providers as xyz
import math
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap


def geographic_to_web_mercator(x_lon, y_lat):
    if abs(x_lon) <= 180 and abs(y_lat) < 90:
        num = x_lon * 0.017453292519943295
        x = 6378137.0 * num
        a = y_lat * 0.017453292519943295
        x_mercator = x
        y_mercator = 3189068.5 * \
            math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
        return x_mercator, y_mercator
    else:
        print('Invalid coordinate values for conversion')


df = pd.read_csv("melb_data.csv")
price_coordinates = df[["Price", "Longtitude", "Lattitude"]]

log_mapper = LogColorMapper(palette="Inferno256", low=price_coordinates['Price'].min(), high=price_coordinates['Price'].max())

colour_bar = ColorBar(color_mapper=log_mapper, label_standoff=12, border_line_color=None, location=(0, 0), ticker=LogTicker(), title="Price")

# Convert coordinates to web mercator
price_coordinates["x"], price_coordinates["y"] = zip(*price_coordinates.apply(
    lambda row: geographic_to_web_mercator(row["Longtitude"], row["Lattitude"]), axis=1))

output_file("map.html")

map_provider = MapPlot.add_tile(xyz.OpenStreetMap.Mapnik)

source = ColumnDataSource(price_coordinates)



p = figure(title="Prices by location", x_axis_label="X", y_axis_label="Y", x_range=(1.605e7, 1.62e7), y_range=(-4.55e6, -4.5e6), tools="pan, wheel_zoom, reset", active_scroll="wheel_zoom")
p.add_tile(map_provider)
cr = p.circle(x="x", y="y", source=source, color={'field': 'Price', 'transform': log_mapper})
p.add_layout(colour_bar, 'right')

tool = p.select_one(TapTool).renderers = [cr]
show(p)
