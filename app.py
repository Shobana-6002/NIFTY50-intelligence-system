import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="NIFTY 50 Intelligence System", page_icon="📈",layout="wide")
st.title("NIFTY 50 Intelligence System")
st.markdown("""<style> .block-container{padding-top:2rem}</style>""",unsafe_allow_html=True)

##Data Loading
@st.cache_data
def load_data():
    data      = pd.read_csv(os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv'))
    signals   = pd.read_csv(os.path.join(BASE_DIR, 'data', 'processed', 'current_signal.csv'))
    indicators = pd.read_csv(os.path.join(BASE_DIR, 'data', 'processed', 'final_df.csv'))
    return data , signals,indicators

data, signals ,indicators = load_data()

#datetime
data['Date']=pd.to_datetime(data['Date'],format="%Y-%m-%d")
indicators['Date']=pd.to_datetime(indicators['Date'],format="%Y-%m-%d")

tickers=data['Ticker'].unique()



##Tabs
Tab1,Tab2,Tab3,Tab4=st.tabs(["Overview","Market Analysis","Stock Analysis","Signal Dashboard"])

#Tab 1
with Tab1:
    st.markdown("""<h1 style='text-align:center;'>Overview</h1>""",unsafe_allow_html=True) 
    
    col1,col2,col3,col4,col5=st.columns(5)
    
    #col 1
    with col1:
        st.metric("Total Stocks",50)
    
    #col 2
    with col2:
        bullish_count=len(signals[signals['total_score']>0])
        st.metric("📈Bullish stocks",bullish_count)

    #col 3
    with col3:
        bearish_count=len(signals[signals['total_score']<0])
        st.metric("📉Bearish Stocks",bearish_count)
    
    #col 4
    with col4:
        netural_count=len(signals[signals['total_score']==0])
        st.metric("⚖️Neutral Stocks",netural_count)

    #col 5
    with col5:
        st.metric("🗓️Last Updated",data['Date'].max().strftime('%d %b %Y'))


    #Today's Market Mood

    today_df=data[data['Date']==data['Date'].max()]

    total_stocks=len(today_df)
    sediments=((bullish_count-bearish_count)/50)*100

    if sediments>0:
        st.markdown(f"<h2 style='text-align:center;color:green;'>Today's Market is Bullish ({sediments:.2f}%)</h2>",unsafe_allow_html=True)
        color = "green"
    elif sediments<0:
        st.markdown(f"<h2 style='text-aling:center;color:red;'>Today's Market is Bearish ({sediments:.2f}%)</h2>",unsafe_allow_html=True)
        color = "red"
    else:
        st.markdown(f"<h2 style='text-align:center;color:orange;'>Today's Market is Neutral ({sediments:.2f}%)</h2>",unsafe_allow_html=True)
        color = "orange"
    st.write("Note: Market mood reflects today's price movement.")
    today_df=today_df.sort_values(by="daily_return",ascending=False)

    #top gainers and losers
    gainers=today_df.head(5)[['Ticker','Company','daily_return']]
    losers=today_df.tail(5)[['Ticker','Company','daily_return']]
    
    gainers['daily_return']=round(gainers['daily_return']*100,2)
    losers['daily_return']=round(losers['daily_return']*100,2)

    gainers=gainers.rename(columns={'daily_return':'Return %'})
    losers=losers.rename(columns={'daily_return':'Return %'})

    col1,col2=st.columns(2)
    
    with col1:
        st.subheader("Top 5 GAINERS TODAY")
        st.dataframe(gainers,hide_index=True,use_container_width=True)

    with col2:
        st.subheader("Top 5 LOSERS TODAY")
        st.dataframe(losers,hide_index=True,use_container_width=True)
        
##Tab 2
with Tab2: 
    st.markdown("""<h1 style='text-align:center;'>Market Analysis</h1>""",unsafe_allow_html=True) 

    duration=st.selectbox("Select duration os analysis",['1 week','1 month','3 months','6 months','1 year','5 years'],index=2)

    today_date=data['Date'].max()

    duration_map={ "1 week": 7,
    "1 month": 30,
    "3 months": 90,
    "6 months": 180,
    "1 year": 365}

    if duration == "5 years":
        start_date = data["Date"].min()
    else:
        days=duration_map[duration]
        start_date =today_date - pd.DateOffset(days=days)
    
    period_df=data[data['Date']>=start_date]

    period_returns = []

    for ticker, group in period_df.groupby('Ticker'):

        first_close = group['Close'].iloc[0]
        last_close = group['Close'].iloc[-1]

        returns = ((last_close - first_close) / first_close) * 100

        period_returns.append({
            'Ticker': ticker,
            'Company': group['Company'].iloc[0],
            'Sector': group['Sector'].iloc[0],
            'Return %': returns
        })

    period_returns = pd.DataFrame(period_returns)

    ##SECTOR Performance CHART
    sector_data=period_returns.groupby('Sector')['Return %'].mean().sort_values(ascending=False)
    sector_data=sector_data.reset_index()

    fig=px.bar(sector_data ,x='Sector',y='Return %',title="Sector Performance",color='Return %',color_continuous_scale = 'RdYlGn',color_continuous_midpoint = 0)
    fig.add_hline(y=0, line_dash='dash', line_color='white')

    st.plotly_chart(fig, use_container_width=True)

    #HEATMAP

    fig=px.treemap(period_returns,path = ['Sector', 'Ticker'],values = period_returns['Return %'].abs(), color = 'Return %',color_continuous_scale = 'RdYlGn',color_continuous_midpoint = 0,title="Nifty 50 Heatmap",hover_data = ['Company', 'Return %'])
    st.plotly_chart(fig, use_container_width=True)

    
    col1, col2 = st.columns(2)

    # col1 - Risk vs Return
    with col1:
        vol_data = []
        for ticker in period_df['Ticker'].unique():        # ← period_df not period_returns
            filter_data = period_df[period_df['Ticker']==ticker]
            vol = filter_data['daily_return'].std() * np.sqrt(252)  # ← daily_return no 's'
            vol_data.append({'Ticker': ticker, 'volatility': vol})
        vol_df = pd.DataFrame(vol_data)

        period_returns = period_returns.merge(vol_df, on='Ticker', how='left')  # ← merge!

        fig = px.scatter(
        period_returns,
        x='volatility',
        y='Return %',
        color='Sector',              # ← color by sector
        hover_name='Ticker',         # ← hover shows ticker
        hover_data=['Company'],
        title='Risk vs Return')

        fig.add_vline(x=period_returns['volatility'].mean(), line_dash='dash', line_color='gray')
        fig.add_hline(y=period_returns['Return %'].mean(), line_dash='dash', line_color='gray')
        st.plotly_chart(fig, use_container_width=True)

    # col2 - Correlation Heatmap
    with col2:
        pivot_df = period_df.pivot_table(    # ← period_df not period_returns
            index='Date',
            columns='Ticker',
            values='daily_return'            # ← daily_return no 's'
        )
        corr = pivot_df.corr()

        fig = px.imshow(
        corr,
        color_continuous_scale='RdBu_r',
        title='Stock Correlation',
        zmin=-1, zmax=1
        )
        fig.update_layout(
        xaxis=dict(tickfont=dict(size=7)),   # ← tiny font so labels fit
        yaxis=dict(tickfont=dict(size=7))
        )
        st.plotly_chart(fig, use_container_width=True)

with Tab3:
    st.markdown("""<h1 style='text-align:center;'>Stock Analysis</h1>""",unsafe_allow_html=True) 
    selected_ticker=st.selectbox("Select a stock",tickers)
   
    stock_data=data[data['Ticker']==selected_ticker].sort_values(by='Date',ascending=True)
    stock_indicators=indicators[indicators['Ticker']==selected_ticker].sort_values(by='Date',ascending=True)
    stock_signals=signals[signals['Ticker']==selected_ticker]

    col1,col2,col3,col4,col5=st.columns(5)
   
    with col1:
       st.metric("currrent price",f"₹{stock_data['Close'].iloc[-1]:.2f}")
    
    with col2:
        st.metric("RSI",f"{stock_indicators['RSI'].iloc[-1]:.1f}")

    with col3:
        st.metric("Current Signal",f"{stock_signals['final_signal'].iloc[-1]}")

    with col4:
        one_month_ago = stock_data['Date'].max() - pd.DateOffset(days=30)
        month_data = stock_data[stock_data['Date'] >= one_month_ago]
        first_price = month_data['Close'].iloc[0]
        last_price = month_data['Close'].iloc[-1]
        monthly_return = ((last_price - first_price) / first_price) * 100
        st.metric("Last Month Returns",f"{monthly_return:.2f}%")

    with col5:
        today_vol=stock_data['Volume'].iloc[-1]
        avg_vol=stock_data['Volume'].tail(20).mean()
        ratio=today_vol/avg_vol
        if ratio>1.5:
            label=f"{ratio:.2f}x[High]"
        elif ratio<0.5:
            label=f"{ratio:.2f}x[Low]"
        else:
            label=f"{ratio:.2f}x[Normal]"

        st.metric("Volume Signal",label)


    #price chart

    duration=st.selectbox("Select duration os analysis",['1 week','1 month','3 months','6 months','1 year','5 years'],index=5)
    
    today_date=data['Date'].max()

    duration_map={ "1 week": 7,
    "1 month": 30,
    "3 months": 90,
    "6 months": 180,
    "1 year": 365}
     
    if duration == "5 years":
        start_date = data["Date"].min()
    else:
        days=duration_map[duration]
        start_date =today_date - pd.DateOffset(days=days)

    price_data=stock_data[stock_data['Date']>=start_date]
    indicator_data=stock_indicators[stock_indicators['Date']>=start_date]
    rsi_chart=pd.DataFrame(price_data.merge(indicator_data[['Date','RSI']],on='Date',how='left'))

    ma20 = price_data['Close'].rolling(window=20).mean()
    ma200 = price_data['Close'].rolling(window=200).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=price_data['Date'],y=price_data['Close'],mode='lines',name='Close price',line=dict(color='blue',width=2)))
    fig.add_trace(go.Scatter(x=price_data['Date'],y=ma20,mode='lines',name='MA20',line=dict(color='orange',width=2)))
    fig.add_trace(go.Scatter(x=price_data['Date'],y=ma200,mode='lines',name='MA200',line=dict(color='red',width=2)))

    fig.update_layout(title=f"{selected_ticker} price chart",xaxis_title="Date",yaxis_title="Price (₹)")
    
    st.plotly_chart(fig,use_container_width=True)

    col1,col2=st.columns(2)

    with col1:
        fig=px.line(rsi_chart,x='Date',y='RSI',title="RSI Chart")
        fig.update_yaxes(range=[0,100])
        fig.add_hline(y=70,line_dash='dash',line_color='red',line_width=2.5)
        fig.add_hline(y=50,line_dash='dash',line_color='grey',line_width=3.5)
        fig.add_hline(y=30,line_dash='dash',line_color='green',line_width=2.5)

        st.plotly_chart(fig,use_container_width=True)

    with col2:
        fig=go.Figure()
        colors=['green' if val>=0 else 'red' for val in indicator_data['histogram']]
        fig.add_trace(go.Bar(x=indicator_data['Date'],y=indicator_data['histogram'],name="Histogram",marker_color=colors,showlegend=False))
        fig.add_trace(go.Scatter(x=indicator_data['Date'],y=indicator_data['macd_line'],mode='lines',line=dict(color='blue',width=1.5),name="MACD line"))
        fig.add_trace(go.Scatter(x=indicator_data['Date'],y=indicator_data['signal_line'],mode='lines',line=dict(color='orange',width=1.5),name="Signal line"))
        fig.add_hline(y=0,line_dash='dash',line_color='grey',line_width=2.5)
        
        
        fig.update_layout(title="MACD Chart",xaxis_title="Date",yaxis_title="MACD Value",barmode='relative')
        
        st.plotly_chart(fig,use_container_width=True)
   
    current_values=stock_indicators.iloc[-1][['RSI','histogram','Close','bb_upper','bb_lower']]

    current_rsi=current_values['RSI']
    current_histogram=current_values['histogram']
    current_price=current_values['Close']
    current_bb_upper=current_values['bb_upper']
    current_bb_lower=current_values['bb_lower']

    if current_rsi<30:
        st.info(f'RSI is currently at {current_rsi:.2f}, indicating that the stock is oversold. This could be a potential buying opportunity.')
    elif current_rsi>70:
        st.info(f'RSI is currently at {current_rsi:.2f}, indicating that the stock is overbought. This could be a potential selling opportunity.')
    else:
        st.info(f'RSI is currently at {current_rsi:.2f}, indicating that the stock is neither overbought nor oversold. It is in a neutral state.')

    if current_histogram>0:
        st.info(f'The MACD histogram is currently at {current_histogram:.2f}, Bullish momentum building.')
    elif current_histogram<0:
        st.info(f'The MACD histogram is currently at {current_histogram:.2f},  Bearish momentum present.')
    
    if current_price<current_bb_lower:
        st.info(f'The stock price is currently at ₹{current_price:.2f}, which is below the lower Bollinger Band.Statistically low,This could be a potential buying opportunity.')
    elif current_price>current_bb_upper:
        st.info(f'The stock price is currently at ₹{current_price:.2f}, which is above the upper Bollinger Band.Statistically high,This could be a potential selling opportunity.')
    else:
        st.info(f'The stock price is currently at ₹{current_price:.2f}, which is within the Bollinger Bands. This indicates that the stock is in a normal trading range.')

with Tab4 :
    st.markdown("""<h1 style='text-align:center;'>Signal Dashboard</h1>""",unsafe_allow_html=True) 
    
    ticker_price=data.groupby(['Ticker','Company','Sector'])['Close'].last().reset_index()
    merged_df=ticker_price.merge(signals[['Ticker','RSI','total_score','final_signal']],on='Ticker',how='left')
  
    col1,col2,col3,col4,col5=st.columns(5)
    
    with col1:
        st.metric("Strong Buy",len(signals[signals['final_signal']=='STRONG BUY 🟢']))
    with col2:
        st.metric("Strong Sell",len(signals[signals['final_signal']=='STRONG SELL 🔴']))
    with col3:
        st.metric("Neutral",len(signals[signals['final_signal']=='NEUTRAL ⚪']))
    with col4:
        st.metric("Weak Buy",len(signals[signals['final_signal']=='WEAK BUY 🔵']))
    with col5:
        st.metric("weak Sell",len(signals[signals['final_signal']=='WEAK SELL 🟡']))

    
   
    merged_df=merged_df.sort_values(by='total_score',ascending=False)
    merged_df=merged_df.rename(columns={'Close':'Current Price (₹)','RSI':'RSI Value','total_score':'Total Score','final_signal':'Signal'})
    merged_df=merged_df.reset_index()

    

    signal_counts=signals['final_signal'].value_counts().reset_index()
    signal_counts.columns=['Signal','Count']

    color_map = {
    "STRONG BUY 🟢": "darkgreen",
    "WEAK BUY 🔵": "blue",
    "NEUTRAL ⚪": "gray",
    "WEAK SELL 🟡": "orange",
    "STRONG SELL 🔴": "red"}
    
    col1,col2=st.columns(2)

    with col1:
        st.subheader("🏆 Top 3 Buy Recommendations")
        
        top3=merged_df[merged_df['Total Score']>0].reset_index()
        top3=top3.sort_values(ascending=False,by='Total Score').head(3)
        top3=top3[['Ticker','Company','Current Price (₹)','RSI Value','Total Score','Signal']]
        
        if top3.empty:
            st.warning("No Buy Opportunities Found")
        else:
            cols=st.columns(3)
            for col, (_, row) in zip(cols, top3.iterrows()):

                with col:
                     
                     with st.container(border=True):

                        st.markdown(f"""<div style=text-align:center>
                                <h3>{row['Company']}</h3>
                                <h2>₹{row['Current Price (₹)']:.2f}</h2>
                                <p>RSI: {row['RSI Value']:.2f}</p>
                                <p>Signal:{row['Signal']}</p>
                                <p>Total Score: {row['Total Score']}</p>""",unsafe_allow_html=True)
    


    with col2:
    # Create donut chart
        fig = px.pie(signal_counts,names="Signal", values="Count",hole=0.4,color="Signal",color_discrete_map=color_map,title="Distribution of Trading Signals")
        fig.update_traces(textposition="inside",textinfo="percent+label")
        fig.update_layout(title_x=0.5,legend_title="Signal Type")

        st.plotly_chart(fig,use_container_width=True)
    
    options=['ALL SIGNALS','STRONG BUY 🟢','STRONG SELL 🔴','NEUTRAL ⚪','WEAK BUY 🔵','WEAK SELL 🟡']
    selected_signal = st.selectbox("Select Signal Type",options=options,index=0)
   
    filter_df=merged_df[merged_df['Signal']==selected_signal] if selected_signal != 'ALL SIGNALS' else merged_df
    filter_df=filter_df[['Ticker','Company','Sector','Current Price (₹)','RSI Value','Total Score','Signal']]
    filter_df=filter_df.reset_index(drop=True)

    filter_df