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

filtered_changes_with_emp = changes_with_emp[changes_with_emp['department'].isin(selected_departments)]

## Метрики KPI
col1, col2, col3, col4 = st.columns(4, gap='small')
all_logs = len(filtered_logs)
failure_logs = len(filtered_logs[filtered_logs['status'] == 'failure'])


col1.metric('Всего логов', all_logs)
col2.metric('Неудачные входы', failure_logs)
col3.metric('Процент неудачных входов', round(failure_logs / all_logs * 100))
col4.metric('Количество уникальных сотрудников', filtered_logs['user_id'].nunique())

## Графики
col5, col6 = st.columns(2, gap='medium')
fig1 = px.bar(filtered_employees, x='department', color='department', title='Количество сотрудников в зависимости от отдела')
fig1.update_layout(xaxis={'categoryorder': 'total descending'})
col5.plotly_chart(fig1, width='stretch')

fig2 = px.pie(filtered_logs, names='status', title='Доля успешных/неудачных входов')
col6.plotly_chart(fig2, width='stretch')

groupby_failure = filtered_logs[filtered_logs['status'] == 'failure'].groupby(pd.Grouper(key='date', freq='W'))['status'].count()
fig3 = px.line(groupby_failure, title='Динамика неудачных входов по неделям')
st.plotly_chart(fig3, width='stretch')

col7, col8 = st.columns(2, gap='medium')
changes_by_department = filtered_changes_with_emp.groupby('department')['change_id'].count()
fig4 = px.bar(changes_by_department, color=changes_by_department.index, title='Количество изменений в разных отделах')
fig4.update_layout(xaxis={'categoryorder': 'total descending'})
col7.plotly_chart(fig4, width='stretch')

groupby_emp_failure = filtered_logs[filtered_logs['status'] == 'failure'].groupby(['user_id', 'name'])['status'].count()
top_groupby_emp_failure = groupby_emp_failure.sort_values(ascending=False).head().reset_index()
fig5 = px.bar(top_groupby_emp_failure, x='status', y='name', color='name',
              title='Топ человек по неудачным входам в систему', orientation='h')
fig5.update_layout(yaxis={'categoryorder': 'total ascending'})
col8.plotly_chart(fig5, width='stretch')