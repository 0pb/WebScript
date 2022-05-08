"""
made by 0pb
https://github.com/0pb/WebScript

launch a script from a button on a webpage
Only bottle.py is used, no other third party library are used

Edit the sample_config string below with your script and path
go to the url localhost:11850
Press one of the button and get the result of the script in the text box
"""
import shlex
import subprocess
import configparser


from bottle import auth_basic, request, route, run, static_file, template


# put an absolute path if possible
# In case the script isn't found, be sure you put " " around the path
# in windows : "example/script.bat" won't find anything, but "example/script.bat" will
# Same error can happen if there is a space in your path (eg : New folder/script.bat)
#
# Error may come from / and \ path, eg: "example\script_test.bat" will work on windows but "example/script_test.bat" won't
sample_config = """
[auth]
user:password

[scripts]
script 1:"example\script_test.bat"
script 2:example/script_test.sh
"""


# if you want the server to be accessed from outside, you must put the server ip as host
HOST = 'localhost'
PORT_SRV = "11850"


slots_template = """
<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style type="text/css">body{font-size:1.4em;margin-left:auto;margin-right:auto;width:60%;height:60%;background:#00B2CA;color:#000}#result{text-align:center;border-radius:5px;background:#FFF;color:#000;padding:10px}.centered-element{width:90%;margin-left:auto;margin-right:auto}input,select,textarea{border-radius:1px;background:#FFF;padding:10px;color:#000;font-size:1.4em;box-sizing:border-box;border:none;border-radius:2px;transition:background-color 0.5s ease}ul{margin:0;padding:0;list-style:none;text-align:center;counter-reset:steps}li{margin-bottom:10px}</style>
</head><body>

<div class="centered-element"><ul class="centered-element">
%for script in list_script:
    <li class="centered-element"><input class="center-element" type="submit" onclick="execute_script(this);" data-id="{{script}}" value="{{script}}"/></li>
%end
</ul></div>

<div id="result"></div>

<script>
function execute_script(button) {fetch('/scripts?' + new URLSearchParams({'id':button.dataset.id})).then(response => response.text()).then(function(data) {
          document.getElementById('result').innerHTML = data;});
};
</script>
</body></html>
"""


config = configparser.ConfigParser()

config.read_string(sample_config)
# comment out the line above and uncomment below if you want to use a .ini file instead
# config.read('config.ini')

list_allowed_user = dict(config.items('auth'))
list_script = dict(config.items('scripts'))


def is_authenticated_user(user : str = "default_user", password : str = "default_password") -> bool:
    if user in list_allowed_user:
        if list_allowed_user[user] == password:
            return True
    return False


def launch_script(script_id : int = 0) -> str:
    try:
        if script_id and script_id in list_script:
            output = subprocess.check_output(shlex.split(list_script[script_id]), stderr=subprocess.STDOUT).decode()
            return output.replace('\n', '<br>')
        return ""
    except subprocess.CalledProcessError as e:
        return ""
        # uncomment if you debug, you don't want that string to appear otherwise
        # return "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)
    except FileNotFoundError:
        return "FileNotFoundError :<br>No script was found on the indicated path"
    except OSError:
        return "OSError :<br>Can't execute the script on the OS (eg .sh file on windows)"


@route('/scripts', method='GET')
@auth_basic(is_authenticated_user)
def execute_scripts() -> str:
    return launch_script(request.params.get('id'))


@route('/')
@auth_basic(is_authenticated_user)
def root() -> str:
    return template(slots_template, list_script=list_script)


run(host=HOST, port=PORT_SRV, debug=False)


