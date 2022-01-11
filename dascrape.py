from html.parser import HTMLParser
from db_interface import DB_Interface

import parsing

MAX_URL_LIST = 4000000 # Four hundred thousands seems about right.
MAX_BATCH_PROCCED = 50000000 # This value will increase after testing and
                       # deugging of the code.

PROCLIST_MAX_SIZE = 64000000

procLogFd = open("procced.log", "a")

def sanitize_proc_list(tmp, db):
    tmp2 = []
    
    for i in range(0, len(tmp)):
        if db.check_url(tmp[i]) == False:
            tmp2.append(tmp[i])
        else:
            continue

    return tmp2

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
    
    initDataFd = open('initData.txt', 'r')    
    urlProc = (initDataFd.readlines())
    dataProc = []

    chunkFd = open("chunk.txt", "a+")

    print("Instantiating database go-between and parser.")
    db = DB_Interface()
    parser = parsing.ScrapyParser()

    tmp = []
    counter = 0

    # 

    batch_size = 500
    chunkFlag = False
    exhaustFlag = False

    print("Entering batch processing loop")
    total_batch = 0

    while True:
        if total_batch > MAX_BATCH_PROCCED:
            print("Url Proc Exhaustion! Refusing to add more urls to urlProc list.")
            exhaustFlag = True
            break;
        
        for row in dataProc:
            if len(dataProc) == 0:
                print("dataproc is empty!")
            
            print("Handing off row to database go-between.")
            print(f"url: {row[1]}")
            db.proc(row[0], row[1], cnv_date(row[2]), row[3], row[4])
            total_batch += 1

        dataProc = [] # Reset dataProc to empty list.
        last_idx = 0

        last_list_size = 0
        
        print("Refreshing url process list")

        endval = min(len(urlProc), batch_size)
        
        for idx in range(0, endval-1):
            last_idx = idx
            
            print("Handing off url to parser go-between")
            r_data = parser.proc(urlProc[idx])
            dataProc.append(r_data[0])

            r_data[1] = sanitize_proc_list(r_data[1], db)
            
            # if len(urlProc) + len(r_data[1]) >= MAX_URL_LIST:
            #     chunkFlag = True
                
            if chunkFlag == True:
                print("Starting chunk handling of data input.")
                
                # fetch data to append from chunkFd.
                with open("chunk.txt", 'a+') as chunkFd2:
                    for idx in r_data[1]:
                        chunkFd2.write(idx + "\n")

                    chunkFd2.seek(0)

                    for j in range(0, batch_size):
                        line = chunkFd2.readline()
                        
                        if(line != ''):
                            line = line.strip()

                            urlProc.append(line)
                            procLogFd.write(line)

                    lines = chunkFd2.readlines();
                            
                    with open("chunk.txt", 'w') as groomedChunkFd:
                        ptr = 1
                        
                        for line in lines:                            
                            if ptr > batch_size:
                                groomedChunkFd.write(line)
                                ptr += 1

                            if ptr > PROCLIST_MAX_SIZE:
                                break;

                        groomedChunkFd.close()
                    chunkFd2.close()
            else:
                for e in r_data[1]:
                        urlProc.append(e)
                        chunkFd.write(e + "\n")
                        
            if last_idx < len(urlProc)-1:
                urlProc = urlProc[last_idx+1:]
            else:
                print("Url proc list has been exhausted. This is highly suspicious. Exit.")
                # We've run out of urls in the url proc list!!! Exit
                # and finish.

                logProcFd.close()
                chunkFd.close()
                
                break
                
if __name__ == "__main__":
    main()
