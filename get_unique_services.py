#!/usr/bin/env python3
import subprocess
import sys
import random
from datetime import datetime

def main():
	file = str(sys.argv[1])
	DATABASE = str(sys.argv[2])
	REPOSITORY_ANALYSIS_DIR = str(sys.argv[3])
	METRIC = "class br.unicamp.ic.laser.metrics.StrictServiceImplementationCohesion"

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

		for service in uniques:
			print("SERVICE: *{}*".format(service))
			subprocess.run(["Rscript", "GenericEvolution.R", "-d", DATABASE, "-s", service, "-m", METRIC, "-o", "{}/images/{}.png".format(REPOSITORY_ANALYSIS_DIR, service)])

if __name__ == '__main__':
	main()