import sp_api.api
import json
import pandas as pd
import time
from datetime import datetime
import pyodbc
import random


#with open('creds/amznapi.json','r') as f:
#    credentials = json.load(f)

credentials=dict(refresh_token="Atzr|IwEBIFsyhqfHMlwodV533aZhocYpUn8OJhLZP0JoQcJN_oQR-jfWkBRWeA6_qlwEJKE7ZLFfux6bLj_psQMzk-L7d2MSRCJJEnkAc7mGnhqB_e4lKQ9fyTNjdbR4LLjaPVfL-_y3x63_iwvkrdK7L3998n4tEXlWOBvuW5yk8hzEXURpUdLMSVGZEQMSRQQQwYtPBVYe244bRRqtPlEq9yesZl_OFTaaUqvpRIPNlw0BHQLm-KmhKGvZjxlD5s9W84pbPlCMjUaEBllZWZuSEorCypOTCYSZyYokrv2EyWbYtuc9ns5_tWaE8PYBfEJlytiJNDI",
    lwa_app_id="amzn1.application-oa2-client.c16ff2050ed14929b6337043a4f00700",
    lwa_client_secret="amzn1.oa2-cs.v1.d3a818bab81c15d54f7e67e0ba0b88f3cbbd1860244c7d168ce3e1cf9a83edf4")


def GetMissingMain(startDate,endDate):
    
    amzn = getOrders(startDate, endDate)
    amzn.rename(columns={'AmazonOrderId':'custpo'},inplace=True)
    
    missing = getSXData(amzn)

    #missing = merged.loc[merged['order-status'] == 'Shipped']
    
    return missing


def getSXData(amzn): 
    password = 'U{M[dr`WC?A%jrsvtO'
    conn = pyodbc.connect('Driver={SQL Server};'
                         'Server=tsc-v-sql;'
                         'Database=TurnerPimCatalog;'
                         'UID=ross;'
                         f'PWD={password};')
    
    tables_df = pd.read_sql("SELECT * FROM dbo.[SX.oeeh] WHERE custno=130344", conn)

    tables_custpo = tables_df[['custpo']]

    merged = amzn.merge(tables_custpo, on='custpo',how='left',indicator=True).query('_merge == "left_only"')
    
    return merged



def getOrders(startDate,endDate):
    #todays_Date = datetime.now().date() - timedelta(days=5)

    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d')

    startDateISO = startDate.isoformat()
    endDateISO = endDate.isoformat()

    query = sp_api.api.Orders(credentials=credentials).get_orders(CreatedAfter=startDateISO, CreatedBefore=endDateISO, OrderStatuses='Shipped')

    payload = query.payload

    orders_list = query.Orders
    exBackoff = 0
    throttled = 0

    while payload.get('NextToken') != None:
        try:
            print(throttled)
            if throttled > 0:
                exBackoff = throttled 

            rFloat = round(random.uniform(0,1), 3) 
            time.sleep(exBackoff + rFloat)

            next_token= payload['NextToken']
            print(next_token)

            query = sp_api.api.Orders(credentials=credentials).get_orders(NextToken=next_token)
            payload = query.payload

            orders_list.extend(query.Orders)
            throttled = 0
            exBackoff = 0

        except sp_api.base.SellingApiRequestThrottledException:
            print('Amazon Throttle Error: Attempting to rerun last token')
            throttled +=1

    df_all = pd.DataFrame(orders_list)
    df = df_all[['AmazonOrderId','SellerOrderId', 'PurchaseDate','LastUpdateDate','OrderStatus','NumberOfItemsShipped','FulfillmentChannel','SalesChannel','ShipServiceLevel','OrderTotal','MarketplaceId']]

    
    return df



