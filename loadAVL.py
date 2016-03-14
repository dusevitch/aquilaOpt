import subprocess
import sys
import re
import os

def loadAVLvars(x, filename="AVLtest.avl"):
  #--------------------------VARIABLES ------------------------
  print x  
  aoa = x[3] # Angle of Attack

  #Write the correct AVL file
  #---------------------------Run AVL and Commands---------------------------------
  try:  
    file = open("AVLoutput.avl", "wb")
  except:
    print 'That didnt work.'

  p = subprocess.Popen('../bin/avl vanilla.avl', shell=True, stdout=file, stderr=subprocess.PIPE, stdin=subprocess.PIPE) #Change 'avl.exe' to whatever line of code opens AVL
  p.stderr.close()
  p.stdin.write('load ' + filename +'\n')
  p.stdin.write('oper'+'\n')

  p.stdin.write('a a ' + str(aoa) +'\n')	#set angle of attack

  # file.close()
  # file = open("AVLoutput.avl", "w") #clear file before getting contents needed

  p.stdin.write('x'+'\n') # get solution


  p.stdin.close()
  file.close()
  return_code = p.wait()
  print p

  #-------------------Parse Output file for Variables needed----------------------
  list = ['CLtot', 'CDtot']  # list of variables to find - insert vars here
  pattern = []


  for i in list:
    pattern.append(re.compile(i+'[ ]=[ ]{1,4}\-?[0-9]+.[0-9]{1,6}'))

  var_array = []

  for i in pattern:
    file = open('AVLoutput.avl', 'r+')
    for line in file:
      answer = i.findall(line)
      for ans in answer:
        var_array.append(ans);
    file.close()

  dict = {}
  for var in var_array:
    spstr = var.split()
    sub1 = spstr[0]
    sub2 = spstr[2]
    dict[sub1] = sub2

#Check to see if output file is empty:

  if os.stat('AVLoutput.avl').st_size == 0:
    print '\n'
    print '***************************\n'
    print '        AVL ERROR          '
    print '    Output file is blank   '
    print '         x input:          \n'
    print x
    print '\n***************************\n'
    print '                           '

  return dict
  
#x = 7
#loadAVLvars(x)
print 'done'