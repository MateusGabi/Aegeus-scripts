#!/usr/bin/env python3

import numpy as np
import json

file = "/home/mgm/.aegeus/repos/spinnaker-gate/analysis/final.csv"

def __filter_expected_rows(controller, metric, obj):
    return obj.get('controller') == controller and obj.get('metric') == metric and obj.get('version') != "master"


def filter_expected_rows(controller, metric):
    return lambda x: __filter_expected_rows(controller, metric, x)

def str_to_dict(row):
    controller, version, metric, value = row.split(",")
    return {
        'controller': controller,
        'version': version,
        'metric': metric,
        'value': value.split("\n")[0],
    }


def just_version_and_value(obj):
    return obj.get('version'), float(obj.get('value'))


def compare(a, b):
    v1 = a[0].replace("v", "")
    v1 = v1.split(".")

    v2 = b[0].replace("v", "")
    v2 = v2.split(".")

    major1 = int(v1[0])
    minor1 = int(v1[1])
    patch1 = int(v1[2])

    major2 = int(v2[0])
    minor2 = int(v2[1])
    patch2 = int(v2[2])

    if major1 != major2:
        return major2 - major1

    if minor1 != minor2:
        return minor2 - minor1

    if patch1 != patch2:
        return patch2 - patch1

    return 0


def ns(i):
    value = i[1]
    v1 = i[0].replace("v", "")
    v1 = v1.split(".")

    major = int(v1[0])
    minor = int(v1[1])
    patch = int(v1[2])

    return (value, major, minor, patch)


def back_version(i):
    return "v{}.{}.{}".format(i[1], i[2], i[3]), i[0]


def sort_version(iterable):
    return sorted(sorted(sorted(iterable, key=lambda i: i[3]), key=lambda i: i[2]), key=lambda i: i[1])


def filter_by_metric_and_controller(controller, metric, lines):
    t = map(back_version, sort_version(list(map(ns, map(
        just_version_and_value, filter(filter_expected_rows(controller, metric), map(str_to_dict, lines)))))))
    return t

def std_deviation(values):
    return np.std(values)

def __just_key(key, obj):
    return obj.get(key)

def just_key(key):
    return lambda x: __just_key(key, x)

def get_controllers(lines):
    return list(set(map(just_key('controller'), map(str_to_dict, lines))))

def get_metrics(lines):
    return list(set(map(just_key('metric'), map(str_to_dict, lines))))

if __name__ == '__main__':
    expect_service = "AwsCodeBuildController"
    expect_metric = "LackOfMessageLevelCohesion"

    with open(file, "r") as f:
        lines = f.readlines()

        controllers = np.array(get_controllers(lines))
        metrics = np.array(get_metrics(lines))

        pairs = np.array(np.meshgrid(controllers, metrics)).T.reshape(-1, 2)

        a = []
        
        for pair in pairs:
            c = pair[0]
            m = pair[1]

            f = filter_by_metric_and_controller(c, m, lines)
            values = map(lambda i: i[1], f)
            lv = list(values)
            
            a.append((c, m, std_deviation(lv), np.var(lv)))

        dtype = [('controller', 'S100'), ('metric', 'S100'), ('deviation', float), ('variance', float)]
        aarr = np.array(a, dtype=dtype)
        b = np.sort(aarr, order=['deviation'])
        b = b[::-1]
        # print(json.dumps(b))
        for c in b:
            print("{},{},{},{}".format(c[0].decode('UTF-8'), c[1].decode('UTF-8'), c[2], c[3]))
