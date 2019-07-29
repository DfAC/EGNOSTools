rem Processing DGPS data using RTkLib
rem LKB 2015-19(c)

rem part of MarRINav WP2.1 work
rem estimates accuracy of the EGNOS


@ECHO OFF
md out


FOR /f %%F IN ('dir /b .\EGNOS\*.19b') DO (
	ECHO     **Processing EGNOS solution for station:  %%~nF
	python runConverter.py -o out\%%~nF.ems ".\EGNOS\%%F"	
)

ECHO  ...DONE
ECHO.
