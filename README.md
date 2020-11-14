# remarkable-cloud-tools

## Motivation
There seem to be no official method to upload files to `reMarkable 2` through a GNU/Linux operating system, and we also like to share some files with out beloved device. Hence these Python3 scripts (tested on Python 3.8), will allow uploading files to our reMarkable Device(s). They may work on other Operating Systems, of course.

### Pull Requests are very welcome
If you want to improve this, you are welcome to.
Specially in terms of packaging and stop kicking PEP-everything.
Pull-requests are welcome!

## Improvements
Well, it'll be nice if this could be connected to some Frameworks like `django` or `flink in order to use it as a hub. Meaning you could even generate some reports and send them right into your reMarkable device.

## Configuration
Example configuration file:
```yaml
devices:
  default: reMarkable2
  device:
    reMarkable2:
      device_token: youR_super_secret_token
      last_user_token:
    mom_reMarkable2:
      device_token: yomammas_big_secret_token
      last_user_token:
    dad_reMarkable2:
      device_token: yodaddy_mega_secret_token
      last_user_token:
```
A default configuration would be created first time these scripts are called and this expect to find it at `~/.reMarkable2/reMarkable2.yaml`.

### Obtain Device Token
Currently I'm obtaining this token from Google Chrome reMarkable extension. This means you must have linked this extension with your reMarkable 2 device first.
For GNU/Linux users you can try something like this:
```shell
for log in "$(find $HOME"/.config/google-chrome/Default/Local Extension Settings/bfhkfdnddlhfippjbflipboognpdpoeh/" -iname \*.log)"; do strings "${log}" | grep -1 deviceToken | cut -d '"' -f2 ; done
```
This would print at least 2 lines, one should say `deviceToken` and the second one should be our device token itself.

## install
Inside project:
```shell
python3 -mvenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
Create an alias just for easier access
```shell script
cat <<EOF
alias remarkable2_cloud_upload='$(which python3) ${PWD}/remarkable2_cloud_upload.py'
EOF
```
Add it to your `.bash_aliases` so you can call it from anywhere later as:
```shell script
remarkable2_cloud_upload your_file.pdf
# or
remarkable2_cloud_upload --device AnotherReMarkableDevice your_file.pdf

```

# Author
Roberto Salgado A.K.A. DRoBeR.
Check reMarkable 2 website if you don't have already 3 of them.
 