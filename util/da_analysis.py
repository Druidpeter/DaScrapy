import mariadb

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime

db_connection = mariadb.connect(
    user="dascrapy_user",
    password="dascrapy_user",
    host="127.0.0.1",
    port=3306,
    database="dascrapy")

session = db_connection.cursor()

def plotWeekDayUploadsPerMonthTimeSeries():
    # Time Series graph for each
    pass

def calcWeekDayUploadsPerMonthTimeSeries():
    # Time series graph for each weekday at month intervals over a
    # year.
    pass

def plotUploadTimeSeries(data, startYear, endYear):
    fig, axs = plt.subplots(3, 7, figsize=(27, 13), constrained_layout=True)

    axsf = axs.flat
    
    for i in range(0, endYear-startYear):
        dt1 = f"{startYear+i}-01-01"
        dates = np.arange(np.datetime64(dt1),
                          np.datetime64(dt1) + np.timedelta64(365, 'D'),
                          np.timedelta64(1, 'D'))
    
        axsf[i].plot(dates, data[i])
        cdf = mpl.dates.ConciseDateFormatter(axsf[i].xaxis.get_major_locator())
        axsf[i].xaxis.set_major_formatter(cdf)

    plt.show()

def calcUploadTimeSeries():
    startYear = 2000
    endYear = 2021
    
    data = np.zeros((endYear-startYear, 365))
    intr = 365
    
    for j in range(startYear, endYear):
        print("Fetching date points")
        session.execute(f"select '{str(j)}-01-01' + interval seq day from seq_1_to_{intr}; ")
        
        dateList = session.fetchall()
        dateList = [ d[0] for d in dateList ]
        dateListLen = len(dateList)

        dy_index = j - startYear;
        
        for i in range(dateListLen):
            print(f"Fetching deviations uploaded at date point {dateList[i]}")
            session.execute(f"select count(id) from urls where urlDate >= '{dateList[i]}' and urlDate < adddate('{dateList[i]}', 1)")
            data[dy_index][i] = session.fetchone()[0]

    plotUploadTimeSeries(data, startYear, endYear)
    
def plotAverageDailyUploads(data, xlabel="Weekday", ylabel="Uploads", year_start = 0, year_end = 0):
    fig, axs = plt.subplots(5, 4, figsize=(13.3,7.2), constrained_layout=True)
    # colors = plt.get_cmap('Greens')(np.linspace(0.2, 0.7, len(data)))
    # ax.pie(data, colors=colors, radius = 6, center = (4, 4),
    #        wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=False)

    # ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
    #        ylim=(0, 8), yticks=np.arange(1, 8))
    
    categories = ['Sun', 'Mon', 'Tue', 'Wed',
                  'Thu', 'Fri', 'Sat']

    j = year_start
    i = 0
    
    for ax in axs.flat:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title("year " + str(j))
        ax.bar(categories, data[i])
        
        j += 1
        i += 1
        
    plt.show()

def calcAverageDailyUploads():
    year = 2000

    all_data = np.zeros((1, 7))
    
    for i in range(0, 21):
        session.execute(f"select dayofweek(urlDate) from urls where urlDate >= '{year}-01-01' and urlDate < '{year+1}-01-01';")
        results = session.fetchall()
    
        for result in results:
            all_data[-1][result[0] - 1] += 1

        data = np.zeros((1, 7))
        all_data = np.append(all_data, data, axis = 0)
            
        # for datum in data:
        #     print(datum)

        # print("\n")
        year += 1

    print(all_data)
    plotAverageDailyUploads(all_data, year_start=2000, year_end = 2020)

def main():
    # calcAverageDailyUploads()
    calcUploadTimeSeries()

if __name__ == "__main__":
    main()
