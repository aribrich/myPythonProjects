'''
python gui test

'''

import os
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pandas as pd
import pandas_datareader.data as pdr
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from lxml import html
import requests
from time import sleep
import json
import argparse
import random
import yfinance as yf
import glob


matplotlib.use("TkAgg")

START = dt.date(2000,1,1)
END = dt.date.today()
LARGE_FONT = ("Verdana", 12)

def convert_day_of_week(date, past=True):
    '''
    inputs a date, and returns that date converted into a weekday.
    Adds a day if Sunday, Subtracts a day if Saturday, does nothing other days.
    If "past"=True, Sunday will be converted to Friday as well.
    '''
    weekday_index = date.weekday()
    if weekday_index == 5:
        return date - relativedelta(days=1)
    if weekday_index == 6:
        if past == True:
            return date - relativedelta(days=2)
        else:
            return date + relativedelta(days=1)
    else:
        return date


# Data
class Data_Management:
    def __init__(self, *args):
        # self.fpath = "./stock_dfs/{}.csv".format(ticker)
        self.saved_ticker_list = [os.path.splitext(f)[0] for f in os.listdir("stock_dfs")]
        # print(self.saved_ticker_list)
        self.active_ticker_list = self.saved_ticker_list
        self.all_ticker_data = {}
        self.headers = []
        
        for arg in args:
            if arg not in self.active_ticker_list:
                self.active_ticker_list.append(arg)
        for item in self.active_ticker_list:
            ticker_df = self.get_data(item)
            self.all_ticker_data[item] = ticker_df
        # self.join_close_data()

    def add_to_ticker_list(self, ticker):
        if ticker not in self.active_ticker_list:
            self.active_ticker_list.append(ticker)
        else:
            pass

    def use_pandas_lib(self, ticker):
        try:
            return pdr.DataReader(ticker, "yahoo", START, END)
        except:
            Exception
        
    # https://www.scrapehero.com/scrape-nasdaq-stock-market-data/    
    def scrape_nasdaq_data(self, ticker): 
        key_stock_dict = {}
        header = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "Connection":"keep-alive",
        "Host":"www.nasdaq.com",
        "Referer":"http://www.nasdaq.com",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
        }

        url = "http://www.nasdaq.com/symbol/{}".format(ticker)
        # Try connecting again *times
        for retry in range(5):
            try:
                response = requests.get(url, headers=header, verify=False)
                print("Parsing {}".format(url))

                # add random delay
                sleep(random.randint(1,3))

                parser = html.fromstring(response.text)
                xpath_head = "//div[@id='qwidget_pageheader']//h1//text()"
                xpath_key_stock_table = '//div[@class="row overview-results relativeP"]//div[contains(@class,"table-table")]/div'
                xpath_open_price = '//b[contains(text(),"Open Price:")]/following-sibling::span/text()'
                xpath_open_date = '//b[contains(text(),"Open Date:")]/following-sibling::span/text()'
                xpath_close_price = '//b[contains(text(),"Close Price:")]/following-sibling::span/text()'
                xpath_close_date = '//b[contains(text(),"Close Date:")]/following-sibling::span/text()'
                xpath_key = './/div[@class="table-cell"]/b/text()'
                xpath_value = './/div[@class="table-cell"]/text()'

                raw_name = parser.xpath(xpath_head)
                key_stock_table = parser.xpath(xpath_key_stock_table)
                raw_open_price = parser.xpath(xpath_open_price)
                raw_open_date = parser.xpath(xpath_open_date)
                raw_close_price = parser.xpath(xpath_close_price)
                raw_close_date = parser.xpath(xpath_close_date)

                company_name = raw_name[0].replace("Common Stock Quote & Summary Data", "").strip() if raw_name else ''
                open_price = raw_open_price[0].strip() if raw_open_price else None
                open_date = raw_open_date[0].strip() if raw_open_date else None
                close_price = raw_close_price[0].strip() if raw_close_price else None
                close_date = raw_close_date[0].strip() if raw_close_date else None

                # get and clean stock data
                for i in key_stock_table:
                    key = i.xpath(xpath_key)
                    value = i.xpath(xpath_value)
                    key = ''.join(key).strip()
                    value = ' '.join(''.join(value).split())
                    key_stock_dict[key] = value

                nasdaq_data = {
                    "company_name":company_name,
                    "ticker":ticker,
                    "url":url,
                    "open_price":open_price,
                    "open_date":open_date,
                    "close_price":close_price,
                    "close_date":close_date,
                    "key_stock_data":key_stock_dict
                }
                return nasdaq_data
                print("done parsing!")

            except Exception as e:
                print("Failed to proces the request, Exception:{}".format(e))

        ''' 
        Use in "main" for command line execution
        #!/usr/bin/env python --> program topper
        # -*- coding: utf-8 -*- --> program topper

        argparser = argparse.ArgumentParser()
        argparser.add_argument('ticker',help = 'Company stock symbol')
        args = argparser.parse_args()
        ticker = args.ticker
        print("Fetching data for %s"%(ticker))
        scraped_data = parse_finance_page(ticker)
        print("Writing scraped data to output file")

        with open('%s-summary.json'%(ticker),'w') as fp:
            json.dump(scraped_data,fp,indent = 4,ensure_ascii=False)
        '''

    def scrape_yahoo_data(self):
        pass

    def use_yahoo_api(self, ticker):
        '''
        https://aroussi.com/post/python-yahoo-finance
        Actions:
        ticker_name.info
        ticker_name.history --> period, interval, start, end, ...
        ticker_name.actions
        ticker_name.dividends
        ticker_name.splits
        data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30", group_by="ticker")
        '''
        
        # ticker_dict = {}
        # ticker_dict[ticker] = yf.Ticker(ticker)
        return yf.Ticker(ticker)

    def save_all_data(self, all_ticker_dict):
        # TODO: Add code to skip set_data if currently saved data is up to date.
        for ticker, ticker_data in all_ticker_dict.items():
            fpath = "./stock_dfs/{}.csv".format(ticker)
            if not os.path.exists('./stock_dfs'):
                os.makedirs('./stock_dfs')
            with open(fpath, 'a', newline='') as f:
                ticker_data.to_csv(f, header=f.tell()==0)

    def save_ticker_data(self, ticker, ticker_df):
        fpath = "./stock_dfs/{}.csv".format(ticker)
        if not os.path.exists('./stock_dfs'):
            os.makedirs('./stock_dfs')
        with open(fpath, 'a', newline='') as f:
            ticker_df.to_csv(f, header=f.tell()==0)


    def get_data(self, ticker, daq="yf"):
        # TODO: Add code to read web data first if saved data is not up to date
        # TODO: Add code to check connectivity and consider how to get data

        # self.pdlib = use_pandas_lib()
        fpath = "./stock_dfs/{}.csv".format(ticker)

        up_to_date_flag = True
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            df.set_index("Date", inplace=True)
            # print(df)
            fend_date = df.index[-1]
            fend_date = dt.datetime.strptime(fend_date, "%Y-%m-%d").date()
            if (fend_date < convert_day_of_week(END)):
                # if connects to internet:
                up_to_date_flag = False
                return self.read_web_data(ticker)
            else:
                up_to_date_flag = True
                self.headers = df.columns
                return df
        else:
            # if connects to internet:
            return self.read_web_data(ticker)
        
    def read_web_data(self, ticker, daq="yf"):
        if daq.lower() == "yf":            
            yf_data = self.use_yahoo_api(ticker)
            ticker_hist = yf_data.history(period="max")
            ticker_hist.reset_index(inplace=True)
            ticker_hist.set_index("Date", inplace=True)
            self.headers = ticker_hist.columns
            return ticker_hist
        elif daq.lower() == "yahoo":
            pass
        elif daq.lower() == "google":
            pass
        else:
            print("please select valid data acquisition method")
            
    def join_close_data(self, save=False):
        close_df = pd.DataFrame()
        for ticker, data in self.all_ticker_data.items():
            # fpath = "./stock_dfs/{}.csv".format(ticker)
            # df = pd.read_csv(fpath)
            # df.set_index("Date", inplace=True)
            close_df[ticker] = data['Close']
        if save == True:
            pass
            # df.to_csv('Combined_Close_Data.csv')
        return close_df


class Portfolio(Data_Management):
    def __init__(self, cash, stocks, bonds):
        '''
        # Stocks:
        # [ticker, value, date valued (cost basis)]
        '''
        # super(Portfolio, self).__init__()
        self.stocks = stocks
        self.bonds = bonds

        # joined_close_data = Data_Management.join_close_data()

        # for ticker in stocks.headers:


    def define_pcnt(self):
        pass


class Analysis:
    def __init__(self, ticker, start=START, end=END, *args, **kwargs):
        # super(Analysis,self).__init__()
        # self.all_ticker_data
        self.ticker = ticker
        self.start = start
        self.end = end
        self.ticker_data = dm.all_ticker_data[self.ticker]
        self.data = self.ticker_data[self.start:self.end]

    def dividends(self, start, end, dividend_list):
        return sum(dividend_list)

    def stats(self):
        ans = self.data.describe()
        print(ans)
        return ans

    def moving_avg(self, bin):
        ans = pd.DataFrame()
        for col in self.data:
            temp_df = self.data[col]
            ans[col] = temp_df.rolling(window=bin).mean()
        print(ans)
        return ans

    def internal_plotting(self, data):
        fig = Figure(figsize=(5,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(data)
        chart = FigureCanvasTkAgg(fig, self)
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def external_plotting(self, data):
        fig, ax = plt.subplot(111)


    def calculate_roi(self, pdl, end=END, days=None, weeks=None, months=None, years=None):
        '''
        Don't ender more than one time period
        '''
        start = pdl.index[-1]
        if days is not None:
            start = end - relativedelta(days=days)
        elif weeks is not None:
            start = end - relativedelta(weeks=weeks)
        elif months is not None:
            start = end - relativedelta(months=months)
        elif years is not None:
            start = end - relativedelta(years=years)
        start = convert_day_of_week(start)
        if end.weekday() == 6:
            end = end - relativedelta(days=2)
        elif end.weekday() == 5:
            end = end - relativedelta(days=1)

        return round(100 * (pdl[end] - pdl[start]) / pdl[end], 1)


# GUI
class EmbeddedPlot(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.plt_lst = pd.DataFrame()

        self.row = len(self.plt_lst.columns)
        self.col = 1
        self.num = 1

        self.fig = Figure(figsize=(5,5), dpi=100)
        ax1 = self.fig.add_subplot(211)
        ax1.plot(analysis.ticker_data["High"])
        ax2 = self.fig.add_subplot(212)
        ax2.plot(analysis.ticker_data["Low"])
        chart = FigureCanvasTkAgg(self.fig, self)
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(chart, self)
        toolbar.update()
        chart.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=True)


        self.subplot_num = 111
    def add_more_plots(self):
        axn = []
        col = self.subplot_num // 100
        row = (self.subplot_num % 100) // 10 
        num = self.subplot_num % 10
        temp_num = (col * 100) + (row * 10) + 1
        iterations = col * row
        # self.fig.
        for i in range(iterations):
            axn = self.fig.add_subplot(col, row, i+1)
            # temp_num += 1

class NavBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.singleStockBtn = tk.Button(self, text = "One Stock")
        self.multiStickBtn = tk.Button(self, text="Multiple Stocks")
        self.newsBtn = tk.Button(self, text="News")
        self.select_mode = "multiple"
        self.stock_selector = tk.Listbox(self, selectmode=self.select_mode)
        for ticker in dm.active_ticker_list:
            self.stock_selector.insert(tk.END, ticker)
        self.stockScroll = tk.Scrollbar(self)
        self.add_stock_ent = tk.Entry(self, width=10, font=LARGE_FONT)
        self.edit_prt_btn = tk.Button(self, text="Edit Portfolio", state=tk.DISABLED, command=self.edit_portfolio)
        self.lbl = "Stock List"
        self.list_lbl = tk.Label(self, text=self.lbl)
        self.add_stock_button = tk.Button(self, text="Add", command=self.add_stock_to_list)
        self.remove_stock_button = tk.Button(self, text="Remove", command=self.remove_stock_from_list)
        
        self.add_stock_ent.bind('<Return>', self.add_stock_to_list)

        self.singleStockBtn.grid(row=0, column=0, columnspan=2, sticky="nwe")
        self.multiStickBtn.grid(row=1, column=0, columnspan=2, sticky="nwe")
        self.newsBtn.grid(row=2, column=0, columnspan=2, sticky="nwe")
        self.add_stock_ent.grid(row=3, column=0, sticky="nswe")
        self.add_stock_button.grid(row=3, column=1, sticky="e")
        self.remove_stock_button.grid(row=4, column=0, columnspan=2, sticky="nwe")
        self.edit_prt_btn.grid(row=5, column=0, columnspan=2, sticky="nwe")
        self.list_lbl.grid(row=6, column=0, columnspan=2, sticky="nwe")
        self.stock_selector.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.stockScroll.grid(row=7, column=1, sticky="nse")

        self.stock_selector.config(yscrollcommand=self.stockScroll.set)
        self.stockScroll.config(command=self.stock_selector.yview)
    '''
        lbl_portforlio = tk.Label(self, text="Portfolio")
        lbl_portforlio.grid(row=6, column=1, columnspan=2, sticky="nwe")
        prt_selector = tk.Listbox(self)
        prt_selector.grid(row)
    '''    

    def add_stock_to_list(self, event=None):
        entered_stock = self.add_stock_ent.get()
        if entered_stock != "":
            dm.active_ticker_list.append(entered_stock)
            df = dm.get_data(entered_stock)
            dm.save_ticker_data(entered_stock, df)
            dm.all_ticker_data[entered_stock] = df
            self.stock_selector.insert(tk.END, entered_stock)
            self.add_stock_ent.delete(0, tk.END)

    def remove_stock_from_list(self):
        selection = self.stock_selector.curselection()
        if not selection:
            pass
        else:
            self.stock_selector.delete(selection[0])
            dm.active_ticker_list.remove(selection[0])
            self.remove_stock_from_list()        

    def edit_portfolio(self):
        pass

    def show_nav_selection(self):
        pass

class singleStockFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        '''
        self.all_radio_frames = {}
        for header in dm.headers:
            frame = ScrollFrame(self, titleText=header)
            self.all_radio_frames[header] = frame
            frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")
        '''

        '''
        chk_frame = tk.Frame(self, bg="red")
        chk_frame.grid(row=0, column=0, padx=5, pady=5, sticky="NSW")
        self.var = tk.StringVar()
        self.var.set(dm.headers[0])
        for header in dm.headers:
            rad_view = tk.Radiobutton(chk_frame, text=header, variable=self.var, value=header, command=self.show_radio_select)
            # rad_view.grid(row=i, column=0, sticky="N")
            rad_view.pack(side=tk.TOP, anchor='w')
        self.show_radio_select()
        '''
        
        analysis_lst = ["Dividends", "ROI", "Moving Avg (Std)"]
        analysis_box = tk.Listbox(self, selectmode="multiple")
        for item in analysis_lst:
            analysis_box.insert(tk.END, item)
        analysis_box.grid(row=0, column=0)


        self.range_lbl = tk.Label(self, text="Range")
        self.min_lbl = tk.Label(self, text="Min")
        self.min_date = tk.Entry(self, text="min")
        self.to_txt = tk.Label(self, text=" to ")
        self.max_lbl = tk.Label(self, text="Max")
        self.max_date = tk.Entry(self, text="max")


        # growth = analysis.calculate_roi()
        # self.pcnt_growth_lbl = tk.Label(self, text=growth)
        # dividends = analysis.dividends()
        # self.div_lbl = tk.Label(self, text=dividends)


        plot_frame = EmbeddedPlot(self)
        plot_frame.grid(row=0, column=1, rowspan=1, sticky="NSEW")

        '''
    def show_radio_select(self):
        # print(self.var.get())
        frame = self.all_radio_frames[self.var.get()]
        frame.tkraise()
        '''


class ScrollFrame(tk.Frame):
    def __init__(self, parent, titleText):
        tk.Frame.__init__(self, parent)

        self.titleText = titleText

        title = tk.Label(self, text=self.titleText)
        data = tk.Listbox(self, width=10)
        scroll = tk.Scrollbar(self)

        title.pack(side=tk.TOP)
        data.pack(side=tk.LEFT, fill=tk.Y)
        self.fill_data(data, titleText)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        data.config(yscrollcommand=scroll.set)
        scroll.config(command=data.yview)

    def fill_data(self, data, title):
        for num in analysis.ticker_data[title]:
            data.insert(tk.END, round(num,2))

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="green")

        navBar = NavBar(self)
        navBar.pack(side=tk.LEFT, fill=tk.Y, anchor="nw")
        # navBar.grid(row=0, column=0, pady=5, padx=5, sticky="nsw")

        single_stock_frame = singleStockFrame(self)
        single_stock_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # self.rowconfigure(0, minsize=300, weight=1)
        # self.columnconfigure([0,1], minsize=100, weight=1)


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, minsize=400, weight=1)
        container.grid_columnconfigure(0, minsize=500, weight=1)

        self.frames = {}

        frame = StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


if __name__ == "__main__":

    # hand_build_tickers = ["GOOG", "AAPL", "BYND"]
    ticker = "GOOG"
    Active_Item = ticker
    # DM = Data_Management(ticker)
    dm = Data_Management()
    analysis = Analysis(Active_Item)
    
    app = MainApp()
    app.mainloop()


    # A.plotting

    # fig, (ax1, ax2) = plt.subplot(2,1)
    # high = dat["High"]
    # Low = dat["Low"]
    # high.plot()
    # Low.plot()
    # plt.show()

    # fig, ax = plt.subplots()
    # ax.plot(dat["High"])
    # fig