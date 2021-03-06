import io
import random
import sys
import json
import networkx as nx
import datetime

import matplotlib 
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import dbconnector.dbconnector as dbcon
from subnet import Subnet

###
# create plots for website
###
class Plotter():
    def __init__(self, datadb, subnet):
        self.datadb = datadb
        self.sub = subnet
        self.font_size = 6

    #create diagram corresponding to filename
    def create_image(self, image_name, dark = 1):
        if dark:
            plt.style.use('dark_background')
            rcParams.update({'figure.autolayout': True})
        else:
            plt.style.use('default')
            rcParams.update({'figure.autolayout': True})

        #create special image
        if image_name == "measurements_frequenc.png":
            fig = Figure()
            fig = self.measurements_frequenc()
            plt.close('all')

            return fig

        #create special image
        if image_name == "measurements_amount.png":
            fig = Figure()
            fig = self.measurements_amount()
            plt.close('all')

            return fig

        matplotlib.rc('xtick', labelsize=self.font_size) 
        matplotlib.rc('ytick', labelsize=self.font_size)
        
        #0: name (total => all, name => only for this person)
        #1: diagramtype
        #2: diagramsubtype
        #e.g. Total_2_2.png
        #split filename
        parts = image_name.split('_')
        fig_number = int(parts[1])
        fig_subplot =int(parts[2])

        if len(parts) > 3:
            from_date = parts[3]

            end = parts[4].split(".")
            to_date = end[0]
        else:
            from_date = self.datadb.get_first_measurement(parts[0])
            now = datetime.datetime.now()
            to_date = now.strftime("%Y-%m-%d")
    

        #creat plot
        fig = Figure()
        if(fig_number == 0):
            if(fig_subplot == 0):
                fig = self.distance_between_measurement(parts[0], from_date, to_date)
            elif(fig_subplot == 1):
                fig = self.distance_between_measurement_minutes(parts[0], from_date, to_date)
            elif(fig_subplot == 2):
                fig = self.measurement_during_day(parts[0], from_date, to_date)
            elif(fig_subplot == 3):
                fig = self.measurement_during_hour(parts[0], from_date, to_date)
            else:
                fig = self._create_random_figure()

        elif(fig_number == 1):
            if(fig_subplot == 0):
                fig = self.ip_distribution(parts[0], from_date, to_date)
            elif(fig_subplot == 1):
                fig = self.ip_distribution_trace(parts[0], from_date, to_date)
            elif(fig_subplot == 2):
                fig = self.isp_distribution(parts[0], from_date, to_date)
            elif(fig_subplot == 3):
                fig = self.isp_distribution_in_trace(parts[0], from_date, to_date)
            else:
                fig = self._create_random_figure()

        elif(fig_number == 2):
            if(fig_subplot== 0):
                fig = self.ip_vs_hour(parts[0], from_date, to_date)
            elif(fig_subplot == 1):
                fig = self.ip_in_trace_vs_hour(parts[0], from_date, to_date)
            elif(fig_subplot== 2):
                fig = self.isp_vs_time(parts[0], from_date, to_date)
            elif(fig_subplot== 3):
                fig = self.isp_in_trace_vs_time(parts[0], from_date, to_date)
            else:
                fig = self._create_random_figure()

        elif(fig_number == 3):
            if(fig_subplot == 0):
                fig = self.ip_change(parts[0], from_date, to_date)
            elif(fig_subplot== 1):
                fig = self.ip_change_vs_time(parts[0], from_date, to_date)
            elif(fig_subplot== 2):
                fig = self.ip_change_vs_time_vs_frequency(parts[0], from_date, to_date)
            elif(fig_subplot== 3):
                fig = self.isp_change(parts[0], from_date, to_date)
            elif(fig_subplot == 4):
                fig = self.isp_change_graph(parts[0], from_date, to_date, dark)
            elif(fig_subplot == 5):
                fig = self.isp_change_vs_hour(parts[0], from_date, to_date)
            else:
                fig = self._create_random_figure()

        elif(fig_number == 4):
            if(fig_subplot == 0):
                fig = self.city_distribution(parts[0], from_date, to_date)
            elif(fig_subplot== 1):
                fig = self.city_vs_ip(parts[0], from_date, to_date)
            elif(fig_subplot== 2):
                fig = self.city_change(parts[0], from_date, to_date)
            elif(fig_subplot== 3):
                fig = self.city_change_vs_time_vs_frequency(parts[0], from_date, to_date)
            elif(fig_subplot== 4):
                fig = self.city_graph(parts[0], from_date, to_date, dark)
            elif(fig_subplot== 5):
                fig = self.city_vs_isp(parts[0], from_date, to_date)
            else:
                fig = self._create_random_figure()

        else:
            fig = self._create_random_figure()

        plt.close('all')

        return fig

    #create image which shows how many measurements where taken in the last 20 days
    def measurements_frequenc(self):
        measurements=self.datadb.get_measurements_per_day_last_20()

        measurement_per_person = {}
        for i in measurements:
            if i[0] not in measurement_per_person.keys():
                measurement_per_person[i[0]] = [0 for k in range(20)]

            if i[1] == 20:
                continue

            measurement_per_person[i[0]][19-i[1]] += i[2]

        #create figure
        fig, axis = plt.subplots()

        for k in measurement_per_person.keys():
            axis.plot(range(len(measurement_per_person[k])), measurement_per_person[k], label=k)

        axis.legend(loc="lower left")

        #description
        #axis.set_title('Time between measurements (hour based)')
        axis.set_xlabel('Days sice today')
        #axis.set_ylabel('Percent')

        #set how many lables where needed and text for it
        axis.set_xticks(range(20))
        axis.set_xticklabels([i-19 for i in range(20)])

        return fig

    #diagram shows how many measurements everon had in the last 20 days
    def measurements_amount(self):
        measurements=self.datadb.get_measurements_per_day_last_20()
        persodata=self.datadb.get_persons()

        measurement_per_person = {}
        for i in measurements:
            if i[0] not in measurement_per_person.keys():
                measurement_per_person[i[0]] = [0 for k in range(20)]

            measurement_per_person[i[0]][19-i[1]] += i[2]

        aggregated = {}
        for person in measurement_per_person.keys():
            aggregated[person] = [0 for k in range(20)]

            amount = 0
            for p in persodata["persons"]:
                if p["name"] == person:
                    amount = int(p["number"])

            aggregated[person][19] = amount

            for i in range(len(aggregated[person])-1):
                aggregated[person][18-i] = aggregated[person][19-i] - measurement_per_person[person][19-i]

        #create figure
        fig, axis = plt.subplots()

        for k in aggregated.keys():
            axis.plot(range(len(aggregated[k])), aggregated[k], label=k)

        axis.legend(loc="upper left")

        #description
        #axis.set_title('Time between measurements (hour based)')
        axis.set_xlabel('Days sice today')
        #axis.set_ylabel('Percent')

        #set how many lables where needed and text for it
        axis.set_xticks(range(20))
        axis.set_xticklabels([i-19 for i in range(20)])

        return fig

    #create rondom plot
    def _create_random_figure(self, person="total", dark=1):
        fig, axis = plt.subplots()
        xs = range(100)
        ys = [random.randint(1, 50) for x in xs]
        #axis.set_title('Smarts')
        axis.set_xlabel('random')
        axis.set_ylabel('random')
        axis.plot(xs, ys)
        return fig

    #create plot that shows time between measurements
    def distance_between_measurement(self, person, from_date, to_date):
        #get timestamps from db
        timestamps = self.datadb.get_person_timestamps(person, from_date, to_date)

        #init count array
        total_count=[0 for i in range(24)] 

        #calculate difference between two timestamps and count 
        for i in range(0,len(timestamps)-1):
            t1 = int(timestamps[i][1].strftime("%H"))
            t2 = int(timestamps[i+1][1].strftime("%H"))

            idx = abs(t2-t1)
            total_count[idx] = total_count[idx]+1

        #calc percentage per entry
        values=[0.0 for i in range(24)] 
        sum_total = sum(total_count)

        #avoide devicion with 0
        if sum_total == 0:
            values = total_count
        else:
            #calc percentage
            for i in range(len(total_count)):
                values[i] = total_count[i] / sum_total

        #create label
        labels=[i for i in range(24)]

        #create figure
        fig, axis = plt.subplots()
        axis.bar(labels, values)

        #description
        #axis.set_title('Time between measurements (hour based)')
        axis.set_xlabel('Hours between measurements')
        axis.set_ylabel('Percent')

        #set how many lables where needed and text for it
        axis.set_xticks(labels)
        axis.set_xticklabels(labels)

        return fig

    # distance between measurements in minutes when they are less than one hour apart
    def distance_between_measurement_minutes(self, person, from_date, to_date):
                #get timestamps from db
        timestamps = self.datadb.get_person_timestamps(person, from_date, to_date)

        #init count array
        total_count=[0 for i in range(60)] 

        #calculate difference between two timestamps and count 
        for i in range(0,len(timestamps)-1):
            t1 = int(timestamps[i][1].strftime("%H"))
            t2 = int(timestamps[i+1][1].strftime("%H"))

            idx = abs(t2-t1)

            #check if distance is 0 ( 0 hours apart)
            if idx == 0:
                t1 = int(timestamps[i][1].strftime("%M"))
                t2 = int(timestamps[i+1][1].strftime("%M"))

                idx = abs(t2-t1)
                total_count[idx] = total_count[idx]+1

        #calc percentage per entry
        values=[0.0 for i in range(60)] 
        sum_total = sum(total_count)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = total_count
        else:
            #calc percentage
            for i in range(len(total_count)):
                values[i] = total_count[i] / sum_total

        #create label
        labels=[i for i in range(60)]

        #create figure
        fig, axis = plt.subplots()
        axis.bar(labels, values)

        #description
        #axis.set_title('Time between measurements (hour based)')
        axis.set_xlabel('Minutes between measurements')
        axis.set_ylabel('Percent')

        #set how many lables where needed and text for it
        axis.set_xticks(labels)
        axis.set_xticklabels(labels)

        return fig

    #create plot to display how many measurements where made per weekday
    def measurement_during_day(self, person, from_date, to_date):
        #get timestamps from db
        timestamps = self.datadb.get_person_timestamps(person, from_date, to_date)

        #init count array
        total_count=[0 for i in range(7)] 

        #count weekdays
        for i in range(0,len(timestamps)):
            twday = int(timestamps[i][1].strftime("%w"))
            total_count[twday] = total_count[twday]+1

        #calc percentage per entry
        values=[0.0 for i in range(7)] 
        sum_total = sum(total_count)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = total_count
        else:
            #calc percentage
            for i in range(len(total_count)):
                values[i] = total_count[i] / sum_total

        #create label
        labels=[i for i in range(7)]

        #create figure
        fig, axis = plt.subplots()
        axis.bar(labels, values)

        #description
        #axis.set_title('Measurement Day')
        #axis.set_xlabel('Week Day')
        axis.set_ylabel('Percent')

        #set how many lables where needed and text for it
        axis.set_xticks(labels)
        axis.set_xticklabels(["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"])

        return fig

    #create a plot which sohows measurement per hour
    def measurement_during_hour(self, person, from_date, to_date):
        #get timestamps from db
        timestamps = self.datadb.get_person_timestamps(person, from_date, to_date)

        #init count array
        total_count=[0 for i in range(24)] 

        #calculate difference between two timestamps and count 
        for i in range(0,len(timestamps)):
            t1 = int(timestamps[i][1].strftime("%H"))

            idx = t1
            total_count[idx] = total_count[idx]+1

        #calc percentage per entry
        values=[0.0 for i in range(24)] 
        sum_total = sum(total_count)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = total_count
        else:
            #calc percentage
            for i in range(len(total_count)):
                values[i] = total_count[i] / sum_total

        #create label
        labels=[i for i in range(24)]

        #create figure
        fig, axis = plt.subplots()
        axis.bar(labels, values)

        #description
        #axis.set_title('Time between measurements (hour based)')
        axis.set_xlabel('Time of day')
        axis.set_ylabel('Percent')

        #set how many lables where needed and text for it
        axis.set_xticks(labels)
        axis.set_xticklabels(labels)

        return fig

    #create diagram which shows ip adresses of the user and how often it was used
    def ip_distribution(self, person, from_date, to_date):
        ips = self.datadb.get_ip_address_distribution(person, from_date, to_date)
        label = []
        total = []

        #fill array
        for i in ips:
            label.append(i[0])
            total.append(i[1])
        
        #calc percentage per entry
        values=[0.0 for i in range(len(total))] 
        sum_total = sum(total)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = total
        else:

            #calc percentage
            for i in range(len(total)):
                values[i] = total[i] / sum_total

        #check if to big
        if(len(values) > 20):
            label=label[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(label)), values)

        #description
        #axis.set_title('IP Addresses form user')
        axis.set_xlabel('Percent')
        #axis.set_ylabel('Addresses')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        return fig

    #create plot which shows ip adresses in trace and how often it was used
    def ip_distribution_trace(self, person, from_date, to_date):
        trace_ip = self.datadb.get_ip_address_in_trace_distribution(person, from_date, to_date)
        own_ip = self.datadb.get_ip_address_distribution(person, from_date, to_date)

        #create list of device ip's to filter them out of trace
        ips = []
        for i in own_ip:
            if i[0] == '-' : continue
            ips.append(i[0])

        label = []
        total = []
        for i in trace_ip:
            if i[0] in ips: continue
            if i[0] == '-': continue
            label.append(i[0])
            total.append(i[1])

        #calc percentage per entry
        values=[0.0 for i in range(len(total))] 
        sum_total = sum(total)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = total
        else:
            #calc percentage
            for i in range(len(total)):
                values[i] = total[i] / sum_total

        #check if to big
        if(len(values) > 20):
            label=label[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(label)), values)

        #description
        #axis.set_title('IP-Addresses in trace')
        axis.set_xlabel('Percent')
        #axis.set_ylabel('Addresses')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        return fig

    #create diagram which shows distribution of ISP of the end device
    def isp_distribution(self, person, from_date, to_date):
        timestamps = self.datadb.get_ip_address_distribution(person, from_date, to_date)
        
        #store which ip was used and how often
        labels_old = []
        size_old = []
        for i in timestamps:
            if i[0] == '-': continue
            labels_old.append(i[0])
            size_old.append(i[1])

        #get isp of ip and sum up how often it was used
        label = []
        size = []
        for i in range(len(labels_old)):
            owner = self.sub.find_Ownder(labels_old[i])
            if owner not in label:
                label.append(owner)
                size.append(size_old[i])
            else:
                idx = label.index(owner)
                size[idx] += size_old[i]

        #calc percentage per entry
        values=[0.0 for i in range(len(size))] 
        sum_total = sum(size)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = size
        else:
            #calc percentage
            for i in range(len(size)):
                values[i] = size[i] / sum_total

        #check if to big
        if(len(values) > 20):
            label=label[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(label)), values)

        #description
        #axis.set_title('ISP\'s of IP-Addresses')
        axis.set_xlabel('Percent')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        return fig

    #create diagram which shows distribution of ISP of the trace addresses
    def isp_distribution_in_trace(self, person, from_date, to_date):
        timestamps = self.datadb.get_ip_address_in_trace_distribution(person, from_date, to_date)
        own_ip = self.datadb.get_ip_address_distribution(person, from_date, to_date)

        #create list of device ip's to filter them out of trace
        ips = []
        for i in own_ip:
            if i[0] == '-' : continue
            ips.append(i[0])

        #store which ip was used and how often
        labels_old = []
        size_old = []
        for i in timestamps:
            if i[0] in ips: continue
            if i[0] == '-': continue
            labels_old.append(i[0])
            size_old.append(i[1])

        #get isp of ip and sum up how often it was used
        label = []
        size = []
        for i in range(len(labels_old)):
            owner = self.sub.find_Ownder(labels_old[i])
            if owner not in label:
                label.append(owner)
                size.append(size_old[i])
            else:
                idx = label.index(owner)
                size[idx] += size_old[i]

        #calc percentage per entry
        values=[0.0 for i in range(len(size))] 
        sum_total = sum(size)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = size
        else:
            #calc percentage
            for i in range(len(size)):
                values[i] = size[i] / sum_total

        #check if to big
        if(len(values) > 20):
            label=label[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(label)), values)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Percent')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        return fig

    #create ip vs time scatter
    def ip_vs_hour(self, person, from_date, to_date):
        ips = self.datadb.get_ip_and_time(person, from_date, to_date)

        label = []
        x = [0 for i in range(len(ips))]
        y = [0 for i in range(len(ips))]

        #calculate x,y coordinates for dots
        for i in ips:
            if i[0] not in label:
                label.append(i[0])

            time = int(i[1].strftime("%H"))

            x.append(time)
            y.append(label.index(i[0]))


        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        return fig

    #create ip in trace vs time
    def ip_in_trace_vs_hour(self, person, from_date, to_date):
        timestamps = self.datadb.get_ip_and_time_trace(person, from_date, to_date)
        own_ip = self.datadb.get_ip_address_distribution(person, from_date, to_date)

        #create list of device ip's to filter them out of trace
        ips = []
        for i in own_ip:
            if i[0] == '-' : continue
            ips.append(i[0])

        label = []
        x = []
        y = []

        #calculate x,y coordinates for dots
        for i in timestamps:
            if i[0] in ips: continue
            if i[0] == '-' : continue
            if i[0] not in label:
                label.append(i[0])

            time = int(i[1].strftime("%H"))

            x.append(time)
            y.append(label.index(i[0]))

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        return fig

    #create ISP vs time graph
    def isp_vs_time(self, person, from_date, to_date):
        timestamps = self.datadb.get_ip_and_time(person, from_date, to_date)

        label = []
        x = []
        y = []

        #calculate x,y coordinates for dots
        for i in timestamps:
            isp = self.sub.find_Ownder(i[0])

            #check if ISP already exists in label value
            if isp not in label:
                label.append(isp)

            time = int(i[1].strftime("%H"))

            x.append(time)
            y.append(label.index(isp))

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        return fig

    #create ISP vs time graph
    def isp_in_trace_vs_time(self, person, from_date, to_date):
        timestamps = self.datadb.get_ip_and_time_trace(person, from_date, to_date)
        own_ip = self.datadb.get_ip_address_distribution(person, from_date, to_date)

        #create list of device ip's to filter them out of trace
        ips = []
        for i in own_ip:
            if i[0] == '-': continue
            ips.append(i[0])

        label = []
        x = []
        y = []

        #calculate x,y coordinates for dots
        for i in timestamps:
            if i[0] in ips: continue
            if i[0] == '-': continue

            isp = self.sub.find_Ownder(i[0])

            if isp not in label:
                label.append(isp)

            time = int(i[1].strftime("%H"))

            x.append(time)
            y.append(label.index(isp))

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        return fig

    #creates graph which shows amount of direct change in ip adresses
    def ip_change(self, person, from_date, to_date):
        ips = self.datadb.get_ip_sorted_by_time(person, from_date, to_date)

        labels = []
        values_total = []

        #count changes 
        for i in range(len(ips)-1):
            #create label
            label = ""
            if ips[i][0] == ips[i+1][0]: continue
            if ips[i][0] < ips[i+1][0]:
                label = ips[i][0] + "<->"+ ips[i+1][0]
            else:
                label = ips[i+1][0] + "<->"+ ips[i][0]

            #check if label exists
            if label not in labels:
                labels.append(label)
                values_total.append(0)

            idx = labels.index(label)
            values_total[idx] += 1

        #calc percentage per entry
        values=[0.0 for i in range(len(values_total))] 
        sum_total = sum(values_total)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = values_total
        else:
            #calc percentage
            for i in range(len(values_total)):
                values[i] = values_total[i] / sum_total

        #check if to big
        if(len(values) > 20):
            labels=labels[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(labels)), values)

        #description
        #axis.set_title('IP-Addresses in trace')
        axis.set_xlabel('Percent')
        #axis.set_ylabel('Addresses')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)
        return fig

    #graph shows when a change occurred
    def ip_change_vs_time(self, person, from_date, to_date):
        ips = self.datadb.get_ip_and_time(person, from_date, to_date)

        labels = []
        x = [0 for i in range(len(ips))]
        y = [0 for i in range(len(ips))]

        #create edge [["from", "to"], ...]
        for i in range(len(ips)-1):
            #create label
            label = ""
            ip1   = ips[i][0]
            ip2   = ips[i+1][0]
            if ip1 ==ip2: continue
            if ip1 < ip2:
                label = ip1 + "<->"+ ip2
            else:
                label = ip2 + "<->"+ ip1

            time = int(ips[i][1].strftime("%H"))

            #add label
            if label not in labels:
                labels.append(label)

            x.append(time)
            y.append(labels.index(label))

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        return fig
    
    #graph shows when and how often a change occurred
    def ip_change_vs_time_vs_frequency(self, person, from_date, to_date):
        ips = self.datadb.get_ip_and_time(person, from_date, to_date)

        labels = []
        unique = []
        x = []
        y = []
        count = []

        for i in range(len(ips)-1):
            #create label
            label = ""
            ip1   = ips[i][0]
            ip2   = ips[i+1][0]
            if ip1 == ip2: continue
            if ip1 < ip2:
                label = ip1 + "<->"+ ip2
            else:
                label = ip2 + "<->"+ ip1

            time = int(ips[i][1].strftime("%H"))

            #create label with time to count amount of unique changes
            label1 = label+str(time)

            #add label to display
            if label not in labels:
                labels.append(label)

            #add label to count amount of unique changes
            if label1 not in unique:
                unique.append(label1)
                x.append(time)
                y.append(labels.index(label))
                count.append(0)

            count[unique.index(label1)] += 1

        #create array which contains only unique values of the count array
        #to make color legend
        color_label =[]
        for i in count:
            if i not in color_label:
                color_label.append(i)

        #create figure
        fig, axis = plt.subplots()
        scatter = axis.scatter(x,y, c = count)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        axis.legend(*scatter.legend_elements(), loc="lower left", title="Amount")

        return fig

    #creates graph which shows amount of direct change in isp 
    def isp_change(self, person, from_date, to_date):
        ips = self.datadb.get_ip_sorted_by_time(person, from_date, to_date)

        labels = []
        values = []

        #count changes 
        for i in range(len(ips)-1):
            #create label
            label = ""
            ip1   = self.sub.find_Ownder(ips[i][0])
            ip2   = self.sub.find_Ownder(ips[i+1][0])
            if ip1 ==ip2: continue
            if ip1 < ip2:
                label = ip1 + "<->"+ ip2
            else:
                label = ip2 + "<->"+ ip1

            #check if label exists
            if label not in labels:
                labels.append(label)
                values.append(0)

            idx = labels.index(label)
            values[idx] += 1

        #make label multiline
        for i in range(len(labels)):
            label = labels[i].split("<->")
            labels[i] = label[0] + "\n<->\n" +label[1]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(labels)), values)

        #description
        #axis.set_title('IP-Addresses in trace')
        axis.set_xlabel('Total')
        #axis.set_ylabel('Addresses')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)
        return fig

    #create graph which shows change in ISP visualy
    def isp_change_graph(self, person, from_date, to_date, dark=1):
        ips = self.datadb.get_ip_sorted_by_time(person, from_date, to_date)

        labels = []
        values = []

        #create edge [["from", "to"], ...]
        for i in range(len(ips)-1):
            #create label
            label = ""
            ip1   = self.sub.find_Ownder(ips[i][0])
            ip2   = self.sub.find_Ownder(ips[i+1][0])
            if ip1 ==ip2: continue
            if ip1 < ip2:
                label = ip1 + "<->"+ ip2
            else:
                label = ip2 + "<->"+ ip1

            #add edge
            if label not in labels:
                labels.append(label)
                values.append([ip1, ip2])
                values.append([ip2, ip1])

        #create graph
        G = nx.DiGraph()
        G.add_edges_from(values)

        #create figure
        fig, axis = plt.subplots()
        pos = nx.spring_layout(G)
        if dark == 1:
            rcParams.update({'figure.autolayout': True})
            nx.draw_networkx_nodes(G, pos, node_color=["cyan" for i in range(len(pos))], ax=axis)
            nx.draw(G,pos, edge_color=["yellow" for i in range(len(pos))] ,  ax=axis)
            nx.draw_networkx_labels(G, pos, font_color="white", ax=axis, font_size=self.font_size)
            axis.set_facecolor('black')
            fig.set_facecolor('black')
        else:
            rcParams.update({'figure.autolayout': True})
            nx.draw_networkx_nodes(G, pos, ax=axis)
            nx.draw(G,pos, ax=axis)
            nx.draw_networkx_labels(G, pos, ax=axis, font_size=self.font_size)
        return fig

    #create graph which shows when a chang in ISP occurred
    def isp_change_vs_hour(self, person, from_date, to_date):
        ips = self.datadb.get_ip_and_time_sorted(person, from_date, to_date)

        labels = []
        x = [0 for i in range(len(ips))]
        y = [0 for i in range(len(ips))]

        #create edge [["from", "to"], ...]
        idx = 0
        for i in range(len(ips)-1):
            #create label
            label = ""
            ip1   = self.sub.find_Ownder(ips[i][0])
            ip2   = self.sub.find_Ownder(ips[i+1][0])
            if ip1 ==ip2: continue
            if ip1 < ip2:
                label = ip1 + "<->"+ ip2
            else:
                label = ip2 + "<->"+ ip1

            time = int(ips[i][1].strftime("%H"))

            #add label
            if label not in labels:
                labels.append(label)

            x[idx] = time
            y[idx] = labels.index(label)

            idx += 1

                #make label multiline
        for i in range(len(labels)):
            label = labels[i].split("<->")
            labels[i] = label[0] + "\n<->\n" +label[1]

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        return fig

    #show how ofte a user is at a spesific city
    def city_distribution(self, person, from_date, to_date):
        cities = self.datadb.get_city_distribution(person, from_date, to_date)
        label = []
        total = []

        #fill array
        for i in cities:
            if i[0] == '-' : continue
            label.append(i[0])
            total.append(i[1])
        
        #calc percentage per entry
        values=[0.0 for i in range(len(total))] 
        sum_total = sum(total)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = total
        else:
            #calc percentage
            for i in range(len(total)):
                values[i] = total[i] / sum_total

        #check if to big
        if(len(values) > 20):
            label=label[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(label)), values)

        #description
        #axis.set_title('IP Addresses form user')
        axis.set_xlabel('Percent')
        #axis.set_ylabel('Addresses')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label)))
        axis.set_yticklabels(label)

        return fig

    #shows which ip was used at which city
    def city_vs_ip(self, person, from_date, to_date):
        ip_cities = self.datadb.get_ip_and_city(person, from_date, to_date)

        label_ip = []
        label_city = []
        x = [0 for i in range(len(ip_cities))]
        y = [0 for i in range(len(ip_cities))]

        #calculate x,y coordinates for dots
        for i in ip_cities:
            if i[0] == '-' : continue
            if i[1] == '-' : continue
            if i[0] not in label_ip:
                label_ip.append(i[0])

            if i[1] not in label_city:
                label_city.append(i[1])

            x.append(label_city.index(i[1]))
            y.append(label_ip.index(i[0]))

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        #axis.set_xlabel('City')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label_ip)))
        axis.set_yticklabels(label_ip)

        axis.set_xticks(range(len(label_city)))
        axis.set_xticklabels(label_city)

        return fig

    #show chang in city
    def city_change(self, person, from_date, to_date):
        cities = self.datadb.get_city_sorted(person, from_date, to_date)

        labels = []
        values_total = []

        #count changes 
        for i in range(len(cities)-1):
            if cities[i][0] == '-' : continue
            if cities[i+1][0] == '-' : continue
            #create label
            label = ""
            if cities[i][0] == cities[i+1][0]: continue
            if cities[i][0] < cities[i+1][0]:
                label = cities[i][0] + "<->"+ cities[i+1][0]
            else:
                label = cities[i+1][0] + "<->"+ cities[i][0]

            #check if label exists
            if label not in labels:
                labels.append(label)
                values_total.append(0)

            idx = labels.index(label)
            values_total[idx] += 1

        #calc percentage per entry
        values=[0.0 for i in range(len(values_total))] 
        sum_total = sum(values_total)
        
        #avoide devicion with 0
        if sum_total == 0:
            values = values_total
        else:
            #calc percentage
            for i in range(len(values_total)):
                values[i] = values_total[i] / sum_total

        #check if to big
        if(len(values) > 20):
            label=label[:20]
            values=values[:20]

        #create figure
        fig, axis = plt.subplots()
        axis.barh(range(len(labels)), values)

        #description
        #axis.set_title('IP-Addresses in trace')
        axis.set_xlabel('Percent')
        #axis.set_ylabel('Addresses')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)
        return fig

    #show how often the city was changed an when
    def city_change_vs_time_vs_frequency(self, person, from_date, to_date):
        cities = self.datadb.get_city_time(person, from_date, to_date)

        labels = []
        unique = []
        x = []
        y = []
        count = []

        for i in range(len(cities)-1):
            if cities[i][0] == '-' : continue
            if cities[i+1][0] == '-' : continue
            #create label
            label = ""
            city1   = cities[i][0]
            city2   = cities[i+1][0]
            if city1 == city2: continue
            if city1 < city2:
                label = city1 + "<->"+ city2
            else:
                label = city2 + "<->"+ city1

            time = int(cities[i][1].strftime("%H"))

            #create label with time to count amount of unique changes
            label1 = label+str(time)

            #add label to display
            if label not in labels:
                labels.append(label)

            #add label to count amount of unique changes
            if label1 not in unique:
                unique.append(label1)
                x.append(time)
                y.append(labels.index(label))
                count.append(0)

            count[unique.index(label1)] += 1

        #create array which contains only unique values of the count array
        #to make color legend
        color_label =[]
        for i in count:
            if i not in color_label:
                color_label.append(i)

        #create figure
        fig, axis = plt.subplots()
        scatter = axis.scatter(x,y, c = count)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        axis.set_xlabel('Time of day')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(labels)

        axis.set_xticks(range(24))
        axis.set_xticklabels(range(24))

        axis.legend(*scatter.legend_elements(), loc="lower left", title="Amount")

        return fig

    #show city graph
    def city_graph(self, person, from_date, to_date, dark=1):
        cities = self.datadb.get_city_time(person, from_date, to_date)

        labels = []
        values = []

        #create edge [["from", "to"], ...]
        for i in range(len(cities)-1):
            #create label
            label = ""
            ip1   = cities[i][0]
            ip2   = cities[i+1][0]
            if ip1 == '-' : continue
            if ip2 == '-' : continue
            if ip1 ==ip2: continue
            if ip1 < ip2:
                label = ip1 + "<->"+ ip2
            else:
                label = ip2 + "<->"+ ip1

            #add edge
            if label not in labels:
                labels.append(label)
                values.append([ip1, ip2])
                values.append([ip2, ip1])

        #create graph
        G = nx.DiGraph()
        G.add_edges_from(values)

        #create figure
        fig, axis = plt.subplots()
        pos = nx.spring_layout(G)
        if dark == 1:
            rcParams.update({'figure.autolayout': True})
            nx.draw_networkx_nodes(G, pos, node_color=["cyan" for i in range(len(pos))], ax=axis)
            nx.draw(G,pos, edge_color=["yellow" for i in range(len(pos))] ,  ax=axis)
            nx.draw_networkx_labels(G, pos, font_color="white", ax=axis, font_size=self.font_size)
            axis.set_facecolor('black')
            fig.set_facecolor('black')
        else:
            rcParams.update({'figure.autolayout': True})
            nx.draw_networkx_nodes(G, pos, ax=axis)
            nx.draw(G,pos, ax=axis)
            nx.draw_networkx_labels(G, pos, ax=axis, font_size=self.font_size)
            
        return fig

    #show which isp was used in which city
    def city_vs_isp(self, person, from_date, to_date):
        ip_cities = self.datadb.get_ip_and_city(person, from_date, to_date)

        label_ip = []
        label_city = []
        x = [0 for i in range(len(ip_cities))]
        y = [0 for i in range(len(ip_cities))]

        #calculate x,y coordinates for dots
        idx = 0
        for i in ip_cities:
            if i[0] == '-' : continue
            if i[1] == '-' : continue

            isp = self.sub.find_Ownder(i[0])
            if isp not in label_ip:
                label_ip.append(isp)

            if i[1] not in label_city:
                label_city.append(i[1])


            x[idx] = label_city.index(i[1])
            y[idx] = label_ip.index(isp)

            idx += 1

        #create figure
        fig, axis = plt.subplots()
        axis.scatter(x,y)

        #description
        #axis.set_title('ISP\'s of IP-Addresses in Trace')
        #axis.set_xlabel('City')

        #set how many lables where needed and text for it
        axis.set_yticks(range(len(label_ip)))
        axis.set_yticklabels(label_ip)

        axis.set_xticks(range(len(label_city)))
        axis.set_xticklabels(label_city)

        return fig

    #get json which descripes possible images and description for the images
    def get_diagram_json(self, user, from_date, to_date):
        json_str = \
            '{"categories":['+\
                '{"name": "Measurement", "id": "measurement", "images": ['+\
                    '{"url": "/image/'+user+'_0_0_'+from_date+'_'+to_date+'.png", "alt":"Distance Hour", "description":"Shows how frequently measurements were taken. e.g. 1 and 0.6 means, 60% of the measurements were taken one hour apart."} '+\
                    ',{"url": "/image/'+user+'_0_1_'+from_date+'_'+to_date+'.png", "alt":"Distance Minutes", "description":"Shows how frequently in Minutes when they are less than one hour apart."} '+\
                    ',{"url": "/image/'+user+'_0_2_'+from_date+'_'+to_date+'.png", "alt":"Day", "description":"Shows how many measurements were taken per day of the week."} '+\
                    ',{"url": "/image/'+user+'_0_3_'+from_date+'_'+to_date+'.png", "alt":"Time", "description":"Shows at which time of the day the reqest was send."} '+\
                ']}'+\
                ',{"name": "Address distribution", "id": "address_distribution", "images": ['+\
                    '{"url": "/image/'+user+'_1_0_'+from_date+'_'+to_date+'.png", "alt":"IP Addresses distribution", "description":"Shows distribution of IP-End-Addresses of the user\'s device."}'+\
                    ',{"url": "/image/'+user+'_1_1_'+from_date+'_'+to_date+'.png", "alt":"IP Addresses distribution in trace", "description":"Shows different IP-Addresses of the route to the user, captured by trace."}'+\
                    ',{"url": "/image/'+user+'_1_2_'+from_date+'_'+to_date+'.png", "alt":"ISP distribution", "description":"Shows ISP of the IP-End-Addresses of the user\'s device."}'+\
                    ',{"url": "/image/'+user+'_1_3_'+from_date+'_'+to_date+'.png", "alt":"ISP distribution in trace", "description":"Shows ISP of the IP-Addresses in the trace of the route to the user, captured by trace."}'+\
                ']}'+\
                ',{"name": "Address / Time", "id": "address_Time", "images": ['+\
                    '{"url": "/image/'+user+'_2_0_'+from_date+'_'+to_date+'.png", "alt":"IP / Hour", "description":"Shows which IP-Address was used at which time"}'+\
                    ',{"url": "/image/'+user+'_2_1_'+from_date+'_'+to_date+'.png", "alt":"IP in trace / Hour", "description":"Shows which IP-Address in trace was used at which time"}'+\
                    ',{"url": "/image/'+user+'_2_2_'+from_date+'_'+to_date+'.png", "alt":"ISP / Hour", "description":"Shows which ISP was used at which time"}'+\
                    ',{"url": "/image/'+user+'_2_3_'+from_date+'_'+to_date+'.png", "alt":"ISP in trace / Hour", "description":"Shows which ISP in trace was used at which time"}'+\
                ']}'+\
                ',{"name": "Changes in Address", "id": "changes_in_address", "images": ['+\
                    '{"url": "/image/'+user+'_3_0_'+from_date+'_'+to_date+'.png", "alt":"IP Address changes", "description":"Shows how often a change within IP Adresses occurred"}'+\
                    ',{"url": "/image/'+user+'_3_1_'+from_date+'_'+to_date+'.png", "alt":"IP Address changes / Hour ", "description":"Shows how often a change within IP Adresses occurred and when"}'+\
                    ',{"url": "/image/'+user+'_3_2_'+from_date+'_'+to_date+'.png", "alt":"IP Address changes / Hour / Frequency", "description":"Shows frequency of changes in IP Address"}'+\
                    ',{"url": "/image/'+user+'_3_3_'+from_date+'_'+to_date+'.png", "alt":"ISP changes", "description":"Shows how often change within ISP occurred"}'+\
                    ',{"url": "/image/'+user+'_3_4_'+from_date+'_'+to_date+'.png", "alt":"ISP changes graph", "description":"Shows change in ISP"}'+\
                    ',{"url": "/image/'+user+'_3_5_'+from_date+'_'+to_date+'.png", "alt":"ISP changes / Hour", "description":"Shows when a chang in ISP occurred"}'+\
                ']}'+\
                ',{"name": "Geographical", "id": "geographical", "images": ['+\
                    '{"url": "/image/'+user+'_4_0_'+from_date+'_'+to_date+'.png", "alt":"City distribution", "description":"Show distribution of the Cities visited"} '+\
                    ',{"url": "/image/'+user+'_4_1_'+from_date+'_'+to_date+'.png", "alt":"City / IP", "description":"Shows which IP was used at which City"} '+\
                    ',{"url": "/image/'+user+'_4_2_'+from_date+'_'+to_date+'.png", "alt":"City change", "description":"Shows change in city and how often in occurred"} '+\
                    ',{"url": "/image/'+user+'_4_3_'+from_date+'_'+to_date+'.png", "alt":"City change / Time / Frequency", "description":"Shows change when it occred and how often"} '+\
                    ',{"url": "/image/'+user+'_4_4_'+from_date+'_'+to_date+'.png", "alt":"City graph", "description":"Show change in Cities"} '+\
                    ',{"url": "/image/'+user+'_4_5_'+from_date+'_'+to_date+'.png", "alt":"City / ISP", "description":"Show which ISP was used in which City"} '+\
                ']}'+\
            ']}'
        return json.loads(json_str)

    #create compare json from the get_diagram_json method 
    def get_compare_json(self, user1, user2, from_date, to_date):
        j = self.get_diagram_json(user1, from_date, to_date)

        new_j = {}
        new_cat = []

        #ad url1 to each image entry in the json
        for i in j['categories']:
            new_j = {}
            new_image = []
            new_j["name"] = i["name"]
            for k in i['images']:
                val = k['url'].split("_")
                k['url1'] = "/image/" + user2 + "_" + val[1] +"_" +val[2]+"_" +val[3]+"_" +val[4]
                new_image.append(k)
            new_j['images'] = new_image
            new_cat.append(new_j)

        new_j["categories"] = new_cat

        return new_j
