import pandas as pd
import yfinance as yf
import datetime as dt
import os

from indicator_generation import generate_indicators

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DATA = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv')

ticker=['RELIANCE.NS','TCS.NS','HDFCBANK.NS','INFY.NS','ICICIBANK.NS','HINDUNILVR.NS','ITC.NS','SBIN.NS','BAJFINANCE.NS','BHARTIARTL.NS','KOTAKBANK.NS','ASIANPAINT.NS','AXISBANK.NS','MARUTI.NS','SUNPHARMA.NS','WIPRO.NS','TITAN.NS','NESTLEIND.NS','HCLTECH.NS','TMCV.NS','M&M.NS','NTPC.NS','POWERGRID.NS','TATASTEEL.NS','ADANIPORTS.NS','ADANIENT.NS','JSWSTEEL.NS','COALINDIA.NS','ONGC.NS','BAJAJ-AUTO.NS','TECHM.NS','ULTRACEMCO.NS','GRASIM.NS','HINDALCO.NS','CIPLA.NS','EICHERMOT.NS','HEROMOTOCO.NS','DRREDDY.NS','DIVISLAB.NS','BAJAJFINSV.NS','TATACONSUM.NS','APOLLOHOSP.NS','SBILIFE.NS','HDFCLIFE.NS','BRITANNIA.NS','SHRIRAMFIN.NS','INDUSINDBK.NS','LTM.NS','BEL.NS','TRENT.NS']

stock_info = {
    "RELIANCE.NS" : {
                      "company" : "Reliance Industries",
                      "sector"  : "Energy"
                    },

    "TCS.NS"      : {
                      "company" : "TCS",
                      "sector"  : "IT"
                    },

    "HDFCBANK.NS" : {
                      "company" : "HDFC Bank",
                      "sector"  : "Banking"
                    },
    "INFY.NS" : {
                      "company" : "Infosys",
                      "sector"  : "IT"
                    },
    "ICICIBANK.NS" : {
                      "company" : "ICICI Bank",
                      "sector"  : "Banking"
                    },
    "HINDUNILVR.NS" : {
                      "company" : "Hindustan Unilever",
                      "sector"  : "FMCG"
                    },
    "ITC.NS" : {
                      "company" : "ITC",
                      "sector"  : "FMCG"
                    },
    "SBIN.NS" : {
                      "company" : "State Bank of India",
                      "sector"  : "Banking"
                    },
    "BAJFINANCE.NS" : {
                      "company" : "Bajaj Finance",
                      "sector"  : "Finance"
                    },
    "BHARTIARTL.NS" : {
                      "company" : "Bharti Airtel",
                      "sector"  : "Telecom"
                    },
    "KOTAKBANK.NS" : {
                      "company" : "Kotak Mahindra Bank",
                      "sector"  : "Banking"
                    },
    "ASIANPAINT.NS" : {
                      "company" : "Asian Paints",
                      "sector"  : "Consumer"
                    },
    "AXISBANK.NS" : {
                      "company" : "Axis Bank",
                      "sector"  : "Banking"
                    },
    "MARUTI.NS" : {
                      "company" : "Maruti Suzuki",
                      "sector"  : "Auto"
                    },
    "SUNPHARMA.NS" : {
                      "company" : "Sun Pharma",
                      "sector"  : "Pharma"
                    },
    "WIPRO.NS" : {
                      "company" : "Wipro",
                      "sector"  : "IT"
                    },
    "TITAN.NS" : {
                      "company" : "Titan Company",
                      "sector"  : "Consumer"
                    },
    "NESTLEIND.NS" : {
                      "company" : "Nestlé India",
                      "sector"  : "FMCG"
                    },
    "HCLTECH.NS" : {
                      "company" : "HCL Technologies",
                      "sector"  : "IT"
                    },
    "TMCV.NS" : {
                      "company" : "Tata Motors",
                      "sector"  : "Auto"                     
                   },
    "M&M.NS" : {
                      "company" : "Mahindra & Mahindra",
                      "sector"  : "Auto"
                    },
    "NTPC.NS" : {
                      "company" : "NTPC",
                      "sector"  : "Energy"
                    },
    "POWERGRID.NS" : {
                      "company" : "Power Grid Corp",
                        "sector"  : "Energy"
                    },
    "TATASTEEL.NS" : {
                      "company" : "Tata Steel",
                      "sector"  : "Metals"
                    },
    "ADANIPORTS.NS" : {
                        "company" : "Adani Ports",
                        "sector"  : "Infrastructure"
                        },
    "ADANIENT.NS" : {
                        "company" : "Adani Enterprises",
                        "sector"  : "Conglomerate"
                        },
    "JSWSTEEL.NS" : {
                        "company" : "JSW Steel",
                        "sector"  : "Metals"
                        },
    "COALINDIA.NS" : {
                        "company" : "Coal India",
                        "sector"  : "Energy"
                        },
    "ONGC.NS" : {
                        "company" : "ONGC",
                        "sector"  : "Energy"
                        },
    "BAJAJ-AUTO.NS" : {
                        "company" : "Bajaj Auto",
                        "sector"  : "Auto"
                        },
    "TECHM.NS" : {
                        "company" : "Tech Mahindra",
                        "sector"  : "IT"
                        },
    "ULTRACEMCO.NS" : {
                        "company" : "UltraTech Cement",
                        "sector"  : "Cement"
                        },
    "GRASIM.NS" : {
                        "company" : "Grasim Industries",
                        "sector"  : "Conglomerate"
                        },
    "HINDALCO.NS" : {
                        "company" : "Hindalco Industries",
                        "sector"  : "Metals"
                        },
    "CIPLA.NS" : {
                        "company" : "Cipla",
                        "sector"  : "Pharma"
                        },
    "EICHERMOT.NS" : {
                        "company" : "Eicher Motors",
                        "sector"  : "Auto"
                        },
    "HEROMOTOCO.NS" : {
                        "company" : "Hero MotoCorp",
                        "sector"  : "Auto"
                        },
    "DRREDDY.NS" : {
                        "company" : "Dr. Reddy's Labs",
                        "sector"  : "Pharma"
                  },
    "DIVISLAB.NS" : {
                        "company" : "Divi's Laboratories",
                        "sector"  : "Pharma"
                        },
    "BAJAJFINSV.NS" : {
                        "company" : "Bajaj Finserv",
                        "sector"  : "Finance"
                        },
    "TATACONSUM.NS" : {
                        "company" : "Tata Consumer Products",
                        "sector"  : "FMCG"
                        },
    "APOLLOHOSP.NS" : {
                        "company" : "Apollo Hospitals",
                        "sector"  : "Healthcare"
                        },
    "SBILIFE.NS" : {
                        "company" : "SBI Life Insurance",
                        "sector"  : "Insurance"
                        },
    "HDFCLIFE.NS" : {
                        "company" : "HDFC Life Insurance",
                        "sector"  : "Insurance"
                        },
    "BRITANNIA.NS" : {
                        "company" : "Britannia Industries",
                        "sector"  : "FMCG"
                        },
    "SHRIRAMFIN.NS" : {
                        "company" : "Shriram Finance",
                        "sector"  : "Finance"
                        },
    "INDUSINDBK.NS" : {
                        "company" : "IndusInd Bank",
                        "sector"  : "Banking"
                        },
    "LTM.NS" : {
                        "company" : "LTIMindtree",
                        "sector"  : "IT"
                        },
    "BEL.NS" : {
                        "company" : "BEL",
                        "sector"  : "Defence"
                        },
    "TRENT.NS" : {
                        "company" : "Trent",
                        "sector"  : "Retail"
                        }
}

exsisting_data = pd.read_csv(CLEANED_DATA)
exsisting_df=pd.DataFrame(exsisting_data)

exsisting_df['Date']=pd.to_datetime(exsisting_df['Date'])

last_date=exsisting_df['Date'].max()

start_date=last_date+dt.timedelta(days=1)
end_date=dt.datetime.today()

if start_date>=end_date:
    print("Dataset is upto date")

else:

    new_data=[]

    for t in ticker:

        try:
            updated_stock=yf.download(t,start=start_date,end=end_date)
            updated_stock.columns = updated_stock.columns.get_level_values(0)
            updated_stock.reset_index(inplace=True)

            if updated_stock.empty:
                print(f"No new data available for {t}")
                continue

            if not updated_stock.empty:
                updated_stock['Ticker']=t
                updated_stock['Company']=stock_info[t]['company']
                updated_stock['Sector']=stock_info[t]['sector']

                new_data.append(updated_stock)
        
        except Exception as e:
            print(f"Something went wrong while downloading {t} data : {e}")

    if new_data==[]:
        print("No new data found — market may have been closed")
    else:
        new_df=pd.concat(new_data,ignore_index=True)

        ## Claening new DataFrame

        #fixing column order
        col_ord=['Date', 'Ticker','Company', 'Sector', 'Open', 'High', 'Low', 'Close', 'Volume']

        new_df=new_df[col_ord]

        #fixing dtypes
        new_df['Date']=pd.to_datetime(new_df['Date'],errors="coerce")
        new_df['Volume']=new_df['Volume'].fillna(0)
        new_df['Volume']=new_df['Volume'].astype('Int64')
        print(new_df.columns)
        #handling null values
        price_cols=["Open", "High", "Low", "Close"]
        new_df[price_cols]=new_df[price_cols].ffill()
        new_df.dropna(subset=['Date'],axis=0,inplace=True)

        #creating more required cols

        new_df['year']=new_df['Date'].dt.year
        new_df['month']=new_df['Date'].dt.month
        new_df["day_of_week"]=new_df['Date'].dt.dayofweek

        #updating Dataset

        updated_df=pd.concat([exsisting_df,new_df],ignore_index=True)

        #removing duplicates

        updated_df=updated_df.drop_duplicates(subset=['Date','Ticker'])

        #sorting updated df
        updated_df=updated_df.sort_values(by=['Ticker','Date'])
        updated_df=updated_df.reset_index(drop=True)

        #recalculating daily returns
        updated_df['daily_return']=updated_df.groupby('Ticker')['Close'].pct_change()

        #writing updated dataset
        

        updated_df.to_csv(CLEANED_DATA,index=False)

        print("Successfully updated Dataset !! ")

        generate_indicators()
        print("Successfully updated Indicators !! ")

        print(f"old row length:{len(exsisting_df)}")
        print(f"newly added row length:{len(new_df)}")
        print(f"Total rows now : {len(updated_df)}")

