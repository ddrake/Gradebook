import subprocess

# --------------------------------------
# User input and type conversion helpers
# --------------------------------------
def get_string(title, default=None, prompt=" >> "):
    ftitle = title if default == None else title + " ({0:s})".format(default)
    print(ftitle)
    sval = input(prompt)
    return default if default != None and sval == '' else sval

def get_bool(title, default=None, prompt=" >> "):
    ftitle = title if default == None else title + \
            " ({0:s})".format('Y' if default == 1 else 'N')
    while True:
        print(ftitle)
        sval = input(prompt).lower()
        if default != None and sval == '':
            return default
        if sval == 'y':
            return 1
        elif sval == 'n':
            return 0
        else:
            say("invalid")
            print("Value should be Y or N")

def get_valid_float(title, minval, maxval, default=None, prompt=" >> ") :
    valid = False
    ftitle = title if default == None else title + " ({0:.1f})".format(default)

    while not valid:
        print(ftitle)
        sval = input(prompt)
        if default != None and sval == '':
            return default
        try:
            fval = float(sval)
            if fval >= minval and fval <= maxval:
                valid = True
            else:
                say("invalid")
                print("Value should be between {0:d} and {1:d}".format(minval, maxval))
        except ValueError:
            say("What?")
            print("What?")
    return fval

def get_int_from_list(title, slist, default=None, prompt = " >> "):
    valid = False
    ftitle = title if default == None else title + " ({0:d})".format(default)

    while not valid:
        print(ftitle)
        for i, item in enumerate(slist):
            print("{0:d}. {1:s}".format(i+1, item))
        sval = input(prompt)
        if default != None and sval == '':
            return default
        try:
            ival = int(sval)
            if ival >= 1 and ival <= len(slist):
                valid = True
            else:
                say("invalid")
                print("Select one of the numbered options")
        except ValueError:
            say("What?")
            print("What?")
    return ival

def get_space_separated_floats(title, valid_sum, default=None, prompt=" >> "):
    valid = False
    ftitle = title if default == None else title + " ({0:s})".format(' '.join(["{0:.1f}".format(p) for p in default]))
    while not valid: 
        print(ftitle)
        qs = input(prompt)
        if qs == '' and default != None:
            return default

        slst = qs.split()
        try:
            flst = [float(val) for val in slst]
            if sum(flst) >= valid_sum:
                valid = True
            else:
                say("invalid")
                print("The points should sum to at least {0:.1f}".format(valid_sum))
        except ValueError:
            say("What?")
            print("What?")
    return flst

# Give an audible warning
def say(phrase):
    subprocess.call(['spd-say', '-w', '"{0:s}"'.format(phrase)])

