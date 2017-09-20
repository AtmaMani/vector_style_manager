# vector_style_manager
This is a stand-alone Python based command line tool to manage ArcGIS vector styles. This tool is intended to be shipped 
with ArcGIS Data Appliance device to publish new Vector Tile Style items.

## Dependencies to be installed
To build this tool, you need to following dependencies satisfied in your Python environment. I recommend using conda and 
creating a new environment. You can do that using

```
conda create --name vstyle_data_app python=3.5
```
then activate this env
```
source activate vstyle_data_app
```

Then install the following packages in your newly created active env
```
conda install requests
pip install pyinstaller
conda install urllib3
```
If your development env is Windows, then install `pypiwin32`
```
pip install pypiwin32
```
Then clone this project using the command
```
git clone https://github.com/atmamani/vector_style_manager.git
```

## Building the stand-alone tool
The script `src/StyleUploader.py` is the base script that you want to build. It accepts command line arguments. To build this
into an app, run the following
```
pyinstaller src/StyleUploader.py
```
this will create a `dist` and `build` folders. You ship the `dist` to the customers. If this works well, you can build
the app into a single file (which includes a Python kernel and dependencies)
```
pyinstaller src/StyleUploader.py --onefile
```

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

### Dev version of the tool - mac


```
~/Documents/code/arcgis_desktop/vector_style_manager/dist/StyleUploader [master] $ ./StyleUploader --help
=========================================================================================
=================================ESRI VECTOR STYLE MANAGER===============================
usage: StyleUploader [-h] [-p PASSWORD] [-met METADATA]
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

```
#### Dev version of the tool with command line args
You can run it as shown below:
```
~/Documents/code/arcgis_desktop/vector_style_manager/dist/StyleUploader [master] $ ./StyleUploader 
   https://python.playground.esri.com/portal atma.mani 
   https://basemaps.arcgis.com/v1/arcgis/rest/services/World_Basemap/VectorTileServer ../../try
=========================================================================================
=================================ESRI VECTOR STYLE MANAGER===============================
Enter admin password: 
../../try
Connecting to ArcGIS Enterprise : Token obtained: vP72_zAuZrZzC4NBC
connected
Scanning for styles  : found 2 styles

Adding ags.py ...
  ** Error [Errno 20] Not a directory: '../../try/ags.py/metadata/metadata.json'
  ** Skipping to next style
Adding streetmaphybrid ...
    Item created with id : 9ddb8a73fd0d4415809d895e830f1e73
    Uploading styles/root.json
    URL in styles/root.json updated
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
