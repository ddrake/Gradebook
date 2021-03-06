import subprocess
import platform
from os import system

# --------------------------------------
# User input and type conversion helpers
# --------------------------------------
def dinput(prompt=">>> "):
    return input(prompt)

def get_string(gb, title, default=None, is_append=False):
    ftitle = title if default == None else title + " ({})".format(default)
    print(ftitle)
    sval = dinput()
    return default if default != None and sval == '' and not is_append else sval

def get_bool(gb, title, default=None):
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
            say(gb, "invalid")
            print("Value should be Y or N")

def get_valid_float(gb, title, minval, maxval, default=None) :
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
                say(gb, "invalid")
                print("Value should be between {0:.1f} and {1:.1f}".format(minval, maxval))
        except ValueError:
            print_say(gb, "What?")

def get_valid_int(gb, title, minval, maxval, default=None) :
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
                say(gb, "invalid")
                print("Value should be between {0:d} and {1:d}".format(minval, maxval))
        except ValueError:
            print_say(gb, "What?")

def get_int_from_list(gb, title, slist, default=None):
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
                say(gb, "invalid")
                print("Select one of the numbered options")
        except ValueError:
            print_say(gb, "What?")

def get_space_separated_floats(gb, title, default=None, n_as_none=False):
    ftitle = title if default == None else title + " ({})".format(' '.join(["{0:.1f}".format(p) for p in default]))
    while True: 
        print(ftitle)
        qs = dinput()
        if n_as_none and qs.upper() == 'N':
            return None
        if qs == '' and default != None:
            return default
        slst = qs.split()
        try:
            flst = [float(val) for val in slst]
            return flst 
        except ValueError:
            print_say(gb, "What?")

def pause(msg=''):
    input((msg+'  ' if msg else '') + "Press <Enter> to Continue. ")

def confirm(msg):
    print(msg + " (Y/N)")
    resp = dinput()
    return resp.upper() == 'Y'
 
# Give an audible warning
def say(gb, phrase):
    if gb.audible_warnings:
        system = platform.system()
        if system == 'Linux':
            try:
               subprocess.call(['spd-say', '-w', '"{}"'.format(phrase)])
            except Exception:
                print("spd-say is probably unavailable")
        elif system == 'Darwin':
            try:
                subprocess.call(['say', phrase])
            except Exception:
                print("say is probably unavailable")

def print_say(gb, phrase):
    print(phrase)
    if gb.audible_warnings:
        say(gb, phrase)

def open_in_calc(filename):
    try:
        subprocess.call(['soffice', '--calc', filename])
    except Exception:
        print("Libre Calc may not be available")

def num_na_str(number):
    return "{0:.1f}".format(number) if number != None else 'N/A'

def na_str(string):
    return string if string != None else 'N/A'
