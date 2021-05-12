import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
import datetime
import cufflinks as cf

# Establish yfinance periods
yf_periods = ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']
yf_periods_df = pd.DataFrame(yf_periods, columns=['Period'])

from PIL import Image

#Set the title for streamlit webapp
st.title('Argentinean Market - Merval')

#Set subtitle
st.markdown("""
This app retrieves the list of the **Meval** (from Wikipedia) and its corresponding **stock closing price** !
""")

#Add image below the title
image = Image.open("merval.jpg")
st.image(image, use_column_width = True)

#Set subtitle
st.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, yfinance
* **Data source:** [Wikipedia](https://es.wikipedia.org/wiki/Merval).
* **App built by:** Ramiro Inchauspe
""")

st.sidebar.header('Select a Sector ')

# Web scraping of Merval data - Buscarespecífico para yahoo finance
#https://www.youtube.com/watch?v=eNDADqa9858 - Buen video para sacar ideas
#Ticekrs de yahoo finanace -> https://finance.yahoo.com/quote/%5EMERV%3FP%3DMERVAL/components/
@st.cache
def load_data():
    url = 'https://es.wikipedia.org/wiki/Merval'
    html = pd.read_html(url, header = 0)
    df = html[1]
    #Let's select 'Pesos' as the currency
    df[".BA"] = ".BA"
    df["Símbolo"] = df["Símbolo"] + df[".BA"]
    del df['.BA']
    #Let's improve the classification
    df = df.replace(to_replace='Petróleo y Gas',value='Energético')
    df = df.replace(to_replace='Energético',value='Energy')
    df = df.replace(to_replace='Industrial (Aluminio)',value='Industrial')
    df = df.replace(to_replace='Industrial (Siderúrgica)',value='Industrial')
    df = df.replace(to_replace='Inmobiliario-Agropecuario',value='Servicios industriales y otros')
    df = df.replace(to_replace='Fabricación de productos',value='Servicios industriales y otros')
    df = df.replace(to_replace='Servicios industriales y otros',value='Services')
    df = df.replace(to_replace='Finanzas',value='Financiero')
    df = df.replace(to_replace='Financiero',value='Finance')
    df = df.replace(to_replace='Telecomunicaciones',value='Telecommunication')
    df = df.replace(to_replace='Bancario',value='Bank')
    df = df.replace(to_replace='Construcción (Cementos)',value='Construction')
    st.cache(allow_output_mutation=True)
    return df

df = load_data()

sector = df.groupby('Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted( df['Sector'].unique() )
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[ (df['Sector'].isin(selected_sector)) ]

# Sidebar
st.sidebar.subheader('Stock Analysis Parameters')
start_date = st.sidebar.date_input("Start date", datetime.date(2021, 1, 1))
end_date = st.sidebar.date_input("End date", datetime.date(2021, 3, 31))

# Retrieving tickers data
ticker_list = df['Símbolo']
tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol
tickerData = yf.Ticker(tickerSymbol) # Get ticker data
tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker


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

st.header('Stock Analysis')

# https://pypi.org/project/yfinance/

data = yf.download(
        tickers = list(df_selected_sector[:50].Símbolo),
        period = 'ytd',
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



#num_company = st.sidebar.slider('Number of Companies', 0, 5)

if st.button('Look for the selected stock'):
    try:
        #st.header('Stock Closing Price')
        #st.set_option('deprecation.showPyplotGlobalUse', False)
        #for i in list(df_selected_sector.Símbolo)[:num_company]:
        #    price_plot(i)
        # Ticker information
        string_logo = '<img src=%s>' % tickerData.info['logo_url']
        st.markdown(string_logo, unsafe_allow_html=True)

        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name)

        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)

        # Ticker data
        st.header('**Ticker data**')
        st.write(tickerDf)

        # Bollinger bands
        st.header('**Bollinger Bands**')
        qf=cf.QuantFig(tickerDf,title='First Quant Figure',legend='top',name='GS')
        qf.add_bollinger_bands()
        fig = qf.iplot(asFigure=True)
        st.plotly_chart(fig)
    except ValueError:
        st.error('Please enter a valid input')
