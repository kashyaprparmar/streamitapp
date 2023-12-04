import snowflake.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='kashyaprparmar',
    password='Kashyap@246',
    warehouse='COMPUTE_WH',
    account='pf20846.ap-south-1.aws',
    database='BOOKS_DB2',
    schema='books_table'
)

# Create a cursor
cursor = conn.cursor()

# Use the BOOKS_DB
cursor.execute("USE BOOKS_DB")

# Read data from Snowflake into a DataFrame
df = pd.read_sql("SELECT * FROM Books_table2", conn)
rating_mapping = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
df['RATING'] = df['RATING'].map(rating_mapping)

# Extract category name from 'PRODUCT_CATEGORY'
df['PRODUCT_CATEGORY'] = df['PRODUCT_CATEGORY'].apply(lambda x: x.split('_')[0].title())

# Convert 'PRICE' column to numeric
df['PRICE'] = df['PRICE'].astype(float)

# Close the cursor and connection
cursor.close()
conn.close()

# Set page configuration
st.set_page_config(page_title='Book Analysis', page_icon=':books:',layout='wide')
st.title('📚 Book Data Analysis')

# Sidebar
st.sidebar.title("Filters")
selected_category = st.sidebar.selectbox("Select Category", df['PRODUCT_CATEGORY'].unique())
price_range = st.sidebar.slider("Select Price Range", float(df['PRICE'].min()), float(df['PRICE'].max()), (float(df['PRICE'].min()), float(df['PRICE'].max())))

# Filter data
filtered_df = df[(df['PRODUCT_CATEGORY'] == selected_category) & (df['PRICE'] >= price_range[0]) & (df['PRICE'] <= price_range[1])]

# Main content
# Custom CSS
st.markdown(f""" """, unsafe_allow_html=True)


# Sidebar
all_ratings = df['RATING'].unique()
selected_ratings = st.sidebar.multiselect('Select Ratings', all_ratings, default=all_ratings)

# Filter data
category_df = df[(df['PRODUCT_CATEGORY'] == selected_category) & (df['PRICE'].between(price_range[0], price_range[1])) & (df['RATING'].isin(selected_ratings))]
# Filter data
filtered_df = df[(df['PRICE'].between(price_range[0], price_range[1])) & (df['RATING'].isin(selected_ratings))]
fig_pie = px.pie(
    filtered_df,
    names='PRODUCT_CATEGORY',
    title='Book Categories Distribution',
    hole=0.3,
)

# Highlight selected category
if selected_category != 'All':
    fig_pie.update_traces(
        pull=[0.2 if cat == selected_category else 0 for cat in fig_pie.data[0].labels],
        textinfo='percent+label',
    )
st.plotly_chart(fig_pie,use_container_width=True)


col1, col2, col3, col4 = st.columns(4)
col1.metric("Number of Books:", "📖"+str(len(category_df)))
col2.metric("Total Stock", "📦" + str(category_df['AVAILABILITY'].sum()))
col3.metric("Avg Price", "£"+str(round(category_df['PRICE'].mean(),2)))
col4.metric("Avg Rating", "⭐"+ str(round(category_df['RATING'].mean(),2)))


# Plotly Express - Pie chart for Rating distribution
fig1 = px.pie(filtered_df, names='RATING', title='Rating Distribution')

# with col1:
#     fig1 = px.histogram(df, x="Rating")
#     st.plotly_chart(fig1, use_container_width=True)

st.plotly_chart(fig1, use_container_width=True)

# Matplotlib - Bar chart for Category-wise Book Count
fig2, ax = plt.subplots()
sns.countplot(x='PRODUCT_CATEGORY', data=filtered_df, ax=ax)
ax.set_title('Category-wise Book Count')
ax.set_xlabel('Category')
ax.set_ylabel('Count')

# Rotate x-axis labels to 90 degrees and make font size smaller
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='right', fontsize=8)

# Adjust tick parameters for better readability
ax.tick_params(axis='x', which='both', pad=1)


fig3, ax = plt.subplots()
sns.scatterplot(x='PRICE', y='AVAILABILITY', hue='RATING', size='RATING', data=category_df)
ax.set_title('Price vs Availability')
ax.set_xlabel('Price')
ax.set_ylabel('Availability')


# Plotly Express - Scatter plot for Price vs Rating
fig3 = plt.figure(figsize=(10, 8))
sns.scatterplot(x='PRICE', y='AVAILABILITY', hue='RATING', size='RATING', data=category_df)
plt.title('Price vs Availability')


col1,col2 = st.columns(2)
col1.pyplot(fig2)
col2.pyplot(fig3)
# col7.pyplot(fig4)

# Display book details in a table
st.header("Book Details")
st.dataframe(filtered_df[['TITLE', 'PRICE', 'PRODUCT_CATEGORY', 'RATING', 'AVAILABILITY']])

