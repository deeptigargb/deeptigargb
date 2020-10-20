import time

last_modified_time=1601724888956
a = ((time.time() * 1000) - last_modified_time)
print (a)
print(int(a))
print((a/(1000*60*60*24)))



df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

def generate_table(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='Latest load of all domain tables'),
    generate_table(df)
])

if __name__ == '__main__':
    app.run_server(debug=True)































# from airflow.operators.python_operator import PythonOperator
import pandas as pd
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional
)
from google.cloud import bigquery
import datetime
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
from pytz import timezone
import dash_table


# from requests_html import HTML


def get_bigquery_client(
        bq_conn_id: str,
        bq_location: str,
        bq_project: Optional[str] = None,
) -> bigquery.Client:
    print("inside")

    return bigquery.Client(
        project=bq_project
    )


def abc():
    project = 'data-dev-239410'
    client = get_bigquery_client(
        bq_project=project,
        bq_conn_id='bigquery_primary',
        bq_location='europe-west2',
    )
    print(client.list_datasets())
    query = ''
    for a in list(client.list_datasets()):
        if 'insights_domain' in a.dataset_id:
            query1 = f'SELECT * FROM `{project}.{a.dataset_id}.__TABLES__` union all '
            query = query + query1
            # client.g
    return query


query = abc()
main_sql = 'with all_tables as ( ' + query.rstrip("union all") + ') select project_id, dataset_id, table_id,' \
                                                                 'last_modified_time, timestamp_millis(last_modified_time ) as ' \
                                                                 'last_modified from all_tables order by last_modified'
print(main_sql)
client = get_bigquery_client(
    bq_project='data-dev-239410',
    bq_conn_id='bigquery_primary',
    bq_location='europe-west2',
)

results = client.query(main_sql).result()
df = client.query(main_sql).to_dataframe()

for row in results:
    pass
print(row)
print(row[0])
# print(row[5])
print(len(row))

now = datetime.datetime.now(tz=datetime.timezone.utc)


def convert_from_ms(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    seconds = seconds + milliseconds / 1000
    a = f'{days} days, {hours} hours, {minutes} minutes, {seconds} seconds'
    return a


# print ((now).total_seconds())
dt = '2020-10-03 12:05:14.582000+00:00'
print("here is the time ", time.time() * 1000)
a = ((time.time() * 1000) - df['last_modified_time'])
# b = convert_from_ms(a)
df['Time Difference'] = a.astype('int64')
days = (a/(1000*60*60*24)).astype('int64')
hours = ( (a/(1000*60*60))%24 ).astype('int64')
# print (days, "  ", hours)
# b = f'{days} days, {hours} hours'
# print(b)
df['Time Difference in days'] = days.astype(str) + ' days, ' + hours.astype(str) + 'hours'
# df['Time Difference in hours'] = hours
print(df)

# def color_negative_red(value):
#     """
#   Colors elements in a dateframe
#   green if positive and red if
#   negative. Does not color NaN
#   values.
#   """
#
#     if value < 0:
#         color = 'red'
#     elif value > 0:
#         color = 'green'
#     else:
#         color = 'black'
#
#     return 'color: %s' % color


# df.style.applymap(color_negative_red, subset=['Time Difference']).render()

# import seaborn as sns
#
# cm = sns.light_palette("green", as_cmap=True)
#
# html = (df.style.background_gradient(cmap=cm).render())

with open('latest_domain_tables_load.html', 'w') as f:
    f.write(df.to_html())
    # HEADER = '''
    # <html>
    #     <head>
    #         <style>
    #             .df tbody tr:last-child { background-color: #FF0000; }
    #         </style>
    #     </head>
    #     <body>
    # '''
    # FOOTER = '''
    #     </body>
    # </html>
    # '''
    # f.write(HEADER)

    # f.write(FOOTER)
