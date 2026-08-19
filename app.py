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

## Настраиваем sidebar
st.sidebar.title('Сайдбар')

selected_departments = st.sidebar.multiselect('Выберите отдел', employees['department'].unique(), default=employees['department'].unique())
selected_access = st.sidebar.multiselect('Уровень доступа', employees['access_logs'].unique(), default=employees['access_logs'].unique())
start_date = pd.to_datetime(st.sidebar.date_input('Дата начала', value=logs['date'].min()))
end_date = pd.to_datetime(st.sidebar.date_input('Дата конца', value=logs['date'].max()))

## Фильтруем данные
filtered_logs = logs_with_emp[
    (logs_with_emp['department'].isin(selected_departments)) &
    (logs_with_emp['access_logs'].isin(selected_access)) &
    (logs_with_emp['date'] >= start_date) &
    (logs_with_emp['date'] <= end_date)
]

filtered_employees = employees[employees['department'].isin(selected_departments)]

filtered_access = changes_with_emp[changes_with_emp['new_level'].isin(selected_departments)]

