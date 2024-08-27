import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
from functools import reduce

#Some inputs for the User - could be changed from prompts to hard coded values
user = 'apgolf1717'
pw = 'Helten17'
excel = r"C:\Users\apgol\OneDrive\Documents\Health_Dashboard\peloton.xlsx"

#Authenticate the user
s = requests.Session()
payload = {'username_or_email': user, 'password':pw}
s.post('https://api.onepeloton.com/auth/login', json=payload)

'''First API Call - GET User ID for all other Calls'''
#Get User ID to pass into other calls
me_url = 'https://api.onepeloton.com/api/me'
response = s.get(me_url)
apidata = s.get(me_url).json()

#Flatten API response into a temporary dataframe
# df_my_id = json_normalize(apidata, 'id', ['id'])
# df_my_id_clean = df_my_id.iloc[0]
my_id = apidata['id']

'''Second API Call - GET Workout, Ride & Instructor Details''' 
#API URL - 
df_workout_list=[]
for i in range(4):
    url = 'https://api.onepeloton.com/api/user/{}/workouts?joins=ride,ride.instructor&limit=250&page={}'.format(my_id,i)
    response = s.get(url)
    data = s.get(url).json()
    
    #Flatten API response into a temporary dataframe
    df_workouts_raw = json_normalize(data['data'])
    
    #Keep only necessary columns as a new pandas dataframe - this list can be modified based on the user's 
    #preference.  Right now, primarily excluding duplicated columns, excess ID columns, and social media
    #columns for the Instructors
    df_workouts = df_workouts_raw.drop(df_workouts_raw.columns[[4, 5, 11, 13, 
    15, 16, 17, 20, 24, 25, 27, 28, 29, 31, 32, 33, 35, 37, 39, 40, 41, 42, 
    43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60, 63, 
    64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 82, 
    83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 96, 97, 98, 99, 100, 103, 
    105, 106, 107, 108]], axis = 1)
    df_workout_list.append(df_workouts)
    
    #Print Message Workout Data Complete
df_workouts = pd.concat(df_workout_list)
print('Workout Data processing complete')

'''Third API Call - GET Workout Metrics''' 
#Create Dataframe of Workout IDs to run through our Loop
df_workout_ids = df_workouts.filter(['id'], axis=1)

#Define the imputs for the for loop
workout_ids = df_workout_ids.values.tolist()
workout_ids2 = [i[0] for i in workout_ids]

#Create empty dataframes to write iterations to
df_tot_metrics = pd.DataFrame([])
df_avg_metrics = pd.DataFrame([])

for workout_id in workout_ids2:
     response2 = s.get('https://api.onepeloton.com/api/workout/{}/performance_graph?every_n=300'.format(workout_id))
     data2 = response2.json()
     #Flatten API response into a temporary dataframe - exception handling because each workout type has a 
     #different structure to the API response, with different metrics.  Additionally, this call also generates
     #a number of rows so we have to transpose and flatten the dataframe.
     try:
          df_avg_raw = json_normalize(data2['average_summaries'])
     except:
          pass
     else:
          df_avg_raw = json_normalize(data2['average_summaries'])
          df_avg_stg = df_avg_raw.T
     try:
          df_avg_stg.columns = df_avg_stg.iloc[0]
     except:
          pass
     else:
          df_avg_stg.columns = df_avg_stg.iloc[0]
          df_avg = df_avg_stg.drop(['display_name', 'slug', 'display_unit'])
          df_avg['id'] = workout_id
     try:
          df_tot_raw = json_normalize(data2['summaries'])
     except:
          pass
     else:
          df_tot_raw = json_normalize(data2['summaries'])
          df_tot_stg = df_tot_raw.T
     try:
          df_tot_stg.columns = df_tot_stg.iloc[0]
     except:
          pass
     else:
          df_tot_stg.columns = df_tot_stg.iloc[0]
          df_tot = df_tot_stg.drop(['display_name', 'slug', 'display_unit'])
          df_tot['id'] = workout_id
     #Append each run through the loop to the dataframe
     df_tot_metrics = df_tot_metrics.append(df_tot, sort=False)
     try:
          df_avg_metrics = df_avg_metrics.append(df_avg, sort=False)
     except:
          pass
     else:
          df_avg_metrics = df_avg_metrics.append(df_avg, sort=False)

df_tot_metrics_clean = df_tot_metrics.drop_duplicates()
df_avg_metrics_clean = df_avg_metrics.drop_duplicates()
df_workout_metrics = df_avg_metrics_clean.merge(df_tot_metrics_clean, left_on='id', right_on='id', how='right')

#Print Message Workout Metrics Complete
print('Workout Metrics processing complete')


#Left outer join of the Workout Data and Metrics
df_peloton_final_stg = df_workouts.merge(df_workout_metrics, left_on='id', right_on='id', how='left')

df_peloton_final = df_peloton_final_stg
df_peloton_final['created_at'] = pd.to_datetime(df_peloton_final_stg['created_at'], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York')
df_peloton_final['end_time'] = pd.to_datetime(df_peloton_final_stg['end_time'], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York')
df_peloton_final['start_time'] = pd.to_datetime(df_peloton_final_stg['start_time'], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York')


df_peloton_final['created_at']=df_peloton_final['created_at'].dt.tz_localize(None)
df_peloton_final['end_time']=df_peloton_final['end_time'].dt.tz_localize(None)
df_peloton_final['start_time']=df_peloton_final['start_time'].dt.tz_localize(None)
df_peloton_final['duration'] = ((df_peloton_final.end_time - df_peloton_final.start_time).dt.seconds)/60



df_peloton_final = df_peloton_final[['created_at','start_time','end_time','duration','name','ride.difficulty_rating_avg','ride.instructor.name','effort_zones.total_effort_points',
                                     'Avg Output','Avg Cadence','Avg Resistance','Avg Speed',
                                     'Calories','Total Output','Distance']]

df_peloton_final.to_excel(excel)




#Success!
print('Full data exported to Excel!')