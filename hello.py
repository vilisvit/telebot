def number(i):
    return i[1]

symbols=list(input())
symbol_pairs=[]
dict_of_symbols = {}
for name in symbols:
    if name in dict_of_symbols:
        dict_of_symbols[name] += 1
    else:
        dict_of_symbols[name] = 1
symbol_pairs = list(dict_of_symbols.items())
symbol_pairs.sort(key=number, reverse=1)
print(ord(symbol_pairs[0][0]))