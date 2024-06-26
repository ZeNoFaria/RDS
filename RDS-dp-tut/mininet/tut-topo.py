#!/usr/bin/env python3
# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
############################################################################
# RDS-TUT jfpereira - Read all comments from this point on !!!!!!
############################################################################
# This code is given in 
# https://github.com/p4lang/behavioral-model/blob/main/mininet/1sw_demo.py
# with minor adjustments to satisfy the requirements of RDS-TP3. 
# This script works for a topology with one P4Switch connected to 253 P4Hosts. 
# In this TP3, we only need 1 P4Switch and 2 P4Hosts.
# The P4Hosts are regular mininet Hosts with IPv6 suppression.
# The P4Switch it's a very different piece of software from other switches 
# in mininet like OVSSwitch, OVSKernelSwitch, UserSwitch, etc.
# You can see the definition of P4Host and P4Switch in p4_mininet.py
###########################################################################

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSSwitch, Controller

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep

# If you look at this parser, it can identify 4 arguments
# --behavioral-exe, with the default value 'simple_switch'
## this indicates that the arch of our software switch is the 'simple_switch'
## and any p4 program made for this arch needs to be compiled against de 'v1model.p4'
# --thrift-port, with the default value of 9090, which is the default server port of
## a thrift server - the P4Switch instantiates a Thrift server that allows us
## to communicate our P4Switch (software switch) at runtime
# --num-hosts, with default value 2 indicates the number of hosts...
# --json, is the path to JSON config file - the output of your p4 program compilation
## this is the only argument that you will need to pass in orther to run the script


parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", default='simple_switch')
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=2)
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)

args = parser.parse_args()

sw_mac_base = "00:aa:bb:00:00:%02x"
host_mac_base = "00:04:00:00:00:%02x"

sw_ip_base = "10.0.%d.254"
host_ip_base =  "10.0.%d.%d/24"

ips = [10,20,100]



class SingleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        # adding a P4Switch
        switch = self.addSwitch('s1',
                                sw_path = sw_path,                       #mudar thrift port para uma lista
                                json_path = json_path,                  
                                thrift_port = thrift_port)
        # adding host and link with the right mac and ip addrs
        # declaring a link: addr2=sw_mac gives a mac to the switch port
        for h in range(n):                                              
            host = self.addHost('h%d' % (h + 1),
                                ip = host_ip_base % ((h + 1)),
                                mac = host_mac_base % (h + 1))
            sw_mac = sw_mac_base % (h + 1)
            self.addLink(host, switch, addr2=sw_mac)



########################################################################################################################################################################



class DoubleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, n, **opts):
        # Call __init__ of Topo class
        Topo.__init__(self, **opts)
        # Create routers using P4Switch
        routers = []
        for r in range(2):
            router = self.addSwitch('R%d' % r, cls=P4Switch, sw_path=sw_path, json_path=json_path, thrift_port=thrift_port)
            routers.append(router)
            thrift_port = thrift_port + 1

        # Link routers in a circle
        self.addLink(routers[0], routers[1],addr1=(sw_mac_base % 1),addr2=(sw_mac_base % 2))

        for i in range(2):
            host = self.addHost('h%d' % (i + 1),
                                ip = host_ip_base % (i + 1),
                                mac = host_mac_base % (i + 1))
            self.addLink(routers[i], host,addr1=(sw_mac_base % (i + 3)))
        



###################################################################################################################################################################



class TripleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, n, **opts):
        # Call __init__ of Topo class
        Topo.__init__(self, **opts)
        # Create routers using P4Switch
        routers = []
        for r in range(3):
            router = self.addSwitch('R%d' % (r+1), cls=P4Switch, sw_path=sw_path, json_path=json_path, thrift_port=thrift_port)
            routers.append(router)
            thrift_port = thrift_port + 1

        # Link routers in a circle
        comp = 1
        for i in range(3):
            adr1 = (sw_mac_base % (comp))
            comp = comp + 1
            adr2 = (sw_mac_base % (comp))
            self.addLink(routers[i], routers[(i + 1) % 3], 
                        addr1=adr1, addr2=adr2)
            comp = comp + 1
        # Create network switches using OVSSwitch
        switches = []
        for s in range(3):
            switch = self.addSwitch('S%d' % (s+1), cls=OVSSwitch)
            switches.append(switch)

        # Assuming routers and switches are lists of equal length
        for i, (router, switch) in enumerate(zip(routers, switches)):
            self.addLink(router, switch, addr1=(sw_mac_base % (i + 7)),addr2=(sw_mac_base % (i + 10)))


        # Add hosts and connect them to the network switches
        for s, switch  in enumerate(switches):
            for i in range(3):
                host = self.addHost('h%d' % (s * 3 + i + 1),
                                    ip = host_ip_base % ((s+1),ips[i]),
                                    mac = host_mac_base % (s * 3 + i + 1))
                self.addLink(switch, host, addr1=(sw_mac_base % (s * 3 + i + 13)))
            
            

def main():
    num_hosts = args.num_hosts

    topo = TripleSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            num_hosts)

    # the host class is the P4Host
    # the switch class is the P4Switch
    net = Mininet(topo = topo,host = P4Host,controller=None)

    # Here, the mininet will use the constructor (__init__()) of the P4Switch class, 
    # with the arguments passed to the SingleSwitchTopo class in order to create 
    # our software switch.
    net.start()

    # an array of the mac addrs from the switch
    sw_mac = [sw_mac_base % (n + 1) for n in range(num_hosts)]
    # an array of the ip addrs from the switch 
    # they are only used to define defaultRoutes on hosts 
    sw_addr = [sw_ip_base % (n + 1) for n in range(num_hosts)]

    
    #h.setARP(sw_addr[n], sw_mac[n]) # populates the arp table of the host
    #h.setDefaultRoute("dev eth0 via %s" % sw_addr[n]) # sets the defaultRoute for the host
    # populating the arp table of the host with the switch ip and switch mac
    # avoids the need for arp request from the host
    h1 = net.get('h1')
    h1.setARP("10.0.1.254", "00:aa:bb:00:00:07")
    h1.setDefaultRoute("dev eth0 via 10.0.1.254")

    h2 = net.get('h2')
    h2.setARP("10.0.1.254", "00:aa:bb:00:00:07")
    h2.setDefaultRoute("dev eth0 via 10.0.1.254")
    
    h3 = net.get('h3')
    h3.setARP("10.0.1.254", "00:aa:bb:00:00:07")
    h3.setDefaultRoute("dev eth0 via 10.0.1.254")

    h4 = net.get('h4')
    h4.setARP("10.0.2.254", "00:aa:bb:00:00:08")
    h4.setDefaultRoute("dev eth0 via 10.0.2.254")

    h5 = net.get('h5')
    h5.setARP("10.0.2.254", "00:aa:bb:00:00:08")
    h5.setDefaultRoute("dev eth0 via 10.0.2.254")
    
    h6 = net.get('h6')
    h6.setARP("10.0.2.254", "00:aa:bb:00:00:08")
    h6.setDefaultRoute("dev eth0 via 10.0.2.254")

    h7 = net.get('h7')
    h7.setARP("10.0.3.254", "00:aa:bb:00:00:09")
    h7.setDefaultRoute("dev eth0 via 10.0.3.254")

    h8 = net.get('h8')
    h8.setARP("10.0.3.254", "00:aa:bb:00:00:09")
    h8.setDefaultRoute("dev eth0 via 10.0.3.254")
    
    h9 = net.get('h9')
    h9.setARP("10.0.3.254", "00:aa:bb:00:00:09")
    h9.setDefaultRoute("dev eth0 via 10.0.3.254")
    
    for n in range(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()

    sleep(1)  # time for the host and switch confs to take effect

    print("Ready !")

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
