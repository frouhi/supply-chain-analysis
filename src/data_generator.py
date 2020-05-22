"""
 This code randomly generates jason data in the format close to data available by
 SPLC<GO> command in Bloomberg terminal.
 I wrote this program to demonstrate my interest in Bloomberg and Bloomberg tech,
 and to demonstrate my problem solving skills.
 Author: Farhang Rouhi
"""
import json
import random


COMPANY_COUNT = 100
MAX_EDGE = 5
PRODUCT_COUNT = 5
PRODUCTION_VOLUME_MAX = 200
data = {}


def add_unique_node(node_list, current_company):
    """
    Adds a random node that has not already been added
    :param node_list: list of current nodes
    :param current_company: name of the company we are generating
    """
    selected_company = int(random.random() * COMPANY_COUNT)
    while selected_company in node_list or current_company == selected_company:
        selected_company = int(random.random() * COMPANY_COUNT)
    node_list.append(selected_company)


for i in range(COMPANY_COUNT):
    company = {"name": i,  "product": int(random.random() * PRODUCT_COUNT),
               "production_volume": random.random()*PRODUCTION_VOLUME_MAX+1, "suppliers": [], "costumers": []}
    for j in range(MAX_EDGE):
        if random.random()>=0.5:
            add_unique_node(company["costumers"],company["name"])
    if not company["costumers"]:
        add_unique_node(company["costumers"],company["name"])
    data[str(i)] = company

for i in range(COMPANY_COUNT):
    for customer in data[str(i)]["costumers"]:
        data[str(customer)]["suppliers"].append(i)

print(data)
file = open("../data/data.json",'w')
file.write(json.dumps(data))