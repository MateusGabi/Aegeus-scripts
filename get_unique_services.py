#!/usr/bin/env python3
import json
import subprocess
import sys
import random
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def main():
	file = str(sys.argv[1])
	DATABASE = str(sys.argv[2])
	REPOSITORY_ANALYSIS_DIR = str(sys.argv[3])
	METRIC1 = "ServiceInterfaceDataCohesion"
	METRIC1sigl = "SIDC"
	METRIC2 = "StrictServiceImplementationCohesion"
	METRIC2sigl = "SSIC"
	METRIC3 = "LackOfMessageLevelCohesion"
	METRIC3sigl = "LoCMes"
	METRIC4 = "NumberOfOperations"
	METRIC4sigl = "NO"

	metrics = [{
		"name": METRIC1,
		"sigla": METRIC1sigl,
	},{
		"name": METRIC2,
		"sigla": METRIC2sigl,
	},{
		"name": METRIC3,
		"sigla": METRIC3sigl,
	},{
		"name": METRIC4,
		"sigla": METRIC4sigl,
	},]

	print("===============================")
	print("DATABASE: {}".format(DATABASE))

	with open(file, 'r') as f:
		uniques = set()
		lines = f.readlines()

		for line in lines:
			splitted = line.split("/")
			last_index = len(splitted) - 1
			service_name = splitted[last_index]

			uniques.add(service_name.replace(".java", "").replace("\n", ""))

		print("{} services found.".format(len(uniques)))

		# calcular se houver alteração nos valores das métricas 
		with open(DATABASE, 'r') as db:
			lines = db.readlines()
			print("#{} lines".format(len(lines)))

			services_arr = to_array(lines)
			services_arr = drop_version(services_arr, version="master")
			services_dict = group_by(services_arr, "name")
			services_dict = group_by_metrics(services_dict)
			sort_versions(services_dict)

			generate_graphs(DATABASE, services_dict, metrics, path=REPOSITORY_ANALYSIS_DIR)

def sort_key(item):
	version = item['version']
	v1 = version.replace("v", "")
	return list(map(int, v1.split('.')))

def sort_versions(services):
	for service in services.keys():
		for metric in services[service].keys():
			observations = services[service][metric]
			observations.sort(key=sort_key)

def drop_version(arr, version):
	def not_version(item):
		return item.get("version") != version

	ret = filter(not_version, arr)
	# print(json.dumps(ret))
	return ret

def generate_graphs(db, services, metrics, path):
	i = 1
	for service in services.keys():
		print("SERVICE: '{}'".format(service))
		v0 = has_variation_in_the_value_of_metrics(services, service, metrics[0].get("name"))
		v1 = has_variation_in_the_value_of_metrics(services, service, metrics[1].get("name"))
		v2 = has_variation_in_the_value_of_metrics(services, service, metrics[2].get("name"))
		v3 = has_variation_in_the_value_of_metrics(services, service, metrics[3].get("name"))

		if v0:
			generate_using_matplotlib(
				i=i,
				filename="{}/images/{}-{}-EVOLUTION-matplot.png".format(path, service, metrics[0].get("sigla")),
				service_name=service,
				metric=metrics[0],
				observations=get_observations(services, service, metrics[0].get("name"),
				just_value=False)
			)
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[0].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[0].get("sigla"))])	
		if v1:
			generate_using_matplotlib(
				i=i+1,
				filename="{}/images/{}-{}-EVOLUTION-matplot.png".format(path, service, metrics[1].get("sigla")),
				service_name=service,
				metric=metrics[1],
				observations=get_observations(services, service, metrics[1].get("name"),
				just_value=False)
			)
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[1].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[1].get("sigla"))])
		if v2:
			generate_using_matplotlib(
				i=i+2,
				filename="{}/images/{}-{}-EVOLUTION-matplot.png".format(path, service, metrics[2].get("sigla")),
				service_name=service,
				metric=metrics[2],
				observations=get_observations(services, service, metrics[2].get("name"),
				just_value=False)
			)
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[2].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[2].get("sigla"))])
		if v3:
			generate_using_matplotlib(
				i=i+3,
				filename="{}/images/{}-{}-EVOLUTION-matplot.png".format(path, service, metrics[3].get("sigla")),
				service_name=service,
				metric=metrics[3],
				observations=get_observations(services, service, metrics[3].get("name"),
				just_value=False)
			)
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[3].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[3].get("sigla"))])

		i = i + 4

def get_observations(services, service_name, metric_name, just_value=True):
	values = services[service_name][metric_name]
	print("{} observations for {}->{}".format(len(values), service_name, metric_name))

	if not just_value:
		return [{'value': float(item.get("value")), 'version': item.get('version')} for item in values]

	return [float(item.get("value")) for item in values]

def generate_using_matplotlib(service_name, metric, observations, filename, format="png", i=0):	
	plt.figure(i, figsize=(16,12))
	x = np.array(range(0, len(observations)))
	y = np.array(list(map(lambda i: i.get("value"), observations)))
	
	plt.xlabel("Releases")
	plt.ylabel("Value")
	plt.title("{}::{}".format(service_name, metric.get("name")))

	my_xticks = list(map(lambda i: i.get("version"), observations))
	plt.xticks(x, my_xticks, rotation='vertical')
	plt.plot(x, y)
	plt.savefig(fname=filename, format=format,)

def has_variation_in_the_value_of_metrics(services, service_name, metric_name):
	# service exist?
	service_exist = service_name in services
	if service_exist:
		print("Service {} exist.".format(service_name))
	else:
		raise Exception("Service {} donot exist on dict.".format(service_name))

	# metric exist?
	metric_exist = metric_name in services[service_name]
	if metric_exist:
		print("Metric {} exist.".format(metric_name))
	else:
		raise Exception("Metric {} donot exist on dict.".format(metric_name))

	observations = get_observations(services, service_name, metric_name)
	anomaly = has_anomaly(observations)
	print("Has anomaly on observation {}->{}? {}".format(service_name, metric_name, anomaly))
	print(observations)

	return anomaly

def has_anomaly(observations):
	previous_value = observations[0]

	if len(observations) < 2:
		return False

	for observation in observations:
		if observation == previous_value:
			# continue
			previous_value = observation
		else:
			return True
	
	return False

def group_by_metrics(services_dict):
	new_dict = {}
	for service in services_dict.keys():
		arr_of_evaluatings = services_dict[service]
		group_by_metrics = group_by(arr_of_evaluatings, "metric")
		new_dict[service] = group_by_metrics
		
	return new_dict

def group_by(arr, attribute):
	dict_ret = {}

	for item in arr:
		value = item[attribute]
		exist = value in dict_ret
		
		if not exist:
			dict_ret[value] = []
		
		dict_ret[value].append(item)

	return dict_ret

def to_array(lines):
	arr = []

	for line in lines:
		row = line.split(",")

		service_name = row[0]
		version = row[1]
		metric = row[2]
		value = row[3]

		service_dict = {}
		service_dict['name'] = service_name
		service_dict['version'] = version
		service_dict['metric'] = metric
		service_dict['value'] = value.replace("\n", "")

		arr.append(service_dict)


	return arr

if __name__ == '__main__':
	main()