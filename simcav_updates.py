import requests

# Read version from simcav.github.io website (program's own website).
def checkupdates(versionnum):
    # TRY TO RUN THIS IN A SECONDARY THREAD
    try:
        versiondata = requests.get("http://simcav.github.io/version", timeout=5)
        status = 200
    except requests.exceptions.ConnectTimeout as e:
        print(type(e))    # the exception instance
        status = 408
    except requests.exceptions.ConnectionError as e:
        print(type(e))    # the exception instance
        status = 400
    # except requests.exceptions.HTTPError as e:
    #     print(type(e))    # the exception instance
    #     status = 404
    except Exception as e:
        print('type----------------------------\n')
        print(type(e))    # the exception instance
        print('args----------------------------\n')            
        print(e.args)     # arguments stored in .args
        print('e-------------------------------\n')            
        print(e)
        status = 2
    else:
        if versiondata.status_code == requests.codes.ok:
            s = versiondata.text
            # Separate lines (version & important)
            s1, s2 = s.split('\n')
            if versionnum == s1:
                status = 200
            elif versionnum > s1:
                status = 1000
            else:
                # Make warninbar clickable to launch web browser
                if 'important' in s2:
                    status = 0
                else:
                    status = 1
        elif versiondata.status_code == requests.codes.not_found:
            status = 404
        else:
            status = 2
    return status, s1