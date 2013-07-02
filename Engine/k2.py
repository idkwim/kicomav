# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)
'''
+-----------------------------------------------------------------------------+
|                                              KICOM Anti-Virus (Disinfector) |
|                                              Copyright (C) 95-2013, Hanul93 |
|                                              Version 0.20, Made by Kei Choi |
+-----------------------------------------------------------------------------+
'''
import sys
import os
import string
import kavcore
import hashlib
import urllib
import thread
import time
from optparse import OptionParser

KAV_VERSION   = '0.23'
KAV_BUILDDATE = 'June 27 2013'
KAV_LASTYEAR  = KAV_BUILDDATE[len(KAV_BUILDDATE)-4:]

g_EngineInit = 0

#---------------------------------------------------------------------
# �ֿܼ� ���� ����� ���� Ŭ���� �� �Լ���
#---------------------------------------------------------------------
FOREGROUND_BLACK     = 0x0000
FOREGROUND_BLUE      = 0x0001
FOREGROUND_GREEN     = 0x0002
FOREGROUND_CYAN      = 0x0003
FOREGROUND_RED       = 0x0004
FOREGROUND_MAGENTA   = 0x0005
FOREGROUND_YELLOW    = 0x0006
FOREGROUND_GREY      = 0x0007
FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

BACKGROUND_BLACK     = 0x0000
BACKGROUND_BLUE      = 0x0010
BACKGROUND_GREEN     = 0x0020
BACKGROUND_CYAN      = 0x0030
BACKGROUND_RED       = 0x0040
BACKGROUND_MAGENTA   = 0x0050
BACKGROUND_YELLOW    = 0x0060
BACKGROUND_GREY      = 0x0070
BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

if os.name == 'nt' :
    from ctypes import windll, Structure, c_short, c_ushort, byref

    NOCOLOR = False

    SHORT = c_short
    WORD = c_ushort

    class COORD(Structure):
      """struct in wincon.h."""
      _fields_ = [
        ("X", SHORT),
        ("Y", SHORT)]

    class SMALL_RECT(Structure):
        _fields_ = [
            ("Left", SHORT),
            ("Top", SHORT),
            ("Right", SHORT),
            ("Bottom", SHORT)]

    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", WORD),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD)]

    # winbase.h
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

    def get_text_attr():
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
        return csbi.wAttributes

    def set_text_attr(color):
        SetConsoleTextAttribute(stdout_handle, color)

    def cprint(msg, color) :
        if NOCOLOR == False :
            default_colors = get_text_attr()
            default_bg = default_colors & 0x00F0

            set_text_attr(color | default_bg)
            sys.stdout.write(msg)
            set_text_attr(default_colors)
        else :
            sys.stdout.write(msg)
        sys.stdout.flush()
else :
    def cprint(msg, color) :
        sys.stdout.write(msg)
        sys.stdout.flush()

def PrintError(msg) :
    cprint('Error: ', FOREGROUND_RED | FOREGROUND_INTENSITY)
    print (msg)

#---------------------------------------------------------------------
# PrintLogo()
# Ű�޹���� �ΰ� ����Ѵ�
#---------------------------------------------------------------------
def PrintLogo() :
    logo = 'KICOM Anti-Virus II (for %s) Ver %s (%s)\nCopyright (C) 1995-%s Kei Choi. All rights reserved.\n'

    print '------------------------------------------------------------'
    s = logo % (sys.platform.upper(), KAV_VERSION, KAV_BUILDDATE, KAV_LASTYEAR)
    cprint(s, FOREGROUND_CYAN | FOREGROUND_INTENSITY)
    print '------------------------------------------------------------'

#---------------------------------------------------------------------
# Update()
# Ű�޹�� �ֽ� ������ ������Ʈ �Ѵ�
#---------------------------------------------------------------------
def Update() :
    print

    try :
        url = 'https://dl.dropboxusercontent.com/u/5806441/k2/'

        # ������Ʈ�ؾ� �� ���� ����� ���Ѵ�.
        down_list = GetDownloadList(url)

        while len(down_list) != 0 :
            filename = down_list.pop(0)
            # ���� �Ѱ��� ������Ʈ �Ѵ�.
            Download_file(url, filename, hook)

        # ������Ʈ �Ϸ� �޽��� ���
        cprint('\n[', FOREGROUND_GREY)
        cprint('Update complete', FOREGROUND_GREEN)
        cprint(']\n', FOREGROUND_GREY)

        # ������Ʈ ���� ���� ����
        os.remove('update.cfg')
    except :
        cprint('\n[', FOREGROUND_GREY)
        cprint('Update Stop', FOREGROUND_GREY | FOREGROUND_INTENSITY)
        cprint(']\n', FOREGROUND_GREY)

# ������Ʈ ������ ǥ��
def hook(blocknumber, blocksize, totalsize) :
    cprint('.', FOREGROUND_GREY)

# �Ѱ��� ������ �ٿ�ε� �Ѵ�.
def Download_file(url, file, fnhook=None) :
    rurl = url

    # ������Ʈ ���� ���Ͽ� �ִ� ����� URL �ּҷ� ��ȯ�Ѵ�
    rurl += file.replace('\\', '/')

    # �����ؾ� �� ������ ��ü ��θ� ���Ѵ�
    pwd = os.path.abspath('') + os.sep + file

    if fnhook != None :
        cprint(file + ' ', FOREGROUND_GREY)

    # ������ �ٿ�ε� �Ѵ�
    urllib.urlretrieve(rurl, pwd, fnhook)

    if fnhook != None :
        cprint(' update\n', FOREGROUND_GREEN)

# ������Ʈ �ؾ� �� ������ ����� ���Ѵ�
def GetDownloadList(url) :
    down_list = []

    pwd = os.path.abspath('')

    # ������Ʈ ���� ������ �ٿ�ε� �Ѵ�
    Download_file(url, 'update.cfg')

    fp = open('update.cfg', 'r')

    while 1 :
        line = fp.readline().strip()
        if not line :
            break
        t = line.split(' ') # ������Ʈ ��� �Ѱ��� ���Ѵ�

        # ������Ʈ ���� ������ �ؽÿ� ������ �ؽø� ���Ѵ�
        if ChekNeedUpdate(pwd + os.sep + t[1], t[0]) == 1:
            # �ٸ��� ������Ʈ ��Ͽ� �߰�
            down_list.append(t[1])

    fp.close()

    return down_list

# ������Ʈ ���� ������ �ؽÿ� ������ �ؽø� ���Ѵ�
def ChekNeedUpdate(file, hash) :
    try :
        # ���� ������ �ؽø� ���Ѵ�
        fp = open(file, 'rb')
        data = fp.read()
        fp.close()

        # �ؽø� ���Ѵ�
        s = hashlib.sha1()
        s.update(data)
        if s.hexdigest() == hash :
            return 0 # ������Ʈ ��� �ƴ�
    except :
        pass

    return 1 # ������Ʈ ���

#---------------------------------------------------------------------
# PrintUsage()
# Ű�޹���� ������ ����Ѵ�
#---------------------------------------------------------------------
def PrintUsage() :
    print '\nUsage: k2.py path[s] [options]'

#---------------------------------------------------------------------
# PrintOptions()
# Ű�޹���� �ɼ��� ����Ѵ�
#---------------------------------------------------------------------
def PrintOptions() :
    options_string = \
'''Options:
        -f,  --files           scan files *
        -r,  --arc             scan archives
        -I,  --list            display all files
        -V,  --vlist           display virus list
             --update          update
             --sigtool         create a malware signature
             --no-color        not print color
        -?,  --help            this help
                               * = default option'''

    print options_string

#---------------------------------------------------------------------
# DefineOptions()
# Ű�޹���� �ɼ��� �����Ѵ�
#---------------------------------------------------------------------
def DefineOptions() :
    try :
        # fmt = IndentedHelpFormatter(indent_increment=8, max_help_position=40, width=77, short_first=1)
        # usage = "usage: %prog path[s] [options]"
        # parser = OptionParser(add_help_option=False, usage=usage, formatter=fmt)

        usage = "Usage: %prog path[s] [options]"
        parser = OptionParser(add_help_option=False, usage=usage)

        parser.add_option("-f", "--files",
                      action="store_true", dest="opt_files",
                      default=True)
        parser.add_option("-b", "--boot",
                      action="store_true", dest="opt_boot",
                      default=False)
        parser.add_option("-r", "--arc",
                      action="store_true", dest="opt_arc",
                      default=False)
        parser.add_option("-i", "--mail",
                      action="store_true", dest="opt_mail",
                      default=False)
        parser.add_option("-k", "--nopack",
                      action="store_true", dest="opt_nopack",
                      default=False)
        parser.add_option("-h", "--nohed",
                      action="store_true", dest="opt_nohed",
                      default=False)
        parser.add_option("-X", "--xcl=ext1;ext2",
                      action="store_true", dest="opt_xcl",
                      default=False)
        parser.add_option("-G", "--log[=file]",
                      action="store_true", dest="opt_log",
                      default=False)
        parser.add_option("-S", "--cd",
                      action="store_true", dest="opt_cd",
                      default=False)
        parser.add_option("-N", "--fixed",
                      action="store_true", dest="opt_fixed",
                      default=False)
        parser.add_option("-M", "--floppy",
                      action="store_true", dest="opt_floppy",
                      default=False)
        parser.add_option("-I", "--list",
                      action="store_true", dest="opt_list",
                      default=False)
        parser.add_option("-g", "--prog",
                      action="store_true", dest="opt_prog",
                      default=False)
        parser.add_option("-e", "--app",
                      action="store_true", dest="opt_app",
                      default=False)
        parser.add_option("-F", "--infp=path",
                      action="store_true", dest="opt_infp",
                      default=False)
        parser.add_option("-U", "--susp=path",
                      action="store_true", dest="opt_susp",
                      default=False)
        parser.add_option("-R", "--nor",
                      action="store_true", dest="opt_nor",
                      default=False)
        parser.add_option("-p", "--prompt",
                      action="store_true", dest="opt_prompt",
                      default=False)
        parser.add_option("-O", "--info",
                      action="store_true", dest="opt_info",
                      default=False)
        parser.add_option("-W", "--nowarn",
                      action="store_true", dest="opt_nowarn",
                      default=False)
        parser.add_option("-V", "--vlist",
                      action="store_true", dest="opt_vlist",
                      default=False)
        parser.add_option("-d", "--dis",
                      action="store_true", dest="opt_dis",
                      default=False)
        parser.add_option("-o", "--copy",
                      action="store_true", dest="opt_copy",
                      default=False)
        parser.add_option("-y", "--copys",
                      action="store_true", dest="opt_copys",
                      default=False)
        parser.add_option("-l", "--del",
                      action="store_true", dest="opt_del",
                      default=False)

        parser.add_option("", "--sigtool",
                      action="store_true", dest="opt_sigtool",
                      default=False)
        parser.add_option("", "--no-color",
                      action="store_true", dest="opt_nocolor",
                      default=False)
        parser.add_option("", "--noclean",
                      action="store_true", dest="opt_noclean",
                      default=False)
        parser.add_option("", "--move",
                      action="store_true", dest="opt_move",
                      default=False)
        parser.add_option("", "--moves",
                      action="store_true", dest="opt_moves",
                      default=False)
        parser.add_option("", "--ren",
                      action="store_true", dest="opt_ren",
                      default=False)
        parser.add_option("", "--infext=ext",
                      action="store_true", dest="opt_infext",
                      default=False)
        parser.add_option("", "--alev[=n]",
                      action="store_true", dest="opt_alev",
                      default=False)
        parser.add_option("", "--flev[=n]",
                      action="store_true", dest="opt_flev",
                      default=False)
        parser.add_option("", "--update",
                      action="store_true", dest="opt_update",
                      default=False)

        parser.add_option("-?", "--help",
                      action="store_true", dest="opt_help",
                      default=False)

        return parser
    except :
        pass

    return None

#---------------------------------------------------------------------
# ParserOptions()
# Ű�޹���� �ɼ��� �м��Ѵ�
#---------------------------------------------------------------------
def ParserOptions() :
    parser = DefineOptions()

    if parser == None or len( sys.argv ) < 2 :
        return None, None
    else :
        try :
            (options, args) = parser.parse_args()
        except :
            return None, None

        return options, args

def print_result(result) :
    print
    print

    cprint ('Results:\n', FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Folders           :%d\n' % result['Folders'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Files             :%d\n' % result['Files'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Packed            :%d\n' % result['Packed'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Infected files    :%d\n' % result['Infected_files'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Suspect files     :%d\n' % result['Suspect_files'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Warnings          :%d\n' % result['Warnings'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('Identified viruses:%d\n' % result['Identified_viruses'], FOREGROUND_GREY | FOREGROUND_INTENSITY)
    cprint ('I/O errors        :%d\n' % result['IO_errors'], FOREGROUND_GREY | FOREGROUND_INTENSITY)

    print

#---------------------------------------------------------------------
# �Ǽ��ڵ� ����� ���ٿ� ����ϱ� ���� �Լ�
#---------------------------------------------------------------------
def convert_display_filename(real_filename) :
    # ��¿� �̸�
    fsencoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    display_filename = unicode(real_filename, fsencoding).encode(sys.stdout.encoding, 'replace')
    return display_filename


def display_line(filename, message, filename_color=None, message_color=None) :
    filename += ' '
    filename = convert_display_filename(filename)
    len_fname = len(filename)
    len_msg   = len(message)

    if len_fname + 1 + len_msg < 79 :
        fname = '%s' % filename
        msg   = '%s' % message
    else :
        able_size = 79 - len_msg
        able_size -= 5 # ...
        min_size = able_size / 2
        if able_size % 2 == 0 :
            fname1 = filename[0:min_size-1]
        else :
            fname1 = filename[0:min_size]
        fname2 = filename[len_fname - min_size:]

        fname = '%s ... %s' % (fname1, fname2)
        msg   = '%s' % message

    cprint (fname + ' ', FOREGROUND_GREY)
    cprint (message + '\n', message_color)

def listvirus_callback(ret_virus, ret_getinfo) :
    for name in ret_virus :
        print '%-50s [%s.kmd]' % (name, ret_getinfo['kmd_name'])

#---------------------------------------------------------------------
# scan �ݹ� �Լ�
#---------------------------------------------------------------------
def scan_callback(ret_value) :
    real_name = ret_value['real_filename']
    scan_info = ret_value['scan_info']

    if len(scan_info['deep_filename']) != 0 :
        disp_name = '%s (%s)' % (scan_info['display_filename'], scan_info['deep_filename'])
    else :
        disp_name = '%s' % (scan_info['display_filename'])

    message_color = None

    import kernel
    if ret_value['result'] == True :
        if ret_value['scan_state'] == kernel.INFECTED :
            s = 'infected'
        elif ret_value['scan_state'] == kernel.SUSPECT :
            s = 'Suspect'
        elif ret_value['scan_state'] == kernel.WARNING :
            s = 'Warning'
        else :
            s = 'Unknown'

        vname = ret_value['virus_name']
        message = '%s : %s' % (s, vname)
        message_color = FOREGROUND_RED | FOREGROUND_INTENSITY
    else :
        message = 'ok'
        message_color = FOREGROUND_GREY | FOREGROUND_INTENSITY

    display_line(disp_name, message, message_color = message_color)


def Start_Thread() :
    global g_EngineInit
    g_EngineInit = 0

def End_Thread() :
    global g_EngineInit

    g_EngineInit = 1
    time.sleep(0.1)

def PringLoding(id, msg) :
    global g_EngineInit

    progress = ['\\', '|', '/', '-']

    i = 0
    cprint(msg, FOREGROUND_GREY)

    while g_EngineInit == 0 :
        cprint(progress[i] + '\b', FOREGROUND_GREY)
        i += 1
        i %= 4
        time.sleep(0.1)
    cprint('\r', FOREGROUND_GREY)

#---------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------
def main() :
    global NOCOLOR
    global SIGTOOL
    global g_EngineInit

    kav1 = None

    try :
        # �ɼ� �м�
        options, args = ParserOptions()

        # ��� ���� ���ֱ�
        if options != None :
            if os.name == 'nt' and options.opt_nocolor == True :
                NOCOLOR = True

        # �ΰ� ���
        PrintLogo()

        # �߸��� �ɼ�?
        if options == None :
            PrintUsage()
            PrintOptions()
            return 0

        # Help �ɼ� ����?
        if options.opt_help == True :
            PrintUsage()
            PrintOptions()
            return 0

        # ������Ʈ?
        if options.opt_update == True :
            Update()
            return 0

        # Ű�޹�� ���� ����
        kav = kavcore.Engine() # ���� Ŭ����
        kav.SetPlugins('plugins') # �÷����� ���� ����

        # ���� �ν��Ͻ� ����1
        kav1 = kav.CreateInstance()
        if kav1 == None :
            print
            PrintError('KICOM Anti-Virus Engine CreateInstance')
            # print 'Error : KICOM Anti-Virus Engine CreateInstance'
            return 0

        # ������ ����
        Start_Thread()
        thread.start_new_thread(PringLoding, (0, 'Loading Engine... '))

        # ���� �ʱ�ȭ
        if kav1.init() == False :
            print
            PrintError('KICOM Anti-Virus Engine Init')
            # print 'Error : KICOM Anti-Virus Engine Init'
            raise SystemError

        End_Thread()

        # ���� ������ ���
        c = kav1.getversion()
        msg = '\rLast updated %s UTC\n' % c.ctime()
        cprint(msg, FOREGROUND_GREY)

        # �ε��� �ñ׳��� ���� ���
        msg = 'Signature number: %d' % kav1.getsignum()
        print msg
        print

        # �ɼ��� �����Ѵ�
        if kav1.set_options(options) == False :
            PrintError('KICOM Anti-Virus Engine Options')
            # print 'Error : KICOM Anti-Virus Engine Options'
            raise SystemError

        '''
        # �ε��� ���� ���
        s = kav1.getinfo()
        for i in s :
            print 'Loaded Engine : %s' % i['title']
        print
        '''


        if options.opt_vlist == True : # �Ǽ��ڵ� ����Ʈ ���?
            kav1.listvirus(listvirus_callback)
        else :                         # �Ǽ��ڵ� �˻�
            kav1.set_result()

            # �˻�� Path (���� ��� ����)
            for scan_path in args : # �ɼ��� ������ ù��°�� �˻� ���
                scan_path = os.path.abspath(scan_path)

                if os.path.exists(scan_path) : # ���� Ȥ�� ���ϰ� �����ϴ°�?
                    kav1.scan(scan_path, scan_callback)
                else :
                    PrintError('Invalid path: \'%s\'' % scan_path)
                    # print 'Error: Invalid path: \'%s\'' % scan_path

            # ��� ���
            ret = kav1.get_result()
            print_result(ret)

        kav1.uninit()
    except :
        cprint('\n[', FOREGROUND_GREY)
        cprint('Scan Stop', FOREGROUND_GREY | FOREGROUND_INTENSITY)
        cprint(']\n', FOREGROUND_GREY)

        if kav1 != None :
            kav1.uninit()
        pass

if __name__ == '__main__' :
    main()
