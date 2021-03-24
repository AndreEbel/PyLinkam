__version__ = '1.0.0'
import serial
import threading

class programmer(object):
    """ 
    Serial communication via RS232 for
    - the T92, T93, T94 series programmers
    - MDS 600 motorised stage
    - DSC 600
    """
    SB1 = None
    EB1 = None 
    PB1 = None
    T_Bytes = None
    T_C_bytes = None
    T_C = None 
    def __init__(self, port):
        """
        programmer object creator

        Parameters
        ----------
        port : string
            port to be used for serial communication with the controller
        """
        self.lock = threading.Lock()
        self.ser = serial.Serial(port=port,
                                baudrate=19200,
                                bytesize=8,
                                stopbits = serial.STOPBITS_ONE,         
                                timeout=0,
                                parity=serial.PARITY_NONE,
                                rtscts=1)

    def read(self):
        """
        Serial read 

        Returns
        -------
        answer: bytes
            bytes read from the controller

        """
        answer = self.ser.readline()[0:-1] #last byte is a carriage return (useless)
        return answer

    def write(self, command):
        """
        Serial write.

        Parameters
        ----------
        command : string
            command to be passed to the controller
        """
        CR = "\r"
        input_bytes = bytes(command + CR, 'ascii')
        self.ser.write(input_bytes)

    def query(self, command):
        """
        write a command and read the reply.
        
        Parameters
        ----------
        command: string
            command to be passed to the controller

        Returns
        -------
        answer : bytes
            one or more bytes

        """
        with self.lock:
          self.write(command)
          answer =  self.read()
          return answer 
    
   
    def rate_command(self, rate): 
        """
        set the heating or cooling rate of a ramp
        
        Parameters
        ----------
        rate : float
            °C/min, resolution 0.01°C/min

        """
        command = ('R1%d' % (rate*100))
        self.write(command)
        
    def limit_command(self, limit):
        """
        set the limit temperature of a ramp
        
        Parameters
        ----------
        limit : float
            °C, resolution 0.1°C

        """
        command = 'L1%d' %(limit*10)
        self.write(command)
        
    def start(self):
        """
        Tells the programmer to start heating or cooling at the rate specified in R1 and to the limite set by L1
        When the limit is reached, the SB1 byte will return 30H
        """
        self.write('S')
        
    def stop(self): 
        """
        Tells the programmer to stop heating or cooling
        """
        self.write('E')
    
    def hold(self): 
        """
        If the programmer is heating or cooling, this command will hold the current temperature until either a heat or cool command is received. 
        When holding at the limit value either a heat, cool or a hold command will chang the programmer function. 
        When the programmer is holding at the specified limit the SB1 byte will return 40H, otherwise 50H will be returned.
        """
        self.write('O')
    
    def get_T_bytes(self): 
        """
        function that read the bytes return after the 'T' command has been passed
        """
        answer = self.query('T')
        self.T_bytes = bytearray(answer)
        self.SB1 = self.T_bytes[0]
        self.EB1 = self.T_bytes[1]
        self.T_C_bytes = self.T_bytes[6:10]
        
    def decode_temperature(self):
        """
        function to decode the temperature bytes returned by the controller

        Returns
        -------
        T_C : int
            temperature in °C

        """
        hex_temp = ''
        for b in self.T_C_bytes: 
            hex_temp+=(chr(b))
        T_C = int(hex_temp, 16)/10
        self.T_C  = T_C
        return T_C
        
    def decode_status_byte(self):
        """
        function that decode the status byt read from the controller

        Returns
        -------
        status : string
            status of the controller according to the documentation 

        """
        SB1 = self.SB1
        if SB1 == int(str('01'),16): 
            status = 'stopped'
        elif SB1 == int(str('10'),16): 
            status = 'heating'
        elif SB1 == int(str('20'),16): 
            status = 'cooling'
        elif SB1 == int(str('30'),16): 
            status = 'holding at the limit or limit reached end of a ramp'
        elif SB1 == int(str('40'),16): 
            status = 'holding the limit time'
        elif SB1 == int(str('50'),16): 
            status = 'holding the current temperature'
        else: 
            status = 'problem reading SB1'
        return status
    def decode_error_byte(self):
        """
        function that decode the error byte read from the controller

        Returns
        -------
        error_message : string
            error messages according to the documentation 

        """
        EB1 =  format(self.EB1, 'b')
        error_message = ''
        
        if EB1[-1] == 1: 
            error_message += 'Cooling rate cannot be maintained \n'
        if EB1[-2] == 1: 
            error_message += 'Stage not connected or sensor is open circuit \n'
        if EB1[-3] == 1: 
            error_message += 'Current protection has been set due to an overload \n'
        if EB1[-4] == 1: 
            error_message += 'TS1500 stage tried to exit profile at a temperature > 300°C (not allowed)\n'
        if EB1[-5] == 1: 
            error_message += 'TMS92 has a TS1500 and THM stage connected (not allowed)\n'
        if EB1[-6] == 1: 
            error_message += 'Problems with the RS232 data transmission\n'
        
        if error_message == '':
            error_message += 'no error'
        return error_message
    
    def __del__(self):
        self.ser.close()
        print('serial connection off')

