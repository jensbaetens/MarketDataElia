#from Elia_DataReadIn import read_elia_freq_R1, read_combine_elia_freq_R1, fetch_combine_elia_freq_R1, read_elia_activated_energy_volumes, read_elia_activated_energy_prices, read_combine_elia_activated_energy, fetch_combine_elia_activated_energy, read_elia_R1_R2_cap
#functions:
#read_elia_freq_R1
#read_combine_elia_freq_R1
#fetch_combine_elia_freq_R1

#read_elia_activated_energy_volumes
#read_elia_activated_energy_prices
#read_combine_elia_activated_energy
#fetch_combine_elia_activated_energy

#read_elia_R1_R2_cap

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import xlrd
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def read_elia_freq_R1(filename):

    """
    Read 10s Elia data file with frequency and R1.
    
    Parameters
    ----------
    filename : string
        Path to the data file.
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    df = pd.read_excel(filename,skiprows=4,parse_dates=True,index_col=0,dayfirst=True)
    df=df.drop(df.index[[0]])
    df.columns.values[0:3] = ["Frequency","ObligationR1","RequestedR1"]
 
    return df
    
def read_combine_elia_freq_R1(path):

    """
    Read 10s Elia data files with frequency and R1 and combine to one dataframe.
    
    Parameters
    ----------
    path : string
        Path to the folder with data files. If stored in data folder, use "..\data\"
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    i=0
    dfs = []
    data_files = glob.glob(path + 'FrequencyAndDemand_*')
    print(str(datetime.datetime.utcnow()) + "     amount of files to combine: " + str(len(data_files)))
    for file in data_files:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df = read_elia_freq_R1(file)
        dfs.append(df)
        combined_data = pd.concat(dfs, axis = 0)
    return combined_data
    
def fetch_combine_elia_freq_R1(fromdate,todate):
    
    """
    Fetch datafiles from the Elia website and combine into one dataframe. Internet connection needed.
    All datafiles are combined and returned as one df.
    
    Parameters
    ----------
    fromdate : string
        date in the format of 'month-year', e.g., '06-2015' is June 2015
    todate : string
        date in the format of 'month-year', e.g., '05-2016' is April 2016
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    i=0
    dfs = []
    file_names = []
    fromdatepd=pd.to_datetime(fromdate,format="%m-%Y")
    todatepd=pd.to_datetime(todate,format="%m-%Y")
    date = fromdatepd - relativedelta(months=1)
    
    while (date < todatepd):
        date = date + relativedelta(months=1)
        if date.month < 10:
            monthwithzero = "0" + str(date.month)
        else:
            monthwithzero = str(date.month)   
        file_names.append("http://publications.elia.be/Publications/Publications/FileRepository.v1.svc/DownloadFile?filePath=\Tulyp\FrequencyAndDemandR1Export\FrequencyAndDemand_"+str(date.year)+"_"+monthwithzero+".xlsx")
    print(str(datetime.datetime.utcnow()) + "     amount of files to combine: " + str(len(file_names)))        
    for file in file_names:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df = read_elia_freq_R1(file)
        dfs.append(df)
        combined_data = pd.concat(dfs, axis = 0)
    print(str(datetime.datetime.utcnow()) + "     finished")
    return combined_data
    
    
def read_elia_activated_energy_volumes(filename,status):

    """
    Read data file with historical data on activated energy volumes.
    Data comes from the Elia website in xls format.
    Quarter hourly data, but the time is transformed to pandas datetime. Timestamp is begining of quarter.
    
    Parameters
    ----------
    filename : string
        Path to the data file.
    status : string
        choose to use only validated data or all data. Use "valid" or "validated" to only use validated data.
        Any other string will result in all data.
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    df = pd.read_excel(filename,skiprows=2,parse_dates=False)
    df["Timestamp"] = df["Date"]+" "+df['Quarter'].map(lambda x: str(x)[:-9])
    pd.to_datetime(df["Timestamp"])
    df.set_index("Timestamp",inplace=True)
    if ((status == "validated") | (status == "valid")):
        df = df.drop(df[df.Status != "Validated"].index)
    df = df.drop(["Date","Quarter","Status"], axis=1)
    
    if ((len(df.columns)<13) & (len(df.columns)>11)) :
        df.columns.values[0:13] = ["NRV in MW", "GUV in MW", "IGCC+ in MW", "R2+ in MW", "Bids+ in MW", "R3+ in MW", "R3DP+ in MW", "GDV in MW", "IGCC- in MW", "R2- in MW", "Bids- in MW", "R3- in MW"]
    if len(df.columns)<= 11:
        df.columns.values[0:12] = ["NRV in MW", "GUV in MW", "IGCC+ in MW", "R2+ in MW", "Bids+ in MW", "R3+ in MW", "GDV in MW", "IGCC- in MW", "R2- in MW", "Bids- in MW", "R3- in MW"]
    if len(df.columns)>14:
        df.columns.values[0:16] = ["NRV in MW", "SR in MW","GUV in MW", "IGCC+ in MW","R2+ in MW","Bids+ in MW","R3 std in MW","R3 flex in MW","ICH in MW","inter TSO import in MW","GDV in MW","IGCC- in MW","R2- in MW","Bids- in MW","inter TSO export in MW"]
    
    return df
    
def read_elia_activated_energy_prices(filename,status):

    """
    Read data file with historical data on activated energy prices.
    Data comes from the Elia website in xls format.
    Quarter hourly data, but the time is transformed to pandas datetime. Timestamp is begining of quarter.
    
    Parameters
    ----------
    filename : string
        Path to the data file.
    status : string
        choose to use only validated data or all data. Use "valid" or "validated" to only use validated data.
        Any other string will result in all data.
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
   
    df = pd.read_excel(filename,skiprows=2,parse_dates=False)
    df["Timestamp"] = df["Date"]+" "+df['Quarter'].map(lambda x: str(x)[:-9])
    pd.to_datetime(df["Timestamp"])
    df.set_index("Timestamp",inplace=True)
    if ((status == "validated") | (status == "valid")):
        df = df.drop(df[df.Status != "Validated"].index)
    df = df.drop(["Date","Quarter","Status"], axis=1)
    
    if len(df.columns)>14:
        df.columns.values[0:16] = ["NRV in MW","SR in euro/MWh","MIP in euro/MWh","IGGC+ in euro/MWh", "R2+ in euro/MWh","Bids+ in euro/MWh","R3 std in euro/MWh", "R3 flex in euro/MWh", "ICH in euro/MWh", "inter TSO import in euro/MWh", "MDP in euro/MWh", "IGCC- in euro/MWh", "R2- in euro/MWh", "Bids- in euro/MWh", "R3- in euro/MWh"]

    if len(df.columns)<12:
        df.columns.values[0:12] = ["NRV in MW","MIP in euro/MWh","IGGC+ in euro/MWh", "R2+ in euro/MWh","Bids+ in euro/MWh", "R3+ in euro/MWh", "MDP in euro/MWh", "IGCC- in euro/MWh", "R2- in euro/MWh", "Bids- in euro/MWh", "R3- in euro/MWh"]

    return df
    
def fetch_combine_elia_activated_energy(fromdate,todate,status):
    
    """
    Fetch datafiles from the Elia website and combine into one dataframe. Internet connection needed.
    All datafiles are combined and returned as one df. Elia provides data from 01-2012.
    
    Parameters
    ----------
    fromdate : string
        date in the format of 'month-year', e.g., '06-2015' is June 2015
    todate : string
        date in the format of 'month-year', e.g., '05-2016' is April 2016
    status : string
        choose to use only validated data or all data. Use "valid" or "validated" to only use validated data.
        Any other string will result in all data.    
    
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    i=0
    dfsprice = []
    dfsvol = []
    data_files_price = []
    data_files_volume = []  
    fromdatepd=pd.to_datetime(fromdate,format="%m-%Y")
    todatepd=pd.to_datetime(todate,format="%m-%Y")
    date = fromdatepd - relativedelta(months=1)
    
    while (date < todatepd):
        date = date + relativedelta(months=1)
        if date.month < 10:
            monthwithzero = "0" + str(date.month)
        else:
            monthwithzero = str(date.month)   
        data_files_volume.append("http://imbalanceb2c.elia.be/proxy.aspx?pubName=ActivatedEnergyVolumes&fId="+str(date.year)+monthwithzero+".xls")
        data_files_price.append("http://imbalanceb2c.elia.be/proxy.aspx?pubName=ActivatedEnergyPrices&fId="+str(date.year)+monthwithzero+".xls") 
    print(str(datetime.datetime.utcnow()) + "     amount of files to combine: " + str(len(data_files_volume)+len(data_files_price)))        
    for file1 in data_files_price:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df1 = read_elia_activated_energy_prices(file1,status)
        dfsprice.append(df1)
        combined_data_price = pd.concat(dfsprice, axis = 0)
        
    #remove "NRV in MW" column, because it is duplicate   
    if "NRV in MW" in combined_data_price:    
        combined_data_price = combined_data_price.drop(combined_data_price[["NRV in MW"]],axis=1)
    if "NRV\n (MW)" in combined_data_price:
        combined_data_price = combined_data_price.drop(combined_data_price[["NRV\n (MW)"]],axis=1)
    
    for file2 in data_files_volume:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df2 = read_elia_activated_energy_volumes(file2,status)
        dfsvol.append(df2)
        combined_data_vol = pd.concat(dfsvol, axis = 0)
        
    result = pd.concat([combined_data_price, combined_data_vol], axis=1)
    result.reset_index(inplace=True)
    result["Timestamp"]=pd.to_datetime(result["Timestamp"],format=("%d/%m/%Y %H:%M"))
    result=result.set_index("Timestamp")
    
    if "NRV\n (MW)" in result:
        if "NRV in MW" in result:
            result.fillna(0,inplace=True)
            result["Bids+ in euro/MWh"] = result["Bids+\n (\u20ac/MWh)"] + result["Bids+ in euro/MWh"]
            result["Bids- in euro/MWh"] = result["Bids-\n(\u20ac/MWh)"] + result["Bids- in euro/MWh"]
            result["IGCC- in euro/MWh"] = result["IGCC-\n(\u20ac/MWh)"] + result["IGCC- in euro/MWh"]
            result["IGGC+ in euro/MWh"] = result["IGGC+\n(\u20ac/MWh)"] + result["IGGC+ in euro/MWh"]
            result["MDP in euro/MWh"] = result["MDP\n(\u20ac/MWh)"] + result["MDP in euro/MWh"]
            result["MIP in euro/MWh"] = result["MIP\n (\u20ac/MWh)"] + result["MIP in euro/MWh"]
            result["R2+ in euro/MWh"] = result["R2+\n(\u20ac/MWh)"] + result["R2+ in euro/MWh"]
            result["R2- in euro/MWh"] = result["R2-\n(\u20ac/MWh)"] + result["R2- in euro/MWh"]
            result["R3 flex in euro/MWh"] = result["R3 Flex (\u20ac/MWh)"] + result["R3 flex in euro/MWh"]
            result["R3 std in euro/MWh"] = result["R3 std (\u20ac/MWh)"] + result["R3 std in euro/MWh"]
            result["R3- in euro/MWh"] = result["R3-\n(\u20ac/MWh)"] + result["R3- in euro/MWh"]
            result["SR in euro/MWh"] = result["SR\n(\u20ac/MWh)"] + result["SR in euro/MWh"]
            result["inter TSO import in euro/MWh"] = result["Inter-TSO Import\n (\u20ac/MWh)"] + result["inter TSO import in euro/MWh"]
            result["Bids+ in MW"] = result["Bids+\n (MW)"] + result["Bids+ in MW"]
            result["Bids- in MW"] = result["Bids-\n(MW)"] + result["Bids- in MW"]
            result["GDV in MW"] = result["GDV\n(MW)"] + result["GDV in MW"]
            result["GUV in MW"] = result["GUV\n (MW)"] + result["GUV in MW"]
            result["IGCC+ in MW"] = result["IGCC+\n(MW)"] + result["IGCC+ in MW"]
            result["IGCC- in MW"] = result["IGCC-\n(MW)"] + result["IGCC- in MW"]
            result["inter TSO export in MW"] = result["Inter-Tso\nExport\n(MW)"] + result["inter TSO export in MW"]
            result["inter TSO import in MW"] = result["Inter-Tso Import(MW)"] + result["inter TSO import in MW"]
            result["NRV in MW"] = result["NRV\n (MW)"] + result["NRV in MW"]
            result["R2+ in MW"] = result["R2+\n(MW)"] + result["R2+ in MW"]
            result["R2- in MW"] = result["R2-\n(MW)"] + result["R2- in MW"]
            result["R3 flex in MW"] = result["R3 Flex\n(MW)"] + result["R3 flex in MW"]
            result["R3 std in MW"] = result["R3 Std\n (MW)"] + result["R3 std in MW"]
            result["SR in MW"] = result["SR\n(MW)"] + result["SR in MW"]
            result=result.drop(["Bids+\n (\u20ac/MWh)","Bids-\n(\u20ac/MWh)","IGCC-\n(\u20ac/MWh)","IGGC+\n(\u20ac/MWh)","MDP\n(\u20ac/MWh)","MIP\n (\u20ac/MWh)","R2+\n(\u20ac/MWh)","R2-\n(\u20ac/MWh)","R3 Flex (\u20ac/MWh)","R3 std (\u20ac/MWh)","R3-\n(\u20ac/MWh)","SR\n(\u20ac/MWh)","Inter-TSO Import\n (\u20ac/MWh)","Bids+\n (MW)","Bids-\n(MW)","GDV\n(MW)","GUV\n (MW)","IGCC+\n(MW)","IGCC-\n(MW)","Inter-Tso\nExport\n(MW)","Inter-Tso Import(MW)","NRV\n (MW)","R2+\n(MW)","R2-\n(MW)","R3 Flex\n(MW)","R3 Std\n (MW)","SR\n(MW)"],axis=1)
            result[result == 0] = np.nan
    
    print(str(datetime.datetime.utcnow()) + "     finished")
    return result
    
def read_combine_elia_activated_energy(path,status):
    """
    Combine all datafiles in the specified folder containing the words "ActivatedEnergyPrices" or "ActivatedEnergyVolumes" into one dataframe
    All datafiles are combined and returned as one df.
    
    Parameters
    ----------
    path : string
        path to the folder with the files. use for example "../data/" if the files are located in a data folder above the folder in which the script is.
        
    status : string
        choose to use only validated data or all data. Use "valid" or "validated" to only use validated data.
        Any other string will result in all data.
    
    Returns
    -------
        Processed dataframe.
    """
    #loop, read in and combine all data files into one "combined_data"
    i=0
    dfsprice = []
    dfsvol = []
    data_files_price = glob.glob(path + 'ActivatedEnergyPrices*')
    data_files_volume = glob.glob(path + 'ActivatedEnergyVolumes*')
    print(str(datetime.datetime.utcnow()) + "     amount of files to combine: " + str(len(data_files_volume)+len(data_files_price)))
    
    for file1 in data_files_price:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df1 = read_elia_activated_energy_prices(file1,status)
        dfsprice.append(df1)
        combined_data_price = pd.concat(dfsprice, axis = 0)
        
    #remove "NRV in MW" column, because it is duplicate    
    combined_data_price = combined_data_price.drop(combined_data_price.columns[7], axis=1)
    
    for file2 in data_files_volume:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df2 = read_elia_activated_energy_volumes(file2,status)
        dfsvol.append(df2)
        combined_data_vol = pd.concat(dfsvol, axis = 0)
    
    result = pd.concat([combined_data_price, combined_data_vol], axis=1)
    result.reset_index(inplace=True)
    result["Timestamp"]=pd.to_datetime(result["Timestamp"],format=("%d/%m/%Y %H:%M"))
    result=result.set_index("Timestamp")
    print(str(datetime.datetime.utcnow()) + "     finished")
    return result
    
    
def read_elia_cap(filename):

    """
    Read data file with historical data on ancillary services, volumes and prices.
    Data comes from the Elia website, but is copy-pasted into an xlsx
    
    Elia data is usually formated as "Week Year", e.g., "W45 2017". This function will rename to the first day of the week.
    E.g. W52 2017 will be converted to 25-12-2017.
    
    Parameters
    ----------
    filename : string
        Path to the data file.
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    df = pd.read_excel(filename,skiprows=0,parse_dates=False)
    
    #standaard datetime vorm omzetten
    df["Tendering Periodneww"] = pd.to_datetime(df["Tendering Period"],errors='coerce')
    df["Delivery Periodneww"] = pd.to_datetime(df["Delivery Period"],errors='coerce')
    
    #de 'weekvorm' van datetime omzetten
    df["Tendering Period"]=df["Tendering Period"].astype(str).map(lambda x: x.lstrip('W'))
    df["Delivery Period"]=df["Delivery Period"].astype(str).map(lambda x: x.lstrip('W'))
    df["Tendering Period"]=df["Tendering Period"].replace('\s+', '_',regex=True)
    df["Delivery Period"]=df["Delivery Period"].replace('\s+', '_',regex=True)
    df["Tendering Periodnew"] = pd.to_datetime(df["Tendering Period"][df["Delivery Periodneww"].isnull()].astype(str).add('-1'), format="%W_%Y-%w", errors='coerce')
    df["Delivery Periodnew"] = pd.to_datetime(df["Delivery Period"][df["Delivery Periodneww"].isnull()].astype(str).add('-1'), format="%W_%Y-%w", errors='coerce')
    
    #datumkolommen samenvoegen en overbodige kolommen verwijderen
    df["Tendering Period Combined"] = df['Tendering Periodnew'].fillna(df['Tendering Periodneww'])
    df["Delivery Period Combined"] = df['Delivery Periodnew'].fillna(df['Delivery Periodneww'])
    df=df.drop(columns=['Tendering Period', 'Delivery Period','Tendering Periodneww', 'Delivery Periodneww','Tendering Periodnew', 'Delivery Periodnew',])
    df.columns=["duration","reserve type","service type","total contracted volume in MW", "average price in euro/MW/h","forecasted average price in euro/MW/h","total offered volume in MW","tariff period", "symmetry type", "country","tendering period","delivery period"]    
    
    #multi index & sort
    df=df.set_index(["delivery period"])
    df=df.sort_index(ascending=False);
 
    return df
    

def read_elia_imbalanceprices(filename,status):

    """
    Read data file with historical data on imbalance prices.
    Data comes from the Elia website in xls format.
    Quarter hourly data, but the time is transformed to pandas datetime. Timestamp is begining of quarter.
    
    Parameters
    ----------
    filename : string
        Path to the data file.
    status : string
        choose to use only validated data or all data. Use "valid" or "validated" to only use validated data.
        Any other string will result in all data.
        
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
   
    df = pd.read_excel(filename,skiprows=1,parse_dates=False)
    df["Timestamp"] = df["Date"]+" "+df['Quarter'].map(lambda x: str(x)[:-9])
    pd.to_datetime(df["Timestamp"])
    df.set_index("Timestamp",inplace=True)
    if ((status == "validated") | (status == "valid")):
        df = df.drop(df[df.Status != "Validated"].index)
    df = df.drop(["Date","Quarter","Status"], axis=1)
    
    if len(df.columns) == 3:
        df.columns.values[0:3] = ["NRV in MW","POS in euro/MWh", "NEG in euro/MWh"]
        
    if len(df.columns) == 7:
        df.columns.values[0:7] = ["NRV in MW","SI in MW","alpha in euro/MWh","MIP in euro/MWh", "MDP in euro/MWh","POS in euro/MWh", "NEG in euro/MWh"]
    
    if len(df.columns) == 8:
        df.columns.values[0:8] = ["NRV in MW","SI in MW","alpha in euro/MWh","MIP in euro/MWh", "MDP in euro/MWh","SR in euro/MWh","POS in euro/MWh", "NEG in euro/MWh"]

    return df
    
def fetch_combine_elia_imbalanceprices(fromdate,todate,status):
    
    """
    Fetch datafiles from the Elia website and combine into one dataframe. Internet connection needed.
    All datafiles are combined and returned as one df. Elia provides data from 01-2012.
    
    Parameters
    ----------
    fromdate : string
        date in the format of 'month-year', e.g., '06-2015' is June 2015
    todate : string
        date in the format of 'month-year', e.g., '05-2016' is April 2016
    status : string
        choose to use only validated data or all data. Use "valid" or "validated" to only use validated data.
        Any other string will result in all data.    
    
    Returns
    -------
    DataFrame
        Processed dataframe.
    """
    i=0
    dfsprice = []
    dfsvol = []
    data_files_price = []
    fromdatepd=pd.to_datetime(fromdate,format="%m-%Y")
    todatepd=pd.to_datetime(todate,format="%m-%Y")
    date = fromdatepd - relativedelta(months=1)
    
    while (date < todatepd):
        date = date + relativedelta(months=1)
        if date.month < 10:
            monthwithzero = "0" + str(date.month)
        else:
            monthwithzero = str(date.month)   
        data_files_price.append("http://imbalanceb2c.elia.be/proxy.aspx?pubName=ImbalanceNrvPrices&fId="+str(date.year)+monthwithzero+".xls")        
    print(str(datetime.datetime.utcnow()) + "     amount of files to combine: " + str(len(data_files_price)))        
    for file1 in data_files_price:
        i=i+1
        print(str(datetime.datetime.utcnow()) + "     processing file number: "+ str(i))
        df1 = read_elia_imbalanceprices(file1,status)
        dfsprice.append(df1)
        combined_data_price = pd.concat(dfsprice, axis = 0)
    
    
    combined_data_price.reset_index(inplace=True)
    combined_data_price["Timestamp"]=pd.to_datetime(combined_data_price["Timestamp"],format=("%d/%m/%Y %H:%M"))
    combined_data_price=combined_data_price.set_index("Timestamp")
    
    print(str(datetime.datetime.utcnow()) + "     finished")
    return combined_data_price    

