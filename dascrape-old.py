import os
import sys
import subprocess
import mariadb
import re

## NOTE: this file now only deals almost exclusively with the scraping of html data and the formatting of it to be useful to the db_interface object.

# Essentially, we start with a list of lists, with each sublist
# containing username, href, date, global_increment values. For each
# found href, we check to see if it has been processed, and if not, we
# call the scrapyParser to parse it, and store the return data in a
# buffer.

# We then iterate over the list of lists and parse each entry to
# supply additional list values, e.g. urlType, assoc_url, associated
# username, et al.

# Note: Some values will need to be supplied immediately after
# performing a scrapyparser parse operation. The big one here is the
# assoc_url value, which we only have access to while it is the
# current entry being processed. So we will have to iterate over the
# returned scraped html data and supply this particular value
# immediately after every scrapy call.

# If we can satisfy all the missing values for a particular entry,
# remove that entry from the proc list and place it into the
# db_interface list. After we have removed all completed proc entries
# and filled the db_interface list, send the db_interface buffer to
# the db_interface for database processing.

# Then, merge the returned html data buffer with the proc list, and
# start the process over again.

from html.parser import HTMLParser
    
commentRegEx = re.compile("/[0-9]+/([0-9]+)/$")
incRegEx = re.compile("/-([0-9])+$")
dateTimeRegEx = re.compile("<span>.*datetime=\"([0-9]+-[0-9]+-[0-9]+).*\".*</span>")

def main():
    '''DeviantArt Scraping Algorithm'''
    # Load a list of usernames and their associated profile urls.
    initDataFd = open('initData.txt', 'r')
    initData = initDataFd.readlines()
    dataProc = []

    # initData.txt contains a username and a profile url on each line,
    # separated by a space.
    
    for line in initData:
        dataProc.append(line.strip().split())
    
    # For each found url, check database if url has already been
    # processed. If not, then proceed as below. If yes, then drop and
    # proceed to the next url in the queue.

    try:
        db_connection = mariadb.connect(
            user="dascrapy_user",
            password="dascrapy_user",
            host="127.0.0.1",
            port="3306",
            database="dascrapy"
        )
    except mariadb.Error as e:
        print(f"MariaDB Connect Error: {e}")
        sys.exit(-1)

    session = db_connection.cursor()
    htmlParser = DateScraper()

    for urlData in dataProc:
        session.execute("select id from urls where urls.data=?;",
                        (urlData[1]))

        htmlData = subprocess.run(['wget', '-O', '-', urlData[1]], capture_output=True, text=True)
        htmlParser.feed(htmlData)
        
        if session.rowcount != 0:
            # url has already been processed. Drop.
            continue
        else:
            # Url has not been inserted into database. Fetch
            # associated html parse data to get the date of
            # the url and all associated links on that page.

            # Example url.
            # https://www.deviantart.com/thireaart/art/Commission-Elysium-887192802
            hrefDate = htmlParser.pageDate

            session.execute("select id, username from deviants where username like \"" + urlData[0] + "\" limit 1;")

            deviant_id = 0
            
            if session.rowcount == 1:
                # username is in database, so use fetched id.
                deviant_id = session.next()[0]
            else:
                # username is not in database, and we need to insert
                # it.
                session.execute("insert into deviants (username) values (?);", (urlData[0]))
                deviant_id = session.lastrowid
                
            commentMatch = None
            tmpInc = -1
            globalInc = -1
            
            if urlData[1].count("/art/") > 0:
                # Deviation
                urlType = "deviation"
                globalInc = incRegEx.search(urlData[1]).group(0)
            elif urlData[1].count("/journal/") > 0:
                # Journal
                urlType = "journal"
                globalInc = incRegEx.search(urlData[1]).group(0)
            elif (commentMatch = commentRegEx.search(urlData[1])) != None
                # Comment
                urlType = "comment"
                tmpInc = commentMatch.group(1)
                globalInc = commentMatch.group(2)
            elif urlData[1].count("/") == 3:
                # Profile - Does not have a global increment value!!
                urlType = "profile"
                

            # Note: The insertion statement below needs to be updated
            # to also push the global DA increment number into the
            # urls table. This means that the urls table needs to have
            # a global increment column to store this. The combination
            # of urlType and gobal_increment columns should form a
            # unique index key.

            # Of course, this means that we need to extract the
            # necessary global increment number from the url in each
            # case.

            # Profiles are a special case. That is, everytime we
            # insert into the urls table a url that was uploaded by a
            # specific username, the sql needs to check whether the
            # urlDate is less than the joined_on field in the
            # corresponding deviants table. If it is, then we need to
            # update the joined_on field to match the value of the
            # current urlDate.

            # Reason we do this is a simple assumption: Any deviation
            # is considered to have joined upon their earliest upload,
            # be that a comment, journal, or deviation.

            # This means that for the purposes of our tabulation, only
            # deviants that have participated at least once on the
            # site count as being part of the global deviants
            # counter. But that's ok, because that's probably what we
            # want. Any deviants that have never participated at all
            # are lumped into a separate category.
                
            # Insert.
            session.execute("insert into urls (data, urlType, urlDate, global_inc, deviant_id) values (?, ?, ?, ?, ?)", (urlData[1], urlType, hrefDate, globalInc, deviant_id))

            tmpCommentId = session.lastrowid

            if tmpInc != 1:
                session.execute("select id from urls where urlType like \"deviation\" and global_inc = (?)", (tmpInc))

                if session.rowcount == 1:
                    tmp_id = session.next()[0]
                    session.execute("insert into comments_deviations (deviation_id, comment_id) values(?, ?)", (tmp_id, tmpCommentId))

            # At this point, we need to add all of the found hrefs
            # from the htmlParser to an href_proc list. hrefs should
            # be in the form of a list of lists, with each inner list
            # containing:

            # shit. I think I'm going to have to nearly start fresh.

            hrefs = htmlParser.outData
            
            # Tabulate.
            if urlType == "deviation" or urlType == "journal":
                d_number = tabRegEx.search(urlData[1]).group(0)

                cmd = wget_tmpl.format(urlData[1])
                out_data = subprocess.run(cmd, shell=True)
                
                d_date = 
                session.execute("")

            
            # { TBD HERE }
            
    # Call wget using each profile url, and store html.

    # Parse wget returned value. Look for hrefs that indicate:

    # 1. comments
    # 2. profile pages
    # 3. gallery pages
    # 4. art pages

    # Sort the various types of urls and correlate them with
    # the current (e.g. last wgotten) url.

    # Add all traversable urls to queue. Load and unload to manage
    # memory as necessary.

    # Extract data from urls as each is added to queue. Tabulate,
    # then insert data to database.

if __name__ == "__main__":
    main()
