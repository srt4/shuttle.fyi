import requests
import time
import pytz
from datetime import datetime 
from collections import OrderedDict

class Arrival(): 
    def __init__(self, route_id, route_headsign, arrival_time): 
        self.route_id = route_id
        self.route_headsign = route_headsign
        self.arrival_time = arrival_time

class Arrivals(): 
    def __init__(self, route_id, route_headsign, arrival_time): 
        self.route_id = route_id 
        self.route_headsign = route_headsign 
        self.arrival_times = [arrival_time]

    def add_arrival_time(self, arrival_time): 
        self.arrival_times.append(arrival_time)

class ArrivalsProvider(): 

    def get_arrivals(self): 
        # need to transform this into a data structure keyed by route 
        return self.group_and_sort_arrivals(
            # Elliot Way and Prospect St NB 
            self.get_onebusaway_arrivals('1_14070') + 
            # Elliot Way and Prospect St SB 
            self.get_onebusaway_arrivals('1_13890') +
            # Bothell / Kirkland  
            self.get_shuttle_arrivals('11', 'BK')  + 
            # Bellevue 
            self.get_shuttle_arrivals('16', 'B') + 
            # Westlake
            self.get_shuttle_arrivals('6', 'W') + 
            # Issaquah 
            self.get_shuttle_arrivals('2', 'I') + 
            # King Street
            self.get_shuttle_arrivals('12', 'KS') + 
            # Redmond
            self.get_shuttle_arrivals('8', 'R')
        )

    def group_and_sort_arrivals(self, arrivals):
        grouped_arrivals = OrderedDict()
        for arrival in sorted(arrivals, key = lambda arrival: arrival.arrival_time):
            # route ID is not unique enough - as it does not indicate direction 
            route_key = arrival.route_id + arrival.route_headsign 
            if arrival.arrival_time < 7:
                continue
            if route_key in grouped_arrivals: 
                grouped_arrivals[route_key].add_arrival_time(arrival.arrival_time)
            else: 
                grouped_arrivals[route_key] = Arrivals(
                    arrival.route_id, 
                    arrival.route_headsign, 
                    arrival.arrival_time
                )
        return grouped_arrivals.values()

    def get_shuttle_arrivals(self, route, route_id): 
        user_agent = {
            'User-agent': 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0'
        }
        response = requests.get('https://expedia.doublemap.com/map/v2/schedule?route=' + \
             route, headers = user_agent).json()
        
        arrivals = []
        route_name = response['route']['name']
        for arrival in response['schedule']:
            hour = int(arrival[0].split(':')[0])
            minute = int(arrival[0].split(':')[1])
            arrival_datetime = datetime.now().replace(hour=hour, minute=minute)
            arrival_time_minutes = int((arrival_datetime - datetime.now()).total_seconds()) / 60

            # hack
            if arrival_time_minutes > 40: 
                continue 

            arrivals.append(Arrival(
                route_id,
                route_name,
                arrival_time_minutes
            ))
        return arrivals

    def get_onebusaway_arrivals(self, stop_id): 
        response = requests.get(
            "http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/" +
            stop_id + ".json?key=TEST").json()
            
        arrivals = []
        for arrival_departure in response['data']['entry']['arrivalsAndDepartures']:
            arrival_time_s = int(arrival_departure['scheduledArrivalTime']) / 1000
            arrival_time_minutes = (arrival_time_s - int(time.time())) / 60
            arrivals.append(Arrival(
                arrival_departure['routeShortName'],
                arrival_departure['tripHeadsign'],
                arrival_time_minutes
            ))

        return arrivals