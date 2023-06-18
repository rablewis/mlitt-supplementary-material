import urllib


def upload(local_filepath, oxcal_filepath, cj):
    url = f'https://c14.arch.ox.ac.uk/mydata/{oxcal_filepath}'

    local_file = open(local_filepath, 'rb')
    try:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        response = opener.open(url, data=local_file.read())
        print(f'uploaded {local_filepath}')
        local_file.close()

    except urllib.error.HTTPError as error:
        local_file.close()
        print(f'upload failed with status {error.code}: {error.reason}')
        if (error.code == 404):
            print('check oxcal directory exists')

def download(oxcal_filepath, local_filepath, cj):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    url = f'https://c14.arch.ox.ac.uk/mydata/{oxcal_filepath}'

    try:
        response = opener.open(url)
        # copy response content to local file
        local_file = open(local_filepath, 'wb')
        while True:
            chunk = response.read(512 * 1024)
            if not chunk: break
            local_file.write(chunk)
        local_file.close()
        print(f'file saved to {local_filepath}')

    except urllib.error.HTTPError as error:
        if error.code == 404:
            print('File does not exist')
