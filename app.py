
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import dash_table
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Account Service Credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\loren\Python - Lorenzo\\Projetos - Lorenzo\\Portfolio - Personal Budget Dash\\personal-budget-control-428313-044f02dbfccd.json", scope)

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
'Shared'
])

## Or, load data from .csv file:
# df = pd.read_csv('')

# Converting Google Sheets data to DataFrame format 
df = pd.DataFrame(data)
df = df.fillna('')
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
df['M-Y'] = df['Month'].astype(str) + '/' + df['Year'].astype(str)
df['Month-Year'] = pd.to_datetime(df['M-Y'])
df['Value'] = df['Value'].astype(float)
df_outflow_options = df[(df['Macrocategory']!='Salary') & (df['Macrocategory']!='Investment')]

# Auxiliary Variables
width_col1 = '10px'
width_col2 = '10px'

df_status = df[(df['Status']!='') & (df['Status']!='Pending Income - Done')]
df_status['Date'] = pd.to_datetime(df_status['Date']).dt.strftime('%d/%m/%Y')
df_status.dropna(inplace=True)

# Defining options for Period Dropwdown
date_current = datetime.now()
month_current = date_current.month
year_current = date_current.strftime('%Y')
year_current_int = int(year_current)
month_year_current = f"{month_current}/{year_current}"

# DEFINING INVESTMENT GOALS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
investment_target = 40000 # INPUT INVESTMENT CONTRIBUTION GOAL
date_goal = datetime(2025, 8, 1) # INPUT INVESTMENT CONTRIBUTION GOAL DEADLINE / FORMAT YYYY/MM/DD
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

formatted_date = date_goal.strftime('%Y/%m')
date_today = datetime.today()
months_due_goal = relativedelta(date_goal, date_today)
months_due_goal = months_due_goal.years * 12 + months_due_goal.months + 1

# Defining options for Dropdowns
macrocategories = [{'label': x, 'value': x} for x in df_outflow_options["Macrocategory"].unique()]
date_options = [{'label': x, 'value': x} for x in df["M-Y"].unique()]



# layout ==========================================================================================================================================================================
app.layout = dbc.Container([
    dbc.Row([html.H5('')]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='Month-Year', 
                    clearable=False,
                    value=month_year_current,
                    style={"textAlign": "center",
                           "height": "auto"},
                    className='custom-dropdown',
                    options=date_options)
        ], width=2),
        dbc.Col([
            dcc.Dropdown(id='Macrocategories', 
                clearable=False,
                style={"textAlign": "center"},
                value='Personal',
                options=macrocategories)
        ], width=2),
        dbc.Col([
            html.Button('Show User´s Manual', id='show-alert-button', n_clicks=0, className='btn btn-primary')
        ],width=2),
    ], style={'margin':'1px'}),
    dbc.Row([html.H5('')]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_macro')
        ], width=2, align='center'),
        dbc.Col([
            dcc.Graph(id='bar_cat')
        ], width=5),
        dbc.Col([
            dash_table.DataTable(id='table_exp_overview',
                                columns = [{"name": f"Reviewing {month_year_current}", "id": "Variable"}, {"name": '', "id": "Value", "type": "numeric", "format": {'specifier': '.2f'}}],
                                style_cell={
                                'textAlign': 'left',
                                'padding': '5px'},
                                style_cell_conditional=[
                                {'if': {'column_id': 'Value'}, 'textAlign': 'center', 'width':'20px'},
                                {'if': {'column_id': 'Variable'}, 'width':'20px'}],
                                style_table={'marginBottom':'30px','width': '83%'}
            ),
            dash_table.DataTable(id='table_bank_balance',
                                columns = [{"name": "Variable", "id": "Variable"}, {"name": "Value", "id": "Value", "type": "numeric", }], # "format": {'specifier': '.2f'}
                                style_cell={'Variable'
                                'textAlign': 'left',
                                'padding': '5px'},
                                style_cell_conditional=[
                                {'if': {'column_id': 'Value'}, 'textAlign': 'center', 'width':'20px' },
                                {'if': {'column_id': 'Variable'}, 'textAlign': 'left', 'width':'20px'}],
                               style_table={'marginTop':'10px','width': '83%'}
            )
        ], width=3),
    ]),
    dbc.Row([html.H5('')]),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(id='contribution_target',
                                 columns = [{"name": '$ Target', "id": "Target", "type": "numeric", "format": {'specifier': '.2f'}}],
                                 style_cell={
                                'textAlign': 'center',
                                'padding': '5px'},
                                style_table={'marginTop':'0px', 'marginBottom': '4px','width': '110%'}),
            dash_table.DataTable(id='target_date',
                                 columns = [{"name": 'Target Deadline', "id": "Target Deadline", "type": "datetime", "format": {'specifier': '.2f'}}],
                                 style_cell={
                                'textAlign': 'center',
                                'padding': '5px'},
                                style_table={'marginTop':'0px', 'marginBottom': '4px','width': '110%'}),
            dash_table.DataTable(id='total_contribution',
                                 columns = [{"name": '$ Accomplished', "id": "Total", "type": "numeric", "format": {'specifier': '.2f'}}],
                                 style_cell={
                                'textAlign': 'center',
                                'padding': '5px'},
                                style_table={'marginBottom': '4px','width': '110%'}),
            dash_table.DataTable(id='pending_contribution',
                                 columns = [{"name": '$ Pending', "id": "Pending", "type": "numeric", "format": {'specifier': '.2f'}}],
                                 style_cell={
                                'textAlign': 'center',
                                'padding': '5px'},
                                style_table={'marginBottom': '5px','width': '110%'}),
            dash_table.DataTable(id='pctg_target',
                                 columns = [{"name": '% Accomplished', "id": "Percentage", "type": "numeric", "format": {'specifier': '.2%'}}],
                                 style_cell={
                                'textAlign': 'center',
                                'padding': '5px'},
                                style_table={
                                'marginBottom': '4px',
                                'width': '110%'}),
            dash_table.DataTable(id='months_due',
                                 columns = [{"name": 'Months Deadline', "id": "Months Deadline", "type": "numeric"}], #, "format": {'specifier': '.2f'}}
                                 style_cell={
                                'textAlign': 'center',
                                'padding': '5px'},
                                style_table={
                                'width': '110%'})
        ], width=1),
        dbc.Col([
            dcc.Graph(id='bar_target')
        ], width=1),
        dbc.Col([
            dcc.Graph(id='bar_acum'),
            dcc.Graph(id='contributions'),
        ], width=5),
        dbc.Col([
            dash_table.DataTable(id='table_status_container', data=df_status.to_dict('records'),
            columns=[
                {"name": "Date", "id": "Date"},
                {"name": "Category", "id": "Category"},
                {"name": "Description", "id": "Description"},
                {"name": "Status", "id": "Status"},
                {"name": "Value", "id": "Value"},
            ],
            style_table={'overflowY': 'auto', 'overflowX': 'auto', 'borderLeft': '1px solid lightgrey', 'marginLeft':'0px', 'width': '100%'},
            style_cell={'textAlign': 'left', 'padding': '4px'}),
        ])
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
], fluid=True, style={'backgroundColor': 'black'})

# Creating the Callbacks
@app.callback(
    Output("alert-toast", "children"),  
    Input("show-alert-button", "n_clicks"),
)
def update_alert(n):
    if n and n % 2 == 1:
        return "User´s manual goes here" # YOU CAN WRITE WHATEVER YOU WANT IN USER´S MANUAL OVER HERE! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    return ""

@app.callback(
    Output("alert-toast", "is_open"),
    Input("show-alert-button", "n_clicks"),
)
def open_toast(n):
    if n and n % 2 == 1:
        return True
    return False

@app.callback(
    Output('bar_macro', 'figure'),
    Output('bar_cat', 'figure'),
    Output('bar_target', 'figure'),
    Output('contributions', 'figure'),
    Output('total_contribution', 'data'),
    Output('contribution_target', 'data'),
    Output('target_date','data'),
    Output('pending_contribution', 'data'),
    Output('pctg_target', 'data'),
    Output('months_due', 'data'),
    Output('table_exp_overview', 'data'),
    Output('table_bank_balance', 'data'),
    Output('bar_acum', 'figure'),
    
    Input('Month-Year', 'value'),
    Input('Macrocategories', 'value')
)


# Creating Dashboard Graphs
def graphs(selected_period, selected_macrocategory):
    
    # Macrocategories Bar Chart < Changes with Review Period Selection
    df_macro = df[(df["Month-Year"] == selected_period) & (df['Year']==year_current_int) & (df['Macrocategory'] != 'Salary') & (df['Macrocategory'] != 'Investment') & (df['Description']!='Balance')]
    df_macro = df_macro.groupby('Macrocategory')['Value Calculation'].sum().reset_index()
    df_macro['Value Calculation'] = df_macro['Value Calculation'].abs()
    fig_bar_macro = px.bar(df_macro, x='Macrocategory', y='Value Calculation', labels={'Value Calculation': '', 'Macrocategory': ''})
    fig_bar_macro.update_layout(showlegend=False,
                                plot_bgcolor='#B0C4DE', 
                                paper_bgcolor='lightgrey', 
                                xaxis=dict(tickfont=dict(size=15)),
                                yaxis=dict(showgrid=False),
                                margin=dict(l=0, r=25, t=25, b=0, pad=20),
                                width=310,
                                height=420)
    fig_bar_macro.update_traces(texttemplate='%{y}', textposition='outside', marker_color='lightgrey', marker=dict(line=dict(color='#000000', width=1)))
    fig_bar_macro.update_yaxes(showticklabels=False)

    # Categories Bar Chart < Changes with Macrocategory selection
    df_cat = df[(df["Month-Year"] == selected_period) & (df['Year']==year_current_int) & (df['Macrocategory'] == selected_macrocategory)]
    df_cat = df_cat.groupby('Category')['Value Calculation'].sum().reset_index()
    df_cat['Value Calculation'] = df_cat['Value Calculation'].abs()
    fig_bar_cat = px.bar(df_cat, x='Category', y='Value Calculation', labels={'Value Calculation': '', 'Category': ''})
    fig_bar_cat.update_layout(showlegend=False, 
                              plot_bgcolor='#B0C4DE', 
                              paper_bgcolor='lightgrey', 
                              xaxis=dict(tickfont=dict(size=14)), 
                              yaxis=dict(showgrid=False),
                              margin=dict(l=0, r=25, t=25, b=0, pad=20),
                              width=790,
                              height=420) 
    fig_bar_cat.update_traces(texttemplate='%{y}', textposition='outside', marker_color='lightgrey', marker=dict(line=dict(color='#000000', width=1)))
    fig_bar_cat.update_yaxes(showticklabels=False)

    # Investment Contributions Bar Chart
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
    fig_invest.update_layout(showlegend=False, plot_bgcolor='#B0C4DE', paper_bgcolor='lightgrey', barmode='stack', yaxis=dict(showgrid=False, range=[0, max(df['Value Calculation'])*0.7], title=''),
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
    fig_acum.update_layout(showlegend=True, plot_bgcolor='#B0C4DE', paper_bgcolor='lightgrey', yaxis=dict(showgrid=False, range=[0, max(df['Value'])*3.8], title='Value'),
                           margin=dict(l=0, r=25, t=25, b=0, pad=20),
                            width=790,
                            height=200)
    fig_acum.update_traces(texttemplate='%{y:,.0f}', textposition='outside', marker_color='lightgrey', marker=dict(line=dict(color='#000000', width=1)))
    fig_acum.update_yaxes(showticklabels=False, title_text='')
    fig_acum.update_xaxes(showticklabels=False, title_text='', tickformat="%-m/%y", dtick='M1')

    # Total Investment Contribution Table 
    total_contribution = df_invest['Value'].sum()
    table_total_contribution = {
    'Total': [total_contribution]}

    df_total_invest = pd.DataFrame(table_total_contribution)

    # Investment Contributions Target Chart
    names_col = ['Type','Value','dummy']
    dat = [['Accomplished',total_contribution,0],['Unaccomplished',investment_target-total_contribution,0]]
    colors = {
    'Accomplished': '#66c2a5',
    'Unaccomplished': '#e34a33'
    }
    plot_df = pd.DataFrame(data=dat,columns=names_col)
    fig_target = px.bar(plot_df, x='dummy', y='Value', color='Type', color_discrete_map=colors,labels = {'Type':'', 'Value':''})
    fig_target.update_layout(showlegend=False, plot_bgcolor='#B0C4DE', paper_bgcolor='lightgrey', yaxis=dict(showgrid=False),
                            margin=dict(l=20, r=25, t=25, b=0, pad=20),
                            width=150,
                            height=400)
    fig_target.update_traces(texttemplate='%{y:,.0f}', textposition='inside', marker=dict(line=dict(color='#000000', width=1)))
    fig_target.update_yaxes(showticklabels=False, title_text='')
    fig_target.update_xaxes(showticklabels=False, title_text='')

    # Investment Contributions Target Table
    table_target = {
    'Target': [investment_target]}

    df_contribution_target = pd.DataFrame(table_target)

    # Target Goal Date
    date_goal
    table_date_goal = {
        'Target Deadline': [formatted_date]}
    
    df_date_goal = pd.DataFrame(table_date_goal)

    # Pending Investment Contributions Table
    table_pending_contribution = {'Pending': [investment_target-total_contribution]}
    df_pending_contribution = pd.DataFrame(table_pending_contribution)

    # Percentage of Accomplished Investment Target Contributions Table
    pctg_accomplished = total_contribution/investment_target
    table_pctg = {'Percentage': [pctg_accomplished]}
    df_pctg_accomplished = pd.DataFrame(table_pctg)

    # Months To Goal Table
    table_months_to_goal = {
    'Months Deadline': [months_due_goal]}
    df_months_due_goal = pd.DataFrame(table_months_to_goal)

    # Creating Variables for Bank Balance and Expense Overview Calculations
    df_income = df[(df['Month-Year'] == month_year_current) & (df['Year']==year_current_int) & (df['Macrocategory'] == 'Salary')]
    sum_income = df_income['Value Calculation'].sum()

    df_outflow_personal = df[
    (df['Month-Year'] == month_year_current) &
    (df['Year']==year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] == '') &
    (df['Description'] != 'Balance') & 
    (df['Shared']=='')]
    sum_outflow_personal = df_outflow_personal['Value Calculation'].sum()

    df_outflow_shared = df[
    (df['Month-Year'] == month_year_current) &
    (df['Year']==year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] == '') &
    (df['Description'] != 'Balance') & 
    (df['Shared']=='Shared')]
    sum_outflow_shared = df_outflow_shared['Value Calculation'].sum()

    df_outflow_cred_personal = df[
    (df['Month-Year'] == month_year_current) &
    (df['Year']==year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] != '') &
    (df['Shared']=='')]
    sum_outflow_cred_personal = df_outflow_cred_personal['Value Calculation'].sum()

    df_outflow_cred_shared = df[
    (df['Month-Year'] == month_year_current) &
    (df['Year']== year_current_int) &
    (df['Macrocategory'] != 'Salary') & 
    (df['Macrocategory'] != 'Investment') & 
    (df['Type'] != '') &
    (df['Shared']=='Shared')]
    sum_outflow_cred_shared = df_outflow_cred_shared['Value Calculation'].sum()

    df_investment = df[(df['Month-Year'] == month_year_current) & (df['Year'] == year_current_int) & (df['Macrocategory'] == 'Investment')]
    sum_investment = df_investment['Value Calculation'].sum()

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

    actual_balance = apparent_balance + sum_outflow_cred_balance + sum_outflow_accrued

    current_actual_balance = apparent_balance + sum_outflow_cred_balance

    invoice = sum_outflow_cred_personal + sum_outflow_cred_shared

    # Creating Balance Table
    data = {
    'Value': [
        sum_income,
        sum_outflow_cred_personal,
        sum_outflow_cred_shared,
        invoice,
        sum_outflow_accrued,
        sum_outflow_personal,
        sum_outflow_shared,
        sum_investment,

    ],
    "Variable": [
        f"Income - Current",
        f"Credit Outflow - Personal",
        f"Credit Outflow - Others",
        f"Credit Outflow - Total Current",
        f"Credit Outflow - Accrued",
        f"Debit Outflow - Personal",
        f"Debit Outflow - Others ",
        f"Investment Contribution",
    ]
}
    df_overview = pd.DataFrame(data)
    
    # Creating Bank Balance Table
    table_balance = {
        'Value': [
            apparent_balance,
            current_actual_balance,
            # actual_balance # = Apparent Balance - Credit Outflow - Total Current
        ],
        'Variable': [
            'Apparent Balance',
            f'Actual Balance in {month_year_current}',
            # 'Actual Balance'
        ]
    }

    df_balance = pd.DataFrame(table_balance)

    return fig_bar_macro, fig_bar_cat, fig_target, fig_invest, df_total_invest.to_dict('records'), df_contribution_target.to_dict('records'), df_date_goal.to_dict('records'), df_pending_contribution.to_dict('records'), df_pctg_accomplished.to_dict('records'), df_months_due_goal.to_dict('records'), df_overview.to_dict('records'), df_balance.to_dict('records'), fig_acum

# Executing Server ================================================================================================================================================================
if __name__ == '__main__':
    app.run_server(debug=True, port='8051')