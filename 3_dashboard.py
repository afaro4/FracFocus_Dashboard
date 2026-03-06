import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# python3 -m streamlit run "/Users/alishbahfarooq/Desktop/Chirality Research/fracfocus_case_study/3_dashboard.py"

# setting page configuration
st.set_page_config(page_title="FracFocus Insights", layout="wide")

# importing df's for visualization

disclosures_by_state_df = pd.read_csv(Path(__file__).parent / "disclosures_by_state.csv")
common_chemicals_df = pd.read_csv(Path(__file__).parent / 'common_chemicals_df.csv')
water_consump_by_operator_df = pd.read_csv(Path(__file__).parent / 'water_consump_by_operator_df.csv')
top_operators_df = pd.read_csv(Path(__file__).parent / 'top_operators_df.csv')
water_consump_over_time_df = pd.read_csv(Path(__file__).parent / 'water_consump_over_time_df.csv')
operators_by_disclosures_df = pd.read_csv(Path(__file__).parent / 'operators_by_disclosures_df.csv')
jobs_per_year_df = pd.read_csv(Path(__file__).parent / 'jobs_per_year_df.csv')

st.title("FracFocus Insights")

# KPI Metric Cards
h_col1, h_col2 = st.columns(2)

with h_col1:
    Operator = st.selectbox(
        'Select Operator',
        operators_by_disclosures_df['OperatorName'].unique()
    )
    filtered_operator_df = operators_by_disclosures_df[operators_by_disclosures_df['OperatorName'] == Operator]
    st.metric("Total Number of Disclosures for " + str(Operator), 
            filtered_operator_df['num_disclosures'],
            border = True
    )

with h_col2:
    Year_job = st.selectbox(
        'Select Year',
        jobs_per_year_df['year'].unique(),
        key="job_select"
    )

    filtered_year_df = jobs_per_year_df[jobs_per_year_df['year'] == Year_job]
    st.metric("Total Number of Disclosures In " + str(Year_job), 
              filtered_year_df['num_jobs'],
              border = True
    )
    
# avg water consumption over time per operator for top 10 operators (with most avg consumption)
#fig_5 = px.line(
#    water_consump_over_time_df,
#    x='month',
#    y='avg_water_consum',
#    color='OperatorName',
#    labels={'OperatorName': 'Operator Name',
#            'month': 'Month',
#            'avg_water_consum': "Average Water Consumption"},
#    title='Average Water Consumption Over Time By Top 10 Operators'
#)
Year_water = st.selectbox(
        'Select Year',
        sorted(water_consump_over_time_df['year'].unique()),
        key='water_select'
    )
filtered_water_consum_year_df = water_consump_over_time_df[water_consump_over_time_df['year'] == Year_water]

fig_5 = px.scatter(
    water_consump_over_time_df,
    x='avg_water_consum',
    y='num_disclosures',
    color='OperatorName',
    labels={'OperatorName': 'Operator Name',
            'num_disclosures': 'Number of Disclosures',
            'avg_water_consum': "Average Water Consumption"},
    title='Total Number of Disclosures VS Average Water Consumption in ' + str(Year_water)
)
fig_5.update_layout(title_x=0.2)
st.plotly_chart(fig_5)

# Dividing dashboard into columns for visualization
col1, col2 = st.columns(2)

# adding a column with State abbreviations for choropleth map
state_to_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    'District of Columbia': 'DC'
}
disclosures_by_state_df['StateName'] = disclosures_by_state_df['StateName'].str.strip().str.title()
disclosures_by_state_df['StateAbbrev'] = disclosures_by_state_df['StateName'].replace(state_to_abbrev)

with col1:
# Total Hydraulic Fracturing Jobs By State
    #fig_1 = px.scatter(
    #    disclosures_by_state_df,
    #    x='StateName',
    #    y='num_disclosures',
    #    size='num_disclosures',
    #    labels={'StateName': 'State Name',
    #            'num_disclosures': 'Number of Disclosures'},
    #    title='Total Hydraulic Fracturing Jobs By State'
    #)
    fig_1 = px.choropleth(
        disclosures_by_state_df,
        locations = 'StateAbbrev',
        color = 'num_disclosures',
        labels={'StateName': 'State Name',
                'num_disclosures': 'Number of Disclosures'},
        locationmode='USA-states',
        scope='usa',
        title='Total Hydraulic Fracturing Jobs By State'
    )
    fig_1.update_layout(title_x=0.3)
    st.plotly_chart(fig_1)
    #st.map(disclosures_by_state_df, latitude='Latitude', longitude='Longitude', size = 20, zoom=3)

    # Top 30 Most Common Chemicals Used in Fracturing Jobs
    fig_2 = px.bar(
        common_chemicals_df,
        x='IngredientName',
        y='num_disclosures',
        labels= {'IngredientName':'Chemicals', 'num_disclosures': 'Number of Disclosures'},
        title='Top 30 Most Common Chemicals Used in Fracturing Jobs'
    )
    fig_2.update_layout(title_x=0.25)
    st.plotly_chart(fig_2)

with col2:
    # Top 30 Operators With The Most Wells
    #fig_4 = px.scatter(
    #    top_operators_df,
    #    x='OperatorName',
    #    y='num_disclosures',
    #    labels={'OperatorName': 'Operator Name',
    #            'num_disclosures': 'Number of Disclosures'},
    #    title='Top 30 Operators by Total Disclosures'
    #)
    #fig_4.update_layout(title_x=0.4)
    #st.plotly_chart(fig_4)

    # Operators With The Most Water Consumption In X Year
    Year_tree_map = st.selectbox(
        'Select Year',
        sorted(water_consump_by_operator_df['year'].unique()),
        key='water_tree_select'
    )
    filtered_water_year_df = water_consump_by_operator_df[water_consump_by_operator_df['year'] == Year_tree_map]

    fig_3 = px.treemap(
        filtered_water_year_df,
        names='OperatorName',
        values='total_water_consump',
        path=['OperatorName'],
        title='Operators with the Most Water Consumption in ' + str(Year_tree_map)
    )
    fig_3.update_layout(height=1000,title_x=0.25)
    st.plotly_chart(fig_3)