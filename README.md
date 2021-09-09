# PyLinkam
Python package for controlling the Linkam TMS94 programmer via RS232

__Disclaimer:__
USB to Null Modem (Cross-Wired) RS232 Serial Adapter is required to communicate with the TMS94 programmer. 
See the 'Cable connections' section page 3 of the documentation in the doc folder for more details. 

## Basic usage 

```
import PyLinkam as PL
TMS94 = PL.programmer('COM14')
T_C = TMS94.temperature
print(T_C)
```

In order to heat the stage to a target temperature: 
``` 
T_C_target = 500 #°C
TMS94.set_rate(10) #°C/min
TMS94.set_limit(T_C_target)
TMS94.start()
```

The stage will hold this temperature until the limit is changed: 
```
RT = 25 °C
TMS94.set_limit(RT)
```

or until the program is closed: 
```
TMS94.stop()
```

Before shutting down your python program, make sure to close the serial communication: 
```
TMS94.ser.close()
```

## Installation 

This package can be installed locally with pip after having downloaded the files
