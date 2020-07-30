# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
import xlrd
import pathlib

# get relative assets
#html.Img(src=app.get_asset_url('logo.png')) 

# get relative data

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# set colours:
colors = {
    'background': '#111111',
    'text': '#FCF3CF '
}
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#TODO need to make an app folder and an assets folder and a data folder inside! 
#try to make a plotly plot with the deaths:
london=['Camden', 'Greenwich', 'Hackney', 'Hammersmith and Fulham', 'Islington', 'Kensington and Chelsea', 
        'Lambeth', 'Lewisham', 'Southwark', 'Tower Hamlets', 'Wandsworth', 'Westminster', 'Barking and Dagenham', 'Barnet', 
        'Bexley','Brent', 'Bromley', 'Croydon', 'Ealing', 'Enfield', 'Haringey', 'Harrow', 'Havering', 'Hillingdon', 'Hounslow', 
        'Kingston upon Thames', 'Merton', 'Newham', 'Redbridge', 'Richmond upon Thames', 'Sutton', 'Waltham Forest']
d_occ=pd.read_excel(DATA_PATH.joinpath('lahbtablesweek27.xlsx'), sheet_name='Occurrences - All data', skiprows=[0,1,2])
d_occ.columns=[col.replace(' ', '_') for col in d_occ.columns]
d_occ_cov=d_occ[(d_occ['Cause_of_death'] == 'COVID 19') & (d_occ['Geography_type']=='Local Authority')]
gp_cov=d_occ_cov.groupby(['Area_code','Area_name','Week_number'])['Number_of_deaths'].agg('sum').reset_index(name='deaths')
gp_cov_lon=gp_cov[gp_cov['Area_name'].isin(london)]
gp_cov_lon['cum_deaths']=gp_cov_lon.groupby('Area_name')['deaths'].transform(pd.Series.cumsum)

#get population data to make plots adjusted per 100,000 people
pop=pd.read_excel(DATA_PATH.joinpath('pop_ons.xls'), sheet_name='Persons', skiprows=[0, 1, 2, 3, 4, 5],
                 usecols=[0, 1, 2, 5])
pop_all=pop[pop['AGE GROUP'] == 'All ages']
#TODO this needs to be adapted to the death_df
with_pop=pd.merge(gp_cov_lon, pop_all, how='left', left_on=['Area_name'], right_on='AREA')
with_pop=with_pop.drop(columns=['AGE GROUP', 'AREA'])
with_pop=with_pop.rename(columns={2020:'Projected_2020_pop'})


with_pop['deaths_per_100t']=with_pop['cum_deaths']/with_pop['Projected_2020_pop']*100000
with_pop=with_pop.sort_values(by='deaths_per_100t', ascending = False)

#now fig
figD = px.line(gp_cov_lon, x="Week_number", y="deaths", color="Area_name",
              line_group="Area_name", hover_name="Area_name")
figCD = px.line(gp_cov_lon, x='Week_number', y='cum_deaths', color='Area_name',
             line_group="Area_name", hover_name="Area_name")
figCDP = px.line(with_pop, x='Week_number', y='deaths_per_100t', color='Area_name', line_group='Area_name',
             hover_name='Area_name')

### Define layout:
figD.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

figCD.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

figCDP.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='COVID19 UK data',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Confirmed COVID19 deaths in London', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='deaths-graph',
        figure=figD
    ),

    html.Div(children='Cumulative confirmed COVID19 deaths in London', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='cum-deaths-graph',
        figure=figCD
    ),

    html.Div(children='Adjusted Cumulative confirmed COVID19 deaths in London per 100, 000', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='cum-deaths-pop-graph',
        figure=figCDP
    )
    # ,

    # html.Div(children='Map of Adjusted Cumulative Lab Confirmed COVID19 Deaths in London per 100, 000', style={
    #     'textAlign': 'center',
    #     'color': colors['text']
    # }),

    # html.Iframe(
    #     id='map',
    #     srcDoc=open('<name_of_map.html>', 'r').read(), width='100%', height='600'
    # )
])


###


if __name__ == '__main__':
    app.run_server(debug=True)