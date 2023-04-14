import pandas as pd
import json
from numpy.core.defchararray import upper
import geopandas
import numpy as np
import math

import geopandas
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer

from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select
from bokeh.layouts import row, column
from util import geographic_to_web_mercator

def add_suburb_tile(p):
  cleaned_suburbs = open('cleaned_suburbs.json', 'w')
  csv = pd.read_csv("melb_data.csv")
  csv = csv[["Suburb", "Rooms", "Price", "Distance", "Bedroom2",
            "Bathroom", "Landsize", "BuildingArea", "YearBuilt"]].rename(columns={'Suburb': 'suburb'})
  csv = csv.groupby("suburb").median().reset_index()
  #csv = csv.astype({"Rooms": "int", "Price" : "int", "Bedroom2": "int", "Bathroom" : "int",
                    #"Landsize" : "int", "BuildingArea" : "int", "YearBuilt" : "int"})
  df = geopandas.read_file('ckan_af33dd8c_0534_4e18_9245_fc64440f742e.geojson')
  df = df.to_crs(epsg=3857)
  df = df[["vic_loca_2", "geometry"]].rename(columns={'geometry': 'geometry',
                                                      'vic_loca_2': 'suburb'}).set_geometry('geometry')
  drop = ["BELLFIELD", "HILLSIDE"]
  df = df[df.suburb.isin(drop) == False]
  csv["suburb"] = upper(csv["suburb"].tolist())
  df = pd.merge(df, csv, on="suburb", how="inner")
  df_json = json.loads(df.to_json())
  json_data = json.dumps(df_json)
  cleaned_suburbs.write(json.dumps(df_json))
  geosource = GeoJSONDataSource(geojson = json_data)
  input_field = 'Price'
  palette = brewer['Blues'][8]
  palette = palette[::-1]
  suburbs = p.patches('xs','ys', source = geosource,
            line_color = 'black', line_width = 0.25, fill_alpha = 0.3, legend_label="Suburbs")
  hover = HoverTool(tooltips = [ ('Suburb','@suburb'),
                                ('Median # Rooms', '@Rooms'),
                                ('Median Price', '$@Price'),
                                ('Median Land Size (m^2)', '@Landsize'),
                                ('Median Year Built', '@YearBuilt'),
                                ('Average distance from CBD', '@Distance')], renderers=[suburbs])

  p.xgrid.grid_line_color = None
  p.ygrid.grid_line_color = None
  p.axis.visible = False
  p.add_tools(hover)













#
#data = json.load(open('Vic_suburbs.json'))
#cleaned_suburbs = open('cleaned_suburbs.json', 'w')
#suburbs= upper(df["Suburb"].unique().tolist())
#l = []
#for item in (data["features"]):
  #if item["properties"]["vic_loca_2"] in suburbs:
    #l.append(item)
#cleaned_suburbs.write(json.dumps(l))
