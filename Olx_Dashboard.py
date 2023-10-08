import pandas as pd
import streamlit as st
import plotly.express as px



dfff = pd.read_excel("BI Assignment Data.xlsb", engine='pyxlsb')
dff = pd.read_excel("BI_Short.xlsb", engine='pyxlsb', index_col=False)
df = pd.read_excel("BI_Short.xlsb", engine='pyxlsb')


#Totals Data Frame
dfff= pd.read_excel("Totals_Pivot.xls", index_col=False)
dfff_table= pd.DataFrame(dfff).head(7)



#Scatter Plot
#Taking 0's out
zero_revenue_df = df[df["Total Revenue"] == 0]
zero_revenue_df.to_csv('Zero_Revenue_Users.csv', index=False)
df = df[df["Total Revenue"] != 0]

#Segmentation
quartiles = df["Total Revenue"].quantile([0.25, 0.50, 0.75])
segment_names = ["Low Revenue", "Middle Revenue", "Top Revenue"]
def assign_segment(total_revenue):
    if total_revenue <= quartiles[0.25]:
        return segment_names[0]
    elif total_revenue <= quartiles[0.50]:
        return segment_names[1]
    else:
        return segment_names[2]
df["Segments"] = df["Total Revenue"].apply(assign_segment)
df = df.sort_values('Total Revenue', ascending=False)
df.to_csv('BI Short Segments.csv', index=False)

df= pd.read_csv("/Users/tiberiuradan/PycharmProjects/DataAnalysis/BI Short Segments.csv")
df = df.sort_values('Total Revenue', ascending=True)

x=(df['User ID'])
y=df['Total Revenue']
z=df['Segments']

#From categorical to numerical
df['Segments'] = pd.Categorical(df['Segments'])
df['Segments_Label'] = df['Segments'].cat.codes

#Highlighting the 10th Highest and Lowest
top_10_highest = df['Total Revenue'].tail(10)
top_10_lowest = df['Total Revenue'].head(10)

#Setting the marker size for each scatter
df['Marker Size'] = 8
df.loc[top_10_highest.index, 'Marker Size'] = 20
df.loc[top_10_lowest.index, 'Marker Size'] = 20

#Setting a color scale
color_scale = px.colors.sequential.Jet

#The color scale is being added by 'color', using the numerical values obtained eariler
fig_scatter= px.scatter(df, x='User ID', y='Total Revenue',
                        color='Segments_Label',
                        color_continuous_scale=px.colors.sequential.Blugrn_r,
                        size= 'Marker Size',
                        range_color=[-2, df['Segments_Label'].rename("Type of Value").max()])
fig_scatter.update_layout(coloraxis_colorbar_title="Type of Value")

#Stopping Plotly from scientifical encoding and setting what to display when hover
fig_scatter.update_traces(hovertemplate='User ID: %{x}<br>Total Revenue: %{y:$,.2f}')
fig_scatter.update_layout(xaxis=dict(tickformat='d'), yaxis=dict(tickformat='d'))




#Creating a piechart
dff= pd.DataFrame(dff)
No_Revenue_Users = len(dff[dff['Total Revenue'] == 0])
Positive_Revenue_Users = len(dff[dff['Total Revenue'] > 0])
Negative_Revenue_Users = len(dff[dff['Total Revenue'] < 0])

data= {"Type Of User": ['No Revenue User', 'Positive Revenue User', 'Negative Revenue User'],
       "Value": [No_Revenue_Users, Positive_Revenue_Users, Negative_Revenue_Users]}
data=pd.DataFrame(data)
fig_pie = px.pie(data, values='Value',
                 names='Type Of User',
                 color_discrete_sequence=px.colors.sequential.RdBu)
fig_pie.update_layout(uniformtext_minsize=16, uniformtext_mode='hide')




#Horizontal Barchart: Users by Promo Revenue
dff= dff.sort_values('Promo Revenues', ascending=False)
dff= pd.DataFrame(dff).head(11)
dff= dff[['User ID', 'Promo Revenues']]
fig_user_line= px.bar(dff, x="Promo Revenues", y="User ID", orientation='h', color_discrete_sequence=px.colors.sequential.Blugrn_r)
fig_user_line.update_yaxes(type='category')


#Linechart: Total Revenue by Month
df = pd.read_excel("/Users/tiberiuradan/PycharmProjects/DataAnalysis/Total Revenue by Month.xlsx", index_col=False)
x= df['Month']
y= df['Total Revenue'].astype(float)
fig_line = px.line(df, x='Month', y='Total Revenue', markers= True)
fig_line.update_xaxes(title_text='Month', tickangle=0)

#Streamlit integration
st.set_page_config(layout="wide")
st.title("OLX Dashboard")
with st.sidebar:
    st.title("User Guide")
    st.write("""
    Welcome to the OLX Dashboard! 
    
    This tool offers valuable insights into OLX user data and revenue statistics.
    It provides a moderate level of interaction, therefore you can set the order of your data frame, hover over a certain datapoint and get the core information, or calculate the revenue by using the slider. 
    
    Monthly Revenue:
    View monthly revenue trends from July to December.
    Select a month to see cumulative revenue, or preview the fluctuation in a line chart.
    
    User Data:
    Explore user segments and total revenue.
    The scatterplot shows User ID vs. Total Revenue, highlighting top and bottom users.
    The bar chart displays the top users by promo revenue.
    
    Type of Users:
    Metrics for different user types:
    Positive Revenue Users,
    Negative Revenue Users,
    No Revenue Users.
    
    Ads, Listings, and Renewals by Month:
    Get totals for ads, listings, and renewals by month.
    Metrics identify the high and low months in each category.
    """)


with st.expander("Monthly Revenue", expanded=True):
    st.write("<h1 style='font-size: 17px;'>Total Revenue by Month</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1], gap="medium")
    col1.plotly_chart(fig_line)
    #Slider
    months_range = ['July', 'August', 'September', 'October', 'November', 'December']
    filtered_df = df[df['Month'].isin(months_range)]
    selected_month = col2.select_slider("Select a month:", options=filtered_df['Month'].tolist())
    selected_month_index = filtered_df[filtered_df['Month'] == selected_month].index[0]
    sum_revenue = filtered_df['Total Revenue'].iloc[:selected_month_index+1].sum()
    start_month = "July"
    end_month = selected_month
    date_range = f"{start_month} - {end_month}"
    #Metrc
    col2.metric(label="Total Revenue", value=date_range, delta=f"${sum_revenue:,}")
    col2.write("<div style='margin-left: 100px;'></div>", unsafe_allow_html=True)
    col2.dataframe(filtered_df, hide_index=True, width=245, height=245)



with st.expander("User Data", expanded=True):
    col3, col4, col0= st.columns([3,2,1], gap="medium")
    #Scatterplot
    col3.write("<h1 style='font-size: 17px;'>Users by Total Revenue</h1>", unsafe_allow_html=True)
    col3.plotly_chart(fig_scatter, use_container_width=True)
    #Line Chart
    col4.write("<h1 style='font-size: 17px;'>Top Users by Promo Revenue</h1>", unsafe_allow_html=True)
    col4.plotly_chart(fig_user_line, use_container_width=True)
    #Metrics
    col0.write("<h1 style='font-size: 17px;'>Type of Users</h1>", unsafe_allow_html=True)
    #Taking the arrow down
    col0.write( """<style>[data-testid="stMetricDelta"] svg {display: none;}</style>""",unsafe_allow_html=True,)
    col0.metric(label="Positive Revenue Users", value="18.6%", delta="27,899 users")
    col0.metric(label="Negative Revenue Users", value="0.07%", delta="106 users", delta_color="inverse")
    col0.metric(label="No Revenue Users", value="81.3%", delta="121,605 users", delta_color="off")

with st.expander("Ads, Listings and Renewals by Month", expanded=True):
    col6, col7, col8 = st.columns([3,1,1])
    col6.write("<h1 style='font-size: 17px;'>Totals by Month</h1>",unsafe_allow_html=True)
    col6.write("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
    col6.dataframe(dfff_table, hide_index=True, width=700, height=280)

    #Metrics

    #Good Months
    col7.write("<h1 style='font-size: 17px;'>High Month in:</h1>", unsafe_allow_html=True)
    col7.metric(label="Ads Bought", value="233,182", delta="October")
    col7.metric(label="New Listings", value="222,054", delta="October")
    col7.metric(label="Listing Revenue", value="556,530", delta="October")
    col7.metric(label="Renewals", value="684,090", delta="October")

    #Bad Months

    #Switching the metric arrow down
    col8.write("<h1 style='font-size: 17px;'>Low Month in:</h1>", unsafe_allow_html=True)
    col8.metric(label="Ads Bought", value="197,714", delta="July", delta_color="inverse")
    col8.metric(label="New Listings", value="197,103", delta="August", delta_color="inverse")
    col8.metric(label="Listing Revenue", value="436,307", delta="December", delta_color="inverse")
    col8.metric(label="Renewals", value="629,823", delta="December", delta_color="inverse")





