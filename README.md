# vscan-directory-listing-detector
Checks if directory listing is enabled on web servers, potentially exposing sensitive files and information. The check looks for "Index of" in the page title when one exists and in the page body, plus file-like links. A page with no title element is checked on its body and links. If the request fails and no response is received, the tool prints a failure line and exits non-zero instead of reporting that listing is not enabled. - Focused on Lightweight web application vulnerability scanning focused on identifying common misconfigurations and publicly known vulnerabilities

## Install
`git clone https://github.com/ShadowGuardAI/vscan-directory-listing-detector`

## Usage
`./vscan-directory-listing-detector [params]`

## Parameters
- `-h`: Show help message and exit
- `-t`: Timeout for the HTTP request in seconds. Default is 5.
- `-v`: Enable verbose logging for debugging.
- `-o`: No description provided

## License
Copyright (c) ShadowGuardAI
