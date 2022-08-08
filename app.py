import pandas as pd
import numpy as np 
import plotly.express as px 
import dash_cytoscape as cyto 
import dash 
from dash import dcc 
import dash_bootstrap_components as dbc
from dash import html 
from dash.dependencies import Input, Output, State
from dash import ctx 
from dash.exceptions import PreventUpdate
import os 
import requests 
from update_data_frame import update_df, feature_eng_data
import math 


# Instantiate the app
app = dash.Dash(__name__
                , meta_tags=[{"name": "viewport", "content": "width=device-width"}]
                , external_stylesheets=[dbc.themes.BOOTSTRAP]
                )
server = app.server
app.config["suppress_callback_exceptions"] = True


#------ Reading and Updating Data 
# Reading csv files.
data = pd.read_csv('all_scraped_wine_info.csv') # contains all attributes of the wine
recc = pd.read_csv('recommendation.csv') # contains data about top 5 recommendations 
img_df = pd.read_csv('image_df.csv') # contains image links 


data, img_df, recc = update_df(data, img_df, recc)

data = feature_eng_data(data)

wine_style = data.Style.drop_duplicates()


#------ Building the dash app 

intro_text = """

### Find a wine you like from the list and see what other wines are similar.

"""


button_github = dbc.Button(
    "View Code on github",
    outline=True,
    color="primary",
    href="https://github.com/shroffp05",
    id="gh-link",
    size="lg",
    className="button"
)

def header_section():
	return dbc.Navbar(
			dbc.Container([
				dbc.Row([
					dbc.Col(
						html.Img(className="logo", src=app.get_asset_url("dash-logo-new.png")),
						md="auto"
						),
					dbc.Col([
						html.Div(
							children=html.H1("Wine Recommender", className="wine-rec")
							)
						],
						align="center",
						md=True
						)
				]),
				 dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(button_github),
                                    ],
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            )
                        ],
                        md=2,
                    ),
                ],
                align="center",
            ),
				
			],
			fluid=True),
			dark=True,
    		color="dark",
   			sticky="top",
		)


def update_nodes_edges(wine_rec):

	df = recc.loc[recc['Name']==wine_rec, :]

	nodes = [
			{
				'classes': 'nodes',
				'data': {'id': ID, 'label': Name, 'url': url}
			}
			for ID, Name, url in (
					('0', wine_rec.title(), img_df.loc[img_df['Name']==wine_rec, 'image'].values.tolist()[0]),
					('1', df['1'].values.tolist()[0].title(), img_df.loc[img_df['Name']==df['1'].values.tolist()[0], 'image'].values.tolist()[0]),
					('2', df['2'].values.tolist()[0].title(), img_df.loc[img_df['Name']==df['2'].values.tolist()[0], 'image'].values.tolist()[0]),
					('3', df['3'].values.tolist()[0].title(), img_df.loc[img_df['Name']==df['3'].values.tolist()[0], 'image'].values.tolist()[0]),
					('4', df['4'].values.tolist()[0].title(), img_df.loc[img_df['Name']==df['4'].values.tolist()[0], 'image'].values.tolist()[0]),
					('5', df['5'].values.tolist()[0].title(), img_df.loc[img_df['Name']==df['5'].values.tolist()[0], 'image'].values.tolist()[0]),
				)
		]

	edges = [
		{'data': {'source': source, 'target': target}}
		for source, target in (
				('0','1'),
				('0','2'),
				('0','3'),
				('0','4'),
				('0','5')
			)
	]

	elements = nodes + edges 
	return elements 


def generate_options_list(df):

	output = []

	for x in df.Name.values.tolist():
		sub_output = {}
		label = html.Div(
							[
								html.Img(src=df.loc[df.Name==x, 'image'].values.tolist()[0], height=50),
								html.Div(x.title(), style={'font-size': 25, 'padding-left': 5}),
							], style={'display': 'flex', 'align-items': 'left', 'justify-content': 'left'}
						)
		value = x  
		sub_output["label"] = label
		sub_output["value"] = value

		output.append(sub_output)

	return output


def create_wine_link(wine_name):
	base_url = r"https://vinepair.com/review/"

	wine = wine_name.lower().replace(" ", "-")

	return base_url + wine + "/"

def wine_recommendations(wine_name):

	wine_rec = data.loc[data['Name']==wine_name, :]


	markdown_text = """

	### Wine
	##### {}

	### Style 

	##### {}

	### Blend/Variety 

	##### {}

	### ABV 

	##### {}

	### Price 

	##### {}

	### Perfect For 

	##### {}

	### Drink If You Like

	##### {}

	### Link

	##### {}

	""".format(
		wine_rec['Name'].values.tolist()[0].title(),
		wine_rec['Style'].values.tolist()[0].title(),
		wine_rec["Blend/Variety"].values.tolist()[0].title(),
		wine_rec['ABV'].values.tolist()[0],
		wine_rec['Price'].values.tolist()[0],
		wine_rec['Perfect For'].values.tolist()[0].title(),
		wine_rec['Drink If You Like'].values.tolist()[0].title(),
		wine_rec['link'].values.tolist()[0],
		)

	return markdown_text


stylesheet = [
		{

			'selector': '.nodes',
			'style': {
				'width': 150,
				'height': 250,
				'background-fit': 'cover',
				'background-image': 'data(url)',
				'background-color': '#fcfce1'

			}
		},
		{
			'selector': "edge",
          	'style': {
            	"curve-style": "straight",
            	"source-endpoint": "inside-to-node",
            	"target-endpoint": "inside-to-node"
            }
        }
]

app.layout = html.Div(
		id="root",
		children=[
			header_section(),
			html.Div(className="intro-text", children=dcc.Markdown(intro_text)),
			html.Div([
					html.Div(children=[
						html.Div(children=[
									html.H4("Style Filter"),
									dcc.Dropdown(
											id="style-filter",
											options=[{"label": x.title(), "value": x} for x in wine_style],
											value="Red"
										)
									],
									className="six columns pretty_container",
									style={"height": "250px"}),
						html.Div(children=[
									html.H4("Wine Filter"),
									dcc.Dropdown(
											id="wine-filter",
											options=generate_options_list(img_df),
											value="domaines barons de rothschild lafite 'legende r' 2016"
										),
								],
								className="six columns pretty_container",
								style={"height": "250px"})
						], className="filters"),
						html.Div([
						html.Div([
										cyto.Cytoscape(
												id='cytocsape-callback',
												layout={
											        'name': "cose",
											        'nodeDimensionsIncludeLabels': True,
											        'idealEdgeLenght': 50
											      },
												style={'width': '150%', 'height':'750px'},
												stylesheet=stylesheet,
												zoomingEnabled=False,
												elements = update_nodes_edges("domaines barons de rothschild lafite 'legende r' 2016")
											)
							],
							className="six columns pretty_container"
						),
						html.Div(className="six columns pretty_container", id="wine-info", children=dcc.Markdown(wine_recommendations("domaines barons de rothschild lafite 'legende r' 2016")))
						], className="graph_layout")
					]
				)
		]
	)


@app.callback(
		Output('cytocsape-callback', 'elements'),
		Input('wine-filter', 'value'),
		State('cytocsape-callback', 'elements')
	)
def update_wine_value(value, elements):

	return update_nodes_edges(value)


@app.callback(
		[Output('wine-filter', 'options'),
		 Output('wine-filter', 'value')],
		Input('style-filter', 'value')
	)
def update_wine_filter(value):


	wine_list = data.loc[data['Style']==value, 'Name'].values.tolist()

	df = img_df.loc[img_df['Name'].isin(wine_list), :]

	return generate_options_list(df), wine_list[0]


@app.callback(
		Output('wine-info', 'children'),
		Input('cytocsape-callback', 'tapNodeData'),
		Input('wine-filter', 'value')
	)
def update_wine_info(data, value):

	if ctx.triggered[0]["prop_id"] == "wine-filter.value":
		return dcc.Markdown(wine_recommendations(value))
	else:
		if data is None:
			raise PreventUpdate
		else:
			name = data["label"].lower()
			return dcc.Markdown(wine_recommendations(name))

if __name__ == '__main__':
    app.run_server(debug=True)


							