# coding=utf-8
#
# Copyright 2014 Sascha Schirra
#
# This file is part of Ropper.
#
# Ropper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ropper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ropper.printer.printer import *
from ropper.loaders.elf import *


class ELFPrinter(FileDataPrinter):

    @classmethod
    def validType(cls):
        return Type.ELF

    def printInformation(self, binary):
        ehdr = binary._binary.elfHeader.header
        data = [(cstr('Class', Color.BLUE), cstr(elf.ELFCLASS[ehdr.e_ident[elf.EI.CLASS]], Color.WHITE)),
                (cstr('Machine', Color.BLUE), cstr(elf.EM[ehdr.e_machine], Color.WHITE)),
                (cstr('Version', Color.BLUE), cstr(ehdr.e_version, Color.WHITE)),
                (cstr('EntryPoint', Color.BLUE), cstr(self._toHex(
                    ehdr.e_entry,binary.arch.addressLength), Color.WHITE)),
                (cstr('ProgramHeader Offset', Color.BLUE), cstr(ehdr.e_phoff, Color.WHITE)),
                (cstr('SectionHeader Offset', Color.BLUE), cstr(ehdr.e_shoff, Color.WHITE)),
                (cstr('Flags', Color.BLUE), cstr(self._toHex(ehdr.e_flags, int(binary.arch.addressLength)), Color.WHITE)),
                (cstr('ELF Header Size', Color.BLUE), cstr(ehdr.e_ehsize, Color.WHITE)),
                (cstr('ProgramHeader Size', Color.BLUE), cstr(ehdr.e_phentsize, Color.WHITE)),
                (cstr('ProgramHeader Number', Color.BLUE), cstr(ehdr.e_phnum, Color.WHITE)),
                (cstr('SectionHeader Size', Color.BLUE), cstr(ehdr.e_shentsize, Color.WHITE)),
                (cstr('SectionHeader Number', Color.BLUE), cstr(ehdr.e_shnum, Color.WHITE))]

        self._printTable('ELF Header', (cstr('Name', Color.LIGHT_GRAY), cstr('Value',Color.LIGHT_GRAY)), data)

    def printSymbols(self, binary):
        for section in binary._binary.sections:
            if section.name in ('.symtab','.dynsym'):  
                data = []
                symbols = section.symbols
                for idx in range(len(symbols)):
                    symbol = symbols[idx]
                    data.append((cstr(idx, Color.BLUE),
                                cstr(elf.STT[symbol.type], Color.GREEN),
                                cstr(elf.STB[symbol.bind], Color.LIGHT_GRAY),
                                cstr(symbol.name, Color.WHITE)))
                self._printTable('Symbols from %s' % section.name,
                                (cstr('Nr', Color.LIGHT_GRAY),
                                    cstr('Type', Color.LIGHT_GRAY),
                                    cstr('Bind', Color.LIGHT_GRAY),
                                    cstr('Name', Color.LIGHT_GRAY)),
                                data)

    def printSections(self, binary):
        data = []
        for index in range(len(binary._binary.sections)):
            data.append((cstr('[%.2d]' % index, Color.BLUE),
                        cstr(binary._binary.sections[index].name, Color.WHITE),
                        cstr(elf.SHT[binary._binary.sections[index].header.sh_type], Color.YELLOW)))

        self._printTable('Sections',
                        (cstr('Nr', Color.LIGHT_GRAY),
                            cstr('Name', Color.LIGHT_GRAY),
                            cstr('Type', Color.LIGHT_GRAY)),
                        data)

    def printSegments(self, elffile):
        phdrs = elffile._binary.segments

        data = []
        for phdrData in phdrs:
            phdr = phdrData.header
            ptype = 'Not available'
            if phdr.p_type in elf.PT:
                ptype = elf.PT[phdr.p_type]
            data.append((cstr(ptype, Color.BLUE),
                        cstr(self._toHex(phdr.p_offset), Color.WHITE),
                        cstr(self._toHex(phdr.p_paddr, int(elffile.arch.addressLength)), Color.LIGHT_GRAY),
                        cstr(self._toHex(phdr.p_filesz), Color.WHITE),
                        cstr(self._toHex(phdr.p_memsz), Color.LIGHT_GRAY),
                        cstr(elf.PF.shortString(phdr.p_flags), (Color.GREEN if phdr.p_flags & elf.PF.EXEC == 0 else Color.RED) )))

        self._printTable('Segments',
                        (cstr('Type', Color.LIGHT_GRAY),
                            cstr('Offset', Color.LIGHT_GRAY),
                            cstr('VAddress', Color.LIGHT_GRAY),
                            cstr('FileSize', Color.LIGHT_GRAY),
                            cstr('MemSize', Color.LIGHT_GRAY),
                            cstr('Flags', Color.LIGHT_GRAY)),
                        data)

    def printEntryPoint(self, binary):
        self._printLine(self._toHex(binary.entryPoint, binary.arch.addressLength))

    def printImageBase(self, binary):
        self._printLine(
            self._toHex(binary.imageBase, binary.arch.addressLength))

    def printArchitecture(self, binary):
        self._printLine(str(binary.arch))

    def printFileType(self, binary):
        self._printLine(str(binary.type))

    def printImports(self, elffile):
        printed = False
        for section in elffile._binary.sections:
            if section.header.sh_type in (elf.SHT.REL,elf.SHT.RELA):  
                relocs = section.relocations
                data = []

                for reloc in relocs:
                    data.append((cstr(self._toHex(reloc.header.r_offset, elffile.arch.addressLength), Color.BLUE),
                                cstr(elf.R_386[reloc.type], Color.YELLOW),
                                cstr(reloc.symbol.name, Color.WHITE)))

                self._printTable('Relocation section: %s' % section,
                                (cstr('Offset', Color.LIGHT_GRAY),
                                    cstr('Type', Color.LIGHT_GRAY),
                                    cstr('Name', Color.LIGHT_GRAY)),
                                data)
                printed = True

        if not printed:
            self._printLine('no imorts!')
