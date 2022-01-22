<<<<<<< Updated upstream
STORE_LIST = {
  "1" : "Amazon",
  "2" : "Dell"
}

print("These are the available stores:")
print('{:<5} {:<20}'.format('Code', 'Store'))
for c, s in STORE_LIST.items():
  s = store
  print('{:<5} {:<20}'.format(c, store))

STORE_SELEC = input('\n\n',"Enter the store's code: ")

return STORE_SELEC
=======
from cProfile import label


AVAILABLE_STORES = {
    '1' : 'Amazon',
    '2' : 'Dell'
}

print('Current available stores:')
print("{:<8} {:<15}".format('CODE','STORE'))
for k, s in AVAILABLE_STORES.items():
   label = s
   print("{:<8} {:<15}".format(k, label))
print()

PRODUCT_STORE = input('Enter the store code: ')
#PRODUCT_URL = input('Paste the URL to the page of the product: ')

print('Connecting to', AVAILABLE_STORES[PRODUCT_STORE], '...')
>>>>>>> Stashed changes

