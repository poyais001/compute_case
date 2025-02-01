@echo off
title Running Case

REM STEP_CheckParameter
if "%1"=="" (
    echo No parameter provided.
    set subFlag=0
    goto STEP_BuildNewFolder
) else (
    echo Parameter provided: %1
    set subFlag=1
)

REM STEP_BuildSubFolder
:loop_checkFolderNumber
if exist %1\case_%subFlag%\ (
    set /a subFlag+=1
    goto loop_checkFolderNumber
)
set targetFolder=%1\case_%subFlag%\
mkdir %targetFolder%
echo Target folder created: %targetFolder%
goto STEP_CopyFiles

:STEP_BuildNewFolder
set scriptDir=%~dp0
:loop_inputFolderName
set /p folderName=Enter a new folder name: 
set targetFolder=%scriptDir%%folderName%\
if exist targetFolder (
    echo Folder %folderName% already exists.
    goto loop_inputFolderName
)
mkdir %targetFolder%
echo Folder created : %targetFolder%

:STEP_CopyFiles
copy %scriptDir%input.lmp %targetFolder%
echo Input file copied to %targetFolder%

REM STEP_StartComputation
cd %targetFolder%
echo Ready to start computation.
pause
mpiexec -n 8 "C:\LAMMPS\lammps-private\build\Release\lmp_msmpi.exe" -in %targetFolder%input.lmp

REM STEP_CheckResultFile
if exist %targetFolder%dump.LAMMPS (
    echo Computation finished.
) else (
    echo Computation failed !!!
    pause
    goto :EOF
)

REM STEP_Visualization
echo Computation finished.
cd %scriptDir%\
echo Open output in OVITO.
"C:\Program Files\OVITO Basic\ovito.exe" %targetFolder%dump.LAMMPS

REM STEP_AddSuffix
if %subFlag% GTR 0 (
    goto notAddSuffix
)
set /p suffix=Enter a suffix for this case: 
rename %targetFolder% %folderName%_%suffix%
echo Folder renamed to %folderName%_%suffix%
:notAddSuffix

:end