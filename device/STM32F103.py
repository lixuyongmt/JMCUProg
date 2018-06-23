#coding: utf-8

import time

FLASH_KR = 0x40022004
FLASH_SR = 0x4002200C
FLASH_CR = 0x40022010
FLASH_AR = 0x40022014

FLASH_KR_KEY1 = 0X45670123
FLASH_KR_KEY2 = 0XCDEF89AB

FLASH_SR_BUSY = (1 << 0)

FLASH_CR_PWRITE = (1 << 0)
FLASH_CR_PERASE = (1 << 1)  #Page  Erase
FLASH_CR_CERASE = (1 << 2)  #Chip  Erase
FLASH_CR_ESTART = (1 << 6)  #Erase Start
FLASH_CR_LOCK   = (1 << 7)

class STM32F103_MD(object):
    PAGE_SIZE = 1024

    def __init__(self, jlink):
        super(STM32F103_MD, self).__init__()
        
        self.jlink  = jlink

    def unlock(self):
        self.jlink.write_U32(FLASH_KR, FLASH_KR_KEY1)
        self.jlink.write_U32(FLASH_KR, FLASH_KR_KEY2)

    def lock(self):
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) | FLASH_CR_LOCK)

    def wait_ready(self):
        while self.jlink.read_U32(FLASH_SR) & FLASH_SR_BUSY:
            time.sleep(0.1)
    
    def chip_erase(self):
        self.unlock()
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) | FLASH_CR_CERASE)
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) | FLASH_CR_ESTART)
        self.wait_ready()
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) &~FLASH_CR_CERASE)
        self.lock()

    def page_erase(self, count):
        self.unlock()
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) | FLASH_CR_PERASE)
        for i in range(count):
            self.jlink.write_U32(FLASH_AR, 0x08000000 + self.PAGE_SIZE * i)
            self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) | FLASH_CR_ESTART)
            self.wait_ready()
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) &~FLASH_CR_PERASE)
        self.lock()

    def page_write(self, addr, data):
        self.unlock()
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) | FLASH_CR_PWRITE)
        for i in range(self.PAGE_SIZE//2):
            self.jlink.write_U16(addr + i*2, data[i*2] | (data[i*2+1] << 8))
        self.wait_ready()
        self.jlink.write_U32(FLASH_CR, self.jlink.read_U32(FLASH_CR) &~FLASH_CR_PWRITE)
        self.lock()
    
    def chip_write(self, data):
        data = data + [0xFF] * (self.PAGE_SIZE - len(data)%self.PAGE_SIZE)
        n_page = len(data)//self.PAGE_SIZE
        self.page_erase(n_page)
        for i in range(n_page):
            self.page_write(0x08000000 + self.PAGE_SIZE * i, data[self.PAGE_SIZE*i : self.PAGE_SIZE*(i+1)])


class STM32F103_HD(STM32F103_MD):
    PAGE_SIZE = 2048

class STM32F103_LD(STM32F103_MD):
    pass
