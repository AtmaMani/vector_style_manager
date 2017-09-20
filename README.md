# vector_style_manager
This is a stand-alone Python based command line tool to manage ArcGIS vector styles. This tool is intended to be shipped 
with ArcGIS Data Appliance device to publish new Vector Tile Style items.

## Running the tool
### Stand-alone version on Windows
The tool accepts command line args. The `password` is optional. If you don't specify as command line arg, then the tool will ask for it during runtime. Running this tool in `help` mode prints the following
```
λ StyleUploader.exe -h
=========================================================================================
=================================ESRI VECTOR STYLE MANAGER===============================
usage: StyleUploader.exe [-h] [-p PASSWORD] [-met METADATA] [-pub PUBLIC]
                         portalurl username service_url folder_path

positional arguments:
  portalurl             Enter portal url in the form:
                        https://portalname.domain.com/webadaptor
  username              Enter admin username
  service_url           Enter the URL of base vector tile service. URL should
                        be of the form https://servername.domain.com/webadapto
                        r/rest/services/service_name/VectorTileServer
  folder_path           Enter path to the folder containing one or more vector
                        styles

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        Enter admin password. If password is not entered, it
                        will be requested during runtime
  -met METADATA, --metadata METADATA
                        Metadata foler name
  -pub PUBLIC, --public PUBLIC
                        Make Items public?
```

### Stand-alone version on Windows with all arguments
```
E:\code\arcgis_desktop\vector_style_manager\dist\StyleUploader (master)                                             
λ StyleUploader.exe https://dev005219.esri.com/portal admin https://dev0000585.esri.com/server/rest/services/Hosted/
World_basemap_v2017R15_wmas/VectorTileServer E:\code\arcgis_desktop\vector_style_manager\sample_styles -pub True    
=========================================================================================                           
=================================ESRI VECTOR STYLE MANAGER===============================                           
Enter admin password:                                                                                               
E:\code\arcgis_desktop\vector_style_manager\sample_styles                                                           
Connecting to ArcGIS Enterprise : Token obtained: vhQIQx4RxAlkSTw-oeKGw8MvNsi9G-a8FjbDy-FfuKZOi-uR1fpKQLoSXClgTlmyPE
BXIk-iEJsfDod2t8TyDrUmcFdWlu9JIFAdvUYPeOoHnCdLrn7cc-c9o_U4fVT3                                                      
connected                                                                                                           
Scanning for styles  : found 1 styles                                                                               
                                                                                                                    
Adding dark_gray ...                                                                                                
    Item created with id : 898c3b2e965f4ccaacdc2f28867a9a2f                                                         
    Item shared with public                                                                                         
    Uploading styles/root.json                                                                                      
    URLs in styles/root.json updated                                                                                
    Uploaded styles/root.json                                                                                       
    Uploading sprites                                                                                               
    Uploaded sprite.json                                                                                            
    Uploaded sprite.png                                                                                             
    Uploaded sprite@2x.json                                                                                         
    Uploaded sprite@2x.png                                                                                          
    Uploading info/root.json                                                                                        
    Uploaded info/root.json                                                                                         
    Uploading fonts                                                                                                 
    Found 0 font files                                                                                              
    Fonts - total files on disk: 0. Number of files uploaded: 0                                                     
  Finished uploading item and its resources                                                                         
                                                                                                                    
End of tool                                                                                                         
=========================================================================================                    
```