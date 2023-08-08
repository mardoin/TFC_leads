import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_table
import gunicorn

# Load the CSV data
url = "https://raw.githubusercontent.com/mardoin/mardoin/main/tfc_leads_with_coordinates.csv"
df = pd.read_csv(url)

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout
app.layout = html.Div([
    dcc.Dropdown(
        id='name-dropdown',
        options=[
            {'label': 'All Names', 'value': 'All'},
            * [{'label': name, 'value': name} for name in df['name'].unique()]
        ],
        value='All'
    ),
    dcc.Graph(id='map', style={'height': '80vh'}),
    dcc.Graph(id='box-plot', style={'height': '60vh'}),
    dash_table.DataTable(
        id='average-table',
        style_table={'margin': '30px'},
        style_data={'textAlign': 'center'}
    )
])

# Create callback functions to update the figures and the table
@app.callback(
    [Output('map', 'figure'), Output('box-plot', 'figure'), Output('average-table', 'data')],
    [Input('name-dropdown', 'value')]
)
def update_figures_and_table(selected_name):
    if selected_name == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['name'] == selected_name]
    
    map_fig = go.Figure()

    map_fig.add_trace(go.Scattermapbox(
        lat=filtered_df['latitude'],
        lon=filtered_df['longitude'],
        text=filtered_df.apply(lambda row: f"{row['name']}<br>Monthly Income: ${row['monthly_total_income']:.2f}", axis=1),
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.7,
            color='blue',
        )
    ))
    
    map_fig.update_layout(
        title='Map of Leads',
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=38, lon=-95),
            zoom=3,
        )
    )
    
    box_plot_fig = px.box(
        filtered_df,
        x='monthly_total_income',
        y='source',
        title='Box Plot of Monthly Total Income by Source'
    )
    
    average_data = [
        {'Column': 'monthly_total_income', 'Average': filtered_df['monthly_total_income'].mean()},
        {'Column': 'call_id', 'Average': filtered_df['call_id'].count()}
    ]
    
    return map_fig, box_plot_fig, average_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
