# DAScrape

DAScrape is a small(-ish) data analytics project I entered into at about May(-ish) of the year 2021. It basically scrapes urls and other data off of the DeviantArt website (only publicly available data, mind you. =_=) and stuffs said data into a mysql database.

I then use that database and other python scripts to process and refine the data into JSON ingest batches for druid.io clusters, which I then use to create pretty sparkly analytics time-series graphs for me and interested parties. 

Neat, eh? :3