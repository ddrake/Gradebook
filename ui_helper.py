import subprocess

# --------------------------------------
# User input and type conversion helpers
# --------------------------------------
def dinput(prompt=">>> "):
    return input(prompt)

def get_string(title, default=None, is_append=False):
    ftitle = title if default == None else title + " ({})".format(default)
    print(ftitle)
    sval = dinput()
    return default if default != None and sval == '' and not is_append else sval

def get_bool(title, default=None):
    ftitle = title if default == None else title + \
            " ({})".format('Y' if default == 1 else 'N')
    while True:
        print(ftitle)
        sval = dinput().upper()
        if default != None and sval == '':
            return default
        if sval == 'Y':
            return 1
        elif sval == 'N':
            return 0
        else:
            say("invalid")
            print("Value should be Y or N")

def get_valid_float(title, minval, maxval, default=None) :
    ftitle = title if default == None else title + " ({0:.1f})".format(default)
    while True:
        print(ftitle)
        sval = dinput()
        if default != None and sval == '':
            return default
        try:
            fval = float(sval)
            if fval >= minval and fval <= maxval:
                return fval
            else:
                say("invalid")
                print("Value should be between {0:.1f} and {1:.1f}".format(minval, maxval))
        except ValueError:
            say("What?")
            print("What?")

def get_valid_int(title, minval, maxval, default=None) :
    ftitle = title if default == None else title + " ({0:d})".format(default)
    while True:
        print(ftitle)
        sval = dinput()
        if default != None and sval == '':
            return default
        try:
            ival = int(sval)
            if ival >= minval and ival <= maxval:
                return ival
            else:
                say("invalid")
                print("Value should be between {0:d} and {1:d}".format(minval, maxval))
        except ValueError:
            say("What?")
            print("What?")

def get_int_from_list(title, slist, default=None):
    ftitle = title if default == None else title + " ({0:d})".format(default)
    while True:
        print(ftitle)
        for i, item in enumerate(slist):
            print("{0:d}. {1:s}".format(i+1, item))
        sval = dinput()
        if default != None and sval == '':
            return default
        try:
            ival = int(sval)
            if ival >= 1 and ival <= len(slist):
                return ival 
            else:
                say("invalid")
                print("Select one of the numbered options")
        except ValueError:
            say("What?")
            print("What?")

def get_space_separated_floats(title, default=None):
    ftitle = title if default == None else title + " ({})".format(' '.join(["{0:.1f}".format(p) for p in default]))
    while True: 
        print(ftitle)
        qs = dinput()
        if qs == '' and default != None:
            return default
        slst = qs.split()
        try:
            flst = [float(val) for val in slst]
            return flst 
        except ValueError:
            say("What?")
            print("What?")

def pause(msg=''):
    input((msg+'  ' if msg else '') + "Press <Enter> to Continue. ")

def confirm(msg):
    print(msg + " (Y/N)")
    resp = dinput()
    return resp.upper() == 'Y'
 
# Give an audible warning
def say(phrase):
    subprocess.call(['spd-say', '-w', '"{}"'.format(phrase)])

def print_say(phrase):
    print(phrase)
    say(phrase)

def open_in_calc(filename):
    try:
        subprocess.call(['soffice', '--calc', filename])
    except Exception:
        print("Libre Calc may not be available")

def num_na_str(number):
    return "{0:.1f}".format(number) if number != None else 'N/A'

def na_str(string):
    return string if string != None else 'N/A'
