import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
from datetime import datetime
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta
from dash_ag_grid import AgGrid

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Account Service Credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name(PATH_TO_JSON_FILE, scope)

# Google Sheets Authentication and Opening
gc = gspread.authorize(credentials)
sheet = gc.open('Personal Budget Control').sheet1

# Select Google Sheets Columns for dashboard analysis
data = sheet.get_all_records(expected_headers=[
'Date',
'Month',
'Year',
'Description',
'Macrocategory',
'Category',
'Condition',
'Value',
'Value Calculation',
'Status',
'Type',
'Others'
])

## Or, load data from .csv file:
# df = pd.read_csv('')

# Converting Google Sheets into DataFrame format 
df = pd.DataFrame(data)
df = df.fillna('')
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
df['M-Y'] = df['Month'].astype(str) + '/' + df['Year'].astype(str)
df['Month-Year'] = pd.to_datetime(df['M-Y'], format='%m/%Y')
df['Value'] = df['Value'].astype(float)
df_outflow_options = df[(df['Macrocategory']!='Salary') & (df['Macrocategory']!='Investment')]

# Defining options for Period Dropwdown
date_current = datetime.now()
month_current = date_current.month
year_current = date_current.strftime('%Y')
year_current_int = int(year_current)
month_year_current = f"{month_current}/{year_current}"

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# DEFINING DASHBOARD INPUTS

# INPUT INVESTMENT CONTRIBUTION GOAL
investment_target = 40000
# INPUT INVESTMENT CONTRIBUTION GOAL DEADLINE / FORMAT YYYY/MM/DD
date_goal = datetime(2025, 8, 1)
# INPUT USER´S MANUAL TEXT
manual_text = """ User's manual goes here """ 

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

date_today = datetime.today()
months_due_goal = relativedelta(date_goal, date_today)
months_due_goal = months_due_goal.years * 12 + months_due_goal.months + 1

# Defining options for Dropdowns and Status Table
macrocategories = [{'label': x, 'value': x} for x in df_outflow_options["Macrocategory"].unique()]
date_options = [{'label': x, 'value': x} for x in df["M-Y"].unique()]
status_options = [{'label': x, 'value': x} for x in df["Status"].unique()]

### Creating dashboard elements
# Status Table
df_status = df[(df['Status'] != '') & (df['Status'] != 'Pending Income - Done')].copy()
df_status.loc[:, 'Date'] = pd.to_datetime(df_status['Date']).dt.strftime('%m/%d')
df_status.dropna()

# Historic Investment Contributions Bar Chart
df_invest = df[df['Macrocategory']=='Investment']

colors= {
'Expected Contribution': '#A9A9A9',
'Additional Contribution': 'lightgrey'}  

fig_invest = px.bar(
    df_invest,
    x = 'Month-Year',
    y = 'Value Calculation',
    color='Category',
    color_discrete_map=colors,
    labels = {'Month-Year':'', 'Value Calculation':''}
)
fig_invest.update_layout(showlegend=False,
                        plot_bgcolor='#aacfc1',
                        paper_bgcolor='lightgrey',
                        barmode='stack', 
                        yaxis=dict(showgrid=False, range=[0, max(df['Value Calculation'])*0.7], title=''),
                        margin=dict(l=0, r=25, t=25, b=0, pad=20),
                        width=790,
                        height=200,
                        uniformtext_minsize=8,
                        uniformtext_mode='hide',
                        font=dict(size=14))
fig_invest.update_traces(texttemplate='%{y}', textposition='inside', marker=dict(line=dict(color='#000000', width=1)))
fig_invest.update_yaxes(showticklabels=False)
fig_invest.update_xaxes(tickformat="%-m/%y", dtick='M1')

# Accumulated Investment Chart
df_invest_ac = df_invest[['Month-Year','Value']]
df_invest_ac_gp = df_invest_ac.groupby('Month-Year')['Value'].sum().reset_index()
df_invest_ac_gp['Accumulated'] = df_invest_ac_gp['Value'].cumsum()

fig_acum = px.bar(df_invest_ac_gp, x='Month-Year', y='Accumulated')
fig_acum.update_layout(showlegend=True, 
                       plot_bgcolor='#aacfc1', 
                       paper_bgcolor='lightgrey', 
                       yaxis=dict(showgrid=False, range=[0, max(df['Value'])*4.5], title='Value'),
                       margin=dict(l=0, r=25, t=25, b=0, pad=20),
                       width=790,
                       height=200)
fig_acum.update_traces(texttemplate='%{y:,.0f}', textposition='outside', marker_color='lightgrey', marker=dict(line=dict(color='#000000', width=1)))
fig_acum.update_yaxes(showticklabels=False, title_text='')
fig_acum.update_xaxes(showticklabels=False, title_text='', tickformat="%-m/%y", dtick='M1')

# Creating Investment Performance Table
## Target Goal Date
formatted_date = date_goal.strftime('%m/%y')

## Total Investment Contribution Table 
total_contribution = df_invest['Value'].sum()

## Pending Investment Contributions Table
pending_contribution = investment_target-total_contribution

## Percentage of Accomplished Investment Target Contributions Table
pctg_accomplished = (total_contribution/investment_target)*100

variables = [investment_target, 
            formatted_date,
            total_contribution,
            pending_contribution,
            pctg_accomplished, 
            months_due_goal]

invest_table = {
            'Columns' : ['Target', 'Deadline', 'Contribution', 'Pending', '% Done', 'Months left'],
            'Variables': variables}

df_invest_table = pd.DataFrame(invest_table)

# Investment Contributions Target Chart
names_col = ['Type','Value','dummy']
dat = [['Accomplished',total_contribution,0],['Unaccomplished',investment_target-total_contribution,0]]
colors = {
'Accomplished': '#66c2a5',
'Unaccomplished': '#e34a33'
}
plot_df = pd.DataFrame(data=dat,columns=names_col)
fig_target = px.bar(plot_df, x='dummy', y='Value', color='Type', color_discrete_map=colors,labels = {'Type':'', 'Value':''})
fig_target.update_layout(showlegend=False, plot_bgcolor='#aacfc1', paper_bgcolor='lightgrey', yaxis=dict(showgrid=False),
                        margin=dict(l=20, r=25, t=25, b=0, pad=20),
                        width=150,
                        height=400)
fig_target.update_traces(texttemplate='%{y:,.0f}', textposition='inside', marker=dict(line=dict(color='#000000', width=1)))
fig_target.update_yaxes(showticklabels=False, title_text='')
fig_target.update_xaxes(showticklabels=False, title_text='')

# Creating Bank Balance Table
month_initial_date = df.loc[df['Description'] == 'Balance', 'Month'].values[0]
df_apparent_balance = df[df['Description']=='Balance']
apparent_balance = df_apparent_balance['Value Calculation'].sum()

df_outflow_cred_balance = df[
(df['Month']==month_initial_date) &
(df['Year']==year_current_int) &
(df['Type']!='')]
sum_outflow_cred_balance = df_outflow_cred_balance['Value Calculation'].sum()

df_outflow_accrued = df[
(df['Month']>month_initial_date) &
(df['Year']==year_current_int) &
(df['Type']!='')]
sum_outflow_accrued = df_outflow_accrued['Value Calculation'].sum()

current_actual_balance = apparent_balance + sum_outflow_cred_balance

table_balance = {
    'Value': [
        apparent_balance,
        current_actual_balance,
    ],
    'Variable': [
        'Apparent Balance',
        f'Actual Balance',
    ]
}
df_balance = pd.DataFrame(table_balance)

# layout ==========================================================================================================================================================================
# Auxiliary Variables
width_col1 = '10px'
width_col2 = '10px'

app.layout = dbc.Container([
    dbc.Row([html.H5('')]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='Month-Year', 
                    clearable=False,
                    value=month_year_current,
                    style={"textAlign": "center",
                           "height": "auto",
                           'width':'445px'},
                    className='custom-dropdown',
                    options=date_options)
        ], width=3),
        dbc.Col([
            dcc.Dropdown(id='Macrocategories', 
                clearable=False,
                style={"textAlign": "center", 'width':'930px'},
                value='Personal',
                options=macrocategories)
        ], width=6),
        dbc.Col([
            dbc.Button('Show User´s Manual', id='show-alert-button', color="light", n_clicks=0, className='btn btn-primary', style={'width':'465px'})
        ],width=3),
    ], style={'margin':'1px'}),
    dbc.Row([html.H5('')]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_macro')
        ], width=3),
        dbc.Col([
            dcc.Graph(id='bar_cat')
        ], width=6),
        dbc.Col([
            AgGrid(id='table_exp_overview',
            columnSize="sizeToFit",
            defaultColDef={
                "cellStyle": {
                    "backgroundColor": "#cadbd4",
                    "color": "#000000",
                }},
            columnDefs=[
                {"headerName": "Cashflow Overview Selected Month", "field": "Variable", 'maxWidth': 400},
                {"headerName": "Amount", "field": "Value", 'maxWidth': 100, "type": "numericColumn", "valueFormatter": {"function": "x.toFixed(2)", "cellStyle": {"textAlign": "left"}}}
            ],
            style={'height': '278px', 'width': '100%', 'marginBottom': '14px'},
            dashGridOptions = {'headerHeight': 35,
                               "rowHeight": 30}
            ),
            AgGrid(id='table_bank_balance',
            columnSize="sizeToFit",
            defaultColDef={
                "cellStyle": {
                    "backgroundColor": "#cadbd4",
                    "color": "#000000",
                }},
            columnDefs=[
            {"headerName": "Current Balance Overview", "field": "Variable"}, 
            {"headerName": "Amount", "field": "Value", "type": "numericColumn", "valueFormatter": {"function": "x.toFixed(2)"}, 'maxWidth': 100}
            ],
            rowData=df_balance.to_dict('records'),
            style={'height': '98px', 'width': '100%'},
            dashGridOptions = {'headerHeight': 35,
                               "rowHeight": 30}
           ),
        ], width=3),
    ]),
    dbc.Row([html.H5('')]),
    dbc.Row([
        dbc.Col([
            AgGrid(id='investment_performance_table',
            columnDefs=[
            {"headerName": "Columns",
            "field": "Columns",
            "cellStyle": {
                'display': 'flex ',
                "justify-content": "center",
                "align-items": "center",
                "fontSize": "20px",
                "textAlign": "left"},
                "wrapText": True,
                'width':100},
            {"headerName": "Variables", 
            "field": "Variables",
            'maxWidth': 120,
            "type": "numericColumn",
            "valueFormatter": {
                "function": "x.toFixed(2)"},
            "cellStyle": {
                "fontSize": "20px",
                'display': 'flex ',
                "justify-content": "center",
                "align-items": "center",}},
            ],
            style={'height': '100%', 'width': '105%'},
            columnSize="sizeToFit",
            defaultColDef={
                "cellStyle": {
                    "backgroundColor": "#cadbd4",
                    "color": "#000000",
                }},
            dashGridOptions = {'headerHeight': 0,
                               "rowHeight": 66},
            rowData=df_invest_table.to_dict('records')),
        ], width=2),
        dbc.Col([
            dcc.Graph(id='bar_target', figure=fig_target)
        ], width=1),
        dbc.Col([
            dcc.Graph(id='bar_acum', figure=fig_acum),
            dcc.Graph(id='contributions', figure=fig_invest),
        ], width=5),
        dbc.Col([
            AgGrid(id='status',
                   columnSize="sizeToFit",
                   columnDefs=[ 
                   {"headerName": "Date",'maxWidth': 110, "field": "Date"},
                   {"headerName": "Category",'maxWidth': 180, "field": "Category", "filter": "agTextColumnFilter"},
                   {"headerName": "Description", "field": "Description", "filter": "agTextColumnFilter"},
                   {"headerName": "Status", "field": "Status", "filter": "agSetColumnFilter", "filterParams": {"values": ["Completed", "Pending", "In Progress"]}},
                   {"headerName": "Value",'maxWidth': 100, "field": "Value", "type": "numericColumn", "valueFormatter": {"function": "x.toFixed(2)"}, "cellStyle": {"textAlign": "right"}}
                ],
                defaultColDef={
                "cellStyle": {
                    "backgroundColor": "#cadbd4",
                    "color": "#000000",
                }},
           rowData=df_status.to_dict('records'),
           style={'height': '400px', 'width': '100%'}
        )]),
    ]),
    dbc.Row([html.H5('')]),
    dbc.Toast(id="alert-toast", 
    header="User's Manual", 
    is_open=False, 
    dismissable=True, 
    style={
    'position': 'fixed',
    'top': '50%',
    'left': '50%',
    'width': '700px',  
    'height': '700px',
    'margin-top': '-350px',
    'margin-left': '-350px' 
    }),
], fluid=True, style={'background': 'linear-gradient(to top, #39a78a, #c4f4e8)'})

# Creating the Callbacks
# Callbacks for User´s Manual
@app.callback(
    Output("alert-toast", "children"),  
    Input("show-alert-button", "n_clicks"),
)
def update_alert(n):
    if n and n % 2 == 1:
        return manual_text
    return ""

@app.callback(
    Output("alert-toast", "is_open"),
    Input("show-alert-button", "n_clicks"),
)
def open_toast(n):
    if n and n % 2 == 1:
        return True
    return False

# Callbacks for Dashboard Elements
@app.callback(
    Output('bar_macro', 'figure'),
    Output('bar_cat', 'figure'),
    Output('table_exp_overview', 'rowData'),

    Input('Month-Year', 'value'),
    Input('Macrocategories', 'value')
)

# Creating Dashboard Graphs
def output_elements(selected_period, selected_macrocategory):
    
    # Macrocategories Bar Chart < Changes with Review Period Selection
    df_macro = df[(df["Month-Year"] == selected_period) & (df['Macrocategory'] != 'Salary') & (df['Macrocategory'] != 'Investment') & (df['Description']!='Balance')]
    df_macro = df_macro.groupby('Macrocategory')['Value Calculation'].sum().reset_index()
    df_macro['Value Calculation'] = df_macro['Value Calculation'].abs()
    fig_bar_macro = px.bar(df_macro, x='Macrocategory', y='Value Calculation', labels={'Value Calculation': '', 'Macrocategory': ''})
    fig_bar_macro.update_layout(showlegend=False,
                                plot_bgcolor='#aacfc1',
                                paper_bgcolor='lightgrey',
                                xaxis=dict(tickfont=dict(size=15)),
                                yaxis=dict(showgrid=False, range=[0, max(df_macro['Value Calculation'])*1.1]), 
                                margin=dict(l=0, r=25, t=25, b=0, pad=20),
                                width=470,
                                height=390)
    fig_bar_macro.update_traces(texttemplate='%{y}', textposition='outside', marker_color='lightgrey', marker=dict(line=dict(color='#000000', width=1)))
    fig_bar_macro.update_yaxes(showticklabels=False)

    # Categories Bar Chart < Changes with Macrocategory selection
    df_cat = df[(df["Month-Year"] == selected_period) & (df['Macrocategory'] == selected_macrocategory)]
    df_cat = df_cat.groupby('Category')['Value Calculation'].sum().reset_index()
    df_cat['Value Calculation'] = df_cat['Value Calculation'].abs()
    fig_bar_cat = px.bar(df_cat, x='Category', y='Value Calculation', labels={'Value Calculation': '', 'Category': ''})
    fig_bar_cat.update_layout(showlegend=False, 
                              plot_bgcolor='#aacfc1', 
                              paper_bgcolor='lightgrey', 
                              xaxis=dict(tickfont=dict(size=14)), 
                              yaxis=dict(showgrid=False, range=[0, max(df_cat['Value Calculation'])*1.1]),
                              margin=dict(l=0, r=25, t=25, b=0, pad=20),
                              width=950,
                              height=390) 
    fig_bar_cat.update_traces(texttemplate='%{y}', textposition='outside', marker_color='lightgrey', marker=dict(line=dict(color='#000000', width=1)))
    fig_bar_cat.update_yaxes(showticklabels=False)

    
    # Creating Variables for Bank Balance and Expense Overview Calculations
    df_income = df[(df['Month-Year'] == selected_period) & (df['Year']==year_current_int) & (df['Macrocategory'] == 'Salary')]
    sum_income = df_income['Value Calculation'].sum()

    df_outflow_personal = df[
    (df['Month-Year'] == selected_period) &
    (df['Year']==year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] == '') &
    (df['Description'] != 'Balance') & 
    (df['Others']=='')]
    sum_outflow_personal = df_outflow_personal['Value Calculation'].sum()

    df_outflow_others = df[
    (df['Month-Year'] == selected_period) &
    (df['Year']==year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] == '') &
    (df['Description'] != 'Balance') & 
    (df['Others']=='Others')]
    sum_outflow_others = df_outflow_others['Value Calculation'].sum()

    df_outflow_cred_personal = df[
    (df['Month-Year'] == selected_period) &
    (df['Year']==year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] != '') &
    (df['Others']=='')]
    sum_outflow_cred_personal = df_outflow_cred_personal['Value Calculation'].sum()

    df_outflow_cred_others = df[
    (df['Month-Year'] == selected_period) &
    (df['Year']== year_current_int) &
    (df['Macrocategory'] != 'Salary') &
    (df['Macrocategory'] != 'Investment') &
    (df['Type'] != '') &
    (df['Others']=='Others')]
    sum_outflow_cred_others = df_outflow_cred_others['Value Calculation'].sum()

    df_investment = df[(df['Month-Year'] == selected_period) & (df['Year'] == year_current_int) & (df['Macrocategory'] == 'Investment')]
    sum_investment = df_investment['Value Calculation'].sum()

    invoice = sum_outflow_cred_personal + sum_outflow_cred_others

    # Creating Balance Table
    data = {
    'Value': [
        sum_income,
        sum_outflow_cred_personal,
        sum_outflow_cred_others,
        invoice,
        sum_outflow_accrued,
        sum_outflow_personal,
        sum_outflow_others,
        sum_investment,

    ],
    "Variable": [
        f"Income",
        f"Credit Outflow - Personal",
        f"Credit Outflow - Others",
        f"Credit Outflow - Total",
        f"Credit Outflow - Accrued",
        f"Debit Outflow - Personal",
        f"Debit Outflow - Others ",
        f"Investment Contribution",
    ]
}
    df_overview = pd.DataFrame(data)

    return fig_bar_macro, fig_bar_cat, df_overview.to_dict('records')

# Executing Server ================================================================================================================================================================
if __name__ == '__main__':
    app.run_server(debug=True, port='8051')
