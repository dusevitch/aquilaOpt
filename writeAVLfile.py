#!/usr/bin/python

def writeFileAVL(x, airfoil='s7075.dat', filename='AVLtest.avl'):
#if True:
#  # Open a file
#  filename='AVLtest.avl'
  file = open(filename, "wb")

  #-------------VARIABLES---------------------

  
#  b0 = 3.0 # m
#  c0 = .5 # m
#  V0 = 20.0 #m/s
#  aoa0 = 7.0 # deg
#
#  x = [b0, c0, V0, aoa0]

  airfoil_file = airfoil # We'll need to change this to allow more airfoil files to be used.
  Cref = x[1] # Chord
  Bref = x[0] # Span
# velocity = x[2]# Velocity of Plane. Not needed in this script.
# aoa = x[3] # angle of Attack. Currently unnecessary with the way loadAVLtest is written (3/8/16)


  Sref = Bref*Cref# Surface Area
  #--------------Functions---------------------
  def w(string, file=file):
    file.write(string + '\n');

  #-------------Write to File-----------------------

  # Beginning
  w('Current AVL File')
  w('#Mach')
  w('0.0')
  w('#IYsym   IZsym   Zsym')
  w('0       0       0.0')
  w('#Sref    Cref    Bref')
  w(str(Sref) + ' ' + str(Cref) + ' ' + str(Bref))
  w('#Xref    Yref    Zref')
  w(str(Cref/4.0)+' 0.0 0.0')

  # Main Wing Components
  w('#====================================================================');
  w('SURFACE ')
  w('Wing')
  w('#Nchordwise  Cspace   Nspanwise   Sspace')
  w('10 1.0') # We can change the number of chordwise sections here, 10 max is recommended, in the future
  w('YDUPLICATE') # Duplicate across Y-AXIS
  w('0.0')
  w('ANGLE') # Rotate surface by angle (when duplicated)
  w('0.0')

  w('#-------------------------------------------------------------')
  w('SECTION')
  w('#Xle Yle Zle Chord Ainc Nspanwise Sspace')
  w('0 0 0 ' + str(Cref) + ' 0.0 10 1')
  w('AFILE')
  w(airfoil_file)

  w('SECTION')
  w('#Xle Yle Zle Chord Ainc Nspanwise Sspace')
  w('0 '+str(Bref/2.0)+' 0 ' + str(Cref) + ' 0.0 10 1')
  w('AFILE')
  w(airfoil_file)

  # Close file
  file.close()


#-----------------------------------------------------------------------------------#
# This section allows this module to be run as a script directly from the terminal.
# To run, type the following in the terminal:
# $ python writeAVLfile.py bValue cValue airfoilFile
# bValue: wingspan of the plane
# cValue: chord of the plane
# airfoilFile: name of the .dat file of the desired airfoil
#-----------------------------------------------------------------------------------#

if __name__ == '__main__':
    import sys
    
    x = [float(sys.argv[1]), float(sys.argv[2])]
    try:
        airfoilTemp = sys.argv[3]
    except:
        print 'Missing/invalid airfoil. Using s7075.dat as default.'
        airfoilTemp = 's7075.dat'
    
    writeFileAVL(x, airfoilTemp)



















# #------------- This is EXTRA Code for running AVL Program (needs edits to syntax from Matlab)------------------------

# #Load the AVL definition of the aircraft
# file.write(  'LOAD %s\n', strcat(filename,'.avl'))

# #Load mass parameters
# file.write(  'MASS %s\n', strcat(filename,'.mass'))
# file.write(  'MSET\n')
# #Change this parameter to set which run cases to apply
# file.write(  '%i\n',   0)

# #Disable Graphics
# file.write(  'PLOP\ng\n\n')

# #Open the OPER menu
# file.write(  '%s\n',   'OPER')

# #Define the run case
# file.write(  'c1\n',   'c1')
# file.write(  'v %6.4f\n',velocity)
# file.write(  '\n')

# #Options for trimming %fprintf(  '%sn', 'd1 rm 0'); %Set surface 1 so rolling moment is 0 %fprintf(  '%sn', 'd2 pm 0'); %Set surface 2 so pitching moment is 0

# #Run the Case
# file.write(  '%s\n',   'x')




# #Save the st data
# file.write(  '%s\n',   'st')
# file.write(  '%s%s\n',basename,'.st')
# #Save the sb data
# file.write(  '%s\n',   'sb')
# file.write(  '%s%s\n',basename,'.sb')
# #Drop out of OPER menu
# file.write(  '%s\n',   '')




# #Switch to MODE menu
# file.write(  '%s\n',   'MODE')
# file.write(  '%s\n',   'n')
# #Save the eigenvalue dat
# file.write(  '%s\n',   'w')
# file.write(  '%s%s\n', basename,'.eig')

# #Exit MODE Menu
# file.write(  '\n')



# #Quit Program
# file.write(  'Quit\n')


# Close file
#file.close()
