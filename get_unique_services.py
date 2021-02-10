#!/usr/bin/env python3
import json
import subprocess
import sys
import random
from datetime import datetime

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

			generate_graphs(DATABASE, services_dict, metrics, path=REPOSITORY_ANALYSIS_DIR)

def drop_version(arr, version):
	def not_version(item):
		return item.get("version") != version

	ret = filter(not_version, arr)
	# print(json.dumps(ret))
	return ret

def generate_graphs(db, services, metrics, path):
	for service in services.keys():
		print("SERVICE: '{}'".format(service))
		v0 = has_variation_in_the_value_of_metrics(services, service, metrics[0].get("name"))
		v1 = has_variation_in_the_value_of_metrics(services, service, metrics[1].get("name"))
		v2 = has_variation_in_the_value_of_metrics(services, service, metrics[2].get("name"))
		v3 = has_variation_in_the_value_of_metrics(services, service, metrics[3].get("name"))

		if v0:
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[0].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[0].get("sigla"))])	
		if v1:
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[1].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[1].get("sigla"))])
		if v2:
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[2].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[2].get("sigla"))])
		if v3:
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", db, "-s", service, "-m", metrics[3].get("name"), "-o", "{}/images/{}-{}-EVOLUTION.png".format(path, service, metrics[3].get("sigla"))])


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

	values = services[service_name][metric_name]
	print("{} observations for {}->{}".format(len(values), service_name, metric_name))

	observations = [float(item.get("value")) for item in values]
	anomaly = has_anomaly(observations)
	print("Has anomaly on observation {}->{}? {}".format(service_name, metric_name, anomaly))
	print(observations)

	return anomaly

def has_anomaly(observations):
	previous_value = observations[0]
	for observation in observations:
		if observation == previous_value:
			# continue
			previous_value = observation
		else:
			return True
	
	return False

def group_by_metrics(services_dict):
	# grouping by metrics
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

# def should_generate_graph(db, service):
# 	print("Checking if service '{}' is possible to generate graph.".format(service))
# 	lines = db.readlines()

# 	collect = retrieve_service_row(lines, service)

# 	if len(collect) == 0:
# 		print("Service '{}' was not evaluated.".format(service))

# def retrieve_service_row(lines, service):
# 	collect = []

# 	for line in lines:
# 		row = line.split(",")

# 		service_name = row[0]
# 		version = row[1]
# 		metric = row[2]
# 		value = row[3]

# 		if service_name == service:
# 			print("found {}".format(service))
# 			collect.append({
# 				'service_name': service_name,
# 				'version': version,
# 				'metric': metric,
# 				'value': value
# 			})
	
# 	return collect

if __name__ == '__main__':
	main()