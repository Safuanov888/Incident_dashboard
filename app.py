import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title='Дашборд по инцидентам',
    page_icon='🚀',
    layout='wide',
    initial_sidebar_state='auto'
)


## Загрузка данных
@st.cache_data
def read_data():
    employees = pd.read_csv('employees.csv')
    logs = pd.read_csv('logs.csv', parse_dates=['date'])
    changes = pd.read_csv('changes.csv', parse_dates=['date'])

    return employees, logs, changes


employees, logs, changes = read_data()
changes_with_emp = changes.merge(employees, how='left', left_on='user_id', right_on='id').drop('id', axis=1)
logs_with_emp = logs.merge(employees, how='left', left_on='user_id', right_on='id').drop('id', axis=1)
