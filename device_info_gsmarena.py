#!/usr/bin/env python3
# *-* coding: utf-8 *-*

#    Copyright (C) 2015 by Ángel Guzmán Maeso, shakaran at gmail dot com

#    device_info_gsarena is a simple python script for scrap device info data from GSM Arena webpage

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from bs4 import BeautifulSoup
import requests
import json

import time

def show_time(start):
    end = time.time()
    
    elapsed = end - start
    print (elapsed)

headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'keep-alive',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Pragma' : 'no-cache',
                'Accept-Encoding' : 'gzip, deflate, sdch',
                'Accept-Language': 'es-ES,es;q=0.8,en;q=0.6',
                'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36',
                'Cache-Control' : 'no-cache',
             }
    
def get_brands():
    print('* Getting brands')
    brands = []
    makers_url = 'http://www.gsmarena.com/makers.php3'
    
    r = requests.get(makers_url, headers = headers)
    
    if r and r.status_code == 200:
         #print(r.text)
         links = BeautifulSoup(r.text).find('div', {'id':'mid-col'}).find_all('a', href=True)

         for link in links:
            if link.name == 'a' and len(link.text) > 0:
                brands.append({'link' : 'http://www.gsmarena.com/' + link['href'], 'manufacturer' : link.text.split(' phones')[0] })
    
    print ('Fetched ' + str(len(brands)) + ' brands\n')       
    return brands

def get_models(brand, page = 1):
    models = []
    current_page = page
    r = requests.get(brand['link'], headers = headers)
    
    if r and r.status_code == 200:
         #print(r.text)
         links = BeautifulSoup(r.text).find('div', {'class':'makers'}).find_all('a', href=True)
         
         block_pages = BeautifulSoup(r.text).find('div', {'class':'nav-pages'})
         
         if block_pages:
             current_page_data = block_pages.strong.text
         else:
             current_page_data = 1 # Assuming only one page
             #print 'Error current page data: ' + str(r.url)

         if int(current_page_data) == int(current_page):
            print('* Getting models for brand ' + str(brand))
             
            #print('Parsing page: ' + str(current_page_data))
            #print('Current page: ' + str(current_page))
         
            for link in links:
                models.append({ 'manufacturer' : brand['manufacturer'], 'link' : 'http://www.gsmarena.com/' + link['href'] })

            print ('\tFetched ' + str(len(models)) + ' models for brand ' + str(brand['manufacturer']) + ' for page ' + str(current_page_data) + '\n')
            
            if block_pages:
                more_pages = block_pages.find_all('a')
                
                if more_pages:
                    for more_page in more_pages:
                        #print more_page.get_text()
                        if more_page.get_text() != '»' and more_page.get_text() != '«' and more_page.get_text() > current_page :
                            current_page += 1
                            models.extend(get_models({'manufacturer' : brand['manufacturer'], 'link' : 'http://www.gsmarena.com/' + more_page['href']}, current_page))
                        #else:
                        #    print 'Skiping ' + str(more_page.get_text() + '\n')
                        
                #print(more_pages)
    
    return models   

def get_info(model):
    print('Getting device info for model ' + str(model))
    device = []
    r = requests.get(model['link'], headers = headers)
    
    if r and r.status_code == 200:
         #print(r.text)
         device_name = BeautifulSoup(r.text).find('div', {'id':'ttl'}).find('h1').get_text()
         specs_list = BeautifulSoup(r.text).find('div', {'id':'specs-list'}).find_all('td', {'class':'ttl'})
         
         specs = {}
         for data in specs_list:
             if data.get_text() != None and len(data.get_text()) > 2: # Skip blank spaces keys
                 if data.get_text() == 'Dimensions':
                     # Fetch only mm and skip inches
                     dimensions_data = data.findNextSibling().get_text().split(' mm (')[0]
                     specs[data.get_text()] = dimensions_data
                 else:
                     specs[data.get_text()] = data.findNextSibling().get_text()
        
         device.append({'name': device_name, 'manufacturer' : model['manufacturer'], 'specs' : specs})
       
    return device

start = time.time()
brands = get_brands() 
show_elapsed(start)

#brands = brands[0:1] # Limit here for only some tests

start = time.time()
models = []
for brand_url in brands:
    models.extend(get_models(brand_url))
     
#models = models[0:1] # Limit here for only some tests

print ('Fetched ' + str(len(models)) + ' total models for all brands\n')      
show_elapsed(start)

start = time.time()
result = []
for model in models:
    result.append(get_info(model))
show_elapsed(start)

print ('Writing to file device_info_gsmarena.json')    
with open('device_info_gsmarena.json', 'w') as f:
  json.dump(result, f, ensure_ascii=False)

print('Done')
