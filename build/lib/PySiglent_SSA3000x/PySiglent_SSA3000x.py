import pyvisa
from numpy import linspace

class PySiglent_SSA3000x:

    # exceptions
    class Exceptions:
        class NoAddressSpecified(Exception):
            def __init__(self) -> None:
                super().__init__('no visa address specified')
        class NotConnected(Exception):
            def __init__(self) -> None:
                super().__init__('instrument connection not implemented')

        class InvalidInsturment(Exception):
            def __init__(self, msg: str = '') -> None:
                super().__init__(
                    f'instrument returned wrong identifier : {msg}')

        class ConnectionError(Exception):
            def __init__(self) -> None:
                super().__init__('instrument failed to connect')

        class FrequencyOutOfRange(Exception):
            def __init__(self, value='') -> None:
                super().__init__(
                    f'freqeuncy {value} outside of interument limit')

        class ReferenceLevelOutOfRange(Exception):
            def __init__(self, value='') -> None:
                super().__init__(
                    f'reference level {value} outside of interument limit')

        class InputAttenuatorOutOfRange(Exception):
            def __init__(self, value='') -> None:
                super().__init__(
                    f'input attenuator {value} outside of interument limit')

        class AmplitudeOffsetOutOfRange(Exception):
            def __init__(self, value='') -> None:
                super().__init__(
                    f'output offset {value} outside of interument limit')

        class ScaleDivOutOfRange(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(
                    f'scale/div {value} outside of interument limit')

        class Invalid_RBW(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} not in valid resolution bandwith')

        class Invalid_VBW(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} not in valid video bandwith')

        class Invalid_VBW_RBW_ratio:
            def __init__(self, value: str = '') -> None:
                super().__init__(
                    f'{value} not in valid video / resolution bandwith ratio')

        class InvalidFilter:
            def __init__(self, value: str = '') -> None:
                super().__init__(
                    f'{value} is not a valid filter, valid : emi, gauss')

        class InvalidDataMode(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} is not a valid data type')

        class InvalidMathFunction(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} is not a math function')

        class InvalidMathVariable(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} is not a valid math variable')

        class MathConstantOutOfRange(Exception):
            def __init__(self, value: float = '') -> None:
                super().__init__(f'{value} outside of range')

        class InvalidAverageType(Exception):
            def __init__(self, value: float = '') -> None:
                super().__init__(f'{value} is not a valid average type')

        class InvalidSweepMode(Exception):
            def __init__(self, value: float = '') -> None:
                super().__init__(f'{value} is not a valid sweep mode')

        class SweepTimeOutOFRange(Exception):
            def __init__(self, value: float = '') -> None:
                super().__init__(f'{value} is not a valid sweep time')

        class InvalidSweepSpeed(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} is not a valid sweep speed')

        class InvalidSweepNumber(Exception):
            def __init__(self, value: str = '') -> None:
                super().__init__(f'{value} is not a valid sweep number')

    class Trace:

        class Exceptions:
            class InvalidMode(Exception):
                def __init__(self, value: str = '') -> None:
                    super().__init__(f'{value} is not a valid trace mode')

            class IvalidDetectionType(Exception):
                def __init__(self, value: float = '') -> None:
                    super().__init__(f'{value} is not a valid detection mode')

            class AverageNumberOutOfRange(Exception):
                def __init__(self, value: float = '') -> None:
                    super().__init__(f'{value} is not a valid average number')

            class AverageNotActive(Exception):
                def __init__(self) -> None:
                    super().__init__('average must be active to restart')

        def __init__(self, set_get_method, query_method, id: int) -> None:
            self.id = id
            self._set_get: function = set_get_method
            self._query_method = query_method

            self._valid_modes = ['WRITe','MAXHold','MINHold','VIEW','BLANk','AVERage']

            self._valid_detection_type = [
                'NEGative', 'POSitive', 'SAMPle', 'AVERage', 'NORMAL', 'QUASi']

            self._average_number_min = 1
            self._average_number_max = 999

            self.average_on = False

        def mode(self, mode: str = None):
            """Selects the display mode for the selected trace,
            WRITe: puts the trace in the normal mode, updating the data.
            MAXHold: displays the highest measured trace value for all the data that has been measured since the function was turned on.
            MINHold: displays the lowest measured trace value for all the data that has been measured since the function was turned on.
            VIEW: turns on the trace data so that it can be viewed on the display.
            BLANk: turns off the trace data so that it is not viewed on the display.
            AVERage: averages the trace for test period."""
            if mode is not None and mode not in self._valid_modes:
                raise self.Exceptions.InvalidMode(mode)
            return self._set_get(f':TRACe' + str(self.id) + ':MODE', mode)  #str

        def get_data(self):
            """This query command returns the current displayed data."""
            data:str = self._query_method(f':TRACe:DATA? {self.id}')
            data_points = data.split(',')[:-1]#last string is ''
            data_float_points = [float(i) for i in data_points]
            return data_float_points 

        def detection_type(self, mode: str = None):
            """Specifies the detection mode. For each trace interval (bucket), average detection displays the average of all the samples within the interval.
            NEGative: Negative peak detection displays the lowest sample taken during the interval being displayed.
            POSitive: Positive peak detection displays the highest sample taken during the interval being displayed.
            SAMPle: Sample detection displays the sample taken during the interval being displayed, and is used primarily to display noise or noise-like signals.
            In sample mode, the instantaneous signal value at the present display point is placed into memory. This detection should not be used to make the most accurate amplitude measurement of non noise-like signals.
            AVERage: Average detection is used when measuring the average value of the amplitude across each trace interval (bucket). The averaging method used by the average detector is set to either video or power as appropriate when the average type is auto coupled.
            NORMAL: Normal detection selects the maximum and minimum video signal values alternately. When selecting Normal detection,”Norm”appears in the upper-left corner.
            QUASi: Quasipeak detection is a form of detection where a signal level is weighted based on the repetition frequency of the spectral components making up the signal. That is to say, the result of a quasi-peak measurement depends on the repetition rate of the signal."""
            if mode is not None and mode in self._valid_detection_type:
                raise self.Exceptions.IvalidDetectionType(mode)
            return self._set_get(f':DETector:TRAC ' + str(self.id), mode) #str

        def average_number(self, avg_number: int = None):
            """Specifies the number of measurements that are combined."""
            if avg_number is not None and self._average_number_min <= avg_number <= self._average_number_max:
                raise self.Exceptions.AverageNumberOutOfRange(avg_number)
            avg = int(self._set_get(':SENSe:AVERage:TRACe' + str(self.id) + ':COUNt', avg_number))
            self.average_on = avg > 1
            return avg

        def average_restart(self):
            """Restarts the trace average. This command is only available when average is on."""
            if not self.average_on:
                raise self.Exceptions.AverageNotActive
            else:
                self._set_get(':SENSe]:AVERage:TRACe' +
                              str(self.id), ':CLEar')  # not return
        
        def sweep_state(self):
            """This query command returns True if trace scan is completed else returns False."""
            return bool(int(self._query_method(f':TRACe:SWEep:STATe? {self.id}')))
            
    def __init__(self, VISA_resource_manager: pyvisa.ResourceManager, address:str = None, open: bool = True, debug:bool = False) -> None:
        # insert the VISA resourceManager object and VISA address, if you do not want to connect the SA right away use opne = False and uhan the open() command to connect
        
        self.rm = VISA_resource_manager
        self.address = address
        self.interface = None
        self.connected = False
        self.debug = debug

        # RF
        self.frequency_min = 50.0
        self.frequency_max = 3199999900  # 3.199.. GHz

        self.ref_level_min = -100.0  # dBm
        self.ref_level_max = +30

        self.input_att_min = 0
        self.input_att_max = 50

        self.amplitude_offset_min = -300  # dB
        self.amplitude_offset_max = +300

        self.scale_div_min = 1  # dB
        self.scale_div_max = 10

        self.valid_RBW = [10, 30, 100, 300, 1 * 10**3, 3 * 10**3,
                          10 * 10**3, 30 * 10**3, 100 * 10**3, 300 * 10**3, 1 * 10**6]
        self.valid_VBW = [1, 3, 10, 30, 100, 300, 1 * 10**3, 3 * 10**3,
                          10 * 10**3, 30 * 10**3, 100 * 10**3, 300 * 10**3, 1 * 10**6]
        self.valid_RBW_VBW_ratio = [
            0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]

        self.traces = [self.Trace(self._set_get,self.query, i) for i in range(1, 5)]

        self._valid_math_functions = [
            'Off', 'X-Y+Ref->Z', 'Y-X+Ref->Z', 'X+Y-Ref->Z', 'X+Const->Z', 'X-Const->Z']
        self._math_variables = ['A', 'B', 'C']

        self._math_const_min = -300  # dB
        self._math_const_max = +300

        self._valid_average_type = ['LOGPower', 'POWer', 'VOLTage']
        self._valid_sweep_modes = ['AUTO', 'FFT', 'SWEep']

        self._sweep_time_min = 917 * 10 ** -9
        self._sweep_time_max = 1000

        self._valid_sweep_speed = ['NORMal', 'ACCUracy']

        self._sweep_number_min = 1
        self._sweep_number_max = 99999

        if open:
            self.connect()

    def write(self, data):
        if self.interface is not None:
            if self.debug:
                print(f'write ->{data}')
            self.interface.write(data)
        else:
            raise self.Exceptions.NotConnected

    def query(self, query_string: str):
        if self.debug:
            print(f'query ->{query_string}')
        response = self.interface.query(query_string)
        if self.debug:
            print(f'response -> {response}')
        return response

    def connect(self, address:str = None):
        """conenct VISA device"""
        if address is not None:  # allow to specify address at connection
            self.address = address
        try:
            if self.address is None: # check for valid address
                raise self.Exceptions.NoAddressSpecified
            self.interface = self.rm.open_resource( #make interface
                self.address, read_termination='\n', write_termination='\n')
            model = self.interface.model_name #check for correect insturment 
            if model in ('SSA3021X', 'SSA3032X'):
                self.connected = True
                # self.setup()  # todo
            else:
                self.connected = False
                self.interface.close()
                # raise Exception(f'Invalid instrument model, only SSA3000x Series analyzers are supported, got : {model}')
                raise self.Exceptions.InvalidInsturment(model)

        except self.pyvisa.errors.VisaIOError:
            self.connected = False
            raise self.Exceptions.ConnectionError
        
        except self.Exceptions.NoAddressSpecified:
            self.connected = False
            raise self.Exceptions.NoAddressSpecified
            

    def disconnect(self):
        """close VISA connection"""
        if self.interface is not None:
            self.interface.close()
        self.connected = False

    def _set_get(self, cmd: str, val=None):
        if self.connected:
            if val is None:
                cmd += '?'
                val = self.query(cmd)
                if self.debug:
                    print(f'response ->{val}')
                return val
            else:
                cmd += f' {val}'
                self.write(cmd)
                return val
        else:
            raise self.Exceptions.NotConnected
    
    def _string_to_bool(self, val:str):
        if val in ('1', 'ON'):
            return True
        return False
    
    # custom fuinctions ---------------
    
    def get_spectrum(self, trace:Trace):
        """used to gwet the spectrum data in a format like [ [freq_1, level_1], [freq_2, level_2], ...]"""
        level_points = trace.get_data()
        start_freq = self.start_frequency()
        stop_freq  = self.stop_frequency()
        frequency_points = linspace(start_freq, stop_freq, len(level_points))
        return list(zip(frequency_points, level_points))

    # function from manual ------------

    def center_freqency(self, frequency: int = None):
        """Sets the center frequency of the spectrum analyzer. [Hz]
        Gets the center frequency."""
        if frequency is not None and not self.frequency_min <= frequency <= self.frequency_max:
            raise self.Exceptions.FrequencyOutOfRange(frequency)
        return float(self._set_get(':FREQuency:CENTer', frequency))

    def start_frequency(self, frequency: int = None):
        """Sets the start frequency of the spectrum analyzer. [Hz]
        Gets the start Frequency"""
        if frequency is not None and not self.frequency_min <= frequency <= self.frequency_max:
            raise self.Exceptions.FrequencyOutOfRange(frequency)
        return float(self._set_get(':FREQuency:STARt', frequency))

    def stop_frequency(self, frequency: int = None):
        """Sets the stop frequency of the spectrum analyzer. [Hz]
        Gets the stop frequency"""
        if frequency is not None and not self.frequency_min <= frequency <= self.frequency_max:
            raise self.Exceptions.FrequencyOutOfRange(frequency)
        return float(self._set_get(':FREQuency:STOP', frequency))

    def center_frequecy_step(self, frequency: int = None):
        """Specifies the center frequency step size. [Hz]
        Gets the center frequency step."""
        if frequency is not None and not self.frequency_min <= frequency <= self.frequency_max:
            raise self.Exceptions.FrequencyOutOfRange(frequency)
        return float(self._set_get(':FREQuency:CENTer:STEP', frequency))

    def center_frequency_step_auto_enable(self, enable: bool = None):
        """Specifies whether the step size is set automatically based on the span.
        Gets center frequency step mode"""
        return self._string_to_bool(self._set_get(':FREQuency:CENTer:STEP:AUTO', enable))
    
    def freqeuncy_offset(self, offset:int = None):
        """include a frequency offset in all measurements.
        gets frequency offset. NOTE: set start-stop/cf-span before and than apply offset"""
        return self._set_get(':FREQuency:OFFSet', offset)
        
    def span(self, frequency: int = None):
        """Sets the frequency span. Setting the span to 0 Hz puts the analyzer into zero span. [Hz]
        Gets span value"""
        if frequency is not None and not self.frequency_min <= frequency <= self.frequency_max:
            raise self.Exceptions.FrequencyOutOfRange(frequency)
        return float(self._set_get(':FREQuency:SPAN', frequency))

    def span_set_full(self):
        """Sets the frequency span to full scale."""
        self.write(':FREQuency:SPAN:FULL')

    def span_set_zero(self):
        """Sets the frequency span to zero span."""
        self.write(':FREQuency:SPAN:ZERO')

    def span_half(self):
        """Sets the frequency span to half of the previous span setting."""
        self.write(':FREQuency:SPAN:HALF')

    def span_half(self):
        """Sets the frequency span to double the previous span setting."""
        self.write(':FREQuency:SPAN:DOUBLE')

        # AUTO TUNE

    def auto(self):
        """Auto tune the spectrum analyzer parameter to display the main signal."""
        self.write(':FREQuency:TUNE:IMMediate')

    # LEVEL
    def reference_level(self, level: float = None):
        """This command sets the reference level for the Y-axis. [dBm]
        Gets reference level."""
        if level is not None and not self.ref_level_min <= level <= self.ref_level_max:
            raise self.Exceptions.ReferenceLevelOutOfRange(level)
        # todo : test resolution
        if level is not None: # build string if level has to be set
            level = f'{level} dBm'
        response:str = self._set_get(':DISPlay:WINDow:TRACe:Y:RLEVel', level)
        try:
            return float(response)
        except ValueError:
            return float(response[:response.rfind(' ')])  #remove last chars until space = remove unit like '10.5 dBm' -> '10.4'

    def input_attenuator(self, att: int = None):
        """Sets the input attenuator of the spectrum analyzer. [dB]
        Gets the input attenuator"""
        if att is not None and not self.input_att_min <= att <= self.input_att_max:
            raise self.Exceptions.InputAttenuatorOutOfRange(att)
        # todo : test resolution
        return float(self._set_get(':POWer:ATTenuation', att)
)
    def input_attenuator_auto(self, enable: bool = None):
        """This command turns on/off auto input port attenuator state.
        Gets input port attenuator state"""
        if type(enable) == bool:
            enable = int(enable)
        return self._string_to_bool(self._set_get(':POWer:ATTenuation:AUTO', enable))  # todo : test resolution

    def input_preamp_enable(self, enable: bool = None):
        """Turns the internal preamp on/off.
        Gets preamp on-off state."""
        if type(enable) == bool:
            enable = int(enable)
        return self._string_to_bool(self._set_get(':POWer:GAIN', enable))  # todo : test resolution

    def amplitude_offset(self, offset: float = None):
        """Sets reference offsets. [dB]
        Gets reference offsets."""
        if offset is not None and not self.amplitude_offset_min <= offset <= self.amplitude_offset_max:
            raise self.Exceptions.ReferenceLevelOutOfRange(offset)
        response:str = self._set_get(':DISPlay:WINDow:TRACe:Y:SCALe:RLEVel:OFFSet', offset)
        try:
            return float(response)
        except ValueError:
            return float(response[:response.rfind(' ')])

    # amplitude unit not implemented
    def scale_mode(self, scale: str = None):
        """Toggles the vertical graticule divisions between logarithmic (log) unit and linear (lin) unit.
        The default logarithmic unit is dBm, and the linear unit is V.
        Gets scale type."""
        if scale not in ('lin', 'log', None):
            raise Exception(f'invalid scale {scale}')
        return self._set_get(':DISPlay:WINDow:TRACe:Y:SPACing', scale)[:3].lower()  # LINear -> LINEAR -> LIN -> lin

    def scale_div(self, scale_div: int = None):
        """This command sets the per-division display scaling for the y-axis when scale type of Y axis is set to Log. [dB]
        Gets Scale/Div when scale type of Y axis is set to Log."""
        if scale_div is not None and not self.scale_div_min <= scale_div <= self.scale_div_max:
            raise self.Exceptions.ScaleDivOutOfRange(scale_div)
        return int(float(self._set_get(':DISPlay:WINDow:TRACe:Y:SCALe:PDIVision', scale_div)))

    # correction not implemented
    def resolution_bw(self, rbw: int = None):
        """Specifies the resolution bandwidth. For numeric entries, all RBW types choose the nearest (arithmetically, on a linear scale, rounding up) available RBW to the value entered. [Hz]"""
        if rbw is not None and rbw not in self.valid_RBW:
            raise self.Exceptions.Invalid_RBW(rbw)
        return float(self._set_get(':SENSe:BWIDth:RESolution', rbw))  # discrete

    def resolution_bw_auto(self, mode: bool = None):
        """Turns on/off auto resolution bandwidth state."""
        if type(mode) == bool:
            mode = int(mode)
        return self._string_to_bool(self._set_get(':SENSe:BWIDth:RESolution:AUTO', mode))

    def video_bw(self, vbw: int = None):
        """Specifies the video bandwidth."""
        if vbw is not None and vbw not in self.valid_VBW:
            raise self.Exceptions.Invalid_VBW(vbw)
        return float(self._set_get(':SENSe:BWIDth:VIDeo', vbw)) #discrete

    def video_bw_auto(self, mode: bool = None):
        """This command turns on/off auto video bandwidth state."""
        if type(mode) == bool:
            mode = int(mode)
        return self._string_to_bool(self._set_get(':SENSe:BWIDth:VIDeo:AUTO', mode))

    def video_resolution_bandwith_ratio(self, ratio: float = None):
        """Specifies the ratio of the video bandwidth to the resolution bandwidth."""
        if ratio is not None and ratio not in self.valid_RBW_VBW_ratio:
            raise self.Exceptions.Invalid_VBW_RBW_ratio(ratio)
        return float(self._set_get(':SENSe:BWIDth:VIDeo:RATio', ratio))

    def video_resolution_bandwith_ratio_auto(self, mode: bool = None):
        """This command turns on/off auto video to resolution bandwidth ratio."""
        return self._string_to_bool(self._set_get(':SENSe:BWIDth:VIDeo:RATio:CONfig', mode))

    def set_filter(self, filter: str = None):
        """Sets filter type or Gets filter type (emi, gauss)"""
        if filter is not None and filter not in ('emi', 'gauss'):
            raise self.Exceptions.InvalidFilter(filter)
        return self._set_get(':SENSe:FILTer:TYPE', filter).lower()  #str

    # trace general section

    def get_data_format(self, mode: str = None):
        """Sets or gets trace data type. [ASCii, REAL]"""
        if mode is not None and mode not in ('ASCii', 'REAL'):
            raise self.Exceptions.InvalidDataMode
        return self._set_get(':FORMat:TRACe:DATA', mode) # str

    # math section
    def math_type(self, function: str = None):
        """Off: turns off the trace math function.
        X-Y+Ref->Z: math variable X minus math variable Y and add reference level then to output trace.
        Y-X+Ref->Z: math variable Y minus math variable X and add reference level then to output trace.
        X+Y-Ref->Z: math variable X add math variable Y and minus reference level then to output trace.
        X+Const->Z: math variable X add const then to output trace.
        X-Const->Z: math variable X minus const then to output trace."""
        if function is not None and function not in self._valid_math_functions:
            raise self.Exceptions.InvalidMathFunction(function)
        return self._set_get(':TRACe:MATH:TYPE', function) # str

    def math_variable_x(self, variable: str = None):
        """Sets trace math variable X.
        Gets trace math variable X."""
        if variable is not None and variable not in self._math_variables:
            raise self.Exceptions.InvalidMathVariable(variable)
        return self._set_get(':TRACe:MATH:X', variable) #str

    def math_variable_y(self, variable: str = None):
        """Sets trace math variable Y.
        Gets trace math variable Y."""
        if variable is not None and variable not in self._math_variables:
            raise self.Exceptions.InvalidMathVariable(variable)
        return self._set_get(':TRACe:MATH:Y', variable) # str

    def math_output(self, variable: str = None):
        """Sets trace math output.
        Gets trace math output."""
        if variable is not None and variable not in self._math_variables:
            raise self.Exceptions.InvalidMathVariable(variable)
        return self._set_get(':TRACe:MATH:Z', variable) #str

    def math_constant(self, const: float = None):
        """Sets trace math const. [dB]
        Gets trace math const."""
        if const is not None and self._math_const_min <= const <= self._math_const_max:
            raise self.Exceptions.MathConstantOutOfRange(const)
        return self._set_get(':TRACe:MATH:CONSt', const)  #todo : test

    def average_type(self, avg_type: str = None):
        """Toggle the average type between Log power, power and voltage."""
        if avg_type is not None and avg_type in self._valid_average_type:
            raise self.Exceptions.InvalidAverageType(avg_type)
        return self._set_get(':SENSe:AVERage:TYPE', avg_type) #str

    # sweep
    def sweep_mode(self, mode: str = None):
        """Sets sweep mode. [AUTO|FFT|SWEep]
        Gets sweep mode."""
        if mode is not None and mode not in self._valid_sweep_modes:
            raise self.Exceptions.InvalidSweepMode(mode)
        return self._set_get(':SENSe:SWEep:MODE', mode)

    def sweep_time(self, time: float = None):
        """Specifies the time in which the instrument sweeps the display. A span value of 0 Hz causes the analyzer to enter zero span mode. In zero span the X-axis represents time rather than frequency. [s]"""
        if time is not None and not self._sweep_time_min <= time <= self._sweep_time_max:
            raise self.Exceptions.SweepTimeOutOFRange(time)
        return float(self._set_get(':SENSe:SWEep:TIME', time))

    def sweep_time_auto(self, mode: bool = None):
        """This command turns on/off auto sweep time state."""
        if type(mode) == bool:
            mode = int(mode)
        return self._string_to_bool(self._set_get(':SENSe:SWEep:TIME:AUTO', mode))

    def sweep_speed(self, mode: str = None):
        """Toggles the sweep speed between normal and accuracy. [normal|accuracy]"""
        mode = mode[:4].upper() + mode[4:].lower() # normal -> NORMal | accuracy -> ACCUracy
        if mode is not None and mode not in self._valid_sweep_modes:
            raise self.Exceptions.InvalidSweepSpeed(mode)
        return self._set_get(':SENSe:SWEep:SPEed', mode).lower()

    def sweep_number(self, number: int = None):
        """Sets sweep numbers, when single sweep on.
        Gets sweep numbers, when single sweep on."""
        if number is not None and not self._sweep_number_min <= number <= self._sweep_number_max:
            raise self.Exceptions.InvalidSweepNumber(number)
        return int(float(self._set_get(':SENSe:SWEep:COUNt', number)))
    
    def sweep_continous(self, continuous:bool = True):
        """Sets continuous sweep mode on-off.
        Gets continuous sweep mode state."""
        self._set_get(':INITiate:CONTinuous',int(continuous))
    
    def initiate_sweep(self):
        """Sets single sweep."""
        self.write(':INITiate:IMMediate')