@echo off

setlocal

set CURRENT_SCRIPT_DIR=%~dp0

set SYSPATH=%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;
set PATH=%CURRENT_SCRIPT_DIR%\bin;%SYSPATH%

set GDAL_DATA=%CURRENT_SCRIPT_DIR%\share\data
set GEOTIFF_CSV=%CURRENT_SCRIPT_DIR%\share\epsg_csv
:: unset some variables that allows to have an isolate python environment

set PYTHONPATH=
set PYTHONHOME=
set PYTHONEXECUTABLE=
set PYTHONUSERBASE=

set GDAL_DRIVER_PATH=disable

set SEN2COR_HOME=%USERPROFILE%\Documents\sen2cor\2.11
set SEN2COR_BIN=%CURRENT_SCRIPT_DIR%\Lib\site-packages\sen2cor

::echo "setting SEN2COR_HOME is %SEN2COR_HOME%"

if not exist "%SEN2COR_HOME%" ( 
mkdir %SEN2COR_HOME%
)
if not exist "%SEN2COR_HOME%\cfg" mkdir %SEN2COR_HOME%\cfg

if not exist "%SEN2COR_HOME%\cfg\L2A_GIPP.xml" (
 xcopy /F "%SEN2COR_BIN%\cfg\L2A_GIPP.xml" "%SEN2COR_HOME%\cfg\"
)

%CURRENT_SCRIPT_DIR%\bin\python.exe -s %SEN2COR_BIN%\L2A_Process.py %*


endlocal
