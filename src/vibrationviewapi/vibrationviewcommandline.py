import win32com.client as win32
import subprocess
import os
from . import config

def _generate_file_from_vv(filePath: str, outputName: str, operation: str, template_name: str = None) -> str:
    """
    Common function to generate files from VibrationVIEW via command line.

    Args:
        filePath (str): The VV filename
        outputName (str): Desired name of the generated file
        operation (str): Operation type ('/savereport', '/txt', '/uff')
        template_name (str, optional): Name of the report template for report generation

    Returns:
        str: Path to the generated file

    Raises:
        RuntimeError: If the command execution fails
    """
    # Determine if outputName already contains a path
    if os.path.dirname(outputName):
        # If outputName already has a path, use it directly
        outPath = outputName
        # Ensure the directory exists
        os.makedirs(os.path.dirname(outPath), exist_ok=True)
    else:
        # If outputName has no path, use the temporary folder
        reportFolder = os.path.join(config.REPORT_FOLDER, 'Temporary')
        os.makedirs(reportFolder, exist_ok=True)
        outPath = os.path.join(reportFolder, outputName)

    # Build command
    command = [config.EXE_NAME, operation, filePath, '/output', outPath]
    
    # Add template parameter if needed
    if template_name:
        command.insert(3, '/template')
        command.insert(4, template_name)

    # Run command
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        operation_name = operation.lstrip('/')
        raise RuntimeError(
            f'{operation_name.upper()} generation failed.\n'
            f'Command: {" ".join(command)}\n'
            f'Stderr: {result.stderr.strip()}'
        )

    return outPath

def GenerateReportFromVV(filePath: str, templateName: str, outputName: str) -> str:
    """
    Runs the external report generator,
    and returns the path to the generated report.

    Args:
        filePath (str): The VV filename
        templateName (str): Name of the report template to use
        outputName (str): Desired name of the generated report file

    Returns:
        str: Path to the generated report file
    """
    return _generate_file_from_vv(filePath, outputName, '/savereport', templateName)

def GenerateTXTFromVV(filePath: str, outputName: str) -> str:
    """
    Runs the conversion to TXT from commandline,
    and returns the path to the generated text file.

    Args:
        filePath (str): The VV filename
        outputName (str): Desired name of the generated text file

    Returns:
        str: Path to the generated text file
    """
    return _generate_file_from_vv(filePath, outputName, '/txt')

def GenerateUFFFromVV(filePath: str, outputName: str) -> str:
    """
    Runs the conversion to UFF from commandline,
    and returns the path to the generated UFF file.

    Args:
        filePath (str): The VV filename
        outputName (str): Desired name of the generated UFF file

    Returns:
        str: Path to the generated UFF file
    """
    return _generate_file_from_vv(filePath, outputName, '/uff')