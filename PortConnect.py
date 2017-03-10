#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file PortConnect.py
 @brief Port Connect Component
 @date $Date$

 @author 宮本　信彦　n-miyamoto@aist.go.jp
 産業技術総合研究所　ロボットイノベーション研究センター
 ロボットソフトウエアプラットフォーム研究チーム

"""
import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist
import struct

from PortUtil import PortUtil



class DataListener(OpenRTM_aist.ConnectorDataListenerT):
	def __init__(self, outports, file=None):
		self._outports = outports
		self._file = file
	def setFile(self, file):
		self._file = file
	def __call__(self, info, cdrdata):
		if self._file:
			t = time.time()
			time_data = struct.pack("f",float(t))
			self._file.write(time_data)
			length_data = struct.pack("i",len(cdrdata))
			self._file.write(length_data)
			self._file.write(cdrdata)
		for port in self._outports:
			cons = port.connectors()
			for con in cons:
				if con.profile().properties.getProperty("dataflow_type") == "push":
					con._publisher.write(cdrdata, 0, 0)
				elif con.profile().properties.getProperty("dataflow_type") == "pull":
					con.getBuffer().write(cdrdata)

# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
portconnect_spec = ["implementation_id", "PortConnect", 
		 "type_name",         "PortConnect", 
		 "description",       "Port Connect Component", 
		 "version",           "1.0.0", 
		 "vendor",            "AIST", 
		 "category",          "Test", 
		 "activity_type",     "STATIC", 
		 "max_instance",      "1", 
		 "language",          "Python", 
		 "lang_type",         "SCRIPT",
		 "conf.default.filename", "data.dat",
		 "conf.default.nameservers", "localhost",

		 "conf.__widget__.filename", "text",
		 "conf.__widget__.nameservers", "text",

         "conf.__type__.filename", "string",
         "conf.__type__.nameservers", "string",

		 ""]
# </rtc-template>

##
# @class PortConnect
# @brief Port Connect Component
# 
# ネームサーバーからRTCを検索して、データポートに勝手に接続するRTC
# 
# 
class PortConnect(OpenRTM_aist.DataFlowComponentBase):
	
	##
	# @brief constructor
	# @param manager Maneger Object
	# 
	def __init__(self, manager):
		OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

		
		self._d_in = RTC.Time(0,0)
		"""
		勝手に接続するインポート
		 - Type: PortConnect::CdrData
		"""
		self._inIn = OpenRTM_aist.InPort("in", self._d_in)
		
		self._d_out = RTC.Time(0,0)
		"""
		勝手に接続するアウトポート
		 - Type: PortConnect::CdrData
		"""
		self._outOut = OpenRTM_aist.OutPort("out", self._d_out)


		


		# initialize of configuration-data.
		# <rtc-template block="init_conf_param">
		"""
		受信バイナリデータ保存ファイル名
		 - Name: fiename filename
		 - DefaultValue: data.dat
		"""
		self._filename = ['data.dat']
		"""
		検索するネームサーバー
		 - Name: nameservers nameservers
		 - DefaultValue: localhost
		"""
		self._nameservers = ['localhost']
		
		# </rtc-template>

		self._file = None
		 
	##
	#
	# The initialize action (on CREATED->ALIVE transition)
	# formaer rtc_init_entry() 
	# 
	# @return RTC::ReturnCode_t
	# 
	#
	def onInitialize(self):
		# Bind variables and configuration variable
		self.bindParameter("filename", self._filename, "data.dat")
		self.bindParameter("nameservers", self._nameservers, "localhost")
		
		# Set InPort buffers
		self.addInPort("in",self._inIn)
		
		# Set OutPort buffers
		self.addOutPort("out",self._outOut)
		
		# Set service provider to Ports
		
		# Set service consumers to Ports
		
		# Set CORBA Service Ports
		manager = OpenRTM_aist.Manager.instance()
		orb = manager.getORB()
		#names = OpenRTM_aist.split(manager.getConfig().getProperty("corba.nameservers"), ",")
		names = OpenRTM_aist.split(self._nameservers[0], ",")
		self.pu = PortUtil(orb, names)

		self.sendDataListener = DataListener(self._outports)
		self._inIn.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,self.sendDataListener)
		
		return RTC.RTC_OK
	
		##
		# 
		# The finalize action (on ALIVE->END transition)
		# formaer rtc_exiting_entry()
		# 
		# @return RTC::ReturnCode_t
	
		# 
	def onFinalize(self):
	
		return RTC.RTC_OK
	
		##
		#
		# The startup action when ExecutionContext startup
		# former rtc_starting_entry()
		# 
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onStartup(self, ec_id):
	
		return RTC.RTC_OK
	
		##
		#
		# The shutdown action when ExecutionContext stop
		# former rtc_stopping_entry()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onShutdown(self, ec_id):
	
		return RTC.RTC_OK
	
		##
		#
		# The activated action (Active state entry action)
		# former rtc_active_entry()
		#
		# @param ec_id target ExecutionContext Id
		# 
		# @return RTC::ReturnCode_t
		#
		#
	def onActivated(self, ec_id):
		self._file = open(self._filename[0], "wb")
		self.sendDataListener.setFile(self._file)
		return RTC.RTC_OK
	
		##
		#
		# The deactivated action (Active state exit action)
		# former rtc_active_exit()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onDeactivated(self, ec_id):
		if self._file:
			self._file.close()
		return RTC.RTC_OK
	
		##
		#
		# The execution action that is invoked periodically
		# former rtc_active_do()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onExecute(self, ec_id):
		self.pu.connect_ports([self._inIn.getPortRef(),self._outOut.getPortRef()])
		return RTC.RTC_OK
	
		##
		#
		# The aborting action when main logic error occurred.
		# former rtc_aborting_entry()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onAborting(self, ec_id):
	
		return RTC.RTC_OK
	
		##
		#
		# The error action in ERROR state
		# former rtc_error_do()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onError(self, ec_id):
	
		return RTC.RTC_OK
	
		##
		#
		# The reset action that is invoked resetting
		# This is same but different the former rtc_init_entry()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onReset(self, ec_id):
	
		return RTC.RTC_OK
	
		##
		#
		# The state update action that is invoked after onExecute() action
		# no corresponding operation exists in OpenRTm-aist-0.2.0
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#

		#
	def onStateUpdate(self, ec_id):
	
		return RTC.RTC_OK
	
		##
		#
		# The action that is invoked when execution context's rate is changed
		# no corresponding operation exists in OpenRTm-aist-0.2.0
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onRateChanged(self, ec_id):
	
		return RTC.RTC_OK
	



def PortConnectInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=portconnect_spec)
    manager.registerFactory(profile,
                            PortConnect,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    PortConnectInit(manager)

    # Create a component
    comp = manager.createComponent("PortConnect")

def main():
	mgr = OpenRTM_aist.Manager.init(sys.argv)
	mgr.setModuleInitProc(MyModuleInit)
	mgr.activateManager()
	mgr.runManager(True)

	comp = mgr.getComponent("PortConnect0").getObjRef()
	ec = comp.get_owned_contexts()[0]
	ec.activate_component(comp)
	while True:
		time.sleep(0.2)
		state = ec.get_component_state(comp)
		if state == RTC.INACTIVE_STATE:
			ec.activate_component(comp)
		elif state == RTC.ERROR_STATE:
			ec.reset_component(comp)

if __name__ == "__main__":
	main()

