#!/usr/bin/python
# exception list 
# Outputs IP based on orginal scope and left over from completed list
#
import os, optparse
import subprocess
import sys, getopt
import time
import operator
import itertools

parser = optparse.OptionParser(usage='python %prog -s SCOPE -e EXCEPTION',
                               prog=sys.argv[0],
                               )
parser.add_option('-s','--scope',action="store", help="List of IPs in scope. REQUIRED", type="string", dest="scopefile")

parser.add_option('-e', '--except',action="store", help="list of IPs already scanned or out of scope.. REQUIRED", type="string", dest="exceptlist")
parser.add_option('-v', '--verbose',action="store", help="Turn on verbose output. Must be set to on.", dest="ver")

parser.add_option('-o', '--out',action="store", help="Output File. Default results will be written to newlist.txt.", type="string", dest="outfile", default="newlist.txt")

options, args = parser.parse_args()

#grab the options into variables
scopevar = options.scopefile
exceptvar = options.exceptlist
vervar = options.ver
outputvar = options.outfile

def List (file_name):
 if (vervar == 'on'):
  print "Here is the file name";
  print file_name;
 of = open(file_name, 'r').readlines()
 list = []
 for lines in of:
   list.append(lines.strip())  
 return list

def binToAddress(binAddress):
        if (vervar == 'on'):
         print 'Bin address:\t\t%s' % binAddress
        return [ int(val,2) for val in binAddress ]

def getIpList(hostmin, hostmax):
    tmpmin = hostmin.split('.')
    tmpmax = hostmax.split('.') 
    ranges = [ range(i, j + 1) for i, j in zip(list(map(int, tmpmin)),list(map(int, tmpmax))) ]
    complete = [] 
    for ip in itertools.product(*ranges):
        complete.append( '.'.join(list(map(str, list(ip)))))
    return complete

def numhosts(ipwildcard):
    tmpWild = list(map(int, ipwildcard.split('.')))
    ranges = list(map(lambda e: len(range(0, e + 1)), tmpWild))
    numhosts = reduce(operator.mul, ranges)-2
    return numhosts if numhosts > 0 else 1        

def hostMin(address):
    temp = address.split('.')
    temp[3] = str(int(temp[3])+1)
    return listToString(temp)  
    
def hostMax(address, wildcard):
    #print 'hostMax';
    #print 'Address:  %s, wildcard: %s' % (address,wildcard);
    tmpAddr = address.split('.')
    tmpWild = wildcard.split('.')
    tmpWild[3] = str(int(tmpWild[3])-1)
    return listToString(list(map(sum, zip(list(map(int, tmpAddr)), list(map(int, tmpWild))))))
        
def netmask(mask):
    binMask = '%s%s' % ('1'*int(mask), '0'*(32-int(mask)))
    maskList = list(map(''.join, zip(*[iter(binMask)] * 8)))
    netmask = binToAddress(maskList)
    return listToString(netmask)
        
def wildcard(mask):
    binMask = '%s%s' % ('1'*int(mask), '0'*(32-int(mask)))
    maskList = list(map(''.join, zip(*[iter(binMask)] * 8)))
    netmask = binToAddress(maskList)
    wildcard = [ 255-val for val in netmask ]
    return listToString(wildcard)
 
def listToString(ipList):
    return list(map('.'.join, [ list(map(str, ipList))] ))[0]
   
def network(address, netmask):
    #print 'network call';
    #print 'address: %s , netmask: %s ' % (address,netmask)
    binNetwork = [ bin(int(a,2) & int(b,2))[2:].zfill(8) for a, b in zip(addressToBin(address), addressToBin(netmask))]
    return binToAddress(binNetwork)
     
def addressToBin(address):
    #print 'addresstobin:\t\t%s' % address
    return [ bin(int(val))[2:].zfill(8) for val in address.split('.') ]

def allips(iprange):
 if (vervar == 'on'):
  print "Here is the IP given";
  print iprange;
 if "/" in iprange:
  if (vervar == 'on'):
   print "found /";
  index = iprange.index('/')
  base = iprange[:index]
  intMask = iprange[index+1:]
  ipnetmask = netmask(intMask)
  ipwildcard = wildcard(intMask)
  binBase = addressToBin(base)    
  subnet = listToString(network(base, ipnetmask))
  hostmin = hostMin(subnet)
  hostmax = hostMax(subnet, ipwildcard)
  total = numhosts(ipwildcard)
  broadcast = hostMin(hostmax)
  allips = getIpList(hostmin, hostmax) 
  
  if (vervar == 'on'):
   print 'Base:\t\t%s' % base
   print 'Netmask:\t%s' % ipnetmask
   print 'Wildcard:\t%s' % ipwildcard
   print 'Broadcast:\t%s' % broadcast
   print 'Subnet ID:\t%s' % subnet
   print 'Host min:\t%s' % hostmin
   print 'Host max:\t%s' % hostmax
   print 'Total Hosts:\t%s' % total
   print '---------Printing all the ips--------';
   for ip in allips:
    print (ip)
   print '--------End all ips printed----'; 
  return allips

def checkforip(ipaddress,cleanscopelist):
 if (vervar == 'on'):
  print 'The ip address to check: %s' % ipaddress;
  print 'The scope is: %s' % cleanscopelist;
 if (ipaddress not in cleanscopelist):
  if (vervar == 'on'):
   print 'The ip address %s was not looked at' % ipaddress;
 
#main program

dirtyscopelist=[]
dirtyexceptionlist=[]
cleanscopelist=[]
cleanexceptionlist=[]

dirtyscopelist = List(scopevar)
dirtyexceptionlist = List(exceptvar)

#work through the list to check if any CIDR notation and put all ip in one array
for scope in dirtyscopelist:
  if (vervar == 'on'):
   print 'Evalating %s in scope' % scope;
  if ("/" in scope):
   cleanscopelist.extend(allips(scope));
  else:
   cleanscopelist.append(scope)

if (vervar == 'on'):
  print 'scope is: %s' % cleanscopelist;


#for exception in exceptionlist:
for scope in dirtyexceptionlist:
  if (vervar == 'on'):
   print 'Evalating %s in scope' % scope;
  if ("/" in scope):
   cleanexceptionlist.extend(allips(scope));
  else:
   cleanexceptionlist.append(scope)

if (vervar == 'on'):
  print 'exceptionlist is: %s' % cleanexceptionlist;

#ensure list have not duplucates
nodupscopelist = list(set(cleanscopelist))
nodupexceptionlist = list(set(cleanexceptionlist))
if (vervar == 'on'):
  print 'nodupscopelist is: %s' % nodupscopelist;
  print 'nodupexceptionlist is: %s' % nodupexceptionlist;

#remove the excepted ips from the scope
for badips in nodupexceptionlist:
 if (vervar == 'on'):
  print 'Looking for bad ip: %s ' % badips;
 try:
  test = nodupscopelist.remove(badips)
 except ValueError:
  pass
 if (vervar == 'on'):
  if (test == 0):
    print 'Not found';
  else:
    print 'Found';

#nodupscopelist should only have left over IPs
for ipsleft in nodupscopelist:
 print ipsleft;

#write the results
if (outputvar != None):
   f = open(outputvar, 'w')
   for ipsleft in nodupscopelist:
    f.write(ipsleft + '\n')
    


