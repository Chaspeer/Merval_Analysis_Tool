import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
from PIL import Image

#Set the title for streamlit webapp
st.title('Argentinean Market - Merval')

#Set subtitle
st.markdown("""
This app retrieves the list of the **Meval** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
""")

#Add image below the title
image = Image.open("C:/Users/ramir/Desktop/merval.jpg")
st.image(image, use_column_width = True)

#Set subtitle
st.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, yfinance
* **Data source:** [Wikipedia](https://es.wikipedia.org/wiki/Merval).
""")

st.sidebar.header('User Input Features')

# Web scraping of Merval data - Buscarespecífico para yahoo finance
#https://www.youtube.com/watch?v=eNDADqa9858 - Buen video para sacar ideas
#Ticekrs de yahoo finanace -> https://finance.yahoo.com/quote/%5EMERV%3FP%3DMERVAL/components/
@st.cache
def load_data():
    url = 'https://es.wikipedia.org/wiki/Merval'
    html = pd.read_html(url, header = 0)
    df = html[1]
    df[".BA"] = ".BA"
    df["Símbolo"] = df["Símbolo"] + df[".BA"]
    del df['.BA']
    st.cache(allow_output_mutation=True)
    return df

df = load_data()
sector = df.groupby('Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted( df['Sector'].unique() )
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[ (df['Sector'].isin(selected_sector)) ]

st.header('Display Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download Merval data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Merval.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# https://pypi.org/project/yfinance/

data = yf.download(
        tickers = list(df_selected_sector[:50].Símbolo),
        period = "ytd",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )

# Plot Closing Price of Query Symbol
def price_plot(Símbolo):
  df = pd.DataFrame(data[Símbolo].Close)
  df['Date'] = df.index
  plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
  plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
  plt.xticks(rotation=90)
  plt.title(Símbolo, fontweight='bold')
  plt.xlabel('Date', fontweight='bold')
  plt.ylabel('Closing Price', fontweight='bold')
  return st.pyplot()

num_company = st.sidebar.slider('Number of Companies', 2, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    for i in list(df_selected_sector.Símbolo)[:num_company]:
        price_plot(i)
