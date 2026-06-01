import pytest
import win32com.client
import pythoncom
import winreg

# Skip entire module if VibrationVIEW COM components are not registered
_VV_REGISTERED = False
try:
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "VibrationVIEW.TestControl"):
        _VV_REGISTERED = True
except (FileNotFoundError, OSError):
    pass

if not _VV_REGISTERED:
    pytest.skip("VibrationVIEW COM components not registered", allow_module_level=True)


class TestCOMRegistration:
    """Test COM registration for VibrationVIEW components"""

    @pytest.fixture(scope="session", autouse=True)
    def com_initialize(self):
        """Initialize COM for the test session"""
        pythoncom.CoInitialize()
        yield
        pythoncom.CoUninitialize()

    def check_registry_key(self, hkey, subkey):
        """Check if a registry key exists and return its default value"""
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "")
                    return True, value
                except (FileNotFoundError, OSError):
                    return True, "(No default value)"
        except (FileNotFoundError, OSError):
            return False, None

    def check_registry_value(self, hkey, subkey, value_name):
        """Check if a specific registry value exists"""
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                return True, value
        except (FileNotFoundError, OSError):
            return False, None

    @pytest.mark.parametrize("component,clsid", [
        ("VibrationVIEW.TestControl", "{10C5DA8D-4909-4BFF-AD10-2799114907EA}"),
        ("VibrationVIEW.ActiveTest", "{CE4FBD16-5FD1-4A3D-B78C-494D148450C1}"),
        ("VibrationVIEW.ActiveScheduleLevel", "{CE4FBD16-5FD1-4A3D-B78C-494D148450C2}"),
    ])
    def test_progid_registration(self, component, clsid):
        """Test that ProgIDs are properly registered"""
        exists, value = self.check_registry_key(winreg.HKEY_CLASSES_ROOT, component)
        assert exists, f"ProgID {component} not found in registry"
        
        # Check that ProgID points to correct CLSID
        clsid_exists, clsid_value = self.check_registry_value(
            winreg.HKEY_CLASSES_ROOT, f"{component}\\CLSID", ""
        )
        if clsid_exists:
            assert clsid_value == clsid, f"ProgID {component} points to wrong CLSID: {clsid_value} != {clsid}"

    @pytest.mark.parametrize("component,clsid", [
        ("VibrationVIEW.TestControl", "{10C5DA8D-4909-4BFF-AD10-2799114907EA}"),
        ("VibrationVIEW.ActiveTest", "{CE4FBD16-5FD1-4A3D-B78C-494D148450C1}"),
        ("VibrationVIEW.ActiveScheduleLevel", "{CE4FBD16-5FD1-4A3D-B78C-494D148450C2}"),
    ])
    def test_versioned_progid_registration(self, component, clsid):
        """Test that versioned ProgIDs are properly registered"""
        versioned_progid = f"{component}.1"
        exists, value = self.check_registry_key(winreg.HKEY_CLASSES_ROOT, versioned_progid)
        assert exists, f"Versioned ProgID {versioned_progid} not found in registry"

    @pytest.mark.parametrize("clsid,expected_name", [
        ("{10C5DA8D-4909-4BFF-AD10-2799114907EA}", "VibrationVIEW"),
        ("{CE4FBD16-5FD1-4A3D-B78C-494D148450C1}", "ActiveTest"),
        ("{CE4FBD16-5FD1-4A3D-B78C-494D148450C2}", "ActiveScheduleLevel"),
    ])
    def test_clsid_registration(self, clsid, expected_name):
        """Test that CLSIDs are properly registered"""
        clsid_path = f"CLSID\\{clsid}"
        exists, description = self.check_registry_key(winreg.HKEY_CLASSES_ROOT, clsid_path)
        assert exists, f"CLSID {clsid} not found in registry"
        
        # Check InprocServer32 or LocalServer32
        inproc_exists, inproc_path = self.check_registry_value(
            winreg.HKEY_CLASSES_ROOT, f"{clsid_path}\\InprocServer32", ""
        )
        local_exists, local_path = self.check_registry_value(
            winreg.HKEY_CLASSES_ROOT, f"{clsid_path}\\LocalServer32", ""
        )
        
        assert inproc_exists or local_exists, f"Neither InprocServer32 nor LocalServer32 found for CLSID {clsid}"
        
        # Check the server path that exists
        server_path = inproc_path if inproc_exists else local_path
        # Remove quotes from server path if present
        clean_server_path = server_path.strip('"')
        assert clean_server_path.endswith('.dll') or clean_server_path.endswith('.exe'), f"Invalid server path: {server_path}"

    def test_typelib_registration(self):
        """Test that the TypeLib is properly registered"""
        typelib_guid = "{689DBEFA-B0A7-4413-963E-ECB35986DEA4}"
        typelib_path = f"TypeLib\\{typelib_guid}"
        
        exists, _ = self.check_registry_key(winreg.HKEY_CLASSES_ROOT, typelib_path)
        assert exists, f"TypeLib {typelib_guid} not found in registry"

    @pytest.mark.parametrize("progid", [
        "VibrationVIEW.TestControl",
        "VibrationVIEW.ActiveTest",
        "VibrationVIEW.ActiveScheduleLevel"
    ])
    def test_com_object_creation_attempt(self, progid):
        """Test that COM objects can be instantiated (or fail gracefully)"""
        try:
            obj = win32com.client.Dispatch(progid)
            # If successful, clean up
            del obj
        except pythoncom.com_error as e:
            # Check if it's a "library not registered" error
            error_msg = str(e).lower()
            assert "not registered" not in error_msg, f"{progid} reports as not registered: {e}"
            # Other errors (like "no interface" or "class not available") might be expected

    def test_threading_model_registration(self):
        """Test that threading models are properly set"""
        components = [
            "{10C5DA8D-4909-4BFF-AD10-2799114907EA}",  # Application
            "{CE4FBD16-5FD1-4A3D-B78C-494D148450C1}",  # ActiveTest
            "{CE4FBD16-5FD1-4A3D-B78C-494D148450C2}",  # ActiveScheduleLevel
        ]
        
        for clsid in components:
            threading_exists, threading_model = self.check_registry_value(
                winreg.HKEY_CLASSES_ROOT, 
                f"CLSID\\{clsid}\\InprocServer32", 
                "ThreadingModel"
            )
            if threading_exists:
                valid_models = ["Apartment", "Free", "Both", "Neutral"]
                assert threading_model in valid_models, f"Invalid threading model for {clsid}: {threading_model}"

    def test_programmable_flag(self):
        """Test that Programmable flag is set for automation objects"""
        automation_clsids = [
            "{10C5DA8D-4909-4BFF-AD10-2799114907EA}",  # Application
            "{CE4FBD16-5FD1-4A3D-B78C-494D148450C1}",  # ActiveTest
            "{CE4FBD16-5FD1-4A3D-B78C-494D148450C2}",  # ActiveScheduleLevel
        ]
        
        for clsid in automation_clsids:
            programmable_exists, _ = self.check_registry_key(
                winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}\\Programmable"
            )
            assert programmable_exists, f"Programmable flag not set for {clsid}"

    def test_bidirectional_registration(self):
        """Test that ProgID->CLSID->ProgID mappings are consistent"""
        mappings = [
            ("VibrationVIEW.TestControl", "{10C5DA8D-4909-4BFF-AD10-2799114907EA}"),
            ("VibrationVIEW.ActiveTest", "{CE4FBD16-5FD1-4A3D-B78C-494D148450C1}"),
            ("VibrationVIEW.ActiveScheduleLevel", "{CE4FBD16-5FD1-4A3D-B78C-494D148450C2}"),
        ]
        
        for progid, clsid in mappings:
            # Check ProgID -> CLSID
            clsid_from_progid_exists, clsid_from_progid = self.check_registry_value(
                winreg.HKEY_CLASSES_ROOT, f"{progid}\\CLSID", ""
            )
            assert clsid_from_progid_exists, f"No CLSID found under ProgID {progid}"
            assert clsid_from_progid == clsid, f"CLSID mismatch for {progid}: {clsid_from_progid} != {clsid}"
            
            # Check CLSID -> ProgID
            progid_from_clsid_exists, progid_from_clsid = self.check_registry_value(
                winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}\\ProgID", ""
            )
            if progid_from_clsid_exists:
                expected_versioned = f"{progid}.1"
                assert progid_from_clsid == expected_versioned, f"ProgID mismatch for {clsid}: {progid_from_clsid} != {expected_versioned}"


# Mark all tests as COM-related
pytestmark = [pytest.mark.com, pytest.mark.registration]