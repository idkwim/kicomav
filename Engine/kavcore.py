# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import zlib
import zipfile
import hashlib
import StringIO
import marshal
import imp
import sys
import os
import types
import mmap
import glob
import datetime
import time
import struct

#---------------------------------------------------------------------
# Engine Ŭ����
#---------------------------------------------------------------------
class Engine :
    def __init__(self) :
        self.kmd_list = []
        self.mod_list = []
        self.plugins  = None # �÷����� ���� ��ġ

    # plugins ������ kmd ����� �ε��Ѵ�.
    def SetPlugins(self, plugins) :
        ret = False

        self.plugins = plugins
        self.ckmd = KMD()

        try :
            if len(self.kmd_list) == 0 : # �켱���� list ������ ���ٸ�
                # kmd �ε� �켱���� ����Ʈ�� ���� kmd ���Ͽ��� ����Ʈ Ȯ��
                self.kmd_list = self.ckmd.GetList(plugins) # kicom.kmd ���� �ε�
                if len(self.kmd_list) == 0 :      # ��� ���� ������ ����
                    raise SystemError

            # kmd �ε� �켱���� ����Ʈ ������ ���� �ε�
            if len(self.mod_list) == 0 :
                self.mod_list = self.ckmd.Import(plugins, self.kmd_list)

            ret = True
        except :
            pass

        return ret

    def CreateInstance(self) :
        try :
            sys.modules['kernel'] # kernel.kmd�� ������ �־�� ��
            ei = EngineInstance(self.plugins)
            ret = ei.SetModuleList(self.ckmd, self.mod_list)

            if ret == 0 :
                return ei
        except :
            pass

        return None

#---------------------------------------------------------------------
# EngineInstance Ŭ����
#---------------------------------------------------------------------
class EngineInstance :
    def __init__(self, plugins) :
        self.modules        = []
        self.KMD_AntiVirus  = []
        self.KMD_Decompress = []
        self.KMD_FileFormat = []
        self.plugins        = plugins
        self.last_update    = None

    def SetModuleList(self, ckmd, mod_list) :
        try :
            for m in mod_list :
                # ���� �ε� �Ǿ����� ��� ���� ����Ʈ�� �߰�
                mod = ckmd.ExecKavMain(m)
                if mod != None :
                    self.modules.append(mod)

            # �ε��� ����� �ϳ��� ������ ����
            if len(self.modules) == 0 :
                raise SystemError

            # ���� �ֽ� ���� ��¥�� �ð��� �˾ƿ�
            self.last_update = ckmd.GetLastUpdate() 
        except :
            return 1

        return 0

    #-----------------------------------------------------------------
    # init(self)
    # Ű�޹�� ������ �ʱ�ȭ �Ѵ�.
    # ���ϰ� : ���� ���� (True, False)
    #-----------------------------------------------------------------
    def init(self) :
        try :
            # ��� ��� ���� ����� init ��� �Լ� ȣ��
            for mod in self.modules :
                if dir(mod).count('init') != 0 : # API ����
                    ret_init = mod.init(self.plugins) # ȣ��
                    if ret_init != 0 :
                        raise SystemError
        except :
            return False

        self.options = {}
        self.set_options() # �ɼ� �ʱ�ȭ

        self.set_result() # ��� �ʱ�ȭ
        return True

    #-----------------------------------------------------------------
    # uninit(self)
    # Ű�޹�� ������ ����ȭ �Ѵ�.
    #-----------------------------------------------------------------
    def uninit(self) :
        # ��� ���� ����� uninit ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('uninit') != 0 : # API ����
                ret_uninit = mod.uninit()

    #-----------------------------------------------------------------
    # set_result(self)
    # Ű�޹�� ������ �˻� ����� �ʱ�ȭ �Ѵ�.
    #-----------------------------------------------------------------
    def set_result(self) :
        self.result = {}
        self.identified_virus = [] # ����ũ�� �Ǽ��ڵ� ������ ���ϱ� ���� ���

        self.result['Folders']            = 0
        self.result['Files']              = 0
        self.result['Packed']             = 0
        self.result['Infected_files']     = 0
        self.result['Suspect_files']      = 0
        self.result['Warnings']           = 0
        self.result['Identified_viruses'] = 0
        self.result['IO_errors']          = 0

        return True

    #-----------------------------------------------------------------
    # get_result(self)
    # Ű�޹�� ������ �˻� ����� ��´�.
    #-----------------------------------------------------------------
    def get_result(self) :
        return self.result

    #-----------------------------------------------------------------
    # set_options(self, options)
    # Ű�޹�� ������ �ɼ��� �����Ѵ�.
    #-----------------------------------------------------------------
    def set_options(self, options = None) :
        if options == None :
            self.options['opt_files']   = True
            self.options['opt_boot']    = False
            self.options['opt_arc']     = False
            self.options['opt_mail']    = False
            self.options['opt_nopack']  = False
            self.options['opt_nohed']   = False
            self.options['opt_xcl']     = False
            self.options['opt_log']     = False
            self.options['opt_cd']      = False
            self.options['opt_fixed']   = False
            self.options['opt_floppy']  = False
            self.options['opt_list']    = False
            self.options['opt_prog']    = False
            self.options['opt_app']     = False
            self.options['opt_infp']    = False
            self.options['opt_susp']    = False
            self.options['opt_nor']     = False
            self.options['opt_prompt']  = False
            self.options['opt_info']    = False
            self.options['opt_nowarn']  = False
            self.options['opt_vlist']   = False
            self.options['opt_dis']     = False
            self.options['opt_copy']    = False
            self.options['opt_copys']   = False
            self.options['opt_del']     = False
            self.options['opt_noclean'] = False
            self.options['opt_move']    = False
            self.options['opt_moves']   = False
            self.options['opt_ren']     = False
            self.options['opt_infext']  = False
            self.options['opt_alev']    = False
            self.options['opt_flev']    = False
            self.options['opt_update']  = False
            self.options['opt_sigtool'] = False
            # self.options['opt_help']  = False
        else :
            self.options['opt_files']   = options.opt_files
            self.options['opt_boot']    = options.opt_boot
            self.options['opt_arc']     = options.opt_arc
            self.options['opt_mail']    = options.opt_mail
            self.options['opt_nopack']  = options.opt_nopack
            self.options['opt_nohed']   = options.opt_nohed
            self.options['opt_xcl']     = options.opt_xcl
            self.options['opt_log']     = options.opt_log
            self.options['opt_cd']      = options.opt_cd
            self.options['opt_fixed']   = options.opt_fixed
            self.options['opt_floppy']  = options.opt_floppy
            self.options['opt_list']    = options.opt_list
            self.options['opt_prog']    = options.opt_prog
            self.options['opt_app']     = options.opt_app
            self.options['opt_infp']    = options.opt_infp
            self.options['opt_susp']    = options.opt_susp
            self.options['opt_nor']     = options.opt_nor
            self.options['opt_prompt']  = options.opt_prompt
            self.options['opt_info']    = options.opt_info
            self.options['opt_nowarn']  = options.opt_nowarn
            self.options['opt_vlist']   = options.opt_vlist
            self.options['opt_dis']     = options.opt_dis
            self.options['opt_copy']    = options.opt_copy
            self.options['opt_copys']   = options.opt_copys
            self.options['opt_del']     = options.opt_del
            self.options['opt_noclean'] = options.opt_noclean
            self.options['opt_move']    = options.opt_move
            self.options['opt_moves']   = options.opt_moves
            self.options['opt_ren']     = options.opt_ren
            self.options['opt_infext']  = options.opt_infext
            self.options['opt_alev']    = options.opt_alev
            self.options['opt_flev']    = options.opt_flev
            self.options['opt_update']  = options.opt_update
            self.options['opt_sigtool'] = options.opt_sigtool
            # self.options['opt_help']  = # options.opt_help
        return True

    #-----------------------------------------------------------------
    # get_options(self)
    # Ű�޹�� ������ �ɼ��� �����Ѵ�.
    #-----------------------------------------------------------------
    def get_options(self) :
        return self.options

    #-----------------------------------------------------------------
    # scan(self, filename)
    # Ű�޹�� ������ �Ǽ��ڵ带 �����Ѵ�.
    #-----------------------------------------------------------------
    def scan(self, filename, *callback) :
        del_master_file = ''
        del_temp_list = [] # �˻縦 ���� �ӽ÷� ������ ���ϵ�
        ret_value = {
            'result':False, 'engine_id':-1, 'virus_name':'',
            'virus_id':-1, 'scan_state':None, 'scan_info':None
        }

        # �������� Ȯ��
        argc = len(callback)

        if argc == 0 : # ���ڰ� ������
            cb = None
        elif argc == 1 : # callback �Լ��� �����ϴ��� üũ
            cb = callback[0]
        else : # ���ڰ� �ʹ� ������ ����
            return -1

        # 1. �˻� ��� ����Ʈ�� ������ ���
        file_scan_list = [] # �˻� ��� ������ ��� ����
        file_info = {}  # ���� �Ѱ��� ����

        # �˻� ��� ����Ʈ���� �˻� ��� ���� �̸��� ��¿� �̸��� ���ÿ� ����
        file_info['is_arc'] = False # ���� ����
        file_info['arc_engine_name'] = -1 # ���� ���� ���� ���� ID
        file_info['arc_filename'] = '' # ���� ���� ����
        file_info['arc_in_name'] = '' #�������� ��� ����
        file_info['real_filename'] = filename # �˻� ��� ����
        file_info['deep_filename'] = ''  # ���� ������ ���θ� ǥ���ϱ� ���� ���ϸ�
        file_info['display_filename'] = filename # ��¿�
        file_info['signature'] = self.options['opt_sigtool'] # �ñ׳��� ������ ��û ����
        file_scan_list.append(file_info)

        # �˻� ��� ����Ʈ�� ������ ������...
        while len(file_scan_list) != 0 :
            # 1. �˻� ��� ����Ʈ���� ���� �ϳ� ������
            scan_file = file_scan_list.pop(0)

            # �ӽ� ���� ����
            if del_master_file != scan_file['display_filename'] :
                if len(del_temp_list) != 0 :
                    self.__del_temp_file__(del_temp_list)
                    del_temp_list = []
                    del_master_file = scan_file['display_filename']

            real_name = scan_file['real_filename']

            ret_value['real_filename'] = real_name    # ���� ���� �̸�

            # ������ ���� ���ϸ���Ʈ�� �˻� ��� ����Ʈ�� ���
            if os.path.isdir(real_name) == True :
                self.result['Folders'] += 1 # ���� �� ����
                ret_value['result'] = False # �����̹Ƿ� ���̷��� ����
                ret_value['scan_info']  = scan_file

                if self.options['opt_list'] == True : # ��� ����Ʈ ����ΰ�?
                    if cb != None :
                        cb(ret_value)

                # ���� ���� ó���� ���� ���� �ڿ� �Ѵ� os.sep�� �켱 ����
                if real_name[len(real_name)-1] == os.sep :
                    real_name = real_name[:len(real_name)-1]

                # ���� ���� ���ϵ��� �˻��� ����Ʈ�� �߰�
                flist = glob.glob(real_name + os.sep + '*')
                for rfname in flist :
                    tmp_info = {}

                    tmp_info['is_arc'] = False # ���� ����
                    tmp_info['arc_engine_name'] = -1 # ���� ���� ���� ���� ID
                    tmp_info['arc_filename'] = '' # ���� ���� ����
                    tmp_info['arc_in_name'] = '' #�������� ��� ����
                    tmp_info['real_filename'] = rfname # �˻� ��� ����
                    tmp_info['deep_filename'] = ''  # ���� ������ ���θ� ǥ���ϱ� ���� ���ϸ�
                    tmp_info['display_filename'] = rfname # ��¿�
                    tmp_info['signature'] = self.options['opt_sigtool'] # �ñ׳��� ������ ��û ����
                    file_scan_list.append(tmp_info)

            else : # �����̸� �˻�
                self.result['Files'] += 1 # ���� �� ����

                # ����� �����̸� �����ϱ�
                ret = self.__unarc_file__(scan_file)
                if ret != None :
                    ret['signature'] = self.options['opt_sigtool']
                    if ret['is_arc'] == True : # ������ Ǯ���������� ���� ��� ���
                        del_master_file = ret['display_filename']
                        del_temp_list.append(ret['real_filename'])
                    scan_file = ret

                # 2. ���� �м�
                ff = self.__get_fileformat__(scan_file)

                '''
                print '-' * 79
                for k in scan_file.keys() :
                    print '%-16s : %s' % (k, scan_file[k])
                print '-' * 79
                '''

                # 3. ���Ϸ� �Ǽ��ڵ� �˻�
                ret = self.__scan_file__(scan_file, ff)

                #    �Ǽ��ڵ� �߰��̸� �ݹ� ȣ�� �Ǵ� �˻� ���ϰ� ���� ����
                ret_value['result']     = ret['result'    ] # ���̷��� �߰� ����
                ret_value['engine_id']  = ret['engine_id' ] # ���� ID
                ret_value['virus_name'] = ret['virus_name'] # ���̷��� �̸�
                ret_value['scan_state'] = ret['scan_state'] # ���̷��� �˻� ����
                ret_value['virus_id']   = ret['virus_id'  ] # ���̷��� ID
                ret_value['scan_info']  = scan_file

                if self.options['opt_list'] == True : # ��� ����Ʈ ����ΰ�?
                    if cb != None :
                        cb(ret_value)
                else : # �ƴ϶�� ���̷����� �͸� ���
                    if ret_value['result'] == True :
                        if cb != None :
                            cb(ret_value)

                # �̹� �ش� ������ ���̷������ �Ǹ�Ǿ��ٸ�
                # �� ������ ���������ؼ� ���θ� �� �ʿ�� ����.
                if ret_value['result'] == False : # ���� ���̷����� �ƴѰ�츸 �˻�
                    # 4. ���� �����̸� �˻��� ����Ʈ�� �߰�
                    try :
                        scan_file['real_filename'] = scan_file['temp_filename']
                    except :
                        pass
                    arc_file_list = self.__get_list_arc__(scan_file, ff)
                    if len(arc_file_list) != 0 :
                        file_scan_list = arc_file_list + file_scan_list

        # �˻� ������ �۾�(�ӽ� ���� ����)
        if len(del_temp_list) != 0 :
            self.__del_temp_file__(del_temp_list)

        return 0 # ���������� �˻� ����


    def __get_list_arc__(self, scan_file_struct, format) :
        import kernel

        file_scan_list = [] # �˻� ��� ������ ��� ����

        # ���� ���� ����� arclist ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('arclist') != 0 : # API ����
                if self.options['opt_arc'] == True : # ���� �˻� �ɼ��� ������ ��� ȣ��
                    file_scan_list = mod.arclist(scan_file_struct, format) 
                else : # ���� �˻� �ɼ��� ���ٸ� ������ ȣ��
                    if dir(mod).count('getinfo') != 0 : # API ����
                        ret_getinfo = mod.getinfo()
                        try :
                            if ret_getinfo['engine_type'] != kernel.ARCHIVE_ENGINE : 
                                # ���� ������ �ƴϾ ȣ��
                                file_scan_list = mod.arclist(scan_file_struct, format)
                        except :
                            # entine_type�� ��� ȣ��
                            file_scan_list = mod.arclist(scan_file_struct, format)

                if len(file_scan_list) != 0 : # ������ Ǯ������ ����
                    self.result['Packed'] += 1
                    break

        return file_scan_list


    def __unarc_file__(self, scan_file_struct) :
        try :
            if scan_file_struct['is_arc'] == True :
                # ���� ���� ����� arclist ��� �Լ� ȣ��
                for mod in self.modules :
                    if dir(mod).count('unarc') != 0 : # API ����
                        rname_struct = mod.unarc(scan_file_struct)
                        if rname_struct != None : # ������ Ǯ������ ����
                            break

                return rname_struct
        except :
            pass

        return scan_file_struct


    def __del_temp_file__(self, dellist) :
        for file in dellist :
            os.remove(file)


    def __scan_file__(self, scan_file_struct, format) :
        ret_value = {
            'result':False, 'engine_id':-1, 'virus_name':'',
            'virus_id':-1, 'scan_state':None, 'scan_info':None
        }

        filename = scan_file_struct['real_filename']

        try :
            fsize = os.path.getsize(filename)
            if fsize == 0 : # ���� ũ�Ⱑ 0�� ��� �˻� ����
                raise SystemError

            fp = open(filename, 'rb')
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)

            # ��� ���� ����� scan ��� �Լ� ȣ��
            for mod in self.modules :
                if dir(mod).count('scan') != 0 : # API ����
                    ret_value = mod.scan(mm, scan_file_struct, format)
                    ret   = ret_value['result']     # ���̷��� �߰� ����
                    vname = ret_value['virus_name'] # ���̷��� �̸�

                    if ret == True : # �Ǽ��ڵ� �߰��̸� �˻� �ߴ�
                        break

            mm.close()
            fp.close()

            if ret == True :
                import kernel
                if ret_value['scan_state'] == kernel.INFECTED :
                    self.result['Infected_files'] += 1 # �Ǽ��ڵ� �߰� �� ����
                elif ret_value['scan_state'] == kernel.SUSPECT :
                    self.result['Suspect_files'] += 1 # �Ǽ��ڵ� �߰� �� ����
                elif ret_value['scan_state'] == kernel.WARNING :
                    self.result['Warnings'] += 1 # �Ǽ��ڵ� �߰� �� ����

                # ������ �Ǽ��ڵ� �߰� ���� üũ
                if self.identified_virus.count(vname) == 0 :
                    self.identified_virus.append(vname)
                    self.result['Identified_viruses'] += 1

                ret_value['engine_id'] = self.modules.index(mod) # �߰ߵ� ���� ID
                return ret_value
        except :
            self.result['IO_errors'] += 1 # ���� �߻� �� ����
            pass

        ret_value['engine_id'] = -1
        return ret_value


    def __get_fileformat__(self, scan_file_struct) :
        ret = {}
        filename = scan_file_struct['real_filename']

        try :
            fp = open(filename, 'rb')
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)

            # ��� ���� ����� scan ��� �Լ� ȣ��
            for mod in self.modules :
                if dir(mod).count('format') != 0 : # API ����
                    ff = mod.format(mm, filename)
                    if ff != None :
                        ret.update(ff)

            mm.close()
            fp.close()
        except :
            pass

        return ret

    #-----------------------------------------------------------------
    # disinfect(self, filename, modID, virusID)
    # Ű�޹�� ������ �Ǽ��ڵ带 ġ���Ѵ�.
    #-----------------------------------------------------------------
    def disinfect(self, filename, modID, virusID) :
        ret_disinfect = False

        try :
            mod = self.modules[modID]
            if dir(mod).count('disinfect') != 0 : # API ����
                ret_disinfect = mod.disinfect(filename, virusID)

        except :
            pass

        return ret_disinfect

    #-----------------------------------------------------------------
    # getinfo(self)
    # Ű�޹�� ������ �� ���� ����� ������ �����Ѵ�.
    #-----------------------------------------------------------------
    def getinfo(self) :
        ret = []

        # ��� ���� ����� getinfo ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('getinfo') != 0 : # API ����
                ret_getinfo = mod.getinfo()
                ret.append(ret_getinfo)

        return ret

    #-----------------------------------------------------------------
    # listvirus(self, *callback)
    # Ű�޹�� ������ �����ϴ� �Ǽ��ڵ� �̸��� �����Ѵ�.
    #-----------------------------------------------------------------
    def listvirus(self, *callback) :
        # �������� Ȯ��
        argc = len(callback)

        if argc == 0 : # ���ڰ� ������
            cb = None
        elif argc == 1 : # callback �Լ��� �����ϴ��� üũ
            cb = callback[0]
        else : # ���ڰ� �ʹ� ������ ����
            return []

        # ��� ���� ����� listvirus ��� �Լ� ȣ��
        ret = []

        for mod in self.modules :
            if dir(mod).count('listvirus') != 0 : # API ����
                ret_listvirus = mod.listvirus()

                # callback �Լ��� �ִٸ�
                # callback �Լ� ȣ��
                if type(cb) is types.FunctionType :
                    # �ش� kmd�� ������ �Բ� ����
                    ret_getinfo = None
                    if dir(mod).count('getinfo') != 0 :
                        ret_getinfo = mod.getinfo()
                    cb(ret_listvirus, ret_getinfo)
                # callback �Լ��� ���ٸ�
                # �Ǽ��ڵ� �̸��� ����Ʈ�� ����
                else :
                    ret += ret_listvirus

        # callback �Լ� ������ ������ �Ǽ��ڵ� ����Ʈ�� ����
        if argc == 0 :
            return ret

    def getversion(self) :
        t = CTIME()

        # self.last_update���� ���� ���� ��¥�� �ð� ������ ����
        update_date = self.last_update 

        # �� ��� ���� ����� ���� ������ ��¥�� �ð� ������ ���ؼ�
        # �ֽ� ������ ��¥�� �ð������� ����ؾ� ��

        # ��� ���� ����� getinfo ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('getinfo') != 0 : # API ����
                ret_getinfo = mod.getinfo()

                try :
                    pattern_date = ret_getinfo['date']
                    pattern_time = ret_getinfo['time']

                    d_y, d_m, d_d = t.GetDate(pattern_date)
                    t_h, t_m, t_s = t.GetTime(pattern_time)

                    t_datetime = datetime.datetime(d_y, d_m, d_d, t_h, t_m, t_s)

                    # �ֽ� ��¥�� ����

                    if update_date < t_datetime :
                        update_date = t_datetime
                except :
                    pass

        return update_date

    def getsignum(self) :
        sig_num = 0

        # ��� ���� ����� getinfo ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('getinfo') != 0 : # API ����
                ret_getinfo = mod.getinfo()

                try :
                    pattern_signum = ret_getinfo['sig_num']
                    sig_num += pattern_signum
                except :
                    pass

        return sig_num

class CTIME :
    def GetDate(self, t) :
        t_y = 0xFE00
        t_m = 0x01E0
        t_d = 0x001F

        y = (t & t_y) >> 9
        y += 1980
        m = (t & t_m) >> 5
        d = (t & t_d)

        # return '%04d-%02d-%02d' % (y, m, d)
        return (y, m, d)

    def GetTime(self, t) :
        t_h = 0xF800
        t_m = 0x07E0
        t_s = 0x001F

        h = (t & t_h) >> 11
        m = (t & t_m) >> 5
        s = (t & t_s) * 2

        # return '%02d:%02d:%02d' % (h, m, s)
        return (h, m, s)

#---------------------------------------------------------------------
# KMD Ŭ����
#---------------------------------------------------------------------
class KMD :
    def __init__(self) :
        self.max_datetime = datetime.datetime(1980, 1, 1, 0, 0, 0, 0)

    def GetLastUpdate(self) :
        return self.max_datetime

    def GetList(self, plugins) :
        kmd_list = []

        try :
            # kicom.kmd ������ ��ȣȭ
            ret, buf = self.Decrypt(plugins + os.sep + 'kicom.kmd')

            if ret == True : # ����
                msg = StringIO.StringIO(buf) # ���� IO �غ�

                while 1 :
                    # ���� �� ���� �о� ����Ű ����
                    line = msg.readline().strip()
                    if line.find('.kmd') != -1 : # kmd Ȯ���ڰ� �����Ѵٸ�
                        kmd_list.append(line) # kmd ���� ����Ʈ�� �߰�
                    else :
                        break
        except :
            pass

        return kmd_list # kmd ���� ����Ʈ ����

    def Decrypt(self, fname) :
        t = CTIME()
        header_length = 8
        hash_length = 0x40

        try : # ���ܰ� �߻��� ���ɼ��� ���� ó��
            fp = open(fname, 'rb') # kmd ���� �б�
            buf = fp.read()
            fp.close()

            f_hash = buf[len(buf)-hash_length:] # ���� ���ʿ��� MD5 �ؽ� �� �и�

            hash = hashlib.sha256()

            val_5hash = buf[0:len(buf)-hash_length] # ���� ���� hash_lengthByte�� ������ ������ ����
            for i in range(3): # MD5 �ؽ� ���� 3�� �������� ���ϱ�
                hash.update(val_5hash)
                val_5hash = hash.hexdigest()

            if f_hash != val_5hash:
                return False, '' # ����

            buf2 = buf[header_length:len(buf)-hash_length] # KAVM ��� ����

            buf3 =""
            for i in range(len(buf2)):  # buf2 ũ�⸸ŭ...
                c = ord(buf2[i]) ^ 0xFF #��0xFF�� XOR ��ȣȭ �Ѵ�
                buf3 += chr(c)

            buf4 = zlib.decompress(buf3) # ���� ����

            # �ֱ� ��¥ ���ϱ�
            kmd_date = buf[4:6]
            kmd_time = buf[6:8]

            d_y, d_m, d_d = t.GetDate(struct.unpack('<H', kmd_date)[0])
            t_h, t_m, t_s = t.GetTime(struct.unpack('<H', kmd_time)[0])
            t_datetime = datetime.datetime(d_y, d_m, d_d, t_h, t_m, t_s)

            if self.max_datetime < t_datetime :
                self.max_datetime = t_datetime

            return True, buf4 # kmd ��ȣȭ ���� �׸��� ��ȣȭ�� ���� ����
        except : # ���� �߻�
            return False, '' # ����

    def Import(self, plugins, kmd_list) :
        mod_list = []

        for kmd in kmd_list :
            ret_kmd, buf = self.Decrypt(plugins + os.sep + kmd)

            if ret_kmd == True :
                ret_imp, mod = self.LoadModule(kmd.split('.')[0], buf)
                if ret_imp == True :
                    mod_list.append(mod)

        return mod_list

    def LoadModule(self, kmd_name, buf) :
        try :
            code = marshal.loads(buf[8:]) # ���۸� ������ ������ ����ȭ �� ���ڿ��� ��ȯ
            module = imp.new_module(kmd_name) # ���ο� ��� ����
            exec(code, module.__dict__) # ����ȭ �� ���ڿ��� �������Ͽ� ���� ����
            sys.modules[kmd_name] = module # �������� ��밡���ϰ� ���
            return True, module
        except :
            return False, None

    def ExecKavMain(self, module) :
        obj = None

        # �ε��� ��⿡�� KavMain�� �ִ��� �˻�
        # KavMain�� �߰ߵǾ����� Ŭ������ �ν��Ͻ� ����
        if dir(module).count('KavMain') != 0 :
            obj = module.KavMain()

        # ������ �ν��Ͻ��� ���ٸ� ���� �ε��� ����� ���
        if obj == None :
            # �ε� ���
            del sys.modules[kmd_name]
            del module

        return obj # ������ �ν��Ͻ� ����

#---------------------------------------------------------------------
# TEST
#---------------------------------------------------------------------
'''
def cb(list_vir) :
    for vir in list_vir :
        print vir

# ���� Ŭ����
kav = Engine()
kav.SetPlugins('plugins') # �÷����� ���� ����

print '----------------------------'
# ���� �ν��Ͻ� ����1
kav1 = kav.CreateInstance()
if kav1 == None :
    print 'Error : KICOM Anti-Virus Engine CreateInstance1'
else :
    print kav1

# ���� �ν��Ͻ� ����2
kav2 = kav.CreateInstance()
if kav2 == None :
    print 'Error : KICOM Anti-Virus Engine CreateInstance2'
else :
    print kav2

print '----------------------------'
print kav1.init()
print kav2.init()
print '----------------------------'
s = kav1.getinfo()
for i in s :
    print i['title']
print '----------------------------'
kav1.listvirus(cb)
print '----------------------------'
print kav1.scan('dummy.txt')
print kav1.scan('eicar.txt')
print kav1.scan('kavcore.py')
print '----------------------------'
kav1.uninit()
kav2.uninit()
'''