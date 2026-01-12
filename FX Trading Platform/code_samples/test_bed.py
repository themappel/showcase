from operator import index
import main.api.helperBot as helperBot
import time
import csv
from datetime import datetime
import json
from main.api.oanda_api import OandaAPI
from main.constants import *
import traceback
import pandas as pd
from main.signals import worker_functions
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

from main.indicators import ema
from main.indicators import macd
from main.indicators import rsi 

from main.app.brain import Brain
from main.app.dao.data_man import DataMan
from main.app.boss_man import BossMan
from main.api.backtester_api import BacktesterAPI


class TestBed:
    def __init__(self, ticker: str, timeframe, granularity):
        # init stock history
        self.history = {}

        self.ticker = ticker
        self.worker_functions = worker_functions

        # load test bed template 

        f = open('main/app/test_bed/test_bed.json')
        self.strategy = json.load(f)
        f.close()


        self.macd_diff = 0

        self.signals= {"x": [], "y": [] }
        self.granularity = granularity

        self.oanda = BacktesterAPI([ticker], timeframe,granularity, False)
        self.dataman = DataMan(self.oanda)
        self.brain = Brain()

        self.curr_ticker = None

        self.prune = helperBot.get_property("prune")



    def go(self):

        ticker = self.ticker
        while True:

            # if no history found, request a history and initialize ticker history
            if ticker not in self.history:
                self.history[ticker] = self.dataman.init_ticker(self.granularity, ticker)
                data = self.history[ticker][-1]

            # if history found, just ask for past few tickers, update if necesary
            else:
                data = self.dataman.ask_for_data(self.granularity, ticker)

            # if no new data, skip the rest of the flow
            if not data:
                print("\n  ------------ testbed complete ---------------  \n")

                # plot results
                self.show_graph()
              
                return

            self.history[ticker].append(data)


            #calculate indicators using template
            for function in self.strategy['indicators']:
                h = self.history[ticker] 
                eval(function)

            #calculate signals using brain 
            actions, signal_info = self.brain.run_decisioning_v2(self.history[ticker], ticker,
                                                                     self.strategy['flows'], None)

            #TODO store signals in signal chart

            if actions: 
                self.signals["x"].append(data['time'])
                self.signals['y'].append(data['mid']['c'])

           

    def show_graph(self):


        # convert history list to dataframe
        df = pd.json_normalize(self.history[self.ticker])
        df = df.rename(columns={"time": "t", "mid.o": "o", "mid.h": "h", "mid.l": "l", "mid.c": "c"})
        df = df.drop(["volume", "complete"], axis=1)

        color_count = 0
        color_array = [
            'cyan', 'orange', 'lime', 'magenta', 'yellow', 'lightblue', 'lightgreen',
            'pink', 'gold', 'lightcoral', 'turquoise', 'violet', 'springgreen',
            'deepskyblue', 'salmon', 'orchid', 'greenyellow', 'hotpink', 'lightskyblue',
            'lightseagreen', 'plum', 'khaki', 'lightsalmon', 'palegreen'
        ]


        # shave any negative one values off of the df
        for column in df:
            if len(str(column)) > 1:
                df = df[df[column] != -99999]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.25, 0.25], vertical_spacing=0.01)

        # init graph with just price action data
        data = []
        
        fig.add_trace((go.Candlestick(x=df.t, open=df.o, high=df.h, low=df.l, close=df.c, xaxis='x2')), row=1,
                      col=1)
       
          

        for indicator in self.strategy['graph']:
            fig.add_trace(go.Scatter(x=df.t,
                                        y=df[indicator['column']],
                                        name=indicator['column'],
                                        line=dict(color=color_array[color_count], width=1)
                                        ), row=indicator['subplot'] , col=1)
            color_count += 1
            if color_count >= len(color_array):
                color_count = 0 




        """
        def normalize(values):
            if not values or len(values) == 0:
                return values
            max_abs = max(abs(v) for v in values)
            if max_abs == 0:
                return [0] * len(values)
            return [v / max_abs for v in values]
        """

        fig.update_xaxes(gridcolor='#444444', gridwidth=0.5, zerolinecolor='#444444', rangeslider_visible=False,rangebreaks=[dict(bounds=["sat", "sun"])] )
        fig.update_yaxes(gridcolor='#444444', gridwidth=0.5,  zerolinecolor='#444444', fixedrange=False, autorange=True)
        fig.update_layout(
            plot_bgcolor='#2b2b2b',
            paper_bgcolor='#1e1e1e',
            font=dict(color='white'),  # Make text white for visibility
            xaxis=dict(gridcolor='#444'),  # Lighter grid lines
            yaxis=dict(gridcolor='#444')
        )
        print("fig should be showing now...")
        fig.show()
        return
