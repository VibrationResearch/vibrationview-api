import pywintypes

def ExtractComErrorInfo(e):
    """
    Extracts HRESULT, message, excinfo, and argerror from a COM error (pywintypes.com_error).
    Safely handles non-COM exceptions and provides useful diagnostics.

    Returns the detailed COM error message if available,
    otherwise falls back to the string representation of the exception.
    """
    if isinstance(e, pywintypes.com_error):
        args = e.args
        if len(args) >= 3:
            excinfo = args[2]
            if isinstance(excinfo, tuple) and len(excinfo) > 1:
                return excinfo[2]  # This is typically the detailed message
    return str(e)