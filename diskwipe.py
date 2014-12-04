import dmidecode
import subprocess
import threading
import SocketServer
import socket
import sys
import time



class SysInfo:
	class Disk:
		def __init__(self, Type, Model, Vendor, Device, Serial, Size, SectSize):
			self.Type = Type
			self.Model = Model
			self.Vendor = Vendor
			self.Device = Device
			self.Serial = Serial
			self.Size = int(Size)
			self.SectSize = int(SectSize)
			def BlockCount(self):
				#if self.Size is None:
				if self.Size == 0:
					return 0
				else:
					return (self.Size / self.SectSize)
			def Name(self):
				Dev = self.Device.split('/', 2)
				return Dev[2]

	def __init__(self):
		#Get all required system info
		for v in dmidecode.system().values():
                	if type(v) == dict and v['dmi_type'] == 1:
                        	self.Mfg = str((v['data']['Manufacturer']))
                        	self.Model = str((v['data']['Product Name']))
                        	self.Serial = str((v['data']['Serial Number']))
		for x in dmidecode.chassis().values():
                        if type(x) == dict and x['dmi_type'] == 3:
				self.FFactor = str((x['data']['Type']))
        	for x in dmidecode.processor().values():
                	if type(x) == dict and x['dmi_type'] == 4:
                        	self.CPUMfg = str((x['data']['Manufacturer']))
                        	self.CPUFam = str((x['data']['Family']))
                        	self.CPUVer = str((x['data']['Version']))
                        	self.CPUFrq = str((x['data']['Current Speed']))
        	for x in dmidecode.memory().values():
                	if type(x) == dict and x['dmi_type'] == 17:
                        	self.MEMSize = str((x['data']['Size']))
                        	self.MEMType = str((x['data']['Type']))
                        	self.MEMDeta = str((x['data']['Type Detail']))
                        	self.MEMSpeed = str((x['data']['Speed']))
		for x in dmidecode.baseboard().values():
                        if type(x) == dict and x['dmi_type'] == 10:
				if str((x['data']['dmi_on_board_devices'][0]['Type'])) == "Video":
					self.Video = str((x['data']['dmi_on_board_devices'][0]['Description']))
				if str((x['data']['dmi_on_board_devices'][0]['Type'])) == "Sound":
                                        self.Audio = str((x['data']['dmi_on_board_devices'][0]['Description']))
				if str((x['data']['dmi_on_board_devices'][0]['Type'])) == "Ethernet":
                                        self.Network = str((x['data']['dmi_on_board_devices'][0]['Description'])) 
		### Workarounds for things python-dmidecode doesn't do
        	command = "grep \"model name\" /proc/cpuinfo | uniq | awk -F\" \" {' print $4 $5 \" \" $6 \" \" $8 '} | sed 's/(.\{1,2\})/ /g'"
	        self.CPUName = subprocess.check_output(command, shell=True).strip()
	        command = "MSiz=0; for Size in $(dmidecode -t 17 | grep \"Size:\" | awk {' print $2 '}); do MSiz=$(($MSiz+$Size)); done; echo $MSiz"
	        self.MEMSize = subprocess.check_output(command, shell=True).strip()
	        command = "dmidecode -t 17 | grep \"Type:\" | awk {' print $2 '} | uniq"
	        self.MEMType = subprocess.check_output(command, shell=True).strip()
		if self.Video is None:
	        	command = "lspci | grep VGA | awk -F: {' print $3 '}"
	        	self.Video = subprocess.check_output(command, shell=True).strip()
		if self.Audio is None:
	        	command = "lspci | grep Audio | awk -F: {' print $3 '}"
	        	self.Audio = subprocess.check_output(command, shell=True).strip()
		if self.Network is None:
	        	command = "lspci | grep Ethernet | awk -F: {' print $3 '}"
	        	self.Network = subprocess.check_output(command, shell=True).strip()
		command = "lspci | grep 802.11 | awk -F: {' print $3 '}"
                self.WiFi = subprocess.check_output(command, shell=True).strip()
		command = "echo \"Not Yet Implemented\""
                self.Battery = subprocess.check_output(command, shell=True).strip()
		### Get hard drive info
		self.Drive = []
		command = "lshw -C disk"
		CMDOutput = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		Type = None
		Model = None
		Vendor = None
		Device = None
		Serial = None
		Size = 0
		SectSize = 0
		for line in CMDOutput.stdout:
			if "*-" in line:
				#print("Found: "+line)
				Line = line.split('-', 1)
				Type = Line[1].strip()
			if "product:" in line:
				#print("Found: "+line)
				Line = line.split(':', 1)
				Model = Line[1].strip()
			if "vendor:" in line:
				#print("Found: "+line)
				Line = line.split(':', 1)
				Vendor = Line[1].strip()
			if "logical name:" in line:
				#print("Found: "+line)
				Line = line.split(':', 1)
				Device = Line[1].strip()
			if "serial:" in line:
				#print("Found: "+line)
				Line = line.split(':', 1)
				Serial = Line[1].strip()
			if "size:" in line:
				command = "fdisk -l /dev/sda | grep \""+Device+":\" | awk {' print $5 '}"
				Size = subprocess.check_output(command, shell=True).strip()
				#print("Size: "+Size)
				command = "fdisk -l /dev/sda | grep \"Sector\" | awk {' print $4 '}"
				SectSize = subprocess.check_output(command, shell=True).strip()
				#print("SectSize: "+SectSize)
			if "configuration:" in line:
				Dev = Device.split('/', 2)
				if (Type == "cdrom"):
					self.Optical = Vendor+" "+Model
				else:
					if Vendor is None:
						Line = Model.split(' ', 1)
						Vendor = Line[0].strip()
						Model = Line[1].strip()
					self.Drive.append(self.Disk(Type, Model, Vendor, Device, Serial, Size, SectSize))
				Type = None
				Model = None
				Vendor = None
				Device = None
				Serial = None
				Size = 0
				SectSize = 0


Host = SysInfo()
print("System:    "+Host.Mfg+" "+Host.Model+" ("+Host.Serial+")")
print("Type:      "+Host.FFactor)
print("Processor: "+Host.CPUName+" @ "+Host.CPUFrq+"MHz")
print("Memory:    "+Host.MEMSize+" MB "+Host.MEMType+" @ "+Host.MEMSpeed)
print("Optical:   "+Host.Optical)
print("Video:     "+Host.Video)#Video
print("Audio:     "+Host.Audio)#Audio
print("Network:   "+Host.Network)#Network
print("Wireless:  "+Host.WiFi)
print("Battery:   "+Host.Battery)#Battery
print("Connected Drives:")
Drive = Host.Drive
for x in Drive:
	print(x.Device+": "+x.Vendor+" "+x.Model+" "+x.Serial+" "+str(x.Size))
print(" ")
print(" ")
print("Contacting Tabernus Server")

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        Request = self.request.recv(1024)
        cur_thread = threading.current_thread()
	print "Received: {}".format(Request)
        #response = "{}: {}".format(cur_thread.name, data)
	Response = None
	if format(Request) == "NODEMO":
		Response = "NODEMO-OK"
	if format(Request) == "SYSPNG": ### TOD - Respond with proper variables
                Response = "eth0      Link encap:Ethernet  HWaddr 00:1F:29:04:4D:1A  "
	if Response is not None:
        	self.request.sendall(Response)
		print "Sending: {}".format(Response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "192.168.0.7", 5912

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    client("192.168.0.1", 5911, "Xunknown:GASST-"+Host.Serial)
    client("192.168.0.1", 5911, "GUI_VERSION:192.168.0.7")
    
while True: time.sleep(0x7FFFFFFF)
