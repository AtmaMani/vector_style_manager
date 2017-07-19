__author__ = 'atma6951'
__date__ = '3/20/2016'

from StyleFunctions import *

if __name__ == '__main__':
    portalURL = r"https://www.arcgis.com/"
    username = 'username'
    password = 'password'
    referer = r'https://www.arcgis.com'
    folderPath = r'E:\GIS_Data\file_formats\VTPK\vectorStyle_cleaned'
    itemID = '85d10a827d98487abc2432e725f41140' #Provide id of item that has to be updated
    url2service = r'https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer'
    token = getToken(portalURL, username,password,referer)
    update_fonts = False

    if (token):
        itemExists = findItem(itemID, portalURL, token)
        if (itemExists):
            print('Update start time: ' + getTimeStamp())

            if update_fonts:
                deleteSucceeded = deleteResources_fromPortalItem(itemID, portalURL, token, username)
                if (deleteSucceeded):
                    addResources_styles(portalURL, username, token, itemID, folderPath + r'\resources\styles', url2service)
                    addResources_sprites(portalURL, username, token, itemID, folderPath + r'\resources\sprites')
                    addResources_info(portalURL, username, token, itemID, folderPath + r'\resources\info')
                    addResources_fonts(portalURL, username, token, itemID, folderPath + r'\resources\fonts')
                    print('Update end time: ' + getTimeStamp())
                else:
                    print('Delete operation failed. No resources were updated')

            else:
                #Dont update fonts code
                deleteSucceeded = deleteResources_fromPortalItem(itemID, portalURL,
                                                                 token, username, update_fonts = update_fonts)
                if deleteSucceeded:
                    addResources_styles(portalURL, username, token, itemID, folderPath + r'\resources\styles', url2service)
                    addResources_sprites(portalURL, username, token, itemID, folderPath + r'\resources\sprites')
                    print("Update end time: " + getTimeStamp())
                else:
                    print("Delete operation failed. No resources were updated")
        else:
            print("Item cannot be added to portal. Halting script")
    else:
        print("Token not generated. Halting script")