#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 23:32:14 2017

@author: markm

Credit goes to Scott Lobdell for recoding the work of Greg Welch and Gary Bishop
into something more readable.

http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
http://www.cs.unc.edu/~welch/kalman/kalmanIntro.html

A 1d filter suitable for smoothing out the data from the load cells.

"""

from array import array
from math import sin


class KalmanFilter(object):

    # process_variance: This is the error estimate of the sensor.
    #
    # estimated_measurement_variance: The previously measured variance of 
    # the signal. For a static sensor value, this is the measured noise.
    
    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = \
                                estimated_measurement_variance
        self.current_estimate = 0.0
        self.currenti_error_estimate = 1.0

    def get_filtered_value(self, measurement):
        previous_estimate = self.current_estimate
        previous_error_estimate = self.currenti_error_estimate + \
                                                        self.process_variance

        blending_factor = previous_error_estimate / \
                (previous_error_estimate + self.estimated_measurement_variance)
        self.current_estimate = previous_estimate + \
                            blending_factor * (measurement - previous_estimate)
        self.currenti_error_estimate = (1 - blending_factor) * \
                                                        previous_error_estimate
        return self.current_estimate

class RollingAverageFilter(object):
    
    def __init__(self, windowSize = 30, mean = 0.0, variance = 0.0):
        self.oldIndex = 0
        self.oldX = array('f', (0.0 for i in range(0, windowSize)))
        self.mean = mean
        self.variance = variance
        self.N = windowSize
        
    def get_filtered_value(self, x):
        self.oldX[self.oldIndex] = x
        self.oldIndex += 1
        self.oldIndex %= self.N    
        self.mean = sum(self.oldX) / self.N
        return self.mean
    
    def get_variance(self):
        sum2 = 0.0
        for i in range(0, self.N):
            sum2 += (self.oldX[i] - self.mean) * (self.oldX[i] - self.mean)
            
        self.variance = sum2 / (self.N - 1)
        

        return self.variance

if __name__ == "__main__":
    import random
    iteration_count = 500

    actual_values = [(-0.37727 + j * j * 0.00001) + 0.5 * sin(j/2.0) for j in 
                     range(iteration_count)]
    noisy_measurement = [random.random() * 2.0 - 1.0 + actual_val 
                         for actual_val in actual_values]

    # in practice we would take our sensor, log some readings and get the
    # standard deviation
    import numpy
    measurement_standard_deviation = \
        numpy.std([random.random() * 2.0 - 1.0 
                   for j in range(iteration_count)])

    filter = RollingAverageFilter()
    current_estimate_graph = []
    current_variance_graph = []

    for iteration in range(1, iteration_count):
        result = filter.get_filtered_value(noisy_measurement[iteration])
        current_estimate_graph.append(result)
        current_variance_graph.append(filter.get_variance())

    import pylab
    pylab.figure()
    pylab.plot(actual_values, color='g', label='truth value')
    pylab.plot(noisy_measurement, color='r', label='noisy measurements')
    pylab.plot(current_estimate_graph, 'b-', label='filtered results')
    pylab.plot(current_variance_graph, 'c', label='filtered variance')
    pylab.legend()
    pylab.xlabel('Rolling Average Filter')
    pylab.ylabel('Voltage')
    pylab.show()
    
    # actual_values = [-0.37727 + j * j * 0.00001 for j in 
    #                  range(iteration_count)]
    noisy_measurement = [random.random() * 2.0 - 1.0 + actual_val 
                         for actual_val in actual_values]

    # in practice we would take our sensor, log some readings and get the
    # standard deviation
    measurement_standard_deviation = \
        numpy.std([random.random() * 2.0 - 1.0 
                   for j in range(iteration_count)])

    # The smaller this number, the fewer fluctuations, but can also 
    # venture off course...
    process_variance = 1e-3
    estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2
    kalman_filter = KalmanFilter(process_variance, 
                                 estimated_measurement_variance)
    current_estimate_graph = []

    for iteration in range(1, iteration_count):
        result = kalman_filter.get_filtered_value(noisy_measurement[iteration])
        current_estimate_graph.append(result)

    pylab.figure()
    pylab.plot(actual_values, color='g', label='truth value')
    pylab.plot(noisy_measurement, color='r', label='noisy measurements')
    pylab.plot(current_estimate_graph, 'b-', label='filtered results')
    pylab.legend()
    pylab.xlabel('Kalman Filter')
    pylab.ylabel('Voltage')
    pylab.show()
    
