import win32com.client as win32
import pythoncom
import enum
import time
from ComHelper import ExtractComErrorInfo
from typing import List, Union

# Enum definitions from the IDL file
class vvVector(enum.IntEnum):
    """VibrationVIEW vector enumeration for data access"""
    WAVEFORMAXIS = 0
    WAVEFORM1 = 1
    WAVEFORM2 = 2
    WAVEFORM3 = 3
    WAVEFORM4 = 4
    WAVEFORM5 = 5
    WAVEFORM6 = 6
    WAVEFORM7 = 7
    WAVEFORM8 = 8
    WAVEFORM9 = 9
    WAVEFORM10 = 10
    WAVEFORM11 = 11
    WAVEFORM12 = 12
    WAVEFORM13 = 13
    WAVEFORM14 = 14
    WAVEFORM15 = 15
    WAVEFORM16 = 16
    WAVEFORM17 = 17
    WAVEFORM18 = 18
    WAVEFORM19 = 19
    WAVEFORM20 = 20
    WAVEFORM21 = 21
    WAVEFORM22 = 22
    WAVEFORM23 = 23
    WAVEFORM24 = 24
    WAVEFORM25 = 25
    WAVEFORM26 = 26
    WAVEFORM27 = 27
    WAVEFORM28 = 28
    WAVEFORM29 = 29
    WAVEFORM30 = 30
    WAVEFORM31 = 31
    WAVEFORM32 = 32
    WAVEFORM33 = 33
    WAVEFORM34 = 34
    WAVEFORM35 = 35
    WAVEFORM36 = 36
    WAVEFORM37 = 37
    WAVEFORM38 = 38
    WAVEFORM39 = 39
    WAVEFORM40 = 40
    WAVEFORM41 = 41
    WAVEFORM42 = 42
    WAVEFORM43 = 43
    WAVEFORM44 = 44
    WAVEFORM45 = 45
    WAVEFORM46 = 46
    WAVEFORM47 = 47
    WAVEFORM48 = 48
    WAVEFORM49 = 49
    WAVEFORM50 = 50
    WAVEFORM51 = 51
    WAVEFORM52 = 52
    WAVEFORM53 = 53
    WAVEFORM54 = 54
    WAVEFORM55 = 55
    WAVEFORM56 = 56
    WAVEFORM57 = 57
    WAVEFORM58 = 58
    WAVEFORM59 = 59
    WAVEFORM60 = 60
    WAVEFORM61 = 61
    WAVEFORM62 = 62
    WAVEFORM63 = 63
    WAVEFORM64 = 64
    WAVEFORMDEMAND = 90
    WAVEFORMCONTROL = 91
    WAVEFORMDEMAND2 = 92
    WAVEFORMCONTROL2 = 93
    WAVEFORMDEMAND3 = 94
    WAVEFORMCONTROL3 = 95
    WAVEFORMDEMAND4 = 96
    WAVEFORMCONTROL4 = 97
    FREQUENCYAXIS = 100
    FREQUENCY1 = 101
    FREQUENCY2 = 102
    FREQUENCY3 = 103
    FREQUENCY4 = 104
    FREQUENCY5 = 105
    FREQUENCY6 = 106
    FREQUENCY7 = 107
    FREQUENCY8 = 108
    FREQUENCY9 = 109
    FREQUENCY10 = 110
    FREQUENCY11 = 111
    FREQUENCY12 = 112
    FREQUENCY13 = 113
    FREQUENCY14 = 114
    FREQUENCY15 = 115
    FREQUENCY16 = 116
    FREQUENCY17 = 117
    FREQUENCY18 = 118
    FREQUENCY19 = 119
    FREQUENCY20 = 120
    FREQUENCY21 = 121
    FREQUENCY22 = 122
    FREQUENCY23 = 123
    FREQUENCY24 = 124
    FREQUENCY25 = 125
    FREQUENCY26 = 126
    FREQUENCY27 = 127
    FREQUENCY28 = 128
    FREQUENCY29 = 129
    FREQUENCY30 = 130
    FREQUENCY31 = 131
    FREQUENCY32 = 132
    FREQUENCY33 = 133
    FREQUENCY34 = 134
    FREQUENCY35 = 135
    FREQUENCY36 = 136
    FREQUENCY37 = 137
    FREQUENCY38 = 138
    FREQUENCY39 = 139
    FREQUENCY40 = 140
    FREQUENCY41 = 141
    FREQUENCY42 = 142
    FREQUENCY43 = 143
    FREQUENCY44 = 144
    FREQUENCY45 = 145
    FREQUENCY46 = 146
    FREQUENCY47 = 147
    FREQUENCY48 = 148
    FREQUENCY49 = 149
    FREQUENCY50 = 150
    FREQUENCY51 = 151
    FREQUENCY52 = 152
    FREQUENCY53 = 153
    FREQUENCY54 = 154
    FREQUENCY55 = 155
    FREQUENCY56 = 156
    FREQUENCY57 = 157
    FREQUENCY58 = 158
    FREQUENCY59 = 159
    FREQUENCY60 = 160
    FREQUENCY61 = 161
    FREQUENCY62 = 162
    FREQUENCY63 = 163
    FREQUENCY64 = 164
    FREQUENCYDRIVE = 180
    FREQUENCYRESPONSE = 181
    FREQUENCYDRIVE2 = 182
    FREQUENCYRESPONSE2 = 183
    FREQUENCYDRIVE3 = 184
    FREQUENCYRESPONSE3 = 185
    FREQUENCYDRIVE4 = 186
    FREQUENCYRESPONSE4 = 187
    FREQUENCYDEMAND = 190
    FREQUENCYCONTROL = 191
    FREQUENCYDEMAND2 = 192
    FREQUENCYCONTROL2 = 193
    FREQUENCYDEMAND3 = 194
    FREQUENCYCONTROL3 = 195
    FREQUENCYDEMAND4 = 196
    FREQUENCYCONTROL4 = 197
    TIMEHISTORYAXIS = 200
    TIMEHISTORY1 = 201
    TIMEHISTORY2 = 202
    TIMEHISTORY3 = 203
    TIMEHISTORY4 = 204
    TIMEHISTORY5 = 205
    TIMEHISTORY6 = 206
    TIMEHISTORY7 = 207
    TIMEHISTORY8 = 208
    TIMEHISTORY9 = 209
    TIMEHISTORY10 = 210
    TIMEHISTORY11 = 211
    TIMEHISTORY12 = 212
    TIMEHISTORY13 = 213
    TIMEHISTORY14 = 214
    TIMEHISTORY15 = 215
    TIMEHISTORY16 = 216
    TIMEHISTORY17 = 217
    TIMEHISTORY18 = 218
    TIMEHISTORY19 = 219
    TIMEHISTORY20 = 220
    TIMEHISTORY21 = 221
    TIMEHISTORY22 = 222
    TIMEHISTORY23 = 223
    TIMEHISTORY24 = 224
    TIMEHISTORY25 = 225
    TIMEHISTORY26 = 226
    TIMEHISTORY27 = 227
    TIMEHISTORY28 = 228
    TIMEHISTORY29 = 229
    TIMEHISTORY30 = 230
    TIMEHISTORY31 = 231
    TIMEHISTORY32 = 232
    TIMEHISTORY33 = 233
    TIMEHISTORY34 = 234
    TIMEHISTORY35 = 235
    TIMEHISTORY36 = 236
    TIMEHISTORY37 = 237
    TIMEHISTORY38 = 238
    TIMEHISTORY39 = 239
    TIMEHISTORY40 = 240
    TIMEHISTORY41 = 241
    TIMEHISTORY42 = 242
    TIMEHISTORY43 = 243
    TIMEHISTORY44 = 244
    TIMEHISTORY45 = 245
    TIMEHISTORY46 = 246
    TIMEHISTORY47 = 247
    TIMEHISTORY48 = 248
    TIMEHISTORY49 = 249
    TIMEHISTORY50 = 250
    TIMEHISTORY51 = 251
    TIMEHISTORY52 = 252
    TIMEHISTORY53 = 253
    TIMEHISTORY54 = 254
    TIMEHISTORY55 = 255
    TIMEHISTORY56 = 256
    TIMEHISTORY57 = 257
    TIMEHISTORY58 = 258
    TIMEHISTORY59 = 259
    TIMEHISTORY60 = 260
    TIMEHISTORY61 = 261
    TIMEHISTORY62 = 262
    TIMEHISTORY63 = 263
    TIMEHISTORY64 = 264
    REARINPUTHISTORY1 = 301
    REARINPUTHISTORY2 = 302
    REARINPUTHISTORY3 = 303
    REARINPUTHISTORY4 = 304
    REARINPUTHISTORY5 = 305
    REARINPUTHISTORY6 = 306
    REARINPUTHISTORY7 = 307
    REARINPUTHISTORY8 = 308
    REARINPUTHISTORY9 = 309
    REARINPUTHISTORY10 = 310
    REARINPUTHISTORY11 = 311
    REARINPUTHISTORY12 = 312
    REARINPUTHISTORY13 = 313
    REARINPUTHISTORY14 = 314
    REARINPUTHISTORY15 = 315
    REARINPUTHISTORY16 = 316
    REARINPUTHISTORY17 = 317
    REARINPUTHISTORY18 = 318
    REARINPUTHISTORY19 = 319
    REARINPUTHISTORY20 = 320
    REARINPUTHISTORY21 = 321
    REARINPUTHISTORY22 = 322
    REARINPUTHISTORY23 = 323
    REARINPUTHISTORY24 = 324
    REARINPUTHISTORY25 = 325
    REARINPUTHISTORY26 = 326
    REARINPUTHISTORY27 = 327
    REARINPUTHISTORY28 = 328
    REARINPUTHISTORY29 = 329
    REARINPUTHISTORY30 = 330
    REARINPUTHISTORY31 = 331
    REARINPUTHISTORY32 = 332

class vvTestType(enum.IntEnum):
    """VibrationVIEW test type enumeration"""
    TEST_SYSCHECK = 0
    TEST_SINE = 1
    TEST_RANDOM = 2
    TEST_SHOCK = 4
    TEST_TRANSIENT = 5
    TEST_REPLAY = 6
    @classmethod
    def get_name(cls, value):
        try:
            return cls(value).name.replace("TEST_", "").capitalize()
        except ValueError:
            return "Unknown"


class VibrationVIEW:
    def __init__(self):
        """Initialize COM resources and COM objects"""
        pythoncom.CoInitialize()
        try:
            # Use the ProgID that works in your environment
            vv = win32.gencache.EnsureDispatch('VibrationVIEW.TestControl')
            print('VibrationVIEW object created')

            
            retryAttempts = 5
            waitTime = 0.5  # Start with 0.5 seconds
            
            for attempt in range(1, retryAttempts + 1):
                try:
                    if vv and vv.IsReady:
                        print('VibrationVIEW key is now valid')
                        self.vv = vv
                        return
                except Exception as e:
                    print(f'Attempt {attempt} to connect to VibrationVIEW failed: {e}')
                    if attempt == retryAttempts:
                        print('Failed to connect after multiple attempts.')
                        break
                
                print(f'Waiting {waitTime} seconds before next attempt...')
                time.sleep(waitTime)
                waitTime *= 2  # Double the wait time for the next attempt            self.vv = vv
        except Exception as e:
            print(f'Failed to connect to VibrationVIEW: {ExtractComErrorInfo(e)}')
            vv = None

    def __del__(self):
        """
        Clean up COM resources when the object is destroyed
        """
        try:
            # Release COM object references
            if hasattr(self, 'vv') and self.vv is not None:
                self.vv = None
            # Uninitialize COM
            pythoncom.CoUninitialize()
        except:
            pass

    def close(self):
        """Explicitly release COM resources"""
        if hasattr(self, 'vv') and self.vv is not None:
            self.vv = None
        pythoncom.CoUninitialize()
        # -- Basic control methods (IVibrationVIEW Interface) --
    def RunTest(self, testName):
        """Run VibrationVIEW Test with the given name"""
        return self.vv.RunTest(testName)

    def OpenTest(self, testName):
        """Open VibrationVIEW Test with the given name"""
        return self.vv.OpenTest(testName)

    def EditTest(self, testName):
        """Edit VibrationVIEW Test with the given name"""
        return self.vv.EditTest(testName)

    def StartTest(self):
        """Start Currently Loaded VibrationVIEW Test"""
        return self.vv.StartTest()

    def StopTest(self):
        """Stop Test"""
        return self.vv.StopTest()

    def AbortEdit(self):
        """Abort any open Edit session"""
        return self.vv.AbortEdit()

    def SaveData(self, filename):
        """Save data to the specified filename"""
        return self.vv.SaveData(filename)

    def Minimize(self):
        """Minimize VibrationVIEW"""
        return self.vv.Minimize()

    def Restore(self):
        """Restore VibrationVIEW"""
        return self.vv.Restore()

    def Maximize(self):
        """Maximize VibrationVIEW"""
        return self.vv.Maximize()

    def Activate(self):
        """Activate VibrationVIEW"""
        return self.vv.Activate()

    def MenuCommand(self, id):
        """Send menu command to VibrationVIEW"""
        return self.vv.MenuCommand(id)

    # -- Status and properties --
    def Status(self):
        """Get VibrationVIEW Status"""
        stop_code, stop_code_index = self.vv.Status()
        return {'stop_code': stop_code, 'stop_code_index': stop_code_index}

    def IsRunning(self):
        """Check if test is running"""
        return bool(self.vv.Running)

    def IsStarting(self):
        """Check if test is starting but not at level"""
        return  bool(self.vv.Starting)

    def IsChangingLevel(self):
        """Check if test schedule is changing levels"""
        return  bool(self.vv.ChangingLevel)

    def IsHoldLevel(self):
        """Check if schedule timer is in hold"""
        return  bool(self.vv.HoldLevel)

    def IsOpenLoop(self):
        """Check if test is open loop"""
        return  bool(self.vv.OpenLoop)

    def IsAborted(self):
        """Check if test has aborted"""
        return  bool(self.vv.Aborted)

    def CanResumeTest(self):
        """Check if test may be resumed"""
        return  bool(self.vv.CanResumeTest)

    def IsReady(self):
        """Check if Ethernet Box is running"""
        return  bool(self.vv.IsReady)

    def ResumeTest(self):
        """Resume Active Test"""
        return self.vv.ResumeTest()

    # -- Data retrieval methods --
    def Demand(self):
        """Get the demand values for each loop"""
        num_outputs = self.GetHardwareOutputChannels()
        arr = [0.0] * num_outputs
        arr =self.vv.Demand(arr)
        return arr

    def Control(self):
        """Get the control values for each loop"""
        num_outputs = self.GetHardwareOutputChannels()
        arr = [0.0] * num_outputs
        self.vv.Control(arr)
        return arr

    def Channel(self):
        """Get the channel values"""
        try:
            # pre-allocate the return vector by the number of channels in the system
            # vv uses the SIZE of the array to determine the SIZE of the return vector
            num_channels = self.GetHardwareInputChannels()
            arr = [0.0] * num_channels
            arr = self.vv.Channel(arr)
            return arr
        except Exception as e:
            return []

    def Output(self):
        """Get the output values for each loop"""
        num_outputs = self.GetHardwareOutputChannels()
        arr = [0.0] * num_outputs
        self.vv.Output(arr)
        return arr


    def Vector(self, vectorEnum: Union[int, vvVector], columns: int = 1) -> List[List[float]]:
        """
        Get raw data vector

        Args:
            vectorEnum: Either a vvVector enum value or integer corresponding to the vector
                    (e.g., vvVector.FREQUENCY1 or 101)
            columns: The number of columns in the data array. Default is 1.
            rows: The number of rows in the data array. Default is 1.

        Returns:
            List of lists representing the raw data for the requested vector.
        """
        # Initialize a 2D array of zeros
        rows = self.vv.VectorLength(vectorEnum);
        dataArray = [[0.0 for _ in range(columns)] for _ in range(rows)]

        try:
            # Call the Vector method on the instance to retrieve data
            arr = self.vv.Vector(dataArray, int(vectorEnum))
            return arr
        except Exception as e:
            # Handle any potential errors from the Vector method
            self.log(f"Error retrieving data for vector {vectorEnum}: {str(e)}", False)
        return dataArray  # Return empty data if error occurs
    
    def RearInput(self):
        """Get the input readings from the rear inputs"""
        num_inputs = 8
        arr = [0.0] * num_inputs
        self.vv.RearInput(arr)
        return arr

    # -- Properties for raw data vectors --
    def VectorUnit(self, vectorEnum):
        """
        Get units for raw data vector
        
        Args:
            vectorEnum: Either a vvVector enum value or integer corresponding to the vector
                        (e.g., vvVector.FREQUENCY1 or 101)
        
        Returns:
            String containing the units for the specified vector
        """
        return self.vv.VectorUnit(int(vectorEnum))

    def VectorLabel(self, vectorEnum):
        """
        Get label for raw data vector
        
        Args:
            vectorEnum: Either a vvVector enum value or integer corresponding to the vector
                        (e.g., vvVector.FREQUENCY1 or 101)
        
        Returns:
            String containing the label for the specified vector
        """
        return self.vv.VectorLabel(int(vectorEnum))

    def VectorLength(self, vectorEnum):
        """
        Get required array length for Raw Data Vector Array
        
        Args:
            vectorEnum: Either a vvVector enum value or integer corresponding to the vector
                        (e.g., vvVector.FREQUENCY1 or 101)
        
        Returns:
            Integer containing the length required for the vector array
        """
        return self.vv.VectorLength(int(vectorEnum))

    def ControlUnit(self, loopNum):
        """Get the channel unit associated with loop number"""
        return self.vv.ControlUnit(loopNum)

    def ControlLabel(self, loopNum):
        """Get the control unit label associated with loop number"""
        return self.vv.ControlLabel(loopNum)

    def ChannelUnit(self, channelNum):
        """Get the channel unit associated with channel number"""
        return self.vv.ChannelUnit(channelNum)

    def ChannelLabel(self, channelNum):
        """Get the channel unit label associated with channel number"""
        return self.vv.ChannelLabel(channelNum)

    def ReportField(self, fieldName):
        """Get report value specified by field name"""
        return self.vv.ReportField(fieldName)

    def RearInputUnit(self, channel):
        """Get units for the rear input channel"""
        return self.vv.RearInputUnit(channel)

    def RearInputLabel(self, channel):
        """Get label for the rear input channel"""
        return self.vv.RearInputLabel(channel)

    def Teds(self, channel=None):
        """Get TEDs value for requested channel(s)"""
        allTedsData = []
        try:
            numChannels = self.GetHardwareInputChannels()
            allocatedStringArray = [[''] * 2 for _ in range(32)]

            # If a specific channel is provided, only get TEDS for that channel
            channelsToCheck = [channel] if channel is not None else range(numChannels)
            
            for channel in channelsToCheck:
                try:
                    tedsInfo = self.vv.Teds(channel, allocatedStringArray)
                    
                    # Remove trailing empty entries by filtering out those where both key and value are empty
                    teds_info_clean = [item for item in tedsInfo if item[0] and item[1]]
                    
                    tedsData = {
                        "Channel": channel+1,
                        "Teds": teds_info_clean
                    }
                    allTedsData.append(tedsData)

                except Exception as e:
                    comErr = ExtractComErrorInfo(e)
                    tedsError = {
                        "Channel": channel+1,
                        "Error": comErr,
                    }
                    allTedsData.append(tedsError)

            return allTedsData
        except Exception as e:
            return []

    # -- Test control methods --
    def SweepUp(self):
        """Sine Sweep up Sine test"""
        return self.vv.SweepUp()

    def SweepDown(self):
        """Sine Sweep down Sine test"""
        return self.vv.SweepDown()

    def SweepStepUp(self):
        """Sine Sweep Up to next integer frequency"""
        return self.vv.SweepStepUp()

    def SweepStepDown(self):
        """Sine Sweep Down to next integer frequency"""
        return self.vv.SweepStepDown()

    def SweepHold(self):
        """Sine Hold Sweep frequency"""
        return self.vv.SweepHold()

    def SweepResonanceHold(self):
        """Sine Hold Resonance"""
        return self.vv.SweepResonanceHold()

    # -- Properties for multipliers and settings --
    def DemandMultiplier(self, value=None):
        """Get/Set multiplier for Demand output (dB)"""
        if value is None:
            return self.vv.DemandMultipler
        else:
            self.vv.DemandMultipler = value
            return value

    def SweepMultiplier(self, value=None):
        """Get/Set multiplier for Sine Sweep (linear)"""
        if value is None:
            return self.vv.SweepMultiplier
        else:
            self.vv.SweepMultiplier = value
            return value

    def TestType(self, value=None):
        """
        Get/Set Test Type
        
        Args:
            value (optional): Either a vvTestType enum value or integer corresponding to the test type
                             (e.g., vvTestType.TEST_SINE or 1)
                             
                             Possible values:
                             - TEST_SYSCHECK (0): System Check
                             - TEST_SINE (1): Sine
                             - TEST_RANDOM (2): Random
                             - TEST_SHOCK (4): Shock
                             - TEST_TRANSIENT (5): Transient Capture
                             - TEST_REPLAY (6): FDR/Replay
        
        Returns:
            Current test type if value is None, otherwise the new test type value
        """
        if value is None:
            return self.vv.TestType
        else:
            self.vv.TestType = int(value)
            return value

    def SystemCheckFrequency(self, value=None):
        """Get/Set System Check Frequency"""
        if value is None:
            return self.vv.SystemCheckFrequency
        else:
            self.vv.SystemCheckFrequency = value
            return value

    def SystemCheckOutputVoltage(self, value=None):
        """Get/Set System Check output level"""
        if value is None:
            return self.vv.SystemCheckOutputVoltage
        else:
            self.vv.SystemCheckOutputVoltage = value
            return value

    def SineFrequency(self, value=None):
        """Get/Set Sine Frequency"""
        if value is None:
            return self.vv.SineFrequency
        else:
            self.vv.SineFrequency = value
            return value

    # -- Hardware and Input configuration methods (IVibrationVIEWV6 Interface) --
    def GetHardwareInputChannels(self):
        """Get number of hardware input channels"""
        return self.vv.HardwareInputChannels

    def GetHardwareOutputChannels(self):
        """Get number of hardware output channels"""
        return self.vv.HardwareOutputChannels

    def GetHardwareSerialNumber(self):
        """Get hardware serial number"""
        return self.vv.HardwareSerialNumber

    def GetSoftwareVersion(self):
        """Get software version"""
        return self.vv.SoftwareVersion

    def InputCalDate(self, channel):
        """Get input calibration date for a channel"""
        return self.vv.InputCalDate(channel)

    def InputSerialNumber(self, channel):
        """Get input serial number for a channel"""
        return self.vv.InputSerialNumber(channel)

    def InputCapacitorCoupled(self, channel, value=None):
        """Get/Set input capacitor coupled setting for a channel"""
        if value is None:
            return self.vv.InputCapacitorCoupled(channel)
        else:
            self.vv.InputCapacitorCoupled(channel, value)
            return value

    def InputAccelPowerSource(self, channel, value=None):
        """Get/Set input accelerometer power source setting for a channel"""
        if value is None:
            return self.vv.InputAccelPowerSource(channel)
        else:
            self.vv.InputAccelPowerSource(channel, value)
            return value

    def InputDifferential(self, channel, value=None):
        """Get/Set input differential setting for a channel"""
        if value is None:
            return self.vv.InputDifferential(channel)
        else:
            self.vv.InputDifferential(channel, value)
            return value

    def InputSensitivity(self, channel):
        """Get input sensitivity for a channel"""
        return self.vv.InputSensitivity(channel)

    def InputEngineeringScale(self, channel):
        """Get input engineering scale for a channel"""
        return self.vv.InputEngineeringScale(channel)

    def InputMode(self, channel, powerSource, capCoupled, differential):
        """Set input mode for a channel"""
        return self.vv.InputMode(channel, powerSource, capCoupled, differential)

    def InputCalibration(self, channel, sensitivity, serialNumber, calDate):
        """Set input calibration for a channel"""
        return self.vv.InputCalibration(channel, sensitivity, serialNumber, calDate)

    def HardwareSupportsCapacitorCoupled(self, channel):
        """Check if hardware supports capacitor coupled for a channel"""
        return self.vv.HardwareSupportsCapacitorCoupled(channel)

    def HardwareSupportsAccelPowerSource(self, channel):
        """Check if hardware supports accelerometer power source for a channel"""
        return self.vv.HardwareSupportsAccelPowerSource(channel)

    def HardwareSupportsDifferential(self, channel):
        """Check if hardware supports differential for a channel"""
        return self.vv.HardwareSupportsDifferential(channel)

    # -- V8/V11 Methods --
    def GetActiveTest(self):
        """Get the active test object"""
        return self.vv.ActiveTest

    def RecordStart(self):
        """Start recording data"""
        return self.vv.RecordStart()
    
    def RecordStop(self):
        """Stop recording data"""
        return self.vv.RecordStop()
    
    def RecordPause(self):
        """Pause recording data"""
        return self.vv.RecordPause()
    
    def RecordGetFilename(self):
        """Get the last recording's filename"""
        return self.vv.RecordGetFilename
    
    def SetInputConfigurationFile(self, configName):
        """Load input configuration file"""
        return self.vv.set_InputConfigurationFile(configName)


# Example usage
if __name__ == "__main__":
    # Connect to VibrationVIEW
    vv = VibrationVIEW()
    
    # Check if connection was successful
    if vv.vv is None:
        print("Failed to connect to VibrationVIEW")
        exit(1)

#        win32com.client.makepy.main()
#        print(os.path.join(os.path.dirname(win32com.__file__), "gen_py"))
    
    print("Connected to VibrationVIEW")
    
    # Get software version
    version = vv.GetSoftwareVersion()
    print(f"VibrationVIEW version: {version}")
    
    # Get number of hardware channels
    input_channels = vv.GetHardwareInputChannels()
    output_channels = vv.GetHardwareOutputChannels()
    print(f"Hardware: {input_channels} input channels, {output_channels} output channels")
    
    # Open a test
    test_name = "C:\\VibrationVIEW\\Profiles\\sinesweep.vsp"
    print(f"Opening test: {test_name}")
    vv.OpenTest(test_name)
    
    # Get test type
    test_type = vv.TestType()
    print(f"Test type: {vvTestType(test_type).name}")
    
    # Get frequency vector data
    freq_data = vv.Vector(vvVector.FREQUENCYAXIS)
    print(f"Frequency axis has {len(freq_data)} points")
    
    # Get frequency data label and units
    freq_label = vv.VectorLabel(vvVector.FREQUENCYAXIS)
    freq_unit = vv.VectorUnit(vvVector.FREQUENCYAXIS)
    print(f"Frequency axis: {freq_label} [{freq_unit}]")
    
    # Get channel data
    channel_data = vv.Channel()
    print(f"Channel data: {channel_data}")
    
    