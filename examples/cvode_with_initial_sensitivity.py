#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Modelon AB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import numpy as N
import pylab as P
from assimulo.solvers.sundials import CVode
from assimulo.problem import Explicit_Problem

def run_example(with_plots=True):
    """
    This example show how to use Assimulo and CVode for simulating sensitivities
    for initial conditions.
    
    dy1/dt = -(k01+k21+k31)*y1 + k12*y2 + k13*y3 + b1
    dy2/dt = k21*y1 - (k02+k12)*y2
    dy3/dt = k31*y1 - k13*y3
 
    y1(0) = p1, y2(0) = p2, y3(0) = p3
    p1=p2=p3 = 0 
    
    See http://sundials.2283335.n4.nabble.com/Forward-sensitivities-for-initial-conditions-td3239724.html
    """
    
    def f(t, y, p):
        y1,y2,y3 = y
        k01 = 0.0211
        k02 = 0.0162
        k21 = 0.0111
        k12 = 0.0124
        k31 = 0.0039
        k13 = 0.000035
        b1 = 49.3
        
        yd_0 = -(k01+k21+k31)*y1+k12*y2+k13*y3+b1
        yd_1 = k21*y1-(k02+k12)*y2
        yd_2 = k31*y1-k13*y3
        
        return N.array([yd_0,yd_1,yd_2])
    
    def handle_result(solver, t ,y):
        solver.t += [t]
        solver.y += [y]
        solver.p[0] += [solver.interpolate_sensitivity(t, 0, 0)]
        solver.p[1] += [solver.interpolate_sensitivity(t, 0, 1)]
        solver.p[2] += [solver.interpolate_sensitivity(t, 0, 2)]
    
    #The initial conditions
    y0 = [0.0,0.0,0.0]          #Initial conditions for y
    p0 = [0.0, 0.0, 0.0]  #Initial conditions for parameters
    yS0 = N.array([[1,0,0],[0,1,0],[0,0,1.]])
    
    
    #Create an Assimulo explicit problem
    exp_mod = Explicit_Problem(f, y0, p0=p0)
    
    #Sets the options to the problem
    exp_mod.handle_result = handle_result #Change the default handling of the result
    exp_mod.yS0 = yS0
    
    #Create an Assimulo explicit solver (CVode)
    exp_sim = CVode(exp_mod)
    
    #Sets the paramters
    exp_sim.iter = 'Newton'
    exp_sim.discr = 'BDF'
    exp_sim.rtol = 1e-7
    exp_sim.atol = 1e-6
    exp_sim.pbar = [1,1,1] #pbar is used to estimate the tolerances for the parameters
    exp_sim.continuous_output = True #Need to be able to store the result using the interpolate methods
    exp_sim.sensmethod = 'SIMULTANEOUS' #Defines the sensitvity method used
    exp_sim.suppress_sens = False            #Dont suppress the sensitivity variables in the error test.
    
    exp_sim.p = [[],[],[]] #Vector for storing the p result
    
    #Simulate
    exp_sim.simulate(400) #Simulate 400 seconds
    
    #Plot
    if with_plots:
        P.figure(1)
        P.plot(exp_sim.t, N.array(exp_sim.p[0])[:,0],
               exp_sim.t, N.array(exp_sim.p[0])[:,1],
               exp_sim.t, N.array(exp_sim.p[0])[:,2])
        P.title("Parameter p1")
        P.legend(("p1/dy1","p1/dy2","p1/dy3"))
        P.figure(2)
        P.plot(exp_sim.t, N.array(exp_sim.p[1])[:,0],
               exp_sim.t, N.array(exp_sim.p[1])[:,1],
               exp_sim.t, N.array(exp_sim.p[1])[:,2])
        P.title("Parameter p2")
        P.legend(("p2/dy1","p2/dy2","p2/dy3"))
        P.figure(3)
        P.plot(exp_sim.t, N.array(exp_sim.p[2])[:,0],
               exp_sim.t, N.array(exp_sim.p[2])[:,1],
               exp_sim.t, N.array(exp_sim.p[2])[:,2])
        P.title("Parameter p3")
        P.legend(("p3/dy1","p3/dy2","p3/dy3"))
        P.figure(4)
        exp_sim.plot() #Plot the solution

if __name__=='__main__':
    run_example()
