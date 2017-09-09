import csv
import os
import requests
import json
from bs4 import BeautifulSoup

#folsom appears to begin at 69
#000-000-0-000-0000
# map_book_num = 72 #3 leading 0
# page_num = 85 #3 leading 0
# block_num = 0
# parcel_num = 30 #3 leading 0's
# div_num = 0 #4 leading 0's

def downshift(tickType):
    if tickType == 'map_book_num':
        tickType = 'page_num'

    elif tickType == 'page_num':
        tickType = 'block_num'

    elif tickType == 'block_num':
        tickType = 'parcel_num'

    # elif tickType == 'parcel_num':
    #     tickType = 'div_num'

    return(tickType)

def upshift(tickType):
    # if tickType == 'div_num':
    #     tickType = 'parcel_num'

    if tickType == 'parcel_num':
        tickType = 'block_num'

    elif tickType == 'block_num':
        tickType = 'page_num'

    elif tickType == 'page_num':
        tickType = 'map_book_num'

    return(tickType)

def increment(parcel_dict, limit_dict, tickType, loop_track):

    #if current parcel num is less than limit
    if parcel_dict[tickType] < limit_dict[tickType]:

        #at bottom number
        if tickType == 'parcel_num':
            parcel_dict[tickType] += 1
        
        #increment current num then downshift
        else:
            # parcel_dict[tickType] = 0
            tickType = downshift(tickType)
            parcel_dict[tickType] += 1

    #limit has been hit
    else:

        #hit limit of top num
        if tickType == 'map_book_num':
            print("This is probably the end of the line.")
            loop_track = False

        #reset current num and then upshift
        else:
            parcel_dict[tickType] = 0
            tickType = upshift(tickType)
            parcel_dict[tickType] += 1

    # full_parcel = str(parcel_dict['map_book_num']).zfill(3) + \
    #             str(parcel_dict['page_num']).zfill(3) + \
    #             str(parcel_dict['block_num']) + \
    #             str(parcel_dict['parcel_num']).zfill(3) + \
    #             str(parcel_dict['div_num']).zfill(4) 
    
    # print(full_parcel)

    return(parcel_dict, tickType, loop_track)

parcel_dict = {'map_book_num': 69,
               'page_num' : 71,
               'block_num' : 0,
               'parcel_num' : 0,
               'div_num' : 0
              }

# parcel_dict = {'map_book_num': 69,
#                'page_num' : 71,
#                'block_num' : 0,
#                'parcel_num' : 201,
#                'div_num' : 0
#               }

limit_dict = {'map_book_num' : 69,
              'page_num' : 71,
              'block_num' : 5,
              'parcel_num' : 200
            #  'tick_div' : True
            }

# limit_dict = {'map_book_num' : 69,
#               'page_num' : 500,
#               'block_num' : 5,
#               'parcel_num' : 200
#             #  'tick_div' : True
#             }

with open('tax_density_test.csv', "wb") as tax_density:
    writer = csv.writer(tax_density)
    writer.writerow(['City', 'Address', 'Parcel_Num', 'Tax', 'Lot_Size', 'Tax_Density'])

    loop_track = True
    tickType = 'parcel_num'

    while loop_track:

        full_parcel = str(parcel_dict['map_book_num']).zfill(3) + \
                      str(parcel_dict['page_num']).zfill(3) + \
                      str(parcel_dict['block_num']) + \
                      str(parcel_dict['parcel_num']).zfill(3) + \
                      str(parcel_dict['div_num']).zfill(4) 

        # url = 'https://eproptax.saccounty.net/#BillSummary/'

        xhr_url = 'https://eproptax.saccounty.net/service/EPropTax.svc/rest/BillSummary?parcel=' + full_parcel

        sqft_url = 'http://assessorparcelviewer.saccounty.net/GISWebService/GISWebservice.svc/parcels/public/' + full_parcel 

        with requests.Session() as session:

            tax_res = session.get(xhr_url)
            sqft_res = session.get(sqft_url)

            try:
                t = json.loads(tax_res.content)
                sq = json.loads(sqft_res.content)  
            
            except ValueError:
                # print(full_parcel, ValueError)

                parcel_dict, tickType, loop_track = increment(parcel_dict, limit_dict, tickType, loop_track)
                continue

            #if there's a sqft and parcel exists and it's taxable
            if sq['LotSize'] and 'HelpLink' not in t and t['Bills']:
      
                folsomAddress = ' '.join(t['GlobalData']['Address'].split())
                squareFootage = sq['LotSize']
                fullTax = t['Bills'][0]['BillAmount']
                taxDensity = round((float(fullTax)/float(squareFootage)), 2)
    
                writer.writerow([t['GlobalData']['City'], folsomAddress, full_parcel, fullTax, squareFootage, taxDensity])

                parcel_dict, tickType, loop_track = increment(parcel_dict, limit_dict, tickType, loop_track)                

            else:

                parcel_dict, tickType, loop_track = increment(parcel_dict, limit_dict, tickType, loop_track)                
