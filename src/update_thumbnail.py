__author__ = 'atma6951'
__date__ = '10/26/2015'

from StyleFunctions import *
import urllib.parse, urllib.request, urllib.response
import http.client
import json
import uuid
import mimetypes
import io

def RESTcaller(url,data=None, method="GET"):
    """
    Utility function to send and receive REST HTTP calls to ArcGIS Online or Portal for ArcGIS
    :param :dictionary: pass the input parameters for REST call as a query string
    """
    try:
        if (method=="POST"):
            if data == None:
                data = " ".encode('utf-8')
            requestObj = urllib.request.urlopen(url, data)
        else:
            requestObj = urllib.request.urlopen(url)
        responseJSON=""
        while True:
            try:
                responseJSONpart = requestObj.read()
            except http.client.IncompleteRead as icread:
                responseJSON = responseJSON + icread.partial.decode('utf-8')
                continue
            else:
                responseJSON = responseJSON + responseJSONpart.decode('utf-8')
                break

        return json.loads(responseJSON)

    except Exception as RESTex:
        print("Exception occurred making REST call: " + RESTex.__str__())
        return None

class MultiPartForm:
    """Accumulate the data to be used when posting a form."""
    def __init__(self):
        self.form_fields = []
        self.files = []
        # Use a large random byte string to separate
        # parts of the MIME data.
        self.boundary = uuid.uuid4().hex.encode('utf-8')
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary={}'.format(
            self.boundary.decode('utf-8'))

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))

    def add_file(self, fieldname, filename, fileHandle,
                 mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = (
                mimetypes.guess_type(filename)[0] or
                'application/octet-stream'
            )
        self.files.append((fieldname, filename, mimetype, body))
        return

    @staticmethod
    def _form_data(name):
        return ('Content-Disposition: form-data; '
                'name="{}"\r\n').format(name).encode('utf-8')

    @staticmethod
    def _attached_file(name, filename):
        return ('Content-Disposition: file; '
                'name="{}"; filename="{}"\r\n').format(
            name, filename).encode('utf-8')

    @staticmethod
    def _content_type(ct):
        return 'Content-Type: {}\r\n'.format(ct).encode('utf-8')

    def __bytes__(self):
        """Return a byte-string representing the form data,
        including attached files.
        """
        buffer = io.BytesIO()
        boundary = b'--' + self.boundary + b'\r\n'

        # Add the form fields
        for name, value in self.form_fields:
            buffer.write(boundary)
            buffer.write(self._form_data(name))
            buffer.write(b'\r\n')
            buffer.write(value.encode('utf-8'))
            buffer.write(b'\r\n')

        # Add the files to upload
        for f_name, filename, f_content_type, body in self.files:
            buffer.write(boundary)
            buffer.write(self._attached_file(f_name, filename))
            buffer.write(self._content_type(f_content_type))
            buffer.write(b'\r\n')
            buffer.write(body)
            buffer.write(b'\r\n')

        buffer.write(b'--' + self.boundary + b'--\r\n')
        return buffer.getvalue()

#Main
if __name__ == '__main__':
    portalURL = r"https://python.playground.esri.com/portal"
    username = 'atma.mani'
    password = 'am4272017'
    referer = r'https://www.arcgis.com'
    itemID = '8ceee2566b9c43a996254d1dca0bec7b'
    thumbnail = r'/Users/atma6951/Documents/code/arcgis_desktop/vector_style_manager/try/canvasdark/metadata/thumbnail.png'


    token = getToken(portalURL, username,password,referer)

    if token:
        # form = MultiPartForm()
        #
        # with open(thumbnail, 'rb') as th_handle:
        #     form.add_field('token',token)
        #     form.add_file(fieldname='thumbnail', filename='thumbnail.png', fileHandle=th_handle)
        #     data2 = bytes(form)
        #     query_url = portalURL + "/sharing/rest/content/" + "/items/" + itemID + "/update?f=json"
        #
        #     req = urllib.request.Request(query_url, data2)
        #     req.add_header(
        #         'User-agent',
        #         'amani',
        #     )
        #     req.add_header('Content-type', form.get_content_type())
        #     req.add_header('Content-length', len(data2))
        #
        #     resp = urllib.request.urlopen(req).read().decode('utf-8')
        resp  = updateItem_thumbnail(portalURL, token, username, itemID, thumbnail)

            # resp = RESTcaller(query_url, data2, "POST")

        print(resp)
    else:
        print('Cannot get token. Halting')