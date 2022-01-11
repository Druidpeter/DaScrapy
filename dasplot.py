import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from db_interface import DB_Interface

# fig, ax = plt.subplots()
# ax.plot([1,2], [1,4])
# plt.show()

class DB_Plotter(DB_Interface):
    def __init__(self):
        DB_Interface.__init__(self)
        self.fig, self.ax = plt.subplots()
        
    def proc(self):
        # Ok, so apparently we need to create two lists as input to
        # ax.plot(). This first list simply needs to be 1-day unit
        # incremented values, either as integers, or as actual labeled
        # dates. Looking at MatPlotLib docs can show us how to get
        # actual dates, but for now, simple integer increments will
        # do.

        # The second list is simply the number of urls of a specific
        # type we find in the database on that date. Date 1 is simply
        # the oldest date we can find in the database itself, and then
        # each date after that is simply 1 day after the first, until
        # we go past the latest date we can find in the database.

        print("Fetching total indexed dates")
        self.session.execute(f"select distinct urlDate from urls order by urlDate;")

        dates = self.session.fetchall()
        numDates = len(dates)
        
        indList = []
        depList = []
        
        for i in range(0, numDates):
            indList.append(i+1)

            print(f"processing total for date: { dates[i][0] }")
            self.session.execute(f"select id from urls where urlDate = \"{ dates[i][0] }\";")

            tmp = self.session.fetchall()
            depList.append(len(tmp))

        self.ax.plot(indList, depList)
        plt.show()

def main():
    db_plotter = DB_Plotter()
    db_plotter.proc()

if __name__ == "__main__":
    main()
