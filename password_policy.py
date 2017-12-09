#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>
#OpenLDAP Password Policy overlay (ppolicy). The connection parameters and DN parameters deeply depend on your setup

import sys
import os
import ldap
import ldap.modlist as modlist

class LdapPpolicy(object):
	"""docstring for LdapPpolicy"""
	def __init__(self):
		super(LdapPpolicy, self).__init__()
		self.cmd_add_ldif = "ldapmodify -a -x -D \"cn=admin,cn=config\" -W -f {0}"
		self.cmd_ldap_restart = "systemctl restart slapd.service"

	#connect to OpenLdap
	def ldap_connect(self):
		hostname="localhost"
		search_base = "dc=liderahenk,dc=org"
		base_dn = "cn=admin,"+str(search_base)
		pwd = "1"
		ldap_obj = ldap.open(hostname)
		ldap_obj.simple_bind_s(base_dn,pwd)

	def ldap_service(self):
		os.system(self.cmd_ldap_restart)
		print("------>>> restart slapd service\n")

	#add ppolicy.ldif to ldap
	def add_schema(self):
		try:
			os.system(self.cmd_add_ldif.format("/etc/ldap/schema/ppolicy.ldif"))
			print("------------------>>> added ppolicy schema...\n")
		except Exception as e:
			print("[ERROR] Error adding ldif file "+str(e))


	#create ldif file for load ppolicy module 
	def create_ppolicymodule(self):
		ldif_string = "dn: cn=module{0},cn=config\n"\
						"changetype: modify\n"\
						"add: olcModuleLoad\n"\
						"olcModuleLoad: ppolicy"\


		ldif_name = "ppolicymodule.ldif"
		self.ldif_file_create(ldif_string,ldif_name)
		
		#add ldif file
		try:
			os.system(self.cmd_add_ldif.format("ppolicymodule.ldif"))
			print("-------------------->>>> added ppolicy module...\n")

		except Exception as e:
			print("[ERROR] Error adding ldif file "+str(e))

	# ppolicy overlay ldif string
	def create_ppolicyoverlay(self):
		ldif_string = "dn: olcOverlay={0}ppolicy,olcDatabase={1}hdb,cn=config\n"\
								"objectClass: olcOverlayConfig\n"\
								"objectClass: olcPPolicyConfig\n"\
								"olcOverlay: {0}ppolicy\n"\
								"olcPPolicyDefault: cn=DefaultPolicy,ou=PasswordPolicies,dc=liderahenk,dc=org\n"\
								"olcPPolicyHashCleartext: TRUE\n"\
								"olcPPolicyUseLockout: TRUE\n"\
								"olcPPolicyForwardUpdates: FALSE"\

		ldif_name = "ppolicyoverlay.ldif"
		self.ldif_file_create(ldif_string,ldif_name)

		try:
			os.system(self.cmd_add_ldif.format("ppolicyoverlay.ldif"))
			print("------------------->>>> added ppolicyoverlay ldif...\n")
		except Exception as e:
			print("[ERROR] Error adding ldif file "+str(e))	

	# create ldif file
	def ldif_file_create(self,ldif_string,ldif_name):
		cmd_module_file = "touch "+str(ldif_name)
		os.system(cmd_module_file)
		print ("command is running "+str(cmd_module_file))
		module_ldif = open(str(ldif_name),"w")
		module_ldif.write(ldif_string)


if __name__ == '__main__':


	app = LdapPpolicy()
	app.add_schema()
	app.create_ppolicymodule()
	app.create_ppolicyoverlay()
	app.ldap_service()