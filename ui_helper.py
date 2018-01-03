import subprocess

# --------------------------------------
# User input and type conversion helpers
# --------------------------------------
def get_string(title, default=None, prompt=">>> "):
    ftitle = title if default == None else title + " ({0:s})".format(default)
    print(ftitle)
    sval = input(prompt)
    return default if default != None and sval == '' else sval

def get_bool(title, default=None, prompt=">>> "):
    ftitle = title if default == None else title + \
            " ({0:s})".format('Y' if default == 1 else 'N')
    while True:
        print(ftitle)
        sval = input(prompt).upper()
        if default != None and sval == '':
            return default
        if sval == 'Y':
            return 1
        elif sval == 'N':
            return 0
        else:
            say("invalid")
            print("Value should be Y or N")

def get_valid_float(title, minval, maxval, default=None, prompt=">>> ") :
    ftitle = title if default == None else title + " ({0:.1f})".format(default)
    while True:
        print(ftitle)
        sval = input(prompt)
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

def get_valid_int(title, minval, maxval, default=None, prompt=">>> ") :
    ftitle = title if default == None else title + " ({0:d})".format(default)
    while True:
        print(ftitle)
        sval = input(prompt)
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

def get_int_from_list(title, slist, default=None, prompt = ">>> "):
    ftitle = title if default == None else title + " ({0:d})".format(default)
    while True:
        print(ftitle)
        for i, item in enumerate(slist):
            print("{0:d}. {1:s}".format(i+1, item))
        sval = input(prompt)
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

def get_space_separated_floats(title, default=None, prompt=">>> "):
    ftitle = title if default == None else title + " ({0:s})".format(' '.join(["{0:.1f}".format(p) for p in default]))
    while True: 
        print(ftitle)
        qs = input(prompt)
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

# Give an audible warning
def say(phrase):
    subprocess.call(['spd-say', '-w', '"{0:s}"'.format(phrase)])

def print_say(phrase):
    print(phrase)
    say(phrase)

