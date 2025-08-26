import pywintypes

def ExtractComErrorInfo(e):
    """
    Extracts error message from a COM error (pywintypes.com_error).
    Safely handles non-COM exceptions and provides useful diagnostics.

    Returns the error message string for COM errors,
    raises the original exception if it's not a COM error.
    """
    def convert_wstring(value):
        """Convert wide string to regular string if needed."""
        if value is None:
            return None
        if hasattr(value, '__str__'):
            return str(value)
        return value
    
    if isinstance(e, pywintypes.com_error):
        args = e.args
        
        if len(args) >= 3:
            excinfo = args[2]
            if isinstance(excinfo, tuple) and len(excinfo) > 2:
                # Convert the message from wstring
                raw_message = excinfo[2]
                message = convert_wstring(raw_message)
                return message
        
        # Fallback if excinfo structure is different
        return str(e)
    
    # Re-raise non-COM errors
    raise e