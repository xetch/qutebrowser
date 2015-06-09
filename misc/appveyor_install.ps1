# Adapted from Sample script to install Python and pip under Windows
# Authors: Olivier Grisel and Kyle Kastner
# License: CC0 1.0 Universal: http://creativecommons.org/publicdomain/zero/1.0/
# Adapted by Mark Harviston <mark.harviston@gmail.com>
# Adapted again by Florian Bruhin <mail@qutebrowser.org>.

$BASE_URL = "https://www.python.org/ftp/python/"

function InstallPackage ($python_home, $pkg) {
    $pip_path = $python_home + "\Scripts\pip.exe"
    & $pip_path install $pkg
}

function main () {
    InstallPip $env:PYTHON tox
    (new-object net.webclient).DownloadFile("http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4.1/PyQt5-5.4.1-gpl-Py3.4-Qt5.4.1-x64.exe", "C:\install-PyQt5.exe")
    Start-Process -FilePath C:\install-PyQt5.exe -ArgumentList "/S" -Wait -Passthru
}

main
