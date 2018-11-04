import requests


# Read version from simcav.github.io website (program's own website).
def checkupdates(versionnum):
    # TRY TO RUN THIS IN A SECONDARY THREAD
    try:
        versiondata = requests.get("http://simcav.github.io/version", timeout=5)
        status = 200
    except requests.exceptions.ConnectTimeout as e:
        print(type(e))    # the exception instance
        #self.warningbar.warbar_message('Error fetching version information: Timeout error', 'firebrick')
        status = 408
    except requests.exceptions.ConnectionError as e:
        print(type(e))    # the exception instance
        #self.warningbar.warbar_message('Error fetching version information: Connection error (no internet?)', 'firebrick')
        status = 400
    # except requests.exceptions.HTTPError as e:
    #     print(type(e))    # the exception instance
    #     self.warningbar.warbar_message('Error fetching version information: HTTP error (rare invalid HTTP response)', 'firebrick')
    #     status = 404
    except Exception as e:
        print('type----------------------------\n')
        print(type(e))    # the exception instance
        print('args----------------------------\n')            
        print(e.args)     # arguments stored in .args
        print('e-------------------------------\n')            
        print(e)
        #self.warningbar.warbar_message('Unknown error while fetching version information', 'firebrick')
        status = 2
    else:
        if versiondata.status_code == requests.codes.ok:
            s = versiondata.text
            # Separate lines (version & important)
            s1 = s[:5]
            s2 = s[6:]
            print(s1)
            if versionnum == s1:
                #self.warningbar.warbar_message('SimCav is up-to-date (v%s)' %versionnum, 'lawn green')
                status = 200
            elif versionnum > s1:
                status = 1000
            else:
                # Make warninbar clickable to launch web browser
                if 'important' in s2:
                    #self.warningbar.warbar_message('IMPORTANT UPDATE: A new version is available at https://simcav.github.io (v%s, you are using v%s)' %(s1,versionnum), 'firebrick')
                    status = 0
                else:
                    #self.warningbar.warbar_message('A new version is available at https://simcav.github.io (v%s, you are using v%s)' %(s1,versionnum), 'goldenrod')
                    status = 1
        elif versiondata.status_code == requests.codes.not_found:
            #self.warningbar.warbar_message('Unable to retrieve online information about version, please try again later.', 'firebrick')
            status = 404
        else:
            #self.warningbar.warbar_message('Error fetching online version information: error %s (%s)' %(versiondata.status_code, requests.status_codes._codes[versiondata.status_code][0]) , 'firebrick')
            status = 2
    finally:
        #self.warningbar.label_warning.bind("<Button-1>", self.labelclick)
        #self.warningbar.label_warning.config(cursor="hand2")
        #self.warningbar.clickable = True
        pass
    return status