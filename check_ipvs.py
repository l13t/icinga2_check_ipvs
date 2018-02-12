#!/usr/bin/env python3

import argparse
import sys
import re
import os

def parse_ipvs_output(res):
  output = {}
  pattern_vs = '(\w+)\s+([0-9.]+):(\w+)\s+(\w+)'
  pattern_node = '\s->\s([0-9.]+):(\w+)\s+(\w+)\s+(\d+)\s+(\d+)\s+(\d+)'
  cp_vs = re.compile(pattern_vs)
  cp_node = re.compile(pattern_node)
  current_vs = ''
  for line in res.split('\n'):
    if line[:3] == 'TCP' or line[:3] == 'UDP':
      current_vs = line
      result = cp_vs.split(line)
      output = {
        'type': result[1],
        'vip': result[2],
        'vport': result[3],
        'scheduler': result[4],
        'nodes': []
      }
    elif line[2:4]== '->':
      result = cp_node.split(line)
      if len(result) > 1:
        output['nodes'].append({'nip': result[1], 'nport': result[2], 'fwd': result[3], 'weight': result[4], 'active': result[5], 'inactive': result[6]})
  return output

def text_is_ip(txt):
  if re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", txt):
    return True
  else:
    return False

sudo = ""
protocol_list = {
                 'tcp': '-t',
                 'udp': '-u'
}

parent_parser = argparse.ArgumentParser(add_help=True, description='Check for ldirectord/ipvs', epilog="Written 2016, Dmytro Prokhorenkov")
parent_parser.add_argument('--proto', type=str, help="Set protocol for service (tcp, udp)", default="tcp")
parent_parser.add_argument('--service', type=str, help="Specify service name (It should be specified like <ip_address>:<port>)")
parent_parser.add_argument('--sudo', help="Use SUDO to get information", action="store_true")
_args = vars(parent_parser.parse_args())

### Check if specified protocol type is correct
if _args['proto'] not in protocol_list:
  print("ERROR: Wrong protocol type is specified\n")
  parent_parser.print_help()
  sys.exit(3)

### Check if service is specified 
if (_args['service'] == None):
  parent_parser.print_help()
  sys.exit(3)

### Check if service address is correct ip address and port is not out of range
ip_info = re.split(":", _args['service'])
if not(text_is_ip(ip_info[0])):
  print("ERROR: You specified wrong ip\n")
  parent_parser.print_help()
  sys.exit(3)
try:
  port = int(ip_info[1])
except ValueError:
  print("ERROR: You specified not numeric port\n")
  parent_parser.print_help()
  sys.exit(3)
if not(1 <= port <=65535):
  print("ERROR: You specified wrong port\n")
  parent_parser.print_help()
  sys.exit(3)

### Check if sudo is enabled
if _args['sudo']:
  sudo = "sudo "

cmd = sudo + "/sbin/ipvsadm -L -n " + protocol_list[_args['proto']] + " " + _args['service']
result = os.popen(cmd).read()

ipvs = parse_ipvs_output(result)

issues = []

for node in ipvs['nodes']:
  if int(node['weight']) == 0:
    txt = 'Node ' + node['nip'] + ':' + node['nport'] + ' is unreachable by load balancer. '
    issues.append(txt)

nagios_output = ""

if issues != []:
  nagios_output = "CRITICAL: We have next issues:\n"
  for issue in issues:
    nagios_output = nagios_output + issue + "\n"
  print(nagios_output)
  sys.exit(2)
else:
  nagios_output = "OK: Service " + ipvs['vip'] + ":" + ipvs['vport'] + " work as expected. " + str(len(ipvs['nodes'])) + " are available."
  print(nagios_output)
  sys.exit(0)