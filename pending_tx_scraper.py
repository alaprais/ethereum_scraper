from bs4 import BeautifulSoup
import requests
import csv
import re
import time
from time import gmtime, strftime
import os


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0)'
           +' Gecko/20100101 Firefox/86.0'} # google "what is my user-agent?"
                                            # and past into above

def scrape_pending_tx(N):
    """
    Scrapes first 50 tx (<2 sec old) on pending page, returns list of tuples: (bid, time).
    N denotes number of iterations. After each iter wait (2) seconds to prevent
    duplicate observations
    """
    
    url ="https://etherscan.io/txsPending"
    
    data = []
    
    for i in range(N):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find(id = 'transfers')
        tx_elems = results.find_all('tr')
        
        for tx_elem in tx_elems[1:]: #exclude first element which is headers
            tx_data = tx_elem.find_all('td') # list of <td>'s for the specific <tr>
            
            tx_age_string = tx_data[2].get_text() # of the form '(x) sec(s) ago'
            tx_age = float(re.sub(" ?sec(s)? ago", ".0", tx_age_string)) # format to just numeric
            
            if tx_age > 2:    #dont want to overlap with old txs
                break
            
            # transaction data
            tx_hash = tx_data[0].get_text()
            tx_nonce = int(tx_data[1].get_text())
            #tx_age meaningless since always < 2, so instead use tx_time
            tx_time = tx_data[2].find_all('span')[0]['title']  # string of date and time of tx
            tx_gas_limit = int(tx_data[3].get_text())
            tx_gas_price_string = tx_data[4].get_text() # of form 'x,xxx Gwei'
            tx_gas_price_string = tx_gas_price_string.replace(",","")
            tx_gas_price = float(tx_gas_price_string.replace(" Gwei", ""))
            tx_from = tx_data[5].get_text()
            tx_to = tx_data[6].get_text()
            tx_value_string = tx_data[7].get_text()  # need to format to float
            tx_value_string = tx_value_string.replace(" Ether","")
            tx_value = float(tx_value_string)
            #tx_bid = tx_gas_limit * tx_gas_price
          
            
            data.append((tx_hash,tx_nonce, tx_time, tx_gas_limit, 
                         tx_gas_price, tx_from, tx_to, tx_value))
        time.sleep(2)
    return data

 
def scrape_and_write(N,path):
    """"calls scrape_pending_tx(N) and writes data to file at path location"""
    os.chdir(path)
    start_snapshot = strftime("[%Y %b %d %X]", gmtime())
    data = scrape_pending_tx(N)  ## scraper
    end_snapshot = strftime("[%Y %b %d %X]", gmtime())
    
    snapshot_coverage = start_snapshot + " - " + end_snapshot
    snapshot_coverage = snapshot_coverage.replace(":", ";") # system compatible
    
    with open ('data_'+snapshot_coverage+'.txt','w') as file:  # write to file
            writer=csv.writer(file)
            for row in data:
                writer.writerow(row)

# example:
scrape_and_write(1, "C:\\Users\\Arnaud Laprais\\Desktop\\SJSU\\CAMCOS\\scripts")   
