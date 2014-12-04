import subprocess

class Drive:
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
    
### Read drive info from lshw -C disk
Drives = []
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
		print("Found: "+line)
		Line = line.split('-', 1)
		Type = Line[1].strip()
	if "product:" in line:
		print("Found: "+line)
		Line = line.split(':', 1)
		Model = Line[1].strip()
	if "vendor:" in line:
                print("Found: "+line)
                Line = line.split(':', 1)
                Vendor = Line[1].strip()
	if "logical name:" in line:
                print("Found: "+line)
                Line = line.split(':', 1)
                Device = Line[1].strip()
	if "serial:" in line:
                print("Found: "+line)
                Line = line.split(':', 1)
                Serial = Line[1].strip()
	if "size:" in line:
                command = "fdisk -l /dev/sda | grep \""+Device+":\" | awk {' print $5 '}"
		Size = subprocess.check_output(command, shell=True).strip()
		print("Size: "+Size)
		command = "fdisk -l /dev/sda | grep \"Sector\" | awk {' print $4 '}"
                SectSize = subprocess.check_output(command, shell=True).strip()
		print("SectSize: "+SectSize)
	if "configuration:" in line:
		Dev = Device.split('/', 2)
		Drives.append(Drive(Type, Model, Vendor, Device, Serial, Size, SectSize))
		#for Disk in Drives:
		#	print(Disk.Name()+": "+str(Disk.BlockCount()))
		Type = None
		Model = None
		Vendor = None
		Device = None
		Serial = None
		Size = 0
		SectSize = 0

for Disk in Drives:
	print(Disk.Name()+": "+str(Disk.BlockCount()))
