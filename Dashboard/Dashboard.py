import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Reading the CSV file (replace 'all_data.csv' with the name of your data file)
main_data_df = pd.read_csv('main_data.csv')

# Converting 'order_purchase_timestamp' to datetime format
main_data_df['order_purchase_timestamp'] = pd.to_datetime(main_data_df['order_purchase_timestamp'], errors='coerce')

# RFM (Recency, Frequency, Monetary)
rfm_df = main_data_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",  
    "order_id": "nunique",  
    "price": "sum" 
})

rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
rfm_df = rfm_df.dropna(subset=['max_order_timestamp'])
recent_date = main_data_df["order_purchase_timestamp"].dt.date.max()
rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
main_data_df['order_purchase_timestamp'] = pd.to_datetime(main_data_df['order_purchase_timestamp'])

# Sorting data by date
orders_by_date = main_data_df.groupby(main_data_df['order_purchase_timestamp'].dt.date).size()

# Sorting data and calculating unique order_id counts
category_summary = main_data_df.groupby(by="product_category_name").order_id.nunique().sort_values(ascending=False).head(20)

# Sorting Customer State data
state_summary = main_data_df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False)

# Creating the dashboard using Streamlit
st.title("Dashboard")
st.dataframe(main_data_df)

# Displaying the most commonly used payment type
st.subheader("The Most Commonly Used Payment Type")

# Creating a payment summary
payment_summary = main_data_df.groupby(by="payment_type").order_id.nunique().sort_values(ascending=False)

# Displaying the barchart for payment types
fig_payment, ax_payment = plt.subplots(figsize=(10, 5))
payment_summary.plot(kind='bar', color='lightcoral', edgecolor='black', ax=ax_payment)
ax_payment.set_title('The Most Commonly Used Payment Type', fontsize=18, color='darkblue')
ax_payment.set_xlabel(None)
ax_payment.set_ylabel(None)
plt.xticks(rotation=45, color='darkgreen')
plt.tight_layout()

# Displaying the chart in Streamlit
st.pyplot(fig_payment)

# Creating a bar chart using seaborn for RFM
fig_rfm, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1"]

#----------------------------------------------------------------------
# Displaying Orders Over Time
plt.figure(figsize=(10, 6))  
orders_by_date.plot(kind='line', color='darkorange')
plt.title('Number of Orders Over Time', fontsize=18, color="darkblue")
plt.xlabel('Date', color="darkgreen")
plt.ylabel('Number of Orders', color="darkgreen")
plt.xticks(rotation=45)
plt.tight_layout()
st.subheader("Number of Orders Over Time")
st.pyplot(plt)

#----------------------------------------------------------------------
# Displaying the Top 20 States based on Customers
plt.figure(figsize=(10, 8))  
state_summary.plot(kind='barh', color='#FF6F61', edgecolor='black')
plt.title('20 states where customers come from.', fontsize=18, color="darkblue")
plt.xlabel(None)
plt.ylabel(None)
plt.xticks(color="darkgreen")
st.subheader("Top 20 States by Customers")
st.pyplot(plt)

#----------------------------------------------------------------------
# Displaying the Top 20 Categories
plt.figure(figsize=(10, 8))  # Setting figure size
category_summary.plot(kind='barh', color='#92A8D1', edgecolor='black')
plt.title('Top 20 Categories', fontsize=18, color="darkblue")
plt.xlabel(None)
plt.ylabel(None)
plt.xticks(color="darkgreen")
st.subheader("Top 20 Categories by Orders")
st.pyplot(plt)

#----------------------------------------------------------------------
# RFM section
st.subheader("RFM Analysis")
rfm_df['customer_id_last3'] = rfm_df['customer_id'].astype(str).str[-3:]
fig_rfm, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
plt.subplots_adjust(wspace=0.4)

# Plotting Recency
recency_data = rfm_df.sort_values(by="recency", ascending=True).head(5)
sns.barplot(y="recency", x="customer_id_last3", data=recency_data, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18, color="darkred")
ax[0].tick_params(axis='x', labelsize=20, rotation=0)
ax[0].tick_params(axis='y', labelsize=18)

# Plotting Frequency
frequency_data = rfm_df.sort_values(by="frequency", ascending=False).head(5)
sns.barplot(y="frequency", x="customer_id_last3", data=frequency_data, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18, color="darkred")
ax[1].tick_params(axis='x', labelsize=20, rotation=0)
ax[1].tick_params(axis='y', labelsize=18)

# Plotting Monetary
monetary_data = rfm_df.sort_values(by="monetary", ascending=False).head(5)
sns.barplot(y="monetary", x="customer_id_last3", data=monetary_data, palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18, color="darkred")
ax[2].tick_params(axis='x', labelsize=20, rotation=0)
ax[2].tick_params(axis='y', labelsize=18)

plt.suptitle("Top Customers Based on RFM", fontsize=22, color="darkblue")
plt.tight_layout()
st.pyplot(fig_rfm)
