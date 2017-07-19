__author__ = 'atma6951'
__date__ = '10/26/2015'

from StyleFunctions import *

#Main
if __name__ == '__main__':
    portalURL = r"https://www.arcgis.com"
    username = 'username'
    password = 'password'
    referer = r'https://www.arcgis.com'
    itemID = 'f96366254a564adda1dc468b447ed956'
    folderPath = r'D:\Temp\StyleDownloads3'
    downloadFromServerOnly = True

    token = getToken(portalURL, username,password,referer)

    if token:
        styleDownloadPath, VTserviceURL = findItem(itemID, portalURL, token, folderPath)
        if styleDownloadPath:
            if (not downloadFromServerOnly and isResourcesOnPortalItem(itemID, portalURL, token)):
                downloadResources_fromPortalItem(itemID, portalURL, token, styleDownloadPath)
            else:
                downloadResources_fromService(VTserviceURL, token, styleDownloadPath)
        else:
            print('Error trying to findItem. Halting')
    else:
        print('Cannot get token. Halting')