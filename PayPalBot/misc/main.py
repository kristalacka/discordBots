from paypal import PayPalInterface
from datetime import datetime, timedelta
paypal_api = PayPalInterface(API_USERNAME="kristalacka-facilitator_api1.gmail.com",
                             API_PASSWORD="XZC39A9CVNLCCXKL",
                             API_SIGNATURE="A--8MSCLabuvN8L.-MHjxC9uypBtAnOVL5WvYlhXEUS0rgxbR1f8vLMK",
                             DEBUG_LEVEL=0,
                             HTTP_TIMEOUT=30)

date_end = datetime.utcnow()
minute = timedelta(seconds = 60)
date_start = date_end-minute
date_start = date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
transactions = paypal_api._call('TransactionSearch',
                                STARTDATE=date_start,
                                STATUS="Success")

transIds = []
for key, item in transactions.items():
  if (key[:15]=='L_TRANSACTIONID'):
    transIds.append(item)

for i in transIds:
  info = paypal_api._call('GetTransactionDetails',
                          TRANSACTIONID=i)
  print(info)
  
