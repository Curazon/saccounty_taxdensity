import csv
import os
import requests
import json
from bs4 import BeautifulSoup

#folsom appears to begin at 69
#this may have been pointless...
# map_book_num = 72 #3 leading 0
# page_num = 85 #3 leading 0
# block_num = 0
# parcel_num = 30 #3 leading 0's
# div_num = 0 #4 leading 0's

# bad_map = 0
# bad_page = 0 
# bad_block = 0
# bad_parcel = 0 
# bad_div = 0

def judge(parcel_dict, tickType, tickBool):

    #if parcel exists
    if tickBool:
        # bad_track = 0
        #if bottom of parcel
        # if tickType == 'div_num':
        if tickType == 'parcel_num':
            parcel_dict[tickType] += 1
        
        else:
            parcel_dict[tickType] += 0
            tickType = downshift(tickType)
            parcel_dict[tickType] = 1
    
    #if parcel doesn't exist
    else:
        
        # if bad_track > 2:
        #if top of parcel
        if tickType == 'map_book_num':
            parcel_dict[tickType] += 1

        else:
            parcel_dict[tickType] = 0
            tickType = upshift(tickType)
            parcel_dict[tickType] += 1

        # bad_track = bad_track + 1
        # parcel_dict[tickType] += 1

    return(parcel_dict, tickType)


def downshift(tickType):
    if tickType == 'map_book_num':
        tickType = 'page_num'

    elif tickType == 'page_num':
        tickType = 'block_num'

    elif tickType == 'block_num':
        tickType = 'parcel_num'

    elif tickType == 'parcel_num':
        tickType = 'div_num'

    return(tickType)

def upshift(tickType):
    if tickType == 'div_num':
        tickType = 'parcel_num'

    elif tickType == 'parcel_num':
        tickType = 'block_num'

    elif tickType == 'block_num':
        tickType = 'page_num'

    elif tickType == 'page_num':
        tickType = 'map_book_num'

    return(tickType)

def increment(parcel_dict, tickType, tickBool):

    if tickBool:
        parcel_dict[tickType] += 1

    else:


parcel_dict = {'map_book_num': 69,
               'page_num' : 0,
               'block_num' : 0,
               'parcel_num' : 0,
               'div_num' : 0
              }

bad_dict = {'bad_map' : 0,
            'bad_page' : 0,
            'bad_block' : 0,
            'bad_parcel' : 0
            # 'bad_div' : 0
           }

tick_dict = {'tick_map' : False,
             'tick_page' : False,
             'tick_block' : False,
             'tick_parcel' : True
            #  'tick_div' : True
            }

limit_dict = {'limit_map' : 72,
             'limit_page' : 500,
             'limit_block' : 5,
             'limit_parcel' : 200
            #  'tick_div' : True
            }

with open('tax_density_test.csv', "wb") as tax_density:
    writer = csv.writer(tax_density)
    writer.writerow(['City', 'Address', 'Parcel_Num', 'Tax', 'Lot_Size', 'Tax_Density'])

    # bad_track = 0
    loop_track = 0
    tickType = 'parcel_num'

    while loop_track < 2500:

        full_parcel = str(parcel_dict['map_book_num']).zfill(3) + \
                      str(parcel_dict['page_num']).zfill(3) + \
                      str(parcel_dict['block_num']) + \
                      str(parcel_dict['parcel_num']).zfill(3) + \
                      str(parcel_dict['div_num']).zfill(4) 

        # url = 'https://eproptax.saccounty.net/#BillSummary/'

        # print(full_parcel, ' exists.')
        xhr_url = 'https://eproptax.saccounty.net/service/EPropTax.svc/rest/BillSummary?parcel=' + full_parcel

        sqft_url = 'http://assessorparcelviewer.saccounty.net/GISWebService/GISWebservice.svc/parcels/public/' + full_parcel 

        with requests.Session() as session:

            tax_res = session.get(xhr_url)
            sqft_res = session.get(sqft_url)

            try:
                t = json.loads(tax_res.content)
                sq = json.loads(sqft_res.content)  
            
            except ValueError:
                print(full_parcel, ValueError)
                tickBool = False

                parcel_dict, tickType = judge(parcel_dict, tickType, tickBool)
                continue

            #if there's a sqft and parcel exists and it's taxable
            if sq['LotSize'] and 'HelpLink' not in t and t['Bills']:

                tickBool = True
      
                folsomAddress = ' '.join(t['GlobalData']['Address'].split())
                squareFootage = sq['LotSize']
                fullTax = t['Bills'][0]['BillAmount']
                taxDensity = round((float(fullTax)/float(squareFootage)), 2)
    
                writer.writerow([t['GlobalData']['City'], folsomAddress, full_parcel, fullTax, squareFootage, taxDensity])

                parcel_dict, tickType = judge(parcel_dict, tickType, tickBool)                

                print(parcel_dict, tickType, tickBool)
                print( full_parcel )
                print('\n')

            else:

                tickBool = False

                parcel_dict, tickType = judge(parcel_dict, tickType, tickBool)                

                # print(parcel_dict, tickType, tickBool)
                # print( full_parcel )
                # bad_track += 1
                # print('\n')
        
        loop_track += 1