#from Elia_R2plus_activation import R2plusSingleOptimum, R2plusMultiTimeOptimum

#functions:
#R2plusSingleOptimum
#R2plusMultiTimeOptimum

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import xlrd
import math
from decimal import *
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import six

def R2plusSingleOptimum(fromdate,todate,bidvolume,dataframeAct,dataframeCap,variable,plotting):
    """
    Create dataframe with:
    - the bidprice in euro/MWh
    - the return for activation in euro for the selected period
    - the return for contracted capacity (based on weighted averages) and activation in euro for the selected period
    - the activation time in percentage of the selected period
    - the average activated volume of the bidvolume  
    
    Variable steps are used, based on the real marginal prices occuring during the selected period.
    The data includes both the "fromdate" and "todate".
    
    Parameters
    ----------
    fromdate : string
        date in the format of 'YYYY-MM-DD', e.g., '2017-10-22' is the 22th of October 2017
    todate : string
        date in the format of 'YYYY-MM-DD', e.g., '2017-10-22' is the 22th of October 2017
    bidvolume : int
        the volume of power for which is bidded (in MW)
    dataframeAct : dataframe
        dataframe made by executing the "fetch_combine_elia_activated_energy" method. Contains all the prices and volumes of the activated ancillary services.
    dataframeCap : dataframe
        dataframe containing the averaged prices for the standby remuneration for the ancillary services.
    variable : boolean
        select how to perform the calculations, "True" will use the actual bidprices within the period, "False" will use the min and max and use a granularity of 0.1 euro/MWh
    plotting : boolean
        if you which to see the data in a plot, use True.
        
    returns
    -------
    DataFrame
        Processed dataframe.
    plot
        if plotting is selected
    """
    df = dataframeAct
    df1 = dataframeCap
    df.fillna(0,inplace=True)
    
    df1=df1.loc[(df1["reserve type"] == "R2") & (df1["service type"] == "Upward")].resample("15T").mean().ffill()
    df1=df1.drop("forecasted average price in euro/MW/h",axis=1)
    df = df[["R2+ in euro/MWh","R2+ in MW"]]
    df = df.join(df1,how="outer")#was inner
    df=df.rename(columns={"R2+ in euro/MWh":"marginal activation price in euro/MWh","R2+ in MW":"activated volume in MW"})
    mask=df.loc[(df.index >= pd.to_datetime(fromdate)) & (df.index <= (pd.to_datetime(todate)+relativedelta(days=1)-relativedelta(seconds=1)))]
    dfR2plus= pd.DataFrame(columns=["bidprice in euro/MWh","number of quarters","timeActiv","volumeActiv","returnAct"])
    looprange = sorted(mask["marginal activation price in euro/MWh"].unique()[np.logical_not(np.isnan(mask["marginal activation price in euro/MWh"].unique()))])
    looprange = [float(Decimal("%.2f" % e)) for e in looprange]
    
    if (variable==True):
        
        for i in looprange:
            mask['euro/MWh'] = mask.apply(lambda row: (i
                                            if i<= row["marginal activation price in euro/MWh"]
                                            else 0),axis=1)
            mask['volumeActiv'] = mask.apply((lambda row: (row["activated volume in MW"]/row["total contracted volume in MW"])
                                            if i<= row["marginal activation price in euro/MWh"]
                                            else 0),axis=1)
            mask['timeActiv'] = mask.apply((lambda row: 1
                                            if row["activated volume in MW"]>0
                                            else 0),axis=1)
            
            
            dfR2plus=dfR2plus.append({"bidprice in euro/MWh":i,
                                      "number of quarters":(mask[mask["marginal activation price in euro/MWh"]>=i]["marginal activation price in euro/MWh"].count()),
                                      "timeActiv":(mask.apply(lambda row: (row['timeActiv']),axis=1).mean()),
                                      "volumeActiv":(mask.apply(lambda row: (row['volumeActiv']),axis=1).mean()),
                                      "returnAct":(mask.apply(lambda row: ((((bidvolume/row["total contracted volume in MW"])*(row["activated volume in MW"]/4))*row["euro/MWh"])),axis=1).sum()),
                                      "returnCap":(mask.apply(lambda row:(row["average price in euro/MW/h"]*bidvolume/4),axis=1).sum())},
                                     ignore_index=True)
        
    else:
        
        startR2plus = math.floor(mask["marginal activation price in euro/MWh"].min())-1
        stopR2plus = math.ceil(mask["marginal activation price in euro/MWh"].max())
        
        for i in range (startR2plus*10,stopR2plus*10):
            mask['euro/MWh'] = mask.apply(lambda row: (i/10
                                            if i/10<= row["marginal activation price in euro/MWh"]
                                            else 0),axis=1)
            mask['volumeActiv'] = mask.apply((lambda row: (row["activated volume in MW"]/row["total contracted volume in MW"])
                                            if i/10<= row["marginal activation price in euro/MWh"]
                                            else 0),axis=1)
            
            
            dfR2plus=dfR2plus.append({"bidprice in euro/MWh":i/10,
                                      "number of quarters":(mask[mask["marginal activation price in euro/MWh"]>=i/10]["marginal activation price in euro/MWh"].count()),
                                      "timeActiv":(mask[mask["marginal activation price in euro/MWh"]>=i/10]["marginal activation price in euro/MWh"].count()/len(mask)),
                                      "volumeActiv":(mask.apply(lambda row: (row['volumeActiv']),axis=1).mean()),
                                      "returnAct":(mask.apply(lambda row: ((((bidvolume/row["total contracted volume in MW"])*(row["activated volume in MW"]/4))*row["euro/MWh"])),axis=1).sum()),
                                      "returnCap":(mask.apply(lambda row:(row["average price in euro/MW/h"]*bidvolume/4),axis=1).sum())},
                                     ignore_index=True)
        
    
    dfR2plus.set_index("bidprice in euro/MWh",inplace=True)

    if (plotting==True):
        fig,(ax,ax1) = plt.subplots(2,1,sharex=True)
        (dfR2plus["returnAct"]/1000).plot(ax=ax, grid=True, color="red")
        ((dfR2plus["returnCap"]+dfR2plus["returnAct"])/1000).plot(ax=ax, grid=True,color="green")
        (dfR2plus["volumeActiv"]*100).plot(ax=ax1, grid=True)
        (dfR2plus["timeActiv"]*100).plot(ax=ax1, grid=True)

        ax.set_xlabel("Marginal activation prices in euro/MWh")
        ax1.set_xlabel("Marginal activation prices in euro/MWh")
        ax.set_ylabel("Remuneration for selected period \n in thousands of euro")
        ax1.set_ylabel("Activation percentage")
        fig.suptitle("Elia R2+ product optimal bidprice\n averaged for the period " + fromdate + " to " + todate +"\nfor a volume of " + str(bidvolume) + "MW")

        ax.plot(dfR2plus["returnAct"].idxmax(), (dfR2plus["returnAct"]/1000).max(), 'or')
        ax.annotate(xy=(dfR2plus["returnAct"].idxmax(), (dfR2plus["returnAct"]/1000).max()),s=(str(round(dfR2plus["returnAct"].idxmax(),1)),str(round((dfR2plus["returnAct"]/1000).max(),1))))
        ax.plot(dfR2plus["returnAct"].idxmax(), ((dfR2plus["returnCap"]+dfR2plus["returnAct"])/1000).max(), 'or')
        ax.annotate(xy=(dfR2plus["returnAct"].idxmax(), ((dfR2plus["returnCap"]+dfR2plus["returnAct"])/1000).max()),s=(str(round(dfR2plus["returnAct"].idxmax(),1)),str(round(((dfR2plus["returnCap"]+dfR2plus["returnAct"])/1000).max(),1))))
        ax1.plot(dfR2plus["returnAct"].idxmax(), dfR2plus.loc[dfR2plus["returnAct"].idxmax()]["timeActiv"]*100, 'or')
        ax1.annotate(xy=(dfR2plus["returnAct"].idxmax(), dfR2plus.loc[dfR2plus["returnAct"].idxmax()]["timeActiv"]*100), s=(str(round(dfR2plus["returnAct"].idxmax(),1)),str(round((dfR2plus.loc[dfR2plus["returnAct"].idxmax()]["timeActiv"]*100),1))))
        ax1.plot(dfR2plus["returnAct"].idxmax(), dfR2plus.loc[dfR2plus["returnAct"].idxmax()]["volumeActiv"]*100, 'or')
        ax1.annotate(xy=(dfR2plus["returnAct"].idxmax(), dfR2plus.loc[dfR2plus["returnAct"].idxmax()]["volumeActiv"]*100), s=(str(round(dfR2plus["returnAct"].idxmax(),1)),str(round((dfR2plus.loc[dfR2plus["returnAct"].idxmax()]["volumeActiv"]*100),1))))
        ax.legend(("activation", "activation and capacity"))
        ax1.legend(("volume", "time"))
        
    return dfR2plus
    
    
    
def R2plusMultiTimeOptimum(fromdate,todate,averaging,bidvolume,dataframeAct,dataframeCap,variable,plotting):
    """
    Create dataframe containing the bidprice and return for each given volume in each given period, for the maximum return:   
    Method "R2plusSingleOptimum" is used.
    
    Parameters
    ----------
    fromdate : string
        date in the format of 'YYYY-MM-DD', e.g., '2017-10-22' is the 22th of October 2017
    todate : string
        date in the format of 'YYYY-MM-DD', e.g., '2017-10-22' is the 22th of October 2017
    averaging : string or int
        Set the averaging time frame: "week","day","hour","quarter". Or give the amount of days for which the optimum should be calculated. (number of iterations = (todate-fromdate)/frequency))
    bidvolume : int
        the volume of power for which is bidded (in MW)
    dataframeAct : dataframe
        dataframe made by executing the "FetchAndCombine_Elia_ActivEnergy" method. Contains all the prices and volumes of the activated ancillary services.
    dataframeCap : dataframe
        dataframe containing the avereged prices for the standby remuneration for the ancillary services.
    variable : boolean
        select how to perform the calculations, "true" will use the actual bidprices within the period, "false" will use the min and max and use a granularity of 0.1 euro/MWh
    plotting : boolean
        if you which to see the data in a plot, use True.
        
    returns
    -------
    DataFrame
        Processed dataframe.
    """
    
    if (averaging=="week"):
        frequency = 7        
    if (averaging=="day"):
        frequency = 1
    if (averaging=="hour"):
        frequency = 1/24
    if (averaging=="quarter"):
        frequency = 1/96
    if  isinstance(averaging,six.integer_types):
        frequency = averaging
    
    i=0
    df = dataframeAct
    df1 = dataframeCap
    
    fromdatepd=pd.to_datetime(fromdate,format="%Y-%m-%d")
    todatepd=pd.to_datetime(todate,format="%Y-%m-%d")
    todatepd = todatepd + relativedelta(days=1)
    date=fromdatepd
    date1=fromdatepd+relativedelta(days=frequency-1)

    dfR2plus = pd.DataFrame(columns=["timestamp","bidprice in euro/MWh","number of quarters","timeActiv","volumeActiv"])
    while (todatepd-relativedelta(days=frequency)) >= date:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     loopnumber: "+ str(i))
        temp = R2plusSingleOptimum(str(date),str(date1),bidvolume,df,df1,True,"no")
        temp.reset_index(inplace=True)
        temp ["timestamp"] = date
        dfR2plus = dfR2plus.append(temp,ignore_index=True)
        date = date + relativedelta(days=frequency)
        date1 = date1 + relativedelta(days=frequency)
    
    if (plotting==True):
        dfmulti = dfR2plus
        dfmulti = dfmulti.set_index("bidprice in euro/MWh")
        fig,(ax,ax1,ax2) = plt.subplots(3,1, sharex=True)
        dfmulti.groupby(["timestamp"])[["returnAct"]].idxmax().plot(ax=ax,kind="bar",grid=True,legend=False)
        dfmulti.groupby(["timestamp"])[["returnAct","returnCap"]].max().plot(ax=ax1,kind="bar",grid=True,color=["red","green"],legend=False)
        dfmulti.groupby(["timestamp"])[["volumeActiv","timeActiv"]].max().plot(ax=ax2,kind="bar",grid=True,legend=False)
        if (averaging == "week"):
            ax.set_xticklabels(pd.to_datetime(dfmulti["timestamp"].unique()).week, rotation=90)
        if (averaging == "day"):
            ax.set_xticklabels(pd.to_datetime(dfmulti["timestamp"].unique()).dayofyear, rotation=90)
        if (averaging == "hour"):
            ax.set_xticklabels(pd.to_datetime(dfmulti["timestamp"].unique()).hour, rotation=90)
        if (averaging == "quarter"):
            ax.set_xticklabels(pd.to_datetime(dfmulti["timestamp"].unique()).minute, rotation=90)
        if  isinstance(averaging,six.integer_types):
            ax.set_xticklabels(pd.to_datetime(dfmulti["timestamp"].unique()).dayofyear, rotation=90)
        ax1.legend(("activation","capacity"))
        ax2.legend(("volume","time"))
        if (averaging == "week"):
            ax2.set_xlabel("Weeks of the year ")
        if (averaging == "day"):
            ax2.set_xlabel("Days of the year ")
        if (averaging == "hour"):
            ax2.set_xlabel("Hours of the day ")
        if (averaging == "quarter"):
            ax2.set_xlabel("Minutes ")
        if  isinstance(averaging,six.integer_types):
            ax2.set_xlabel("Days of the year ")
        ax.set_ylabel("Optimal marginal activation \n prices in euro/MWh")
        ax1.set_ylabel("Remuneration in euro")
        ax2.set_ylabel("Activation percentage")
        if (frequency>=1):
            fig.suptitle("Elia R2+ product optimised bidprices for maximum activation remuneration\nfor the period " + fromdate + " to " + todate + " averaged over " + str(frequency) + " days\n and a volume of " + str(bidvolume) + "MW")
        if (averaging=="hour"):
            fig.suptitle("Elia R2+ product optimised bidprices for maximum activation remuneration\nfor the period " + fromdate + " to " + todate + " hourly averaged\n and a volume of " + str(bidvolume) + "MW")
        if (averaging=="quarter"):
            fig.suptitle("Elia R2+ product optimised bidprices for maximum activation remuneration\nfor the period " + fromdate + " to " + todate + " real quarterly values\n and a volume of " + str(bidvolume) + "MW")
    return dfR2plus