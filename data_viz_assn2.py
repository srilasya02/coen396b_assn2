import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Read and Cleanup Data
data = pd.read_csv("assign2_wastedata.csv")

# Adding Accuracy
data["Accuracy"] =  np.where(data["Stream"].str.contains(" in "), "Incorrect", "Correct")
data.loc[data["Stream"].str.contains("Food Waste in Compost"),"Accuracy"] = "Correct"
data.loc[data["Stream"].str.contains("Reusables"),"Accuracy"] = "Not-Trash"

# Getting year and month
data["Date"] = pd.to_datetime(data["Date"])
data["Year"] =  data["Date"].dt.year
data["Month"] = data["Date"].dt.month

# Getting the proper waste.
data["Waste"] = data["Stream"].str.split().str[0]
data.loc[data["Substream"].str.contains("Food"),"Waste"] = "Compost" 
data.loc[data["Substream"].str.contains("Food Waste (edible)"),"Accuracy"] = "Not-Trash" 

# =============================================================================



from dash import Dash, dcc, Output, Input, html  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import plotly.express as px


substream = list(data["Substream"].unique())
waste_type = list(data["Waste"].unique())

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Build components
mytitle = dcc.Markdown(children='''## SCU Waste Collection Data''')
mygraph = dcc.Graph(figure={})

button1 = dcc.RadioItems(
    options=[
        {'label': 'Weight', 'value': 'Weight'},
        {'label': 'Volume', 'value': 'Volume'}
    ],
    value='Weight',
    labelStyle={'display': 'block'}
)

button2 = dcc.RadioItems(
    options=[
        {'label': 'Percent', 'value': 'Percent'},
        {'label': 'Value', 'value': 'Value'}
    ],
    value='Percent',
    labelStyle={'display': 'block'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label="Building", tab_id="tab-1"),
        dbc.Tab(label="Stream", tab_id="tab-2"),
        dbc.Tab(label="Substream", tab_id="tab-3"),
    ],
    id="tabs",
    active_tab="tab-1",
)

date_range_picker = dcc.DatePickerRange(
    id="date_filter",
    start_date=data["Date"].min(),
    end_date=data["Date"].max(),
    min_date_allowed=data["Date"].min(),
    max_date_allowed=data["Date"].max(),
    # calendar_orientation="vertical",
    # clearable=True,
    # with_portal=True,
)

date_range_slider = dcc.RangeSlider(
    min=data["Year"].min(),
    max=data["Year"].max(),
    value=[data["Year"].min(), data["Year"].max()],
    marks={int(t1): {'label': str(t1).split()[0]} for t1 in data["Year"].sort_values().unique()},
    step=None
)

app.layout = dbc.Container([
    dbc.Row(dbc.Col(mytitle, width={"size": 6, "offset": 2}), justify="center"),
    dbc.Row(dbc.Col(tabs, width={"size": 6, "offset": 2}), justify="center"),
    dbc.Row([
        dbc.Col([
            dbc.Row(dbc.Col(dcc.Markdown(children='_**Measurment Metric:**_'), width={"size": 6}), justify="bottom"),
            dbc.Row(dbc.Col(button1, width={"size": 6}), justify="center"),
            dbc.Row(dbc.Col(dcc.Markdown(children='_**Display as:**_'), width={"size": 6}), justify="bottom"), 
            dbc.Row(dbc.Col(button2, width={"size": 6}), justify="center")
            ]),
        dbc.Col(mygraph, width=9, align="center")
    ]),
    dbc.Row(dbc.Col(date_range_slider, width={"size": 10, "offset": 0}), justify="center"),
    dbc.Row(dbc.Col(dcc.Markdown(children="**Slide to choose years to include in the chart above**"), width={"size": 6, "offset": 3}), justify="center")
])



# Callback allows components to interact
@app.callback(
    Output(mygraph, 'figure'),
    Input(button1, 'value'),
    Input(button2, 'value'),
    Input(tabs, 'active_tab'),
    Input(date_range_slider, "value"),
)
def update_graph(y_column_name, percent_type ,active_tab, slider_val):  # function arguments come from the component property of the Input
    # start_date = pd.to_datetime(start_dt, unit='s')
    # end_date = pd.to_datetime(end_dt, unit='s')

    # filtered_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
    filtered_data = data[(data['Year'] >= slider_val[0]) & (data['Year'] <= slider_val[1])]

    
    color_map = {'Correct':'green','Incorrect':'red','Not-Trash':'gray'}


    units = " (lbs) "
    if y_column_name == "Weight":
        units = " (lbs) "
    elif y_column_name == "Volume":
        units = " (volume units)"

    if active_tab == 'tab-1':
        x_column = 'Building'
        if percent_type == 'Percent':

            title_text = f"Waste disposed correctly and <br> incorrectly from each building."

            fig = px.histogram(filtered_data, x=x_column, y=y_column_name, color='Accuracy', text_auto=True, barmode='group', barnorm='percent',color_discrete_map = color_map)
            fig.update_layout(hovermode="x")
            fig.update_layout(
                height=700,
                width=1000,
                yaxis_title=f" {y_column_name} {units} as %", 
                xaxis_title=x_column,
                title = {
                    'text' : title_text,
                    'x':0.5,
                    'xanchor': 'center',
                    }
            )
            

        else:
            title_text = f"Waste disposed correctly and  <br> incorrectly from each building."
            fig = px.histogram(filtered_data, x=x_column, y=y_column_name, color='Accuracy', text_auto=True, barmode='group',color_discrete_map = color_map)
            fig.update_layout(hovermode="x")
            fig.update_layout(
                height=700,
                width=1000,
                yaxis_title=f" {y_column_name} {units}", 
                xaxis_title=x_column,
                title = {
                    'text' : title_text,
                    'x':0.5,
                    'xanchor': 'center',
                    }
            )
            

        
    elif active_tab == 'tab-2':
        x_column = 'Waste'
        if percent_type == 'Percent':
            title_text = f"Waste correctly and incorrectly disposed for <br> each Waste Type across all buildings"
            fig = px.histogram(filtered_data, x=x_column, y=y_column_name, color='Accuracy', text_auto=True, barmode='stack', barnorm='percent',color_discrete_map = color_map)
            fig.update_layout(hovermode="x")
            fig.update_layout(
                height=700,
                width=700,
                yaxis_title=f" {y_column_name} {units} as %", 
                xaxis_title=x_column,
                title = {
                    'text' : title_text,
                    'x':0.5,
                    'xanchor': 'center',
                    }
            )
            

        else:
            title_text = f"Waste correctly and incorrectly disposed for <br> each Waste Type across all buildings"
            fig = px.histogram(filtered_data, x=x_column, y=y_column_name, color='Accuracy', text_auto=True, barmode='stack',color_discrete_map = color_map)
            fig.update_layout(hovermode="x")
            fig.update_layout(
                height=700,
                width=700,
                yaxis_title=f" {y_column_name} {units}", 
                xaxis_title=x_column,
                title = {
                    'text' : title_text,
                    'x':0.5,
                    'xanchor': 'center',
                    }
            )
            

    else:
        x_column = 'Substream'
        fig = px.histogram(filtered_data, x=y_column_name, y=x_column, color='Accuracy', text_auto=True, barmode='stack', barnorm='percent')
        fig.update_layout(hovermode="x")

        title_text = "Incorrectly disposed items in the Bins"
        fig = px.pie(filtered_data[filtered_data["Accuracy"]=="Incorrect"], values=y_column_name, names=x_column)
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        fig.update_layout(
            height=700,
            width=700,
            title = {
                    'text' : title_text,
                    'x':0.5,
                    'xanchor': 'center',
                    }
            
        )
        



    return fig  # returned objects are assigned to the component property of the Output



# Run app
if __name__=='__main__':
    app.run_server(debug=True, port=8054)
