import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import xlrd
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def elia_cap_graphs(dfcap, price_vol, aggregated, fromdate, todate, reserve_type, reserve_type2="", reserve_type3=""):
    
    """
    Use the data in the dfcap dataframe to make graphs. Historical data from Elia on the R1, R2 and R3 capacity prices and volumes.
    
    Parameters
    ----------
    dfcap : dataframe
        Dataframe containing the necessary data on R1, R2 and R3 (use the read_elia_cap(filename) method to read in al the data from the Excel)
        
    price_vol : string
        both, volume or price. both will create a plot with 2 windows.
        
    aggregated : boolean
        True will sum al the contracted volumes from the different service types and average the prices. False will show a plot with all different service types from the selected reserve type.
    
    fromdate : string
        In the formatof MM-YYYY, e.g., 06-2016 is June 2016
        
    todate : string
        In the formatof MM-YYYY, e.g., 06-2016 is June 2016
        
    reserve_type : string
        R1, R2, R3 or combinations devided by comma (e.g. R1,R2 or R2,R1,R3)
            
    Returns
    -------
        plots graphs.
    """
    
    dfmask=dfcap.loc[(dfcap["reserve type"] == reserve_type) | (dfcap["reserve type"] == reserve_type2) | (dfcap["reserve type"] == reserve_type3)]
    dfmask=dfmask.loc[(dfmask.index >= fromdate) & (dfmask.index <= todate)]
    dfmask=dfmask.replace(0, np.nan)
    
    if(aggregated == False):
        if ((price_vol == "both") & (reserve_type != "R1")):
            fig, (ax,ax1) = plt.subplots(2,1,sharex=True)
            dfmask.groupby(["reserve type","service type","country","duration"])["total contracted volume in MW"].plot(figsize=(16,6),ax=ax,kind="line", style='.-',grid=True)
            dfmask.groupby(["reserve type","service type","country","duration"])["average price in euro/MW/h"].plot(figsize=(16,6),legend=True, ax=ax1,kind="line", style='.-',grid=True)
            ax1.set_xlabel("start of delivery period")
            ax1.set_ylabel("average price in euro/MW/h")
            ax.set_ylabel("contracted volumes in MW")
            fig.suptitle("capacity average prices and contracted volumes of reserve type(s) "  + reserve_type + " " +  reserve_type2 + " " + reserve_type3)

        if ((price_vol == "both") & (reserve_type == "R1")):
            fig, (ax,ax1) = plt.subplots(2,1,sharex=True)
            dfmask.groupby(["reserve type","service type","country"])["total contracted volume in MW"].plot(figsize=(16,6),ax=ax,kind="line", style='.-',grid=True)
            dfmask.groupby(["reserve type","service type","country"])["average price in euro/MW/h"].plot(figsize=(16,6),legend=True, ax=ax1,kind="line", style='.-',grid=True)
            ax1.set_xlabel("start of delivery period")
            ax1.set_ylabel("average price in euro/MW/h")
            ax.set_ylabel("contracted volumes in MW")
            fig.suptitle("capacity average prices and contracted volumes of reserve type(s) " + reserve_type + " " +  reserve_type2 + " " + reserve_type3)

        if price_vol == "price":
            fig, ax1 = plt.subplots(1,1)
            dfmask.groupby(["reserve type","service type","country","duration"])["average price in euro/MW/h"].plot(figsize=(16,6),legend=True, ax=ax1,kind="line", style='.-',grid=True)
            ax1.set_xlabel("start of delivery period")
            ax1.set_ylabel("average price in euro/MW/h")
            fig.suptitle("capacity average prices of reserve type(s) "  + reserve_type + " " +  reserve_type2 + " " + reserve_type3)

        if price_vol == "volume":  
            fig, ax = plt.subplots(1,1)
            dfmask.groupby(["reserve type","service type","country","duration"])["total contracted volume in MW"].plot(figsize=(16,6),ax=ax,kind="line", style='.-',grid=True,legend=True)
            ax.set_xlabel("start of delivery period")
            ax.set_ylabel("contracted volumes in MW")
            fig.suptitle("contracted volumes of reserve type(s) "  + reserve_type + " " +  reserve_type2 + " " + reserve_type3)
            
    if(aggregated == True):
        if price_vol == "both":
            dfvol=dfmask.groupby(["reserve type","duration","delivery period"])["total contracted volume in MW"].sum()
            dfvol=dfvol.to_frame()
            dfvol=dfvol.reset_index()
            dfvol=dfvol.set_index(["delivery period"])
            dfvol=dfvol.sort_index(ascending=False);
            dfprice=dfmask.groupby(["reserve type","duration","delivery period"])["average price in euro/MW/h"].mean()
            dfprice=dfprice.to_frame()
            dfprice=dfprice.reset_index()
            dfprice=dfprice.set_index(["delivery period"])
            dfprice=dfprice.sort_index(ascending=False);
            fig, (ax,ax1) = plt.subplots(2,1,sharex=True)
            dfvol.groupby(["reserve type","duration"])["total contracted volume in MW"].plot(figsize=(16,6),ax=ax,kind="line", style='.-',grid=True)
            dfprice.groupby(["reserve type","duration"])["average price in euro/MW/h"].plot(figsize=(16,6),legend=True, ax=ax1,kind="line", style='.-',grid=True)
            ax1.set_xlabel("start of delivery period")
            ax1.set_ylabel("average price in euro/MW/h")
            ax.set_ylabel("contracted volumes in MW")
            fig.suptitle("capacity average prices and contracted volumes, aggregated of all service types of reserve type(s) " + reserve_type + " " +  reserve_type2 + " " + reserve_type3)
            
        if price_vol == "price":
            dfprice=dfmask.groupby(["reserve type","duration","delivery period"])["average price in euro/MW/h"].mean()
            dfprice=dfprice.to_frame()
            dfprice=dfprice.reset_index()
            dfprice=dfprice.set_index(["delivery period"])
            dfprice=dfprice.sort_index(ascending=False);
            fig, ax1 = plt.subplots(1,1)
            dfprice.groupby(["reserve type","duration"])["average price in euro/MW/h"].plot(figsize=(16,6),legend=True, ax=ax1,kind="line", style='.-',grid=True)
            ax1.set_xlabel("start of delivery period")
            ax1.set_ylabel("average price in euro/MW/h")
            fig.suptitle("capacity average prices, aggregated of all service types of reserve type(s) " + reserve_type + " " +  reserve_type2 + " " + reserve_type3)
            
        if price_vol == "volume":
            dfvol=dfmask.groupby(["reserve type","duration","delivery period"])["total contracted volume in MW"].sum()
            dfvol=dfvol.to_frame()
            dfvol=dfvol.reset_index()
            dfvol=dfvol.set_index(["delivery period"])
            dfvol=dfvol.sort_index(ascending=False);
            fig, ax= plt.subplots(1,1)
            dfvol.groupby(["reserve type","duration"])["total contracted volume in MW"].plot(figsize=(16,6),ax=ax,kind="line", style='.-',grid=True,legend=True)
            ax.set_xlabel("start of delivery period")
            ax.set_ylabel("contracted volumes in MW")
            fig.suptitle("contracted volumes, aggregated of all service types of reserve type(s) " + reserve_type + " " +  reserve_type2 + " " + reserve_type3)
            


def elia_activatedreserves_graphs(dfpricevol, price_vol, fromdate, todate, producttypes):
    
    """
    Use the data in the dfpricevol dataframe to make graphs. Historical data from Elia on the activated reserves (prices and volumes).
    
    Parameters
    ----------
    dfpricevol : dataframe
        Dataframe containing the necessary elia data. use method fetch_combine_elia_activated_energy("01-2012","03-2018","valid")
        
    price_vol : string
        both, volume or price. both will create a plot with 2 windows.
        
    fromdate : string
        In the formatof MM-YYYY, e.g., 06-2016 is June 2016
        
    todate : string
        In the formatof MM-YYYY, e.g., 06-2016 is June 2016
        
    producttypes : list or string
        list with all the to plot products. choose from: Bids+, Bids-, ICH, IGCC-, IGCC+, MDP, MIP, NRV, R2+, R2-, R3 flex, R3 std, R3+, R3-, SR, inter TSO import.
        or "all"
            
    Returns
    -------
        plots graphs.
    """
    
    if (producttypes == "all"):
        producttypes = ["Bids+", "Bids-", "ICH", "IGCC-", "IGCC+", "R2+", "R2-","R3 flex","R3 std", "R3+","R3-","SR","NRV"]
        
    volumeslist = [s + " in MW" for s in producttypes]
    pricelist = [s + " in euro/MWh" for s in producttypes]
    dfmask=dfpricevol.loc[(dfpricevol.index >= fromdate) & (dfpricevol.index <= todate)]
    dfmask=dfmask.replace(0, np.nan)
    
    if (price_vol == "both"):
        fig, (ax,ax1) = plt.subplots(2,1,sharex=True)
        dfmask[pricelist].plot(ax=ax, grid=True,style=".-")
        dfmask[volumeslist].plot(ax=ax1,grid=True, legend = True,style=".-")
        ax1.set_xlabel("delivery period")
        ax.set_ylabel("activated average energy price in euro/MWh")
        ax1.set_ylabel("activated volumes in MW")
    
    if (price_vol == "volume"):
        fig, ax1 = plt.subplots(1,1)
        dfmask[volumeslist].plot(ax=ax1,grid=True, legend = True,style=".-")
        ax1.set_xlabel("delivery period")
        ax1.set_ylabel("activated volumes in MW")
        
    if (price_vol == "price"):
        fig, ax = plt.subplots(1,1)
        dfmask[pricelist].plot(ax=ax, grid=True,style=".-")
        ax.set_xlabel("delivery period")
        ax.set_ylabel("activated average energy price in euro/MWh")
        
        
        
def negativePOS (dfimbalance, fromdate, todate, period):

    """
    Calculate the number of quarters the POS is negative and the average price in euro/MWh.
    
    Data comes from the Elia website in xls format.
    Quarter hourly data, but the time is transformed to pandas datetime. Timestamp is begining of quarter.
    
    Parameters
    ----------
    dfimbalance : dataframe
        name of the dataframe. 
    fromdate : string
        date in the format of 'year-month-day', e.g., '2015-06-15' is 15th of June 2015
    todate : string
        date in the format of 'year-month-day', e.g., '2016-07-02' is 2nd of July 2016
    period : string
        define how to aggregate data: weekly, monthly, yearly ('W', 'M', 'Y')
        
    Returns
    -------
    plot
    """

    fromdatepd=pd.to_datetime(fromdate,format="%Y-%m-%d")
    todatepd=pd.to_datetime(todate,format="%Y-%m-%d")
    
    #define the number of quarters the POS is negative
    dfmaskimbalance=dfimbalance.loc[(dfimbalance.index >= fromdatepd) & (dfimbalance.index < todatepd)]
    dfmaskimbalance[dfmaskimbalance >= 0] = np.nan
    posneg=dfmaskimbalance.resample(period)["POS in euro/MWh"].count()
    pospriceneg=dfmaskimbalance.resample(period)["POS in euro/MWh"].mean()
    #plot POS imbalance prices
    if period != "Y":
        fig, ax = plt.subplots(sharex=True)
        posneg.plot(figsize=(16,6), ax=ax,kind="line", style='.-',grid=True,sharex=True)
        pospriceneg.plot(figsize=(16,6), ax=ax,kind="line", style='.-',grid=True,sharex=True)
        #ax.set_ylabel("# of quarters")
        fig.legend(labels=("# of quarters","Average price in euro/MWh"))
        
    if period == "Y":
        fig, (ax,ax1) = plt.subplots(2,1)
        posneg.plot(figsize=(16,6),ax=ax,kind="line", style='.-',grid=True)
        pospriceneg.plot(figsize=(16,6),ax=ax1,kind="line", style='.-',grid=True,color="orange")
        ax.set_ylabel("# of quarters")
        ax1.set_ylabel("price in euro/MWh")
        
    if period == "D":
        fig.suptitle("Negative POS - Daily")
    if period == "W":
        fig.suptitle("Negative POS - Weekly")
    if period == "M":
        fig.suptitle("Negative POS - Monthly")
    if period == "Y":
        fig.suptitle("Negative POS - Yearly")
        
        
def durationImbalancePrices(dfimbalance, fromdate, todate, price, incl_zero):  
    
    """
    Plot the load duration curve of the POS imbalance price. 
    
    Data comes from the Elia website in xls format.
    Quarter hourly data, but the time is transformed to pandas datetime. Timestamp is begining of quarter.
    
    Parameters
    ----------
    dfimbalance : dataframe
        name of the dataframe. 
    fromdate : string
        date in the format of 'year-month-day', e.g., '2015-06-15' is 15th of June 2015
    todate : string
        date in the format of 'year-month-day', e.g., '2016-07-02' is 2nd of July 2016
    price : string
        define what is plotted: "NEG" will only plot the negative prices, "POS" will only plot the positive prices, "BOTH" will plot the total
    incl_zero : boolean
        True: to inlude when the price is zero, False: to exclude when the price is zero
    
    Returns
    -------
    plot
    """
    #fromdatepd=pd.to_datetime(fromdate,format="%Y-%m-%d")
    #todatepd=pd.to_datetime(todate,format="%Y-%m-%d")
    dfmaskimbalance=dfimbalance.loc[(dfimbalance.index >= fromdate) & (dfimbalance.index < todate)]

    calcneg = dfmaskimbalance.copy()
    calcneg[calcneg >= 0] = np.nan
    calcneg=calcneg["POS in euro/MWh"]
    negtime = (calcneg.count()/(dfmaskimbalance["POS in euro/MWh"].count()))*100

    if (price == "NEG") & (incl_zero == True):
        dfmaskimbalance[dfmaskimbalance > 0.0] = np.nan
    if (price == "NEG") & (incl_zero == False):
        dfmaskimbalance[dfmaskimbalance >= 0.0] = np.nan
    if (price == "POS") & (incl_zero == True):
        dfmaskimbalance[dfmaskimbalance < 0.0] = np.nan
    if (price == "POS") & (incl_zero == False):
        dfmaskimbalance[dfmaskimbalance <= 0.0] = np.nan

    POS=dfmaskimbalance["POS in euro/MWh"]
    POS=POS.sort_values()
    POS=POS.reset_index()
    POS=POS.drop("Timestamp",axis=1)

    fig, ax = plt.subplots()
    POS.plot(figsize=(16,6), ax=ax,kind="line", style='-',grid=True)
    ax.set_xlabel("# of quarters")
    ax.set_ylabel("price in euro/MWh")

    fig.suptitle("Duration curve POS \n from " + fromdate + " to " + todate + "\n negative for " + "{0:.2f}".format(float(negtime)) + " % of the total time")
    if (price == "NEG") & (incl_zero == True):
        fig.suptitle("Duration curve negative POS including zero \n from " + fromdate + " to " + todate + "\n negative for " + "{0:.2f}".format(float(negtime)) + " % of the total time")
    if (price == "NEG") & (incl_zero == False):
        fig.suptitle("Duration curve negative POS excluding zero \n from " + fromdate + " to " + todate + "\n negative for " + "{0:.2f}".format(float(negtime)) + " % of the total time")
    if (price == "POS") & (incl_zero == True):
        fig.suptitle("Duration curve positive POS including zero \n from " + fromdate + " to " + todate + "\n negative for " + "{0:.2f}".format(float(negtime)) + " % of the total time")
    if (price == "POS") & (incl_zero == False):
        fig.suptitle("Duration curve positive POS excluding zero \n from " + fromdate + " to " + todate + "\n negative for " + "{0:.2f}".format(float(negtime)) + " % of the total time")
    
            
        
