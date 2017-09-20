__author__ = 'atmamani.github.io'
__date__ = '10/15/2015'
__updated__ = '7/19/2017'

from StyleFunctions import *
import argparse
from getpass import getpass
import sys
import os
import urllib3

if __name__ == '__main__':
    #region print banner
    print("=========================================================================================")
    print("=================================ESRI VECTOR STYLE MANAGER===============================")
    #endregion

    #region parse command line args
    parser = argparse.ArgumentParser()

    #add compulsory args
    parser.add_argument('portalurl', help='Enter portal url in the form: https://portalname.domain.com/webadaptor')
    parser.add_argument('username', help='Enter admin username', default='admin')
    parser.add_argument('service_url', help='Enter the URL of base vector tile service. URL should be of the form'
                                            ' https://servername.domain.com/webadaptor/rest/services/service_name/VectorTileServer')
    parser.add_argument('folder_path', help='Enter path to the folder containing one or more vector styles')

    #add optional args
    parser.add_argument('-p', '--password', help='Enter admin password. If password is not entered, it will be requested '
                                                 'during runtime')
    parser.add_argument('-met', '--metadata', help='Metadata foler name', default='metadata')
    parser.add_argument('-pub', '--public', help='Make Items public?', default='true')

    #parse the args
    args = parser.parse_args()

    make_public = False
    if args.public == 'true' or args.public == 'True':
        make_public = True
    #endregion

    #region establish connection to AGS Enterprise
    #check if password is given
    password=None
    if not args.password:
        password = getpass('Enter admin password: ')
    else:
        password = args.password

    #Connect to the portal
    portalURL = args.portalurl
    username = args.username
    referer = r'https://www.arcgis.com'

    folderPath = args.folder_path
    print(folderPath)
    url2service = args.service_url

    print('Connecting to ArcGIS Enterprise', end=" : ")

    token = getToken(portalURL, username, password,referer)

    if (token):
        print('connected')
    else:
        print("unable to connect. Halting the tool")
        sys.exit(1)
    #endregion

    #region scan for styles
    print('Scanning for styles ', end=" : ")
    folder_list = []
    it = os.listdir(folderPath)
    for entry in it:
        if not entry.startswith('.'):
            folder_list.append(entry)
    print("found {} styles".format(str(len(folder_list))))
    #endregion

    #region loop through each style and try to add it as an item
    print()
    for style in folder_list:
        print("Adding " + style + " ...")
        style_path = os.path.join(folderPath, style)
        try:
            itemName = style
            itemID = createItem(portalURL, token, username, url2service,
                                os.path.join(style_path, args.metadata), make_public)

            if (itemID):
                addResources_styles(portalURL, username, token, itemID, os.path.join(style_path, 'resources','styles'), url2service)
                addResources_sprites(portalURL, username, token, itemID, os.path.join(style_path, 'resources', 'sprites'))
                addResources_info(portalURL, username, token, itemID, os.path.join(style_path, 'resources','info'))
                addResources_fonts(portalURL, username, token, itemID, os.path.join(style_path, 'resources','fonts'))
                print('  Finished uploading item and its resources')
            else:
                print("**Item cannot be added to portal. Halting script")

        except Exception as style_ex:
            print("  ** Error " + str(style_ex))
            print("  ** Skipping to next style")
            continue

    print()
    print("End of tool")
    print("=========================================================================================")