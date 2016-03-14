"""
#------------------------------------

            AQUILA OPT

#------------------------------------

Created on March 2, 2016 by David and James Usevitch

Last Edited: March 8, 2016

"""

import subprocess
import sys
import re
from writeAVLfile import writeFileAVL
from loadAVL import *
from scipy.optimize import minimize
from pyoptwrapper import optimize
from pyoptsparse import SNOPT, SLSQP, NSGA2
import math


#Initial values:
b0 = 11.0 # m
c0 = .75 # m
V0 = 11.49 #m/s
aoa0 = 7.0 # deg

#Starting point
x0 = [b0, c0, V0, aoa0]


#Constants:
global mat_Density, rho, t, n, CLmax
mat_Density = 1384 #Must be in kg/m^3. This value is an approximation for carbon fiber.
rho = .11025 #Density of air at Facebook drone height is 9% of density down here: .09*1.225
W = 5.0 * 9.81 #Weight must be in Newtons, !!!NOT KILOGRAMS!!!
t = .005 #Thickness of the airfoil material.

#Bound Constants
n = .9
CLmax = 1.53 #For S7075 Airfoil. Found with XFLR5.

I = 1 #W/m^2/nm
#value from solar chart--efficiency Ncell = Single Junction GaAs Solar Cell - from LG Electronics
Ncell = 0.275

# Objective function

def netPower(x, I=500, cellEff=.275):
    
    print x
    global rho
    S = S_area(x[0],x[1])

    writeFileAVL(x) #Write AVL Loading File
    AVLvars = loadAVLvars(x) # Calls AVL Program and get variable output
    CDtot = float(AVLvars['CDtot'])
#    e = float(AVLvars['e'])
    CL = float(AVLvars['CLtot'])
    V = x[2]
    
    return .5*rho*V**3.0*S*(CDtot) - I*S*cellEff
    #Add in power needed to last each night

def S_area(b, c, shape='rect', taperRatio=1):
    if shape == 'rect':
        return b*c
    elif shape == 'swept':
        # !!!Change this later. Do something with taperRatio.
        return 1.0

def findW(b, c, density, instr=0, spar=None):
    
    global t
    
    if spar == None:
        weight = (2.2*b*c*t + instr)*density
#    elif:
        # Update this based on different options above. If there's a spar, add
        # its weight in. If there are different sized batteries, make the 
        # battery weight an input to the function and add it in.
    
    return weight

def findStress(b, cRoot, t, F):
    #Finds the force at the root of one wing. Hollow rectangle approximation
    # where the thickness of the root airfoil is the thickness of a hollow
    # rectangle.
    #Assumes a point force on the tip of the wing.
    #b is the TOTAL wingspan of the entire plane.
    #cRoot is chord at root.
    #t is the thickness of the
    #Later we'll need to update this to take torsion into account, as well as
    # the Von Mises stress.

    carbonFiberSigma = 4127e6

    #S7075 overall thickness is 9% of chord

    #Does this return negative values if cRoot is less than t?
    thick = .09*cRoot
    I_big = cRoot*thick**3/12.0
    I_small = (cRoot-2.0*t)*(thick-2.0*t)**3/12.0
    I = I_big-I_small

    return (F/2*b/2)*(thick/2.0)/I

# Lift - for constraint Lift must = weight
def L(S, V, CL, rho=1.23):
    return .5*rho*V**2*S*CL
    
#----------------------------------------------
# Constraints
#----------------------------------------------

#Bound order: b, c, V, alpha
bnds = [(0, None), (2.3*t, None), (None, 30.0), (0, None)]
#Note that in the bounds for c, t is a global variable.

#New Constraint Definitions for pyoptsparsewrapper.
#Uses the form Ax <= b or Ax = b, where x is the vector of design variables.
#Using this code as an example, if we wanted to say b - 2c <= 5, then
# A = [1, -2, 0, 0] and b = [5]. 

# Constraint on CL. Inequality.
def conCL(x):
    
    global CLmax
    #CD, CL, sigma
    AVLvars = loadAVLvars(x)
    CL = float(AVLvars['CLtot'])
    
    return (CL - CLmax)
    

# Constraint on stress. Inequality.
def conStress(x):
    
    global t, mat_Density
    
    W = findW(x[0], x[1], mat_Density)
    #height = .09*x[1] #x[1] should be the chord. This is max thickness of an S7075 wing.
    sigma = findStress(x[0], x[2], .005, W/2.0)
    print sigma    
    
    AVLvars = loadAVLvars(x)
    sigmaYield = 4127.0e6 #!!!CHANGE THIS!!!
    
    # This code might be troublesome. Check later.
    if(sigma >= 0):
        return (sigma - sigmaYield)
    elif(sigma < 0):
        return (-sigma - sigmaYield)

# Constraint that L = W. Equality.
def conLW(x):
    
    global mat_Density, rho    
    AVLvars = loadAVLvars(x)
    CL = float(AVLvars['CLtot'])
    W = findW(x[0], x[1], mat_Density)
    
    return (W - (.5)*rho*(x[2])**2*CL)

# Constraint that V can't go below 1.2*Vstall. Inequality.
def conV(x):
    
    global mat_Density, rho, n, CLmax
    S = x[0]*x[1]
    W = findW(x[0], x[1], mat_Density)    
    
 
#Constraint that ensures that the chord never goes so low that .09*chord is 
# less than 2x the thickness. Based on the hollow rectangle approximation. 
# Inequality.
def conChord(x):
    global t
    
    return 2.3*t - x[1]
    

#cons = ({'type': 'ineq', 'fun': conCL}, \
#        {'type': 'ineq', 'fun': conStress}, \
#        {'type': 'eq', 'fun': conLW}, \
#        {'type': 'ineq', 'fun': conV}, \
#        {'type': 'ineq', 'fun': conChord(x)})


#---------------------------------------------------
# Actual Optimization Code
#---------------------------------------------------

opt = SNOPT()
opt2 = SLSQP()
opt3 = NSGA2()

def objective(x):
    global mat_Density, rho, t, n, CLmax    
    
    fRet = netPower(x)
    #All constraints need to have the form c(x) <= 0
    #cRet has 5 fields, because the equality constraint conLW will need two
    # constraints to bound it to zero.
    cRet = [conCL(x), conStress(x), conLW(x), conV(x), conChord(x)]
    
    return fRet, cRet


ub = [10000, 100, 30, 20]
lb = [0, 0, 0, 0]

xopt, fopt, info = optimize(objective, x0, lb, ub, opt2)
    




