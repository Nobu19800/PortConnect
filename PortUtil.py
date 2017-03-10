#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file PortUtil.py
 @brief 
 @date $Date$

 @author 宮本　信彦　n-miyamoto@aist.go.jp
 産業技術総合研究所　ロボットイノベーション研究センター
 ロボットソフトウエアプラットフォーム研究チーム

"""
import sys
import time


import RTC
import OpenRTM_aist
import CosNaming

class PortUtil:
	def __init__(self, orb, names):
		self.nameservers = []
		for name in names:
			cosnaming = OpenRTM_aist.CorbaNaming(orb,name)
			self.nameservers.append(cosnaming)
			
	def create_connector(self, name, prop_arg, port0, port1):
		
		prop = prop_arg
		conn_prof = RTC.ConnectorProfile(name, "", [port0, port1],[])

		p0 = port0.get_port_profile()
		p1 = port1.get_port_profile()
		port_prop0 = OpenRTM_aist.Properties()
		OpenRTM_aist.NVUtil.copyToProperties(port_prop0, p0.properties)
		port_prop1 = OpenRTM_aist.Properties()
		OpenRTM_aist.NVUtil.copyToProperties(port_prop1, p1.properties)
		
		if port_prop0.getProperty("port.port_type") == "DataOutPort" and port_prop1.getProperty("port.port_type") != "DataInPort":
			prop.setProperty("dataport.dataflow_type","pull")
		else:
			prop.setProperty("dataport.dataflow_type","push")


			

 


		prop.setProperty("dataport.interface_type","corba_cdr")

		conn_prof.properties = []
		OpenRTM_aist.NVUtil.copyFromProperties(conn_prof.properties, prop)

		return conn_prof

	def already_connected(self, localport, otherport):
		conprof = localport.get_connector_profiles()
		for c in conprof:
			for p in c.ports:
				if p._is_equivalent(otherport):
					return True

		return False

	def exist_port(self, portList, port):
		for p in portList:
			if port._is_equivalent(p):
				return True
		return False

	def connect_ports(self, localports):
		ports = self.get_ports()
		for port in ports:
			
			if self.exist_port(localports, port):
				continue
			for localport in localports:
				if self.already_connected(localport, port):
					continue
				
							
				p0 = localport.get_port_profile()
				p1 = port.get_port_profile()
				con_name = ""
				con_name += p0.name
				con_name += ":"
				con_name += p1.name
				prop = OpenRTM_aist.Properties()
				cprof = self.create_connector(con_name, prop, localport, port)
				
				localport.connect(cprof)[0]
			
						
						
			

	def get_ports(self):
		ports = []
		rtcs = self.get_components()
		for rtc in rtcs:
			try:
				ports.extend(rtc.get_ports())
			except:
				pass
		return ports

	def get_components(self):
		rtcs = []
		for cns in self.nameservers:
			root_cxt = cns.getRootContext()
			self.search_components(root_cxt, rtcs)
		return rtcs
	
	def search_components(self, context, rtcs):
		length = 500
		bl,bi = context.list(length)
		for i in bl:
			if i.binding_type == CosNaming.ncontext:
				next_context = context.resolve(i.binding_name)
				self.search_components(next_context, rtcs)
			elif i.binding_type == CosNaming.nobject:
				if i.binding_name[0].kind == "rtc":
					try:
						cc = OpenRTM_aist.CorbaConsumer()
						cc.setObject(context.resolve(i.binding_name))
						obj = cc.getObject()._narrow(RTC.RTObject)
						rtcs.append(obj)
					except:
						pass

	

