# SimCav publication guide

Follow this guide to publish any new SimCav version.

**For final tkinter version, change updater to master branch (instead of master-old, as current)**

## Main

1. Change version number in main simcav file.

2. Change version number in website "version" file. Add "important" in a new line if required.

3. Update changelog.

4. Publish new version in master branch of simcav repository (both GitLab and GitHub).

5. Choose release name.


## Portable distribution

1. Rebase *standalone* branch with master. This branch has the update button disabled.

2. Package with pyinstaller:

    **ATTENTION!!! I used developer version of pyinstaller**

    ### Windows

    1. Create python virtual environment with only required modules installed (this reduces exe size A LOT).
    
        Needed: pyqt5, pyinstaller, numpy, matplotlib, requests. Got a size of 60MB (v5.0).

        ATTENTION!!! I used developer version of pyinstaller:

        `pip install https://github.com/pyinstaller/pyinstaller/tarball/develop`

    2. Package with pyinstaller: `pyinstaller SimCav_windows.spec`.

    ### Linux

    1. Use oldish Ubuntu LTS to increase compatibility.

    2. Create virtual environment, as in Windows. Make sure to use python3, pip3...

    3. Package with pyinstaller (same file as in Windows!): `pyinstaller SimCav.spec`

2. Save executables in web repository, in Releases/'version_number'/, together with signatures (see security/integrity).


## Security / integrity

1. Create GPG signatures for installer and portable versions.

2. Calculate SHA1 hashes for said files.


## On Github (for Zenodo integration)

1. Create new release: Name, version tag, new features, fixed bugs.

## On GitLab

1. Create tag.


## On SimCav website

1. Change version number in website "version" file. Add "important" in a new line if required.

2. Change version number wherever corresponds.

3. Add signatures and SHA1 hashes.

4. After Zenodo update, change DOI badge.


## GitLab / GitHub

1. DOI bagde in the repos should refer to lastest version. So far is correct, so do **NOT** change it!

## Analytics
1. If applicable, change goals (eg. file names).