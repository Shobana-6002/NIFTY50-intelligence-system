import pandas as pd
import numpy as np
import os



def generate_indicators():
    print("Inside generate_indicators()")

    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CLEANED_DATA = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv')
    FINAL_DF     = os.path.join(BASE_DIR, 'data', 'processed', 'final_df.csv')
    SIGNALS      = os.path.join(BASE_DIR, 'data', 'processed', 'current_signal.csv')
    df = pd.read_csv(CLEANED_DATA)
    df['Date']=pd.to_datetime(df['Date'])
    df=df.reset_index(drop=True)
    df=df.sort_values(by=['Ticker','Date'])

    tickers=df['Ticker'].unique()
    ## RSI calculation
    def calculate_rsi(data):
        delta=data['Close'].diff()
        delta=delta.reset_index(drop=True)

        gain = pd.Series(np.where(delta>0,delta,0))
        loss = pd.Series(np.where(delta<0,abs(delta),0))

        avg_gain = gain.ewm(span=14, min_periods=14).mean()
        avg_loss = loss.ewm(span=14, min_periods=14).mean()

        Rs = avg_gain/(avg_loss + 1e-10)

        RSI= round(100-(100/(1+Rs)),2)

        data['RSI'] = RSI

        return data['RSI']
    rsi_data=[]

    for ticker in tickers:
        stock_data = df[df['Ticker']==ticker].copy()
        stock_data=stock_data.reset_index(drop=True)
        stock_rsi=calculate_rsi(stock_data)
        stock_data['RSI'] = stock_rsi
        rsi_data.append(stock_data)

    stock_df=pd.concat(rsi_data)

    ##MACD

    def calculate_macd(data):
        ema12=data['Close'].ewm(span=12, min_periods=12).mean()
        ema26=data['Close'].ewm(span=26, min_periods=26).mean()

        macd_line=ema12-ema26
        signal_line=macd_line.ewm(span=9,min_periods=9).mean()

        histogram=macd_line-signal_line

        data['macd_line']=macd_line
        data['signal_line']=signal_line
        data['histogram']=histogram
        return data

    macd_data=[]

    for ticker in tickers:
        stock_data=df[df['Ticker']==ticker].copy()
        stock_data=stock_data.reset_index(drop=True)
        stock_macd=calculate_macd(stock_data)
        macd_data.append(stock_macd)

    macd_df=pd.concat(macd_data)
    macd_df=macd_df.reset_index(drop=True)

   
    ##Bollinger Bands

    def calculate_bb(data):
        middle=data['Close'].rolling(window=20).mean()
        std=data['Close'].rolling(window=20).std()
        upper= middle + (2*std)
        lower= middle - (2*std)
        bandwidth = (upper - lower) / middle*100
        data['bb_middle']=middle
        data['bb_upper']=upper
        data['bb_lower']=lower
        data['bb_bandwidth']=bandwidth
        return data

    bb_lst=[]

    for ticker in tickers:
        bb_data=macd_df[macd_df['Ticker']==ticker].copy()
        bb_data=bb_data.reset_index(drop=True)
        bb_data=calculate_bb(bb_data)
        bb_lst.append(bb_data)

    bb_df=pd.concat(bb_lst)
    bb_df=bb_df.reset_index(drop=True)

  
    ##signal system

    #merging RSI with macd and bb in final_df
    final_df=bb_df.copy()
    if 'RSI' in final_df.columns:
        final_df=final_df.drop(columns=['RSI'])
    final_df = final_df.merge(stock_df[['Ticker', 'Date', 'RSI']],on=['Ticker', 'Date'],how='left')
    final_df=final_df.reset_index(drop=True)
    final_df['Date']=pd.to_datetime(final_df['Date'])
    final_df=final_df.reset_index(drop=True)
    
    

    #rsi score
    rsi_conditions = [
        final_df['RSI'] < 30,
        final_df['RSI'] > 70
    ]
    rsi_choices = [1, -1]

    final_df['rsi_score'] = np.select(rsi_conditions, rsi_choices, default=0)

    #MACD score
    macd_conditions = [
        final_df['histogram'] > 0,
        final_df['histogram'] < 0
    ]
    macd_choices = [1, -1]

    final_df['macd_score'] = np.select(macd_conditions, macd_choices, default=0)

    #BB score
    bb_conditions = [
        final_df['Close'] < final_df['bb_lower'],
        final_df['Close'] > final_df['bb_upper']
    ]
    bb_choices = [1, -1]

    final_df['bb_score'] = np.select(bb_conditions, bb_choices, default=0)

    #total score
    final_df['total_score'] = (
        final_df['rsi_score'] +
        final_df['macd_score'] +
        final_df['bb_score']
    )

    #Final signal
    signal_conditions = [
        final_df['total_score'] >= 2,
        final_df['total_score'] == 1,
        final_df['total_score'] == 0,
        final_df['total_score'] == -1,
        final_df['total_score'] <= -2
    ]
    signal_choices = [
        'STRONG BUY 🟢',
        'WEAK BUY 🔵',
        'NEUTRAL ⚪',
        'WEAK SELL 🟡',
        'STRONG SELL 🔴'
    ]

    final_df['final_signal'] = np.select(
    signal_conditions,
    signal_choices,
    default='NEUTRAL ⚪'
)
    
    #current signal for each stock
    current_signal = final_df.groupby('Ticker').last().reset_index()
    current_signal = current_signal[[
        'Ticker','RSI','rsi_score',
        'macd_score','bb_score',
        'total_score','final_signal'
    ]]
    current_signal = current_signal.sort_values('total_score', ascending=False)
    current_signal = current_signal.reset_index(drop=True)
    

    #csv file
    final_df.to_csv(
        FINAL_DF,
        index=False
    )
    current_signal.to_csv(
        SIGNALS,
        index=False
    )