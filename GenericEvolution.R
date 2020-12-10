#!/usr/bin/env Rscript
library("optparse")
library(ggplot2)
library(dplyr)

option_list = list(
  make_option(c("-d", "--dataset"), type="character", default=NULL, 
              help="dataset file name", metavar="character"),
  make_option(c("-o", "--out"), type="character", default="service.png", 
              help="output file name [default= %default]", metavar="character"),
  make_option(c("-s", "--service"), type="character", default="", 
              help="service name [default= %default]", metavar="character"),
  make_option(c("-m", "--metric"), type="character", default="", 
              help="metric name [default= %default]", metavar="character")
); 

###############
#
# RUN COMMAND:
#
# Rscript GenericEvolution.R -d DATABASE -s SERVICE -m METRICS -o OUTPUT_FILE
#
# Rscript GenericEvolution.R -d /home/mgm/.aegeus/repos/sitewhere/analysis/final.csv -s DeviceManagementImpl -m "class br.unicamp.ic.laser.metrics.StrictServiceImplementationCohesion" -o DeviceManagement-SSIC-Evolution.png

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

#service_name <- "AssetManagementImpl"
#metric <- "class br.unicamp.ic.laser.metrics.StrictServiceImplementationCohesion"
#csv_file <- "/home/mgm/.aegeus/repos/sitewhere/analysis/final.csv"

service_name <- opt$service
metric <- opt$metric
csv_file <- opt$dataset
output_file <- opt$out

df <- read.table(csv_file, header=F, sep=",", row.names=NULL, col.names = c("Service", "Version", "Metric", "Value"))

graph_title <- paste(service_name, "\n", metric)

df %>%
  filter(Service == service_name &
           Version != "master" &
           Metric == metric) %>%
  ggplot( aes(x=Version, y=Value)) +
  geom_line() +
  ggtitle(graph_title) +
  geom_point() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  ggsave(output_file)