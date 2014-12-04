import dmidecode
import subprocess
import dbus
import curses

stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

def ExitProgram():
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()

def GetSysinfo():
	SysDict = {}
	DriveDict= {}
	SysDict["MEMSize"] = 0
	for v in dmidecode.system().values():
		if type(v) == dict and v['dmi_type'] == 1:
            		SysDict["Mfg"] = str((v['data']['Manufacturer']))
			SysDict["Model"] = str((v['data']['Product Name']))
			SysDict["Serial"] = str((v['data']['Serial Number']))
	for x in dmidecode.processor().values():
		if type(x) == dict and x['dmi_type'] == 4:
			#SysDict["CPUMfg"] = str((x['data']['Manufacturer']))
			#SysDict["CPUFam"] = str((x['data']['Family']))
			#SysDict["CPUVer"] = str((x['data']['Version']))
			SysDict["CPUFrq"] = str((x['data']['Current Speed']))
	for x in dmidecode.memory().values():
                if type(x) == dict and x['dmi_type'] == 17:
                        #SysDict["MEMSize"] = str((x['data']['Size']))
                        SysDict["MEMType"] = str((x['data']['Type']))
                        #SysDict["MEMDeta"] = str((x['data']['Type Detail']))
                        SysDict["MEMSpeed"] = str((x['data']['Speed']))

	command = "grep \"model name\" /proc/cpuinfo | uniq | awk -F\" \" {' print $4 $5 \" \" $6 \" \" $8 '} | sed 's/(.\{1,2\})/ /g'"
        SysDict["CPUName"] = subprocess.check_output(command, shell=True).strip()
	command = "MSiz=0; for Size in $(dmidecode -t 17 | grep \"Size:\" | awk {' print $2 '}); do MSiz=$(($MSiz+$Size)); done; echo $MSiz"
        SysDict["MEMSize"] = subprocess.check_output(command, shell=True).strip()
	command = "dmidecode -t 17 | grep \"Type:\" | awk {' print $2 '} | uniq"
        SysDict["MEMType"] = subprocess.check_output(command, shell=True).strip()
	command = "lspci | grep VGA | awk -F: {' print $3 '}"
        SysDict["Video"] = subprocess.check_output(command, shell=True).strip()
	command = "lspci | grep Audio | awk -F: {' print $3 '}"
        SysDict["Audio"] = subprocess.check_output(command, shell=True).strip()
	command = "lspci | grep Ethernet | awk -F: {' print $3 '}"
        SysDict["Network"] = subprocess.check_output(command, shell=True).strip()

	### Read drive info from lshw -C disk
	command = "lshw -C disk"
	CMDOutput = subprocess.check_output(command, shell=True).strip()
	for line in CMDOutput:
		if "*-disk" in line:
			DiskMod = CMDOutput.stdout[line+2]
			DiskDev = CMDOutput.stdout[line+5]
			DiskSer = CMDOutput.stdout[line+7]
			DiskCap = CMDOutput.stdout[line+8]
			print(DiskMod+"\n")
			print(DiskDev+"\n")
			print(DiskSer+"\n")
			print(DiskCap+"\n")	

	return SysDict

#def GetDriveinfo():


MainScreen = curses.initscr()
MainScreen.border(0)
ScreenSize = MainScreen.getmaxyx()
MainTitle = " Data Destruction Client "
TitleStart = ((ScreenSize[1] - len(MainTitle)) / 2)
MainScreen.addstr(0, TitleStart, MainTitle)
#MainScreen.refresh()

StatusWin = MainScreen.subwin(9, 21, 1, 1)
StatusWin.border(0)
WinSize = StatusWin.getmaxyx()
WinTitle = " Client Status "
TitleStart = ((WinSize[1] - len(WinTitle)) / 2)
StatusWin.addstr(0, TitleStart, WinTitle)
#StatusWin.refresh()

InfoWin = MainScreen.subwin(9, 40, 1, 23)
InfoWin.border(0)
WinSize = InfoWin.getmaxyx()
WinTitle = " System Information "
TitleStart = ((WinSize[1] - len(WinTitle)) / 2)
InfoWin.addstr(0, TitleStart, WinTitle)
#InfoWin.refresh()

DeviceWin = MainScreen.subwin(9, (ScreenSize[1] - 65), 1, 64)
DeviceWin.border(0)
WinSize = DeviceWin.getmaxyx()
WinTitle = " System Devices "
TitleStart = ((WinSize[1] - len(WinTitle)) / 2)
DeviceWin.addstr(0, TitleStart, WinTitle)
#DeviceWin.refresh()

DriveWin = MainScreen.subwin((ScreenSize[0] - 11), (ScreenSize[1] - 2), 10, 1)
DriveWin.border(0)
WinSize = DriveWin.getmaxyx()
WinTitle = " Storage Devices "
TitleStart = ((WinSize[1] - len(WinTitle)) / 2)
DriveWin.addstr(0, TitleStart, WinTitle)

### Client Status Info
StatusWin.addstr(1, 1, "IP Addr: ")
StatusWin.addstr(2, 1, "Gateway: ")

### System Specifications
SysDict = GetSysinfo()
InfoWin.addstr(1, 1, "Mfg:    "+SysDict["Mfg"])
InfoWin.addstr(2, 1, "Model:  "+SysDict["Model"])
InfoWin.addstr(3, 1, "Serial: "+SysDict["Serial"])
InfoWin.addstr(4, 1, "CPU:    "+SysDict["CPUName"])
InfoWin.addstr(5, 1, "CPUSpd: "+SysDict["CPUFrq"]+" MHz")
InfoWin.addstr(6, 1, "Memory: "+SysDict["MEMSize"]+" "+SysDict["MEMType"]+" "+SysDict["MEMSpeed"])


### System Devices
DeviceWin.addstr(1, 1, "Optical: ")
DeviceWin.addstr(2, 1, "VideoHW: "+SysDict["Video"])
DeviceWin.addstr(3, 1, "AudioHW: "+SysDict["Audio"])
DeviceWin.addstr(4, 1, "Network: "+SysDict["Network"])
DeviceWin.addstr(5, 1, "Wireless: "+SysDict["Network"])
DeviceWin.addstr(6, 1, "Battery: ")

### Drive Info
#GetDriveinfo()



MainScreen.refresh()
MainScreen.getch()

ExitProgram()

