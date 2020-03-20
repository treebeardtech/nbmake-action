# National Grid Data Portal API Wrapper

<br>

### Overview

<b>About the Portal</b>
 
The new <a href="https://data.nationalgrideso.com/">National Grid ESO Data Portal</a> was created in order to provide a <i>"centralised repository for published ESO data"</i> through means of a public API backed by a CKAN database. Currently it is still in Beta and the layout of the API as well as its contents may be subject to future change, furthermore it should be noted that during this stage the data streams may be updated later than their historic counterparts.

<br>

<b>About this Wrapper</b>

This module creates a Python wrapper around the Data Portal API, providing a more natural way to query data from the National Grid. It has been developed in such a way as to quickly speed up common requests but also enable the full capabilities provided through CKAN. If you have any ideas for the module please feel free to contribute.

<br>
<br>

### Module Usage

<b>Getting Started</b>

The module's <i>Wrapper</i> class is the main interface with the API, it can be imported as follows:

```python
from NGDataPortal import Wrapper
```

n.b. if you haven't already downloaded the module you can use ```pip install NGDataPortal```

<br>

To query a data stream simply specifying the name when the wrapper class is initialised and then use the <i>.query_API()</i> method. To see what data streams are available you can use ```wrapper.streams``` which will return a list of those that are available.

```python
stream = 'embedded-wind-and-solar-forecasts'
wrapper = Wrapper(stream)

df = wrapper.query_API()

df.head()
```

_id|DATE_GMT|TIME_GMT|SETTLEMENT_DATE|SETTLEMENT_PERIOD|EMBEDDED_WIND_FORECAST|EMBEDDED_WIND_CAPACITY|EMBEDDED_SOLAR_FORECAST|EMBEDDED_SOLAR_CAPACITY
---|---|---|---|---|---|---|---|---
1|20200120|1330|2020-01-20T00:00:00|27|1499|6465|3635|13080
2|20200120|1400|2020-01-20T00:00:00|28|1486|6465|3243|13080
3|20200120|1430|2020-01-20T00:00:00|29|1471|6465|2594|13080
4|20200120|1500|2020-01-20T00:00:00|30|1456|6465|1787|13080
5|20200120|1530|2020-01-20T00:00:00|31|1458|6465|977|13080

<br>

<b>Filtering for a Date Range</b>

Often you may wish to specify a specific date range to be requested, this can be achieved in a number of ways. If only the <i>start_date</i> is provided then all observations since that date will be returned, the inverse is true if only <i>end_date</i> is specified. When both are provided the response will be from between those dates.

When you wish to query a date range you must also provided the <i>dt_col</i> which informs the API which column it will be operating the date filtering over. Once the API format has been stabilised this will be automated within the module.

```python
stream = 'current-balancing-services-use-of-system-bsuos-data'
wrapper = Wrapper(stream=stream)

start_date = '2019-12-20'
end_date = '2019-12-22'
dt_col = 'Settlement Day'

df = wrapper.query_API(start_date=start_date, end_date=end_date, dt_col=dt_col)

df.head()
```

Settlement Period|Half-hourly Charge|Run Type|Total Daily BSUoS Charge|BSUoS Price (£/MWh Hour)|Settlement Day|_id
---|---|---|---|---|---|---
1|119,542.669|II|5,585,971.58|4.89096|2019-12-20T00:00:00|47667
2|135,592.386|II|5,585,971.58|5.40753|2019-12-20T00:00:00|47668
3|168,776.958|II|5,585,971.58|6.79153|2019-12-20T00:00:00|47669
4|153,525.796|II|5,585,971.58|6.21355|2019-12-20T00:00:00|47670
5|136,545.346|II|5,585,971.58|5.63209|2019-12-20T00:00:00|47671

<br>

<b>Fully Extensible Queries</b>

One of the advantages in the National Grid opting to use a CKAN backend for the API is that it enables PostgreSQL queries to be directly carried out.

As an example we'll formally define the SQL string that is created 'under-the-hood' when a date range request is carried out.

```python
stream = 'generation-mix-national'
wrapper = Wrapper(stream)

SQL_query = 'SELECT * from "0a168493-5d67-4a26-8344-2fe0a5d4d20b" WHERE "dateTime_from" BETWEEN \'2019-12-30\'::timestamp AND \'2019-12-31\'::timestamp ORDER BY "dateTime_from"'
df = wrapper.query_API(sql=SQL_query)

df.head()
```

dateTime_from|nuclear_perc|wind_perc|hydro_perc|coal_perc|gas_perc|other_perc|imports_perc|solar_perc|dateTime_to|_id|biomass_perc
---|---|---|---|---|---|---|---|---|---|---|---
2019-12-30T00:00:00|25.7|36.3|2.3|1.7|16.4|0.4|6.9|0|2019-12-30T00:30:00|95|10.3
2019-12-30T00:30:00|25.9|36.8|2.3|1.4|15.8|0.5|6.9|0|2019-12-30T01:00:00|94|10.4
2019-12-30T01:00:00|26.2|36.8|2.2|1.4|15.8|0.5|6.7|0|2019-12-30T01:30:00|93|10.4
2019-12-30T01:30:00|26.3|36.6|2.2|1.4|15.7|0.5|6.8|0|2019-12-30T02:00:00|92|10.5
2019-12-30T02:00:00|26.1|37.2|1.9|1.4|15.6|0.5|7.1|0|2019-12-30T02:30:00|91|10.2
