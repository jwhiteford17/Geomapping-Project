import pandas as pd
import pandas_bokeh
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

df = pd.read_csv("melb_data.csv")
distance_price = df[["Distance", "Price"]]

output_file("test.html")

# pd.set_option("plotting.backend", "pandas_bokeh")

# fig = figure(title="Distance from CBD vs Price", x_axis_label="Distance", y_axis_label="Price")

source = ColumnDataSource(distance_price)

p = figure(title="Distance from CBD vs Price", x_axis_label="Distance", y_axis_label="Price")
p.circle(x="Distance", y="Price", source=source)

show(p)
