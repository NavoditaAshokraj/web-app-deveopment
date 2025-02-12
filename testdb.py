import shelve
'''
testing = {'test' : {'user1' : [4, 'Sengkang', 5],
           'user2' : [10, 'Sengkang', 1],
           'user3' : [1, 'Sengkang', 2],
           'user4' : [5, 'Bukit Panjang', 4],
           'user5' : [12,'Punggol', 4],
           'user6' : [10, 'Punggol', 3],
           'user7' : [11, 'Yishun', 4]}}

with shelve.open('storage.db', 'r') as db:
    users = list(db['test'].keys())
    visits = [value[0] for value in db['test'].values()]
    location = [value[1] for value in db['test'].values()]
    ratings = [value[2] for value in db['test'].values()]
    print(users, visits, ratings, location)

testing = {'reports' : {'location_distribution_20240803094757.pdf' : 'Reports\location_distribution_20240803094757.pdf',
           'location_distribution_20240803094805.pdf' : 'Reports\location_distribution_20240803094805.pdf',
           'location_distribution_20240803094807.pdf' : 'Reports\location_distribution_20240803094807.pdf',
           'navo' : 'Reports\\navo.pdf',
           'nova' : 'Reports\\nova.pdf'}}
'''
testing = {'test' : {'user1' : [4, 'Sengkang', 5],
           'user2' : [10, 'Sengkang', 1],
           'user3' : [1, 'Sengkang', 2],
           'user4' : [5, 'Bukit Panjang', 4],
           'user5' : [12,'Punggol', 4],
           'user6' : [10, 'Punggol', 3],
           'user7' : [11, 'Yishun', 4]}}
# Open the shelve database
with shelve.open('storage.db', 'c') as db:
    db['test'] = testing['test']
    print(db['test'])







