import os

domain_dic = {}
with open('node_domains', 'r') as file:
    for line in file:
        key, value = line.strip().split(':')
        domain_dic[key] = value
print(domain_dic)

for key in domain_dic.keys():
    output = os.popen(f'dig {key} +short').read().strip()
    if output:
        print(output)
    else:
        print("none")

