#!/usr/bin/env python3

import sys, os, time



def main():

	os.system("clear")

	print("""

	Script designed for Debian based distributions. Feel free to change it and redistribute it.

		 _______ _______ ______
		(_______|_______|_____ \ 
		 _____      _    _____) )
		|  ___)    | |  |  ____/
		| |        | |  | |
		|_|        |_|  |_|



Choose an option :


	[+] 1 - Install ProFTP
	[+] 2 - Check it's status
	[+] 3 - Start console

	[*] 0 - Exit


							Credit : LoKy

     """)





def choix():

	numero = int(input("Choose an option : "))

	if numero == 3:
		console()

	elif numero == 0:
		print("Closing...")
		os.system("clear")
		sys.exit()

	elif numero == 1:
		os.system("apt install -y proftpd")
		time.sleep(2)

		#### START 2 ####

	elif numero == 2:
		os.system("systemctl status proftpd")
		print('')
		valid = str(input("""
Is it running ? y/n : """))

		if valid == 'y':
			os.system("clear")

		elif valid == 'n':
			print("""Checking /etc/hosts config.

				""")
			os.system("cat /etc/hosts")
			print('')
			valid2 = str(input("Is your ip address and machine name here and correct ? y/n :  "))
			if valid2 == 'y':
				print("Check the logs to find what's wrong.")
				os.system("tail -30 /var/log/syslog")
				sys.exit()

			elif valid2 == 'n':
				os.system("ifconfig")
				print("")
				ipaddr = input("Your ip : ")
				machinename = input("Your machine name ( <username>@<machine_name> ) : ")

				with open ('/etc/hosts', 'a') as file:
					file.write(f'{ipaddr}	{machinename}')
					file.close()
					print('')
					os.system("cat /etc/hosts")
				print('')
				print("Restarting proftpd service...")
				os.system("systemctl restart proftpd")
				os.system("systemctl status proftpd")


		##### END 2 #####



def console():

	os.system("clear")

	print("""

	Welcome to the console.

	[+] 1 - First configuration
	[+] 2 - Add new user
	[+] 3 - Delete a user
	[+] 4 - Delete an interface

	[*] 0 - Exit

	     """)


	numero2 = int(input("Choose an option : "))


	if numero2 == 0:
		os.system("clear")
		return 0;

	elif numero2 == 1:

		print("We have to create a virtual interface. [Step 1/5]")
		print('')
		time.sleep(1)
		os.system("ifconfig")
		print('')
		print("""Check for your network interface (eth0, enp1s0, ...)

We will create new one like this : ifconfig <NetworkInterface>:1 <new ipaddress>/<Mask> up

		      """)
		net = input("Your interface : ")
		num = int(input("A number between 0 and 9 : "))
		ip  = input("A new ip address (example : <your ip>+1 = 192.168.1.23 + 1 -> 192.168.1.24) : ")
		mask = int(input("Your subnet mask (exemple : /24) do not write the '/' : "))
		os.system(f"ifconfig {net}:{num} {ip}/{mask} up")
		print('')
		os.system("ifconfig")
		time.sleep(2)

		### Proftpd.conf Settings ###

		print("\nLet's configure proftpd.conf very quickly. \n Opening /etc/proftpd/proftpd.conf for configuration. Wait a sec... [Step 2/5]")
		with open("/etc/proftpd/proftpd.conf","a") as config:
			config.write("""\nInclude /etc/proftpd/tls.conf
Include /etc/proftpd/virtuals.conf""")
			config.close()
			time.sleep(2)
			print('\nconf ready. Opening /etc/proftpd/virtuals.conf in order to create a first VHost.')
			time.sleep(2)

		print("\nCreating your first user to setup virtuals.conf")
		username = input("Choose a username : ")
		os.system(f"useradd {username} && passwd {username}")
		print(f"\nAdding {username} to a group and creating {username} directories /srv/ftp/{username} and /home/{username}")
		time.sleep(2.5)
		os.system(f"adduser {username} {username} && mkdir /srv/ftp/{username} && chown {username}:{username} /srv/ftp/{username} && mkdir /home/{username}")

		print("""Done.
Configuration of tls.conf ... [Step 3/5]""")

		with open("/etc/proftpd/tls.conf", "w") as tls:
			tls.write("""
#
# Proftpd sample configuration for FTPS connections.
#
# Note that FTPS impose some limitations in NAT traversing.
# See http://www.castaglia.org/proftpd/doc/contrib/ProFTPD-mini-HOWTO-TLS.html
# for more information.
#

<IfModule mod_tls.c>
TLSEngine                               on
TLSLog                                  /var/log/proftpd/tls.log
TLSProtocol                             SSLv23
#
# Server SSL certificate. You can generate a self-signed certificate using
# a command like:
#
# openssl req -x509 -newkey rsa:1024 \
#          -keyout /etc/ssl/private/proftpd.key -out /etc/ssl/certs/proftpd.crt \
#          -nodes -days 365
#
# The proftpd.key file must be readable by root only. The other file can be
# readable by anyone.
#
# chmod 0600 /etc/ssl/private/proftpd.key
# chmod 0640 /etc/ssl/private/proftpd.key
#
TLSRSACertificateFile                   /etc/ssl/certs/proftpd.crt
TLSRSACertificateKeyFile                /etc/ssl/private/proftpd.key
#
# CA the server trusts...
#TLSCACertificateFile                    /etc/ssl/certs/CA.pem
# ...or avoid CA cert and be verbose
#TLSOptions                      NoCertRequest EnableDiags
# ... or the same with relaxed session use for some clients (e.g. FireFtp)
#TLSOptions                      NoCertRequest EnableDiags NoSessionReuseRequired
#
#
# Per default drop connection if client tries to start a renegotiate
# This is a fix for CVE-2009-3555 but could break some clients.
#
#TLSOptions                                                     AllowClientRenegotiations
#
# Authenticate clients that want to use FTP over TLS?
#
TLSVerifyClient                         off
#
# Are clients required to use FTP over TLS when talking to this server?
#
TLSRequired                             on
#
# Allow SSL/TLS renegotiations when the client requests them, but
# do not force the renegotations.  Some clients do not support
# SSL/TLS renegotiations; when mod_tls forces a renegotiation, these
# clients will close the data connection, or there will be a timeout
# on an idle data connection.
#
#TLSRenegotiate                          required off
</IfModule>
""")
			tls.close()


		print('\nCreating rsa-key. If you do not know any answer, write a simple dot "."\n')
		time.sleep(1)
		os.system("sudo openssl req -x509 -newkey rsa:2048 -keyout /etc/ssl/private/proftpd.key -out /etc/ssl/certs/proftpd.crt -nodes -days 3650")
		print("\n\nInstalling proftpd-mod-crypto...")
		os.system("apt install proftpd-mod-crypto")

# modules.conf

		print("\nConfiguration of modules.conf [Step 4/5]")


		with open("/etc/proftpd/modules.conf", "a") as module :
			module.write("LoadModule mod_tls.c")
			module.close()
			time.sleep(2)



		print("\nConfiguration of virtuals.conf [Step 5/5]")



		with open("/etc/proftpd/virtuals.conf", "a") as virtual:

			# VirtualHost creation

			virtual.write(f"""

<VirtualHost {ip}>
Include /etc/proftpd/tls.conf
ServerAdmin             admin@mail.org
ServerName              "FTP"
User                    {username}
Group                   {username}


        <Limit LOGIN>
                Order Allow,Deny
                Allowgroup {username}
                Deny from all
        </Limit>



Umask                   022
TransferLog             /var/log/proftpd/xfer/ftp.logs
MaxLoginAttempts        10
RequireValidShell       no
DefaultRoot             /srv/ftp/{username}
AllowOverwrite          yes
</VirtualHost>
""")
			virtual.close()

		os.system("cat /etc/proftpd/virtuals.conf")
		print('\nCongrats everythings look ok')
		time.sleep(5)
		console()

	elif numero2 == 2:
		print('\nAdding a new user...\n')
		time.sleep(2)
		os.system("ifconfig")
		inter2 = input("Enter your interface name : ")
		num2 = int(input("Choose a number between 1-9 : "))
		ip2 = input("Enter a new ip :  ")
		mask2 = int(input("Your mask ( without '/' ) : "))
		os.system(f"ifconfig {inter2}:{num2} {ip2}/{mask2} up && ifconfig")
		print('')
		username2 = input("Choose a name : ")
		os.system(f"useradd {username2} && passwd {username2}")
		os.system(f"adduser {username2} {username2} && mkdir /srv/ftp/{username2} && mkdir /home/{username2} && chown {username2}:{username2} /srv/ftp/{username2}")
		print("\nCreating a VirtualHost")
		time.sleep(1)

		with open("/etc/proftpd/virtuals.conf","a") as conf2:
			conf2.write(f"""
<VirtualHost {ip2}>
Include /etc/proftpd/tls.conf
ServerAdmin             admin@mail.org
ServerName              "FTP"
User                    {username2}
Group                   {username2}


        <Limit LOGIN>
                Order Allow,Deny
                Allowgroup {username2}
                Deny from all
        </Limit>



Umask                   022
TransferLog             /var/log/proftpd/xfer/ftp.logs
MaxLoginAttempts        10
RequireValidShell       no
DefaultRoot             /srv/ftp/{username2}
AllowOverwrite          yes
</VirtualHost>

""")
		time.sleep(1)
		conf2.close()
		print("Done.")
		time.sleep(2)
		console()


	if numero2 == 3:
		user3 = input("\nEnter a username to delete it : ")
		os.system(f"userdel {user3} && rm -r /home/{user3} && rm -r /srv/ftp/{user3}")
		print(f"Deleting {user3}...")
		time.sleep(0.5)
		print("Done.")
		print(f"Deleting /home/{user3}...")
		time.sleep(0.5)
		print("Done.")
		print(f"Deleting /srv/ftp/{user3}...")
		time.sleep(0.5)
		print("Done.")

		clean = str(input("Would you like to delete the VHost ? y/n : "))
		if clean == 'y' :
			print("Opening /etc/proftpd/virtuals.conf for you to delete the VHost manually. Press Ctrl+k to delete quickly.")
			time.sleep(2)
			os.system("nano /etc/proftpd/virtuals.conf")

		elif clean == 'n':
			return 0;
		console()

	if numero2 == 4:
		print("\n")
		os.system("ifconfig")
		interface2 = input("Choose the complete name of the interface you want to remove : ")
		os.system(f"ifconfig {interface2} down")
		print("Done.\n")
		os.system("ifconfig")
		time.sleep(3)
		console()


if __name__ == '__main__':

	while 1:
		main()
		choix()





