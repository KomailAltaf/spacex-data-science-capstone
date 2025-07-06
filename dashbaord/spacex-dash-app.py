import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Launch site options for dropdown
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# App init
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, max=max_payload, step=1000,
        marks={int(min_payload): str(int(min_payload)), int(max_payload): str(int(max_payload))},
        value=[min_payload, max_payload]
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df, names='Launch Site', values='class',
            title='Total Success Launches by Site'
        )
    else:
        filtered = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered, names='class',
            title=f'Total Success vs Failed Launches for {selected_site}',
            hole=0.3
        )
        fig.update_traces(
            labels=['Failed', 'Success'],
            marker=dict(colors=['red', 'green'])
        )
    return fig

# Scatter plot callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if selected_site != 'ALL':
        filtered = filtered[filtered['Launch Site'] == selected_site]
    fig = px.scatter(
        filtered, x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success for {}'.format(
            selected_site if selected_site != 'ALL' else 'All Sites'
        )
    )
    return fig

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=8060)

