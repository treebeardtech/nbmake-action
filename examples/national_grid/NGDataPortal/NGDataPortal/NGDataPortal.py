"""
Imports
"""
import pandas as pd
import warnings
import requests
import json
import os

"""
Main Scripts
"""
## Loading static files
resource_filepath = os.path.join(os.path.dirname(__file__), 'stream_to_resource_id.json')
with open(resource_filepath, 'r') as fp:
    stream_2_id_map = json.load(fp)
    
## Main class
class Wrapper():
    def __init__(self, stream):
        self.stream = stream
        self.resource_id = stream_2_id_map[self.stream]
        self.streams = list(stream_2_id_map.keys()) 
        
    def NG_request(self, params={}):    
        url_root = 'https://national-grid-admin.ckan.io/api/3/action/datastore_search'

        params.update({'resource_id':self.resource_id})

        if 'sql' in params.keys():
            url_root += '_sql'

        r = requests.get(url_root, params=params)

        return r

    def raise_(self, err_txt, error=ValueError): 
        raise error(err_txt)

    def check_request_success(self, r_json):
        if r_json['success'] == False:
            err_msg = r_json['error']['message']
            self.raise_(err_msg)

    date_between = lambda self, dt_col, start_date, end_date: f'SELECT * from "{self.resource_id}" WHERE "{dt_col}" BETWEEN \'{start_date}\'::timestamp AND \'{end_date}\'::timestamp ORDER BY "{dt_col}"' 
    date_less_than = lambda self, dt_col, date: f'SELECT * from "{self.resource_id}" WHERE "{dt_col}" < \'{date}\'::timestamp ORDER BY "{dt_col}"' 
    date_greater_than = lambda self, dt_col, date: f'SELECT * from "{self.resource_id}" WHERE "{dt_col}" > \'{date}\'::timestamp ORDER BY "{dt_col}"' 

    def form_dt_rng_sql_query(self, dt_col, start_date=None, end_date=None):
        start_end_date_exist = (start_date!=None, end_date!=None)

        func_map = {
            (False, False) : {'error' : 'A start and/or end date should be passed'},
            (True, True) : self.date_between(dt_col, start_date, end_date),
            (False, True) : self.date_less_than(dt_col, end_date),
            (True, False) : self.date_greater_than(dt_col, start_date),
        }

        sql = func_map[start_end_date_exist]

        if not isinstance(sql, str):
            self.raise_(sql['error'])

        return sql

    def query_API(self, params={}, start_date=None, end_date=None, dt_col=None, sql='', return_raw=False):
        ## Handling SQL queries
        if start_date or end_date:
            if sql != '':
                warnings.warn('The start and end date query will overwrite the provided SQL')

            if not dt_col:
                warnings.warn('If a start or end date has been provided the \'dt_col\' parameter must be provided')

            sql = self.form_dt_rng_sql_query(dt_col, start_date=start_date, end_date=end_date)
            params.update({'sql':sql})

        elif sql != '':
            params.update({'sql':sql})
            
        elif 'sql' in params.keys():
            params.pop('sql')

        print(params)
        ## Making the request
        r = self.NG_request(params=params)

        if return_raw == True:
            return r

        ## Checking and parsing the response
        r_json = r.json()
        self.check_request_success(r_json)

        df = pd.DataFrame(r_json['result']['records'])

        return df

    
if __name__ == "__main__":
    main()
