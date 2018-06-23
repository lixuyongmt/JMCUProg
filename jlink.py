#coding: utf-8

import ctypes


class JLinkException(Exception): pass

class JLink(object):
    def __init__(self, dllpath):
        self.jlink = ctypes.cdll.LoadLibrary(dllpath)
        self.tif_select(1)
        self.set_speed(1000)
        self.reset()

    def check_err(fn):
        def checked_transaction(self,*args):
            self.jlink.JLINK_ClrError()
            ret = fn(self, *args)
            errno = self.jlink.JLINK_HasError()
            if errno:
                raise JLinkException(errno)
            return ret
        return checked_transaction

    @check_err
    def tif_select(self, tif): return self.jlink.JLINKARM_TIF_Select(tif)

    @check_err
    def set_speed(self, khz): return self.jlink.JLINKARM_SetSpeed(khz)

    @check_err
    def reset(self): return self.jlink.JLINKARM_Reset()

    @check_err
    def halt(self): return self.jlink.JLINKARM_Halt()

    @check_err
    def clear_tck(self): return self.jlink.JLINKARM_ClrTCK()

    @check_err
    def clear_tms(self): return self.jlink.JLINKARM_ClrTMS()

    @check_err
    def set_tms(self): return self.jlink.JLINKARM_SetTMS()

    @check_err
    def read_reg(self,r): return self.jlink.JLINKARM_ReadReg(r)

    @check_err
    def write_reg(self,r,val): return self.jlink.JLINKARM_WriteReg(r,val)

    @check_err
    def write_U32(self,r,val): return self.jlink.JLINKARM_WriteU32(r,val)

    @check_err
    def write_U16(self,r,val): return self.jlink.JLINKARM_WriteU16(r,val)

    @check_err                       
    def open(self): return self.jlink.JLINKARM_Open()

    @check_err                       
    def close(self): return self.jlink.JLINKARM_Close()

    @check_err                       
    def go(self): return self.jlink.JLINKARM_Go()

    @check_err
    def write_mem(self, startaddress, data):
        buf=ctypes.create_string_buffer(data)
        return self.jlink.JLINKARM_WriteMem(startaddress,len(data),buf)

    @check_err
    def read_mem(self, startaddress, length):
        buf=ctypes.create_string_buffer(length)
        ret=self.jlink.JLINKARM_ReadMem(startaddress,length, buf)
        return buf,ret

    @check_err
    def read_mem_U32(self, startaddress, count):
        buftype=ctypes.c_uint32 * int(count)
        buf=buftype()
        ret=self.jlink.JLINKARM_ReadMemU32(startaddress, count, buf, 0)
        return buf,ret

    def read_U32(self, startaddress):
        buf, ret = self.read_mem_U32(startaddress, 1)
        return buf[0]
