import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Load data - adjust encoding and path as needed
df = pd.read_csv("data/sales_data.csv", encoding="cp1252")
df.columns = [col.upper() for col in df.columns]
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])

# Additional analysis
def get_top_customers(filtered_df, n=5):
    return filtered_df.groupby('CUSTOMERNAME')['SALES'].sum().nlargest(n).reset_index()

def get_sales_by_region(filtered_df):
    if 'TERRITORY' in filtered_df.columns:
        return filtered_df.groupby('TERRITORY')['SALES'].sum().reset_index()
    return pd.DataFrame()

# App layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = dbc.Card(
    [
        html.H2("Sales & Marketing Dashboard", className="display-6"),
        html.Hr(),
        html.P(
            "This dashboard provides insights into sales trends, product performance, and customer segmentation. "
            "Use the date picker to filter data. Key insights include:",
            className="lead",
        ),
        html.Ul([
            html.Li("Monthly sales trends to identify seasonality."),
            html.Li("Sales breakdown by product category."),
            html.Li("Top 5 customers by sales volume."),
            html.Li("Sales distribution by region (if available)."),
        ]),
        html.P(
            "Use these insights to optimize marketing strategies, identify high-value customers, and monitor product performance."
        ),
    ],
    body=True,
    style={"height": "100vh", "position": "fixed", "width": "22rem", "background": "#f8f9fa"}
)

content = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dcc.DatePickerRange(
                    id='date-picker',
                    min_date_allowed=df['ORDERDATE'].min(),
                    max_date_allowed=df['ORDERDATE'].max(),
                    start_date=df['ORDERDATE'].min(),
                    end_date=df['ORDERDATE'].max(),
                    display_format='YYYY-MM-DD'
                ),
                width=12,
                className="mb-4"
            ),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='sales-trend'), md=6),
            dbc.Col(dcc.Graph(id='category-sales'), md=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='top-customers'), md=6),
            dbc.Col(dcc.Graph(id='region-sales'), md=6),
        ]),
    ],
    style={"margin-left": "24rem", "padding": "2rem 1rem"}
)

app.layout = html.Div([sidebar, content])

@app.callback(
    Output('sales-trend', 'figure'),
    Output('category-sales', 'figure'),
    Output('top-customers', 'figure'),
    Output('region-sales', 'figure'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_charts(start_date, end_date):
    mask = (df['ORDERDATE'] >= start_date) & (df['ORDERDATE'] <= end_date)
    filtered_df = df.loc[mask]

    # Monthly sales trend
    trend_df = filtered_df.groupby(pd.Grouper(key='ORDERDATE', freq='M'))['SALES'].sum().reset_index()
    trend_df['ORDERDATE'] = trend_df['ORDERDATE'].dt.strftime('%Y-%m')
    fig1 = px.line(trend_df, x='ORDERDATE', y='SALES', title='Monthly Sales Trend')

    # Sales by category
    cat_df = filtered_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
    fig2 = px.pie(cat_df, names='PRODUCTLINE', values='SALES', title='Sales by Category')

    # Top 5 customers
    top_customers = get_top_customers(filtered_df)
    fig3 = px.bar(top_customers, x='CUSTOMERNAME', y='SALES', title='Top 5 Customers', text='SALES')

    # Sales by region (if available)
    region_df = get_sales_by_region(filtered_df)
    if not region_df.empty:
        fig4 = px.bar(region_df, x='TERRITORY', y='SALES', title='Sales by Region', text='SALES')
    else:
        fig4 = px.bar(title='Sales by Region (No Data)')

    return fig1, fig2, fig3, fig4

if __name__ == '__main__':
    app.run(debug=True)
