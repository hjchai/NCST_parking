import pandas as pd

taz_csv = pd.read_csv('downtown_taz.csv')
tazs = taz_csv['taz_key']

print(tazs)

iter_csv = pd.read_csv('../Caroline_NCST_Data/Scenario_1/indivTripData_5.csv', iterator = True, chunksize = 1000)
#iter_csv = pd.read_csv('test.csv', iterator = True, chunksize = 1000)
# filter out trip records that are related to roi_tazs
df = pd.concat([chunk[ (chunk['orig_taz'].isin(tazs)) | (chunk['dest_taz'].isin(tazs)) ] for chunk in iter_csv])


df.to_csv('indivTripData_5_roi.csv', index = False)
print('Filtering done!')

#| (chunk['dest_taz'] in tazs)