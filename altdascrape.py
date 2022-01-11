from html.parser import HTMLParser
from db_interface import DB_Interface

import altparsing

def cnv_date(date):
    tmp = (date.lower()).split()

    if(tmp[0] == "january"):
        tmp[0] = "01"
    elif(tmp[0] == "february"):
        tmp[0] = "02"
    elif(tmp[0] == "march"):
        tmp[0] = "03"
    elif(tmp[0] == "april"):
        tmp[0] = "04"
    elif(tmp[0] == "may"):
        tmp[0] = "05"
    elif(tmp[0] == "june"):
        tmp[0] = "06"
    elif(tmp[0] == "july"):
        tmp[0] = "07"
    elif(tmp[0] == "august"):
        tmp[0] = "08"
    elif(tmp[0] == "september"):
        tmp[0] = "09"
    elif(tmp[0] == "october"):
        tmp[0] = "10"
    elif(tmp[0] == "november"):
        tmp[0] = "11"
    elif(tmp[0] == "december"):
        tmp[0] = "12"

    rdata = tmp[2][0:len(tmp[2])-1] + "-" + \
            tmp[0] + "-" + \
            tmp[1][0:len(tmp[1])-1]

    return rdata

def main():
    '''DeviantArt Scraping Algorithm'''
    # Load a list of usernames and their associated profile urls.

    print("Loading initial Data.")
    
    datafd = open('chunk.0.txt', 'r')    

    print("Instantiating database go-between and parser.")
    db = DB_Interface()
    parser = altparsing.AltParser()

    data = ''
    counter = 0

    print("Starting Input Loop")
    
    while True:
        data = datafd.readline()
        counter += 1

        if data == '':
            break
        
        if db.check_url(data) == True:
            continue
        
        r_data = parser.proc(data)
        
        print("Handing off row to database go-between.")
        print(f"url: {data}")
        db.proc(r_data[0], r_data[1], cnv_date(r_data[2]), r_data[3], r_data[4])
        
if __name__ == "__main__":
    main()
