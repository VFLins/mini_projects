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

