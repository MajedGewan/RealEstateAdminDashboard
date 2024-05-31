from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import ctx
import plotly.express as px
import pandas as pd
import data_handling
import dash_ag_grid as dag
from dash import dcc
from datetime import date

dcc.DatePickerRange(
    month_format='MMMM Y',
    end_date_placeholder_text='MMMM Y',
    start_date=date(2017, 6, 21)
)
app = Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN])
server = app.server
price_from, price_to = data_handling.get_price_range()
size_from, size_to = data_handling.get_size_range()
bedroom_from, bedroom_to = data_handling.get_bedroom_range()
neighborhoods = data_handling.get_neighborhoods()
houses = data_handling.get_houses()
sources = data_handling.get_sources()

row0 = dbc.Row(html.H2("Admin Portal", className='text-center'))

row1 = dbc.Row([
        dbc.Col(
                    [
                        dbc.Row(html.H3("Properties",className='text-center')),
                        dbc.Row(
                                    [
                                        html.Label('House:'),
                                        dcc.Dropdown(houses, multi=True, id='houses')
                                    ]
                                ),
                        dbc.Row(
                                    [
                                        html.Label('Neighborhood:'),
                                        dcc.Dropdown(neighborhoods, multi=True, id='neighborhoods')
                                    ]
                                ),
                        dbc.Row(
                                    [
                                        html.Label('Source:'),
                                        dcc.Dropdown(sources, multi=True, id='sources')
                                    ]
                                ),
                        dbc.Row(
                                    [
                                        html.Label('Price:'),
                                        dcc.RangeSlider(price_from, price_to,
                                        value=[price_from, price_to],
                                        id='price-slider',
                                        marks=None,
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": False,
                                            "template": "$ {value}"},
                                        ),
                                    ]
                                ),
                                    
                                
                        dbc.Row(
                                    [
                                        html.Label('Size(sqft):'),
                                        dcc.RangeSlider(size_from, size_to,
                                        value=[size_from, size_to],
                                        id='size-slider',
                                        marks=None,
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": False,
                                            "template": "{value}"},
                                        ),
                                    ]
                                ),

                        dbc.Row(
                                    [
                                        html.Label('Bedrooms:'),
                                        dcc.RangeSlider(bedroom_from, bedroom_to, 1, id='bedroom-slider'),
                                    ]
                                ),
                        dbc.Row(
                                    [
                                        html.Label('Quality:'),
                                        dcc.Checklist(
                                                            ['Low', 'Medium', 'High', 'Ultra'],
                                                            ['Low', 'Medium', 'High', 'Ultra'],
                                                            inline=True,
                                                            id='quality',
                                                            inputStyle={"margin-left": "70px"}
                                                        )
                                    ]
                                ),
                        html.Hr(),
                        dbc.Row(html.H3("Visits(Deals)",className='text-center')),
                        dbc.Row(
                            [
                                dcc.DatePickerRange(
                                    start_date=date(2023, 1, 1),
                                    end_date=date(2024, 1, 1),
                                    display_format='M-D-Y',
                                    id='date-range',
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id='total-sales', config= {'displaylogo': False}),md=6),
                                dbc.Col(dcc.Graph(id='deals', config= {'displaylogo': False}, style={
                                    "border-left":"1px solid #C7C8C9",
                                    
                                }),md=6),
                            ]
                        )
                                
                        
                    ],md=4),
        dbc.Col(
                    [
                        dbc.Col(
                            dcc.Graph(id='map', config= {'displaylogo': False}),

                        ),
                        dbc.Col(
                            html.Div(id='properties')

                        )

                    ]
            ,md=8)
            
    ])

app.layout = dbc.Container(
    [
        row0,
        html.Hr(),
        row1,
    ],
    fluid=True,
)

df = pd.read_csv('data.csv')

color_scale = [(0, 'orange'), (1,'red')]



@app.callback(
    [
        Output('map', 'figure'),
        Output('properties', 'children'),
        Output('total-sales', 'figure'),
        Output('deals', 'figure'),
    ],
    [
        Input('price-slider', 'value'),
        Input('size-slider', 'value'),
        Input('houses', 'value'),
        Input('neighborhoods', 'value'),
        Input('sources', 'value'),
        Input('bedroom-slider', 'value'),
        Input('quality', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
    ]
    
)
def update_graph(price, size, houses, neighborhoods, sources, bedrooms, quality, start_date, end_date):
    """update every 3 seconds"""
    try:
        data = data_handling.get_data()
        returned_data = data_handling.filter_data(data, price=price, size=size, houses=houses, neighborhoods=neighborhoods, sources=sources, bedrooms=bedrooms, quality=quality)
        fig = px.scatter_mapbox(returned_data, 
                        lat="Latitude", 
                        lon="Longitude", 
                        hover_name="House", 
                        hover_data=["Neighborhood", "Price"],
                        color="Price",
                        color_continuous_scale=color_scale,
                        size="Size(sqft)",
                        zoom=8)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        columnDefs = [
                        {"field": "House"},
                        {"field": "Neighborhood"},
                        {"field": "Size(sqft)"},
                        {"field": "Bedrooms"},
                        {"field": "Bathrooms"},
                        {"field": "Quality"},
                        {"field": "Furnished"},
                        {"field": "Price"},
                        {"field": "Source"},
                    ]
        table = html.Div(
        [
            dag.AgGrid(
                id="enable-pagination",
                columnDefs=columnDefs,
                rowData=returned_data.to_dict("records"),
                columnSize="sizeToFit",
                defaultColDef={"filter": True},
                dashGridOptions={"pagination": True, "animateRows": False},
            ),
            
        ],
        style={"margin": 20},)

        total_sales = data_handling.get_total_sales(start_date, end_date)


        fig_total_price = go.Figure()
        fig_total_price.add_trace(go.Indicator(
            mode = "number+delta",
            value = total_sales ,
            domain = {'row': 0, 'column': 1}))
        fig_total_price.update_layout(
            height=250,
            template = {'data' : {'indicator': [{
                'title': {'text': "Total sales"},
                'mode' : "number",},
                ]
                                }})
        
        visits, deals = data_handling.get_visits_deals(start_date, end_date)
        
        fig_deal = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = deals,
            title = {'text': "Successful Visits (Deals)"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range':[0,visits]}
            }
        ))
        fig_deal.update_layout(height=250)

        
    except Exception as e:
        raise PreventUpdate
    
    return (fig, table, fig_total_price, fig_deal)

