"""Mock COM objects for CI testing without VibrationVIEW installed."""

from unittest.mock import MagicMock


def create_mock_com_object():
    """Create a mock COM object that simulates VibrationVIEW.TestControl."""
    mock = MagicMock()

    # Properties - status
    mock.IsReady = True
    mock.Running = False
    mock.Starting = False
    mock.ChangingLevel = False
    mock.HoldLevel = False
    mock.OpenLoop = False
    mock.Aborted = False
    mock.CanResumeTest = False

    # Properties - hardware
    mock.HardwareInputChannels = 4
    mock.HardwareOutputChannels = 1
    mock.HardwareSerialNumber = "MOCK-SN-001"
    mock.SoftwareVersion = "Mock 1.0.0"

    # Properties - test settings
    mock.TestType = 0
    mock.DemandMultipler = 0.0  # matches typo in source
    mock.SweepMultiplier = 1.0
    mock.SystemCheckFrequency = 100.0
    mock.SystemCheckOutputVoltage = 0.1
    mock.SineFrequency = 100.0
    mock.RecordGetFilename = ""

    # Methods returning True
    for method_name in [
        "RunTest", "OpenTest", "EditTest", "StartTest", "StopTest",
        "AbortEdit", "SaveData", "Minimize", "Restore", "Maximize",
        "Activate", "MenuCommand", "ResumeTest", "RecordStart",
        "RecordStop", "RecordPause", "set_InputConfigurationFile",
        "CloseTest", "CloseTab", "ImportVirtualChannels",
        "RemoveAllVirtualChannels", "InputMode", "InputCalibration",
        "UpdateChannelConfigFromDatabase", "SweepUp", "SweepDown",
        "SweepStepUp", "SweepStepDown", "SweepHold", "SweepResonanceHold",
        "PostFormFields",
    ]:
        getattr(mock, method_name).return_value = True

    # Status
    mock.Status.return_value = ("Normal Stop", 0)

    # Data array methods - return the input array
    mock.Demand.side_effect = lambda arr: arr
    mock.Control.side_effect = lambda arr: arr
    mock.Channel.side_effect = lambda arr: arr
    mock.Output.side_effect = lambda arr: arr
    mock.RearInput.side_effect = lambda arr: arr
    mock.VectorLength.return_value = 100
    mock.Vector.side_effect = lambda arr, enum: arr

    # String return methods
    mock.VectorUnit.return_value = "g"
    mock.VectorLabel.return_value = "Acceleration"
    mock.ChannelUnit.return_value = "g"
    mock.ChannelLabel.return_value = "Channel 1"
    mock.ControlUnit.return_value = "g"
    mock.ControlLabel.return_value = "Control"
    mock.RearInputUnit.return_value = "V"
    mock.RearInputLabel.return_value = "Rear Input"
    mock.InputSerialNumber.return_value = "SN-001"
    mock.InputCalDate.return_value = "2025-01-01"

    # Numeric return methods
    mock.InputSensitivity.return_value = 10.0
    mock.InputEngineeringScale.return_value = 1.0
    mock.InputCapacitorCoupled.return_value = False
    mock.InputAccelPowerSource.return_value = False
    mock.InputDifferential.return_value = False
    mock.HardwareSupportsCapacitorCoupled.return_value = True
    mock.HardwareSupportsAccelPowerSource.return_value = True
    mock.HardwareSupportsDifferential.return_value = True
    mock.IsChannelDifferentThanDatabase.return_value = False

    # Report methods
    mock.ReportField.return_value = "MockValue"
    mock.ReportVector.return_value = [[0.0, 0.0]]
    mock.ReportVectorHeader.return_value = [["Freq", "Accel"]]
    mock.ReportVectorHistory.return_value = ([[0.0, 0.0]], [["Freq", "Accel"]])
    mock.ReportFields.side_effect = lambda fields, arr: [
        [f, "MockValue"] for f in fields.split(",")
    ]
    mock.ReportFieldsHistory.side_effect = lambda fields, arr: [
        [f, "MockValue"] for f in fields.split(",")
    ]

    # Form methods
    mock.FormFields.return_value = [["Field1", "Value1"]]

    # TEDS methods
    mock.TedsRead.return_value = ["URN1"]
    mock.TedsVerifyAndApply.side_effect = lambda arr: arr
    mock.TedsVerifyStringAndApply.return_value = ["URN1"]
    mock.TedsReadAndApply.return_value = ["URN1"]
    mock.TedsFromURN.return_value = ["TEDS Data"]
    mock.Teds.return_value = [["Manufacturer", "Mock", ""], ["Model", "Test", ""]]

    # Database methods
    mock.ChannelDatabaseIDs.return_value = ["GUID-001"]
    mock.TransducerDatabaseRecord.return_value = ["Record1"]

    # List methods
    mock.ListOpenTests.return_value = []

    # _oleobj_ for indexed property access (InputCapacitorCoupled set, etc.)
    mock._oleobj_ = MagicMock()
    mock._oleobj_.Invoke.return_value = None

    return mock
