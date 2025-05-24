url = 'https://github.com/voletrieulan0907/tool_changemail/releases/'

# Thêm 'api.' vào trước 'github.com' và '/latest' vào cuối
def convert_github_url(url):
    if url.startswith('https://github.com/'):
        url = url.replace('https://github.com/', 'https://api.github.com/repos/', 1)
        if not url.endswith('/latest'):
            if not url.endswith('/'):
                url += '/'
            url += 'latest'
    return url

api_url = convert_github_url(url)
print(api_url)