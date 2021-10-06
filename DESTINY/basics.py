import os
import requests

from DESTINY.enums import *
# NOTE: when running locally, remove "DESTINY." from above

def get_headers():
    """
    Return headers dictionary with api key from .bash_profile
    """
    key = os.environ.get('DDV_API_KEY')
    headers = {"X-API-Key":key}
    return headers


def make_request(endpoint):
    """
    Given an endpoint, make request and return json
    """
    headers = get_headers()
    url = "https://www.bungie.net/platform/"
    url += endpoint

    r = requests.get(url, headers=headers)

    return ResponseSummary(r)



class ResponseSummary:
    '''
    Object contains all the important information about the request sent to bungie.

    From: https://gist.github.com/cortical-iv/a22ef122e771b994454e02b6b4e481c3
    
    TLDR: A class to better make sense of request return information :)
    '''
    def __init__(self, response):
        self.status = response.status_code
        self.url = response.url
        self.data = None
        self.message = None
        self.error_code = None
        self.error_status = None
        self.exception = None
        if self.status == 200:
            result = response.json()
            self.message = result['Message']
            self.error_code = result['ErrorCode']
            self.error_status = result['ErrorStatus']
            if self.error_code == 1:
                try:
                    self.data = result['Response']
                except Exception as ex:
                    print("ResponseSummary: 200 status and error_code 1, but there was no result['Response']")
                    print("Exception: {0}.\nType: {1}".format(ex, ex.__class__.__name__))
                    self.exception = ex.__class__.__name__
            else:
                print('No data returned for url: {0}.\n {1} was the error code with status 200.'.format(self.url, self.error_code))
        else:
            print('Request failed for url: {0}.\n.Status: {0}'.format(self.url, self.status))

    def __repr__(self):
        """What will be displayed/printed for the class instance."""
        disp_header =       "<" + self.__class__.__name__ + " instance>\n"
        disp_data =         ".data: " + str(self.data) + "\n\n"
        disp_url =          ".url: " + str(self.url) + "\n"
        disp_message =      ".message: " + str(self.message) + "\n"
        disp_status =       ".status: " + str(self.status) + "\n"
        disp_error_code =   ".error_code: " + str(self.error_code) + "\n"
        disp_error_status = ".error_status: " + str(self.error_status) + "\n"
        disp_exception =    ".exception: " + str(self.exception)
        return disp_header + disp_data + disp_url + disp_message + \
               disp_status + disp_error_code + disp_error_status + disp_exception
