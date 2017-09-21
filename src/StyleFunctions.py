__author__ = 'atma6951'
__date__ = ''
# NOTE: This script has dependency: Python 3.4 and requests library
# NOTE: do pip install requests

import os
from datetime import datetime as dt
from zipfile import ZipFile
import pathlib
import json
import fnmatch
import requests
import requests.packages.urllib3 as urllib3
from functools import reduce

# Prevent certificate warnings
urllib3.disable_warnings()


def getToken(portalURL, username, password, referer, expiration=1440):
    """
    Generates portal token by exchanging username and password
    :param url: Url to ArcGIS portal. Example https://www.arcgis.com
    :param username:
    :param password:
    :param referer: Example: https://www.arcgis.com
    :param expiration: Optional, time in seconds
    :return:
    """

    query_dict = {'username': username,
                  'password': password,
                  'referer': referer,
                  'expiration': str(expiration)}

    # Construct the url
    queryURL = portalURL + r"/sharing/rest/generateToken?f=json"

    # make the request
    try:
        response = requests.post(queryURL, data=query_dict, verify=False)
    except Exception as ex:
        print("Exception occurred making REST call, " + ex)
        return

    # check if response succeeded
    if response.status_code == 200:
        try:
            responseJSON = response.json()
            try:
                token = responseJSON["token"]
                print("Token obtained: " + token)
                return token
            except Exception as tokenEx:
                print("Error getting token: " + str(tokenEx))
        except Exception as tokenEx2:
            print("Token request did not succeed: " + str(tokenEx2))
            print("Response from portal: " + response.text)
    response.close()


def createItem(portalURL, token, username, url2service, metadata_path, make_public=False):
    """
    Will create portal item of Vector Tile Service type.
    :param portalURL: example: http://www.arcgis.com/
    :param token: token obtained using getToken method
    :param username: the username used to get token
    :param metadata_path: to folder on disk containing style data
    :param make_public: if True, items will be shared to everyone
    :return: string - itemID
    """

    #region get metadata
    with open(os.path.join(metadata_path, 'metadata.json'), 'r') as met_handle:
        met_dict = json.load(met_handle)

    #look for thumbnail file
    thumbnail_path = None
    thumbnail_name = None
    for directory, subdir_list, file_list in os.walk(metadata_path):
        for file in file_list:
            ext = os.path.splitext(file)[-1]
            if ext in ('.gif', '.jpg', '.jpeg', '.png'):
                thumbnail_path =os.path.join(directory, file)
                thumbnail_name = file
    #endregion

    # construct query URL and payload data
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + r"/addItem?f=json"
    met_tags = reduce((lambda x,y: x+","+y), met_dict['item']['tags'])

    #construct thumbnail url parameter
    try:
        thumbnail_url = portalURL + r"/sharing/rest/content/items/" + met_dict['item']['thumbnailItemId']
    except:
        thumbnail_url = r'invlaid_url'

    query_dict = {'type': 'Vector Tile Service',
                  'title': met_dict['item']['title'],
                  'tags': met_tags,
                  'url': url2service,
                  'description':met_dict['item']['description'],
                  'snippet':met_dict['item']['snippet'],
                  'extent':",".join(str(j) for i in met_dict['item']['extent'] for j in i),
                  'accessInformation':met_dict['item']['accessInformation'],
                  'licenseInfo':met_dict['item']['licenseInfo'],
                  'thumbnailurl':thumbnail_url,
                  'token': token}

    #add thumbnail
    files = {}
    if thumbnail_path:
        files = {'file': ('thumbnail.png', open(thumbnail_path, 'rb'))}
        # files = {'thumbnail':open(thumbnail_path, 'rb')}

    # make request
    try:
        # response = requests.post(queryURL, data=query_dict, files=files, verify=False)
        response = requests.post(queryURL, data=query_dict, verify=False)

    except Exception as restEx:
        print("    **Exception making addItem call: " + str(restEx))
        return

    # check if succeeded
    if response.status_code == 200:
        try:
            responseJSON = response.json()
            try:
                itemID = responseJSON["id"]
                print("    Item created with id : " + itemID)
                # updateItem_thumbnail(portalURL, token, username, itemID, thumbnail_path)

                if make_public:
                    queryURL2 = portalURL + r"/sharing/rest/content/users/" + username + r"/items/" + itemID + r"/share?f=json"
                    query_dict2={'everyone':True,
                                 'token':token}
                    response2 = requests.post(queryURL2, data=query_dict2, verify=False)
                    print("    Item shared with public")

                return itemID
            except Exception as additemEx:
                print("    **Add item call succeeded but item not created")
                print("    **response: " + response.text)
        except:
            print("    **Add Item response was non json: " + response.text)
    else:
        print('    **Add Item call resulted in non 200 response: ' + str(response.status_code))
    response.close()


def fixRelativePaths(stylejson_dict):
    """
    Function to add 'resources' word to path in root.json uploaded to itemID/data resource
    :param stylejson_dict: the json as dictionary when styles/root.json is read
    :return: dictionary back with corrected paths
    """
    # Update dictionary elements 'sprite' and 'glyphs'
    try:
        s1 = stylejson_dict['sprite']
        stylejson_dict['sprite'] = s1.replace('../', '../resources/')
        s2 = stylejson_dict['glyphs']
        stylejson_dict['glyphs'] = s2.replace('../', '../resources/')
        return stylejson_dict
    except:
        print('Region: fixRelativePaths. Elements sprite / glyphs not found in JSON')

def updateItem_thumbnail(portalURL, token, username, itemID, thumbnail_path):
    """
    Will add root.json to itemID/data resource
    :param portalURL: example: http://www.arcgis.com/
    :param token: token obtained using getToken method
    :param username: the username used to get token
    :param itemID: Item Id obtained from createItem method
    :param folderPath: to folder on disk containing style data
    :return: string - itemID
    """
    # construct query URL
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + \
               r"/items/" + itemID + r"/update?f=json"

    # read data
    files = {'file':open(thumbnail_path, 'rb')}
    query_dict = {'token': token}

    # make request
    try:
        response = requests.post(queryURL, data=query_dict, files=files, verify=False)
    except Exception as restEx:
        print("Exception making addItem call: " + restEx)
        return

    # check if succeeded
    if response.status_code == 200:
        try:
            responseJSON = response.json()
            try:
                if (responseJSON["success"]):
                    print("    Item updated")
                    return
            except Exception as additemEx:
                print("Add item call succeeded but item not created")
                print("response: " + response.text)
        except:
            print("Add Item response was non json: " + response.text)

def updateItem(portalURL, token, username, itemID, folderPath):
    """
    Will add root.json to itemID/data resource
    :param portalURL: example: http://www.arcgis.com/
    :param token: token obtained using getToken method
    :param username: the username used to get token
    :param itemID: Item Id obtained from createItem method
    :param folderPath: to folder on disk containing style data
    :return: string - itemID
    """
    # construct query URL
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + \
               r"/items/" + itemID + r"/update?f=json"

    # read data
    f1 = open(folderPath + r"/styles/root.json")
    f2 = json.load(f1)
    f3 = json.dumps(f2)
    query_dict = {'text': f3,
                  'token': token}

    # make request
    try:
        response = requests.post(queryURL, data=query_dict, verify=False)
    except Exception as restEx:
        print("Exception making addItem call: " + restEx)
        return

    # check if succeeded
    if response.status_code == 200:
        try:
            responseJSON = response.json()
            try:
                if (responseJSON["success"]):
                    print("Item updated")
                    return
            except Exception as additemEx:
                print("Add item call succeeded but item not created")
                print("response: " + response.text)
        except:
            print("Add Item response was non json: " + response.text)


def addResources_sprites(portalURL, username, token, itemID, folderPath):
    """
    Will upload resources from sprites directory
    :param portalURL: Same URL used to get Token and create item
    :param username: Username used to get Token
    :param token: Token obtained from getToken method
    :param itemID: ItemID obtained from createItem method
    :return: null
    """

    print("    Uploading sprites")
    # construct query url
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + \
               r"/items/" + itemID + r"/addResources?f=json&token=" + token

    # region Loop through sprites folder and upload
    fileList = os.listdir(folderPath)
    for currentFile in fileList:
        if (currentFile.__contains__('.db')): #Exclude hidden files created by Windows OS
            continue
        files = {'file': open(os.path.join(folderPath , currentFile), "rb")}
        data = {'resourcesPrefix': 'sprites'}

        try:
            response = requests.post(queryURL, files=files, data=data, verify=False)
        except Exception as addResourceEx:
            print("    **Exception making addResource for sprites: " + str(addResourceEx))
            return

        if response.status_code == 200:
            try:
                responseJSON = response.json()
                if responseJSON["success"]:
                    print("    Uploaded " + currentFile)
                else:
                    print("    **Error uploading " + currentFile)
                    print("    **Response message: " + str(responseJSON))
            except:
                print("    **addResource response is non JSON: " + str(response.text))
        else:
            print("    ***addResource call got non 200 response. File being uploaded: " + currentFile)
            print("    ***response status code: " + str(response.status_code))
        response.close()
        # endregion


def addResources_styles(portalURL, username, token, itemID, folderPath, url2service):
    """
    Will upload resources from styles directory. The url property will be replaced with that passed in the parameter.
    New - the url to glyph and sprite kvp will be replaced to absolute paths instead of relative.
    :param portalURL: Same URL used to get Token and create item
    :param username: Username used to get Token
    :param token: Token obtained from getToken method
    :param itemID: ItemID obtained from createItem method
    :param folderPath: Path to directory containing styles/root.json file
    :param url2service: Valid URL to the Vector Tile Server the item is pointing to
    :return: null
    """

    print("    Uploading styles/root.json")
    # construct query url
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + \
               r"/items/" + itemID + r"/addResources?f=json&token=" + token

    # region Update url properties in styles/root.json
    with open(os.path.join(folderPath, 'root.json'), 'r') as styleFileReadObj:
        styleJSON = json.load(styleFileReadObj)
    try:
        styleJSON['sources']['esri']['url'] = url2service

        #replace sprite path
        original_sprite_path = styleJSON['sprite']
        styleJSON['sprite'] = portalURL + r'/sharing/rest/content/items/' + itemID + \
                              r'/resources' + r"/sprites/sprite"

        #i decided to hard code the suffix.
        # styleJSON['sprite'] = portalURL + r'/sharing/rest/content/items/' + itemID + \
        #                       r'/resources' + original_sprite_path.split(".")[-1]

        #replace glyph path
        original_glyph_path = styleJSON['glyphs']
        glyph_splitted=original_glyph_path.split(".")
        styleJSON['glyphs'] = url2service + r'/resources' + r"/fonts/{fontstack}/{range}.pbf"

        #i decided to hard code the suffix instead of getting it from existing file.
        # styleJSON['glyphs'] = url2service + r'/resources' + glyph_splitted[-2] + "." + glyph_splitted[-1]

        with open(os.path.join(folderPath, 'root.json'), 'w') as styleFileWriteObj:
            json.dump(styleJSON, styleFileWriteObj)
        print(r'    URLs in styles/root.json updated')
    except Exception as styleRWex:
        print('    **Error updating URL of root.json : ' + str(styleRWex))
        print('    **Proceeding to upload file without URL update')
    # endregion

    files = {'file': open(os.path.join(folderPath, 'root.json'), "rb")}
    data = {'resourcesPrefix': 'styles'}

    try:
        response = requests.post(queryURL, files=files, data=data, verify=False)
    except Exception as addResourceEx:
        print("    **Exception making addResource for styles: " + str(addResourceEx))
        return

    if response.status_code == 200:
        try:
            responseJSON = response.json()
            if responseJSON["success"]:
                print(r"    Uploaded styles/root.json")
            else:
                print("    **Error uploading styles/root.json")
                print("    **Response message: " + str(responseJSON))
        except:
            print("    **addResource response is non JSON: " + str(response.text))
    else:
        print("    ***addResource call got non 200 response : " + str(response.status_code))
    response.close()


def addResources_info(portalURL, username, token, itemID, folderPath):
    """
    Will upload resources from styles directory
    :param portalURL: Same URL used to get Token and create item
    :param username: Username used to get Token
    :param token: Token obtained from getToken method
    :param itemID: ItemID obtained from createItem method
    :param folderPath: Path to directory containing info/root.json file
    :return: null
    """

    print(r"    Uploading info/root.json")
    # construct query url
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + \
               r"/items/" + itemID + r"/addResources?f=json&token=" + token

    files = {'file': open(os.path.join(folderPath, 'root.json'), "rb")}
    data = {'resourcesPrefix': 'info'}

    try:
        response = requests.post(queryURL, files=files, data=data, verify=False)
    except Exception as addResourceEx:
        print("    **Exception making addResource for info: " + str(addResourceEx))
        return

    if response.status_code == 200:
        try:
            responseJSON = response.json()
            if responseJSON["success"]:
                print(r"    Uploaded info/root.json")
            else:
                print("    * Error uploading info/root.json")
                print(r"    * Response message: " + str(responseJSON))
        except:
            print("    ** addResource response is non JSON: " + str(response.text))
    else:
        print("    *** addResource call got non 200 response : " + str(response.status_code))
    response.close()


def addResources_fonts(portalURL, username, token, itemID, folderPath):
    """
    Function to upload fonts as resources. Provide path to fonts folder.
    :param portalURL: Portal from which token was generated and item was created
    :param username: Username used to get Token
    :param token: Token obtained from getToken method
    :param itemID:ItemID obtained from createItem method
    :param folderPath: Directory in which fonts are stored
    :return: null
    """
    # construct query url
    queryURL = portalURL + r"/sharing/rest/content/users/" + username + \
               r"/items/" + itemID + r"/addResources?f=json&token=" + token

    # region Loop through fonts folder and get all subfolders and files
    # snake through directories using some generators and list comprehension
    fontFileList = [os.path.join(dirpath, filtered_files)
                    for dirpath, dirname, files in os.walk(folderPath)
                    for filtered_files in fnmatch.filter(files, '*.pbf')]
    print('    Uploading fonts')
    print('    Found ' + str(len(fontFileList)) + ' font files')

    # Now for each font file, find the folder hierarchy. Create appropriate
    # prefixes during upload
    uploadedFileCount = 0
    for currentFile in fontFileList:
        files = {'file': open(currentFile, "rb")}

        # string manipulation to find fold hierarchy
        nowfilePath = pathlib.Path(currentFile)
        leftStrippedPath = str(nowfilePath.relative_to(folderPath))  # more reliable than lstrip
        prefix, filename = leftStrippedPath.rsplit('\\', 1)
        prefix2 = prefix.replace('\\', '/').replace(' ', '_')  # make URL safe

        # construct data payload
        # data = {'resourcesPrefix':'fonts/' + prefix2} #Not doing space to _ switch.
        data = {'resourcesPrefix': 'fonts/' + prefix}

        try:
            response = requests.post(queryURL, files=files, data=data, verify=False)
        except Exception as addResourceEx:
            print("    **Exception making addResource for sprites: " + str(addResourceEx))
            response.close()
            return

        if response.status_code == 200:
            try:
                responseJSON = response.json()
                if responseJSON["success"]:
                    print("     Uploaded " + leftStrippedPath)
                else:
                    print("    * Error uploading " + leftStrippedPath)
                    print("    * Response message: " + str(responseJSON))
            except Exception as deserializeEx:
                print("    ** addResource response is non JSON: " + str(response.text))
        else:
            print("    *** addResource call got non 200 response. File being uploaded: " + currentFile)

        uploadedFileCount = uploadedFileCount + 1
        response.close()

    print('    Fonts - total files on disk: ' + str(len(fontFileList)) +
          '. Number of files uploaded: ' + str(uploadedFileCount))
    # endregion


def addResources_archive(portalURL, username, token, itemID, folderPath, archiveFolderPath):
    """
    Function to upload all resources as an archive. This is assuming there are no
    unwanted files in the directory.
    :param portalURL: Portal from which token was generated and item was created
    :param username: Username used to get Token
    :param token: Token obtained from getToken method
    :param itemID:ItemID obtained from createItem method
    :param folderPath: Directory in which fonts are stored
    :return: null
    """
    # construct query url - check if adding or updating
    queryURL = portalURL + r"/sharing/content/users/" + username + \
               r"/items/" + itemID + r"/addResources?f=json&token=" + token

    # Get list of files to be archived
    fileList = [os.path.join(dirpath, currentFile)
                for dirpath, dirname, files in os.walk(folderPath)
                for currentFile in files]
    print('Creating archive')
    print('  Found ' + str(len(fileList)) + ' files in total')

    # Open archive file handler. Create generic file name with timestamp
    zipFileName = archiveFolderPath + r"\vectorStyle_" + dt.now().strftime("%Y_%m_%d_%H_%M_%S") + ".zip"

    # Loop through each file and add to archive
    os.chdir(folderPath)
    with ZipFile(zipFileName, "w") as zipFileHandle:
        for file in fileList:
            if (file.__contains__('.db')):
                continue
            relativeFileName = pathlib.Path(file).relative_to(folderPath).__str__()
            zipFileHandle.write(relativeFileName)

    if (pathlib.Path(zipFileName).exists()):
        print("Successfully created archive: " + zipFileName)
    else:
        print("Error creating archive: " + zipFileName)
        return None

    # Upload as multipart archive
    files = {'file': (open(zipFileName, 'rb'), r'application/zip')}
    data = {'archive': 'True'}

    try:
        response = requests.post(queryURL, files=files, data=data, verify=False)
    except Exception as addResourceEx:
        print("  *Exception making addResource for sprites: " + str(addResourceEx))
        response.close()
        return

    if response.status_code == 200:
        try:
            responseJSON = response.json()
            if responseJSON["success"]:
                print("  Uploaded archive")

                # region Check if number of resources has increased
                summary_queryURL = portalURL + r'/sharing/rest/content/items/' + itemID + r'/resources?f=json'
                summary_query_dict = {'token': token}

                try:
                    resSummary_response = requests.post(summary_queryURL, data=summary_query_dict, verify=False)
                except Exception as restEx:
                    print('Exception making REST query to get resources summary info: ' + str(restEx))
                    return False

                if resSummary_response.status_code == 200:
                    try:
                        resSummaryJSON = resSummary_response.json()
                        resource_countA = resSummaryJSON['total']
                        print('Total number of resources on item after updating: ' + str(resource_countA))
                        resSummary_response.close()
                        if (resource_countA <= 0): #upload happened but archive was rejected
                            return False
                    except Exception as summaryEx:
                        print('** Exception getting resource summary info ' + str(summaryEx))
                        return False
                else:
                    print('** Request to get resources summary info was non 200 response: ' +
                          str(resSummary_response.status_code))
                    return False
                # endregion

            else:
                print("  * Error uploading archive")
                print("  * Response message: " + str(responseJSON))
        except Exception as deserializeEx:
            print("  ** addResource response is non JSON: " + str(response.text))
    else:
        print("  *** addResource call got non 200 response")
    response.close()
    # endregion


# Find if item is findable and is of valid type
def findItem(itemID, portalURL, token, folderPath=None):
    # construct item URL
    queryURL = portalURL + r'/sharing/rest/content/items/' + itemID + '?f=json'
    query_dict = {'token': token}

    # make request
    try:
        response = requests.post(queryURL, data=query_dict, verify=False)
    except Exception as restEx:
        print('Exception making REST query to find Item: ' + str(restEx))
        return False

    # Check if item is of valid type
    if response.status_code == 200:
        try:
            responseJSON = response.json()
            if responseJSON['type'] == 'Vector Tile Service':
                itemName = responseJSON['title']
                VTserviceURL = responseJSON['url']

                if (folderPath is not None):
                    styleDownloadPath = os.path.join(folderPath, itemName, 'resources')
                    os.makedirs(styleDownloadPath, exist_ok=True)
                    print('Vector Tile Service item resources will be downloaded to ' + styleDownloadPath)
                    return styleDownloadPath, VTserviceURL
                else:
                    print('Found portal item')
                    return True
            else:
                print('Provided itemID is not VectorTileService. '
                      'Instead it is : ' + responseJSON['type'])
                return False
        except Exception as findItemEx:
            print('Error trying to parse item JSON : ' + str(findItemEx))
    else:
        print('Request to find Item returned with non 200 status code: '
              + str(response.status_code))

# Find if resources are available in portal item or service
def isResourcesOnPortalItem(itemID, portalURL, token):
    # construct query URL to sprites.json
    print('Finding if resources are available as part of portal item')
    queryURL = portalURL + r'/sharing/rest/content/items/' + \
               itemID + r'/resources/sprites/sprite.json?'
    query_dict = {'token': token}

    # make request
    try:
        finder_response = requests.post(queryURL, data=query_dict, verify=False)
    except Exception as restEx:
        print('-- Exception making REST call to sprites.json resource. Error: ' + str(restEx))
        return False

    # Analyze response message
    if finder_response.status_code == 200:
        try:
            finder_responseJSON = finder_response.json()
            try:
                if finder_responseJSON['error']['code'] == 404:
                    return False
                else:
                    print('-- Response from portal : ' + finder_responseJSON.__str__())
            except:
                # Case when error key is not present = sprites is available
                return True
        except Exception as finderEx1:
            print('-- Response from portal was non JSON')
            return False
    else:
        print('-- Request status code was non 200: ' + str(finder_response.status_code))
        return False

# Get sprites resources
def downloadResources_fromPortalItem(itemID, portalURL, token, styleDownloadPath):
    # construct item/resources summary URL
    summary_queryURL = portalURL + r'/sharing/rest/content/items/' + itemID + r'/resources?f=json'
    summary_query_dict = {'token': token}

    # make request
    try:
        resSummary_response = requests.post(summary_queryURL, data=summary_query_dict, verify=False)
    except Exception as restEx:
        print('Exception making REST query to get Items summary resource: ' + str(restEx))
        return False

    # Download data resource to disk
    if resSummary_response.status_code == 200:
        try:
            resSummaryJSON = resSummary_response.json()
            total_files = resSummaryJSON['total']
            print('-- Downloading resources. Total number of files: ' + str(total_files))
            file_list = resSummaryJSON['resources']

            # region Loop through each resource and download
            for currentFile_dict in file_list:
                currentFile = currentFile_dict['resource']
                res_queryURL = portalURL + r'/sharing/rest/content/items/' \
                               + itemID + r'/resources/' + currentFile + r'?&token=' + token

                # find file names and prefixing folder names
                path_analysis = pathlib.Path(currentFile)
                prefixing_folders = path_analysis.parent.__str__()
                currentFile_name = path_analysis.parts[-1]

                # make request
                try:
                    currentFile_response = requests.get(res_queryURL, verify=False)
                    if currentFile_response.status_code == 200:
                        # make directories as request succeeds
                        currentFile_path = os.path.join(styleDownloadPath, prefixing_folders)
                        os.makedirs(currentFile_path, exist_ok=True)

                        # proceed based on file extension
                        if currentFile_name.endswith('.json'):
                            # treat JSON as text file
                            currentFile_responseJSON = currentFile_response.json()
                            with open(os.path.join(currentFile_path, currentFile_name), 'w') as write_currentFile:
                                json.dump(currentFile_responseJSON, write_currentFile, indent=2)

                        else:
                            # store current file as binary
                            with open(os.path.join(currentFile_path, currentFile_name),
                                      'wb') as write_currentFile_binary:
                                write_currentFile_binary.write(currentFile_response.content)

                        print('---- Downloaded ' + currentFile)
                    else:
                        print('**** Request failed when downloading file ' + currentFile +
                              ' with status ' + str(currentFile_response.status_code))
                except Exception as fileDownloadEx:
                    print('** Skipping file download ' + currentFile + ' : ' + str(fileDownloadEx))
                    continue  # Skip to next file in loop
                currentFile_response.close()
            # endregion

            resSummary_response.close()
        except Exception as downloadEx:
            print('** Exception downloading resources. ' + str(downloadEx))
    else:
        print('** Request to get resources resulted in non 200 response '
              + str(resSummary_response.status_code))
        return False


def downloadResources_fromService(VTserviceURL, token, styleDownloadPath):
    print('--Downloading resources from service')
    # region Download resources/styles/root.json
    styles_queryURL = VTserviceURL + r'/resources/styles/root.json?token=' + token

    try:
        styles_response = requests.get(styles_queryURL, verify=False)
        styles_responseJSON = styles_response.json()
        # write to disk
        os.makedirs(os.path.join(styleDownloadPath, 'styles'), exist_ok=True)
        with open(os.path.join(styleDownloadPath, 'styles', 'root.json'), 'w') as write_styleFile:
            json.dump(styles_responseJSON, write_styleFile, indent=2)

        styles_response.close()
        print('--- Downloaded resources/styles/root.json')
    except Exception as restEx_styles:
        print('** Error trying to download resources/styles/root.json : ' + str(restEx_styles))
    # endregion

    # construct VectorTileServer/resources/info.json summary URL
    summary_queryURL = VTserviceURL + r'/resources/info/root.json?token=' + token

    # make request
    try:
        resSummary_response = requests.get(summary_queryURL, verify=False)
    except Exception as restEx:
        print('Exception making REST query to get service summary resource: ' + str(restEx))
        return False

    # Download data resource to disk
    if resSummary_response.status_code == 200:
        try:
            resSummaryJSON = resSummary_response.json()
            total_files = len(resSummaryJSON['resourceInfo'])
            print('--- Total number of sprites and font files: ' + str(total_files))
            file_list = resSummaryJSON['resourceInfo']

            # region Loop through each resource and download
            for currentFilePath in file_list:
                resourcesBaseURL = VTserviceURL + r'/resources/'

                # Adjust for relative paths
                path_analysis = pathlib.Path(currentFilePath)
                currentFile = ""
                if path_analysis.parts[0] == "..":
                    currentFile = currentFilePath[3:]
                else:
                    currentFile = currentFilePath

                res_queryURL = resourcesBaseURL + currentFile + r'?token=' + token

                # find file names and prefixing folder names
                path_analysis2 = pathlib.Path(currentFile)
                prefixing_folders = path_analysis2.parent.__str__()
                currentFile_name = path_analysis2.parts[-1]

                # make request
                try:
                    currentFile_response = requests.get(res_queryURL, verify=False)
                    if currentFile_response.status_code == 200:
                        # make directories as request succeeds
                        currentFile_downloadpath = os.path.join(styleDownloadPath, prefixing_folders)
                        os.makedirs(currentFile_downloadpath, exist_ok=True)

                        # proceed based on file extension
                        if currentFile_name.endswith('.json'):
                            # treat JSON as text file
                            currentFile_responseJSON = currentFile_response.json()
                            with open(os.path.join(currentFile_downloadpath, currentFile_name),
                                      'w') as write_currentFile:
                                json.dump(currentFile_responseJSON, write_currentFile, indent=2)

                        else:
                            # store current file as binary
                            with open(os.path.join(currentFile_downloadpath, currentFile_name),
                                      'wb') as write_currentFile_binary:
                                write_currentFile_binary.write(currentFile_response.content)

                        print('---- Downloaded ' + currentFile)
                    else:
                        print('**** Request failed when downloading file ' + currentFile +
                              ' with status ' + str(currentFile_response.status_code))
                except Exception as fileDownloadEx:
                    print('** Skipping file download ' + currentFile + ' : ' + str(fileDownloadEx))
                    continue  # Skip to next file in loop
                currentFile_response.close()
            # endregion

            resSummary_response.close()
        except Exception as downloadEx:
            print('** Exception downloading resources. ' + str(downloadEx))
    else:
        print('** Request to get resources resulted in non 200 response '
              + str(resSummary_response.status_code))
        return False

# Use delete all to remove resources in 1 go
def deleteResources_fromPortalItem(itemID, portalURL, token, username, update_fonts = True):
    # region Query number of portal resources.
    summary_queryURL = portalURL + r'/sharing/rest/content/items/' + itemID + r'/resources?f=json'
    summary_query_dict = {'token': token}

    try:
        resSummary_response = requests.post(summary_queryURL, data=summary_query_dict, verify=False)
    except Exception as restEx:
        print('Exception making REST query to get resources summary info: ' + str(restEx))
        return False

    if resSummary_response.status_code == 200:
        try:
            resSummaryJSON = resSummary_response.json()
            resource_countA = resSummaryJSON['total']
            print('Total number of resources on item before deleting: ' + str(resource_countA))
            resSummary_response.close()
        except Exception as summaryEx:
            print('** Exception getting resource summary info ' + str(summaryEx))
            return False
    else:
        print('** Request to get resources summary info was non 200 response: ' +
              str(resSummary_response.status_code))
        return False
    # endregion

    # region Delete resources
    if not update_fonts:
        resource_list_forUpdate = ['sprites/sprite.json',
                                   'sprites/sprite.png',
                                   'sprites/sprite@2x.json',
                                   'sprites/sprite@2x.png',
                                   'styles/root.json']

        for resource in resource_list_forUpdate:
            delete_queryURL = portalURL + r'/sharing/rest/content/users/' + username + \
                          r'/items/' + itemID + r'/removeResources?f=json'
            delete_query_dict = {'token': token,
                                 'resource': resource}

            # make request
            try:
                delete_response = requests.post(delete_queryURL, data=delete_query_dict, verify=False)
            except Exception as restEx:
                print('Exception making REST query to get Items summary resource: ' + str(restEx))
                return False

            # Download data resource to disk
            if delete_response.status_code == 200:
                try:
                    deleteSummaryJSON = delete_response.json()
                    print(str.format('Deleting {0}: {1}', resource, str(deleteSummaryJSON)))
                    delete_response.close()
                except Exception as deleteEx:
                    print('** Exception deleting resource {0} : {1} ',resource, str(deleteEx))
            else:
                print('** Request to delete resources resulted in non 200 response '
                      + str(delete_response.status_code))
                return False

    else:
        # construct item/resources summary URL
        delete_queryURL = portalURL + r'/sharing/rest/content/users/' + username + \
                          r'/items/' + itemID + r'/removeResources?f=json'
        delete_query_dict = {'token': token,
                             'deleteALL': "True"}

        # make request
        try:
            delete_response = requests.post(delete_queryURL, data=delete_query_dict, verify=False)
        except Exception as restEx:
            print('Exception making REST query to get Items summary resource: ' + str(restEx))
            return False

        # Download data resource to disk
        if delete_response.status_code == 200:
            try:
                deleteSummaryJSON = delete_response.json()
                print('Delete response from server: ' + str(deleteSummaryJSON))
                delete_response.close()
            except Exception as deleteEx:
                print('** Exception deleting resources. ' + str(deleteEx))
        else:
            print('** Request to delete resources resulted in non 200 response '
                  + str(delete_response.status_code))
            return False
    # endregion

    # region Query number of portal resources - after delete.
    summary_queryURL = portalURL + r'/sharing/rest/content/items/' + itemID + r'/resources?f=json'
    summary_query_dict = {'token': token}

    try:
        resSummary_response = requests.post(summary_queryURL, data=summary_query_dict, verify=False)
    except Exception as restEx:
        print('Exception making REST query to get resources summary info: ' + str(restEx))
        return False

    if resSummary_response.status_code == 200:
        try:
            resSummaryJSON = resSummary_response.json()
            resource_countA = resSummaryJSON['total']
            print('Total number of resources on item after deleting: ' + str(resource_countA))
            return True
        except Exception as summaryEx:
            print('** Exception getting resource summary info ' + str(summaryEx))
            return False
    else:
        print('** Request to get resources summary info was non 200 response: ' +
              str(resSummary_response.status_code))
        return False
    #endregion

#Retun timestamp
def getTimeStamp():
    return dt.now().__str__()