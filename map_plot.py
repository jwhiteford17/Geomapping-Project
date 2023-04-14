import pandas as pd
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LogColorMapper, ColorBar, LogTicker, HoverTool, CustomJS, Slider, RangeSlider, CDSView, CustomJSFilter, FuncTickFormatter, NumeralTickFormatter, Select, BasicTickFormatter
from bokeh.tile_providers import get_provider
import xyzservices.providers as xyz
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap
from suburbs import add_suburb_tile
from util import geographic_to_web_mercator
from bokeh.layouts import column, row


df = pd.read_csv("melb_data.csv")

price_coordinates = df[["Price", "Longtitude", "Lattitude", "Rooms", "YearBuilt", "Address", "Landsize"]]

log_mapper = LogColorMapper(palette="Inferno256", low=price_coordinates['Price'].min(), high=price_coordinates['Price'].max()*1.4)

colour_bar = ColorBar(color_mapper=log_mapper, label_standoff=12, border_line_color=None, location=(0, 0), ticker=LogTicker(), title="Price", formatter=NumeralTickFormatter(format="$0,0"))

# Convert coordinates to web mercator
price_coordinates["x"], price_coordinates["y"] = zip(*price_coordinates.apply(
    lambda row: geographic_to_web_mercator(row["Longtitude"], row["Lattitude"]), axis=1))

output_file("map.html")

map_provider = get_provider(xyz.OpenStreetMap.Mapnik)

source = ColumnDataSource(price_coordinates)

price_slider = RangeSlider(start=1000, end=10_000_000, step=100, value=(1000, 10_000_000), title="Price Range", width=400, margin=(200, 10, 10, 10), bar_color="#e84d60")
price_slider_callback = CustomJS(args=dict(source=source), code="""
    source.change.emit();
""")
price_slider.js_on_change('value', price_slider_callback)

price_filter = CustomJSFilter(args=dict(slider=price_slider), code="""
    var minPrice = slider.value[0];
    var maxPrice = slider.value[1];
    var indices = [];

    const prices = source.data['Price'];
    for (var i = 0; i < source.get_length(); i++) {
        var currPrice = parseInt(prices[i]);
        indices.push(currPrice >= minPrice && currPrice <= maxPrice);
    }
    return indices;
""")

room_slider = RangeSlider(start=0, end=6, step=1, value=(0, 6), title="Number of Bedrooms", width=400, margin=(10, 10, 10, 10), bar_color="#6c5ce7")
room_slider_callback = CustomJS(args=dict(source=source), code="""
    source.change.emit();
""")
room_slider.js_on_change('value', price_slider_callback)

room_filter = CustomJSFilter(args=dict(slider=room_slider), code="""
    var minRooms = slider.value[0];
    var maxRooms = slider.value[1];
    var indices = [];

    const rooms = source.data['Rooms'];
    for (var i = 0; i < source.get_length(); i++) {
        var currRoom = parseInt(rooms[i]);
        indices.push(currRoom >= minRooms && currRoom <= maxRooms);
    }
    return indices;
""")

land_slider = RangeSlider(start=0, end=10_000, step=1, value=(0, 10_000), title="Land Size (m^2)", width=400, margin=(10, 10, 10, 10), bar_color="#00cec9")
land_slider_callback = CustomJS(args=dict(source=source), code="""
    source.change.emit();
""")
land_slider.js_on_change('value', land_slider_callback)

land_filter = CustomJSFilter(args=dict(slider=land_slider), code="""
    var minLandsize = slider.value[0];
    var maxLandsize = slider.value[1];
    var indices = [];

    const lands = source.data['Landsize'];
    for (var i = 0; i < source.get_length(); i++) {
        var currLand = parseInt(lands[i]);
        indices.push(currLand >= minLandsize && currLand <= maxLandsize);
    }
    return indices;
""")

view = CDSView(source=source, filters=[price_filter, room_filter, land_filter])

p = figure(title="Melbourne House Sales", x_axis_label="X", y_axis_label="Y", x_range=(1.605e7, 1.62e7), y_range=(-4.55e6, -4.5e6), tools="pan, wheel_zoom, reset", active_scroll="wheel_zoom", width=700, height=700)
p.title.text_font_size = "30px"
p.add_tile(map_provider)
sales = p.circle(x="x", y="y", view=view, source=source, color={'field': 'Price', 'transform': log_mapper}, legend_label="Locations", radius=250, line_width=0)
p.add_layout(colour_bar, 'right')

field_select = Select(title="Field for Colour Map", value="Price", options=["Price", "Rooms", "Landsize"], margin=(10, 10, 10, 10))

price_formatter = NumeralTickFormatter(format="$0,0")
standard_formatter = BasicTickFormatter(use_scientific=False)

update_plot = CustomJS(args=dict(source=source, sales=sales, field_select=field_select, colour_bar=colour_bar, price_formatter=price_formatter, standard_formatter=standard_formatter), code="""
    const field = field_select.value;
    const data = source.data;
    const vals = data[field].map(x => x == 0 ? 10 : x);
    console.log(vals);
    let min = Math.min(...vals);
    let max = Math.max(...vals);
    max = field == "Price" ? max * 1.4 : max;
    min = min == 0 ? 1 : min;
    console.log(min, max);
    sales.glyph.fill_color = {'field': field, 'transform': colour_bar.color_mapper};
    colour_bar.color_mapper.low = min;
    colour_bar.color_mapper.high = max;
    colour_bar.title = field;
    switch(field) {
        case "Price":
            colour_bar.formatter.format = "$0,0";
            break;
        case "Landsize":
            colour_bar.formatter.format = "0,0'm^2'";
            break;
        default:
            colour_bar.formatter.format = "0,0";
            break;
    }
"""
)
    
field_select.js_on_change('value', update_plot)

radius_callback = CustomJS(args=dict(renderer=sales), code="""
    renderer.glyph.radius = cb_obj.value
""")

slider = Slider(start=1, end=500, value=250, step=1, title="Circle Size", width=400, margin=(10, 10, 10, 10), bar_color="black")
slider.js_on_change('value', radius_callback)

select = HoverTool(tooltips=[("Address", "@Address"), ("Price", "$@Price"), ("# of Bedrooms", "@Rooms"), ("Year Built", "@YearBuilt"), ("Lattitude", "@Lattitude"), ("Longtitude", "@Longtitude")], renderers=[sales])
p.add_tools(select)

p.legend.location = "top_left"
p.legend.click_policy="hide"

add_suburb_tile(p)

sliders = column(price_slider, room_slider, land_slider, slider, field_select)
layout = row(sliders, p, sizing_mode="stretch_both")

show(layout)
