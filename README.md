# PyLinkam
Python package for controlling the Linkam TMS94 programmer via RS232
 
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

Before shutting down yout python program, make sure to close the serial communication: 
```
TMS94.ser.close()
```

## Installation 

This package can be installed locally with pip after having downloaded the files
