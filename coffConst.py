"""
Windows specific constants for coff files grabbed from from winnt.h
appox. line # 6064
"""

class SymbolValues:
    SYM_UNDEFINED = 0
    SYM_ABSOLUTE = -1
    SYM_DEBUG = -2
    SYM_SECTION_MAX = 0xFEFF

    NAME = {SYM_UNDEFINED:"SYM_UNDEFINED",
            SYM_ABSOLUTE:"SYM_ABSOLUTE",
            SYM_DEBUG:"SYM_DEBUG",
            SYM_SECTION_MAX:"SYM_SECTION_MAX"}

class SymbolTypes:
    NULL = 0x0
    VOID = 0x1
    CHAR = 0x2
    SHORT = 0x3
    INT = 0x4
    LONG = 0x5
    FLOAT = 0x6
    DOUBLE = 0x7
    STRUCT = 0x8
    UNION = 0x9
    ENUM = 0xA
    MOE = 0xB # Member of enum
    BYTE = 0xC
    WORD = 0xD
    UINT = 0xE
    DWORD = 0xF
    PCODE = 0x8000

    NAME = {NULL:"NULL",
            VOID:"VOID",
            CHAR:"CHAR",
            SHORT:"SHORT",
            INT:"INT",
            LONG:"LONG",
            FLOAT:"FLOAT",
            DOUBLE:"DOUBLE",
            STRUCT:"STRUCT",
            UNION:"UNION",
            ENUM:"ENUM",
            MOE:"MOE",
            BYTE:"BYTE",
            WORD:"WORD",
            UINT:"UINT",
            DWORD:"DWORD",
            PCODE:"PCODE"}
    
class SymbolDerivedType:
    NULL = 0x0
    POINTER = 0x1
    FUNCTION = 0x2
    ARRAY = 0x3

    NAME = {NULL:"NULL",
            POINTER:"POINTER",
            FUNCTION:"FUNCTION",
            ARRAY:"ARRAY"}

class SymbolClass:
    END_OF_FUNCTION = -1
    NULL = 0x0
    AUTOMATIC = 0x1
    EXTERNAL = 0x2
    STATIC = 0x3
    REGISTER = 0x4
    EXTERNAL_DEF = 0x5
    LABEL = 0x6
    UNDEFINED_LABEL = 0x7
    MEMBER_OF_STRUCT = 0x8
    ARGUMENT = 0x9
    STRUCT_TAB = 0xA
    MEMBER_OF_UNION = 0xB
    UNION_TAG = 0xC
    TYPE_DEFINITION = 0xD
    UNDEFINED_STATIC = 0xE
    ENUM_TAG = 0xF
    MEMBER_OF_ENUM = 0x10
    REGISTER_PARAM = 0x11
    BIT_FIELD = 0x12

    FAR_EXTERNAL =0x44
    
    CLASS_BLOCK = 0x64
    CLASS_FUNCTION = 0x65
    CLASS_END_OF_STRUCT = 0x66
    CLASS_FILE = 0x67
    CLASS_SECTION = 0x68
    CLASS_WEAK_EXTERNAL = 0x69
    CLASS_CLR_TOKEN = 0x6B

    NAME = {END_OF_FUNCTION:"END_OF_FUNCTION",
            NULL:"NULL",
            AUTOMATIC:"AUTOMATIC",
            EXTERNAL:"EXTERNAL",
            STATIC:"STATIC",
            REGISTER:"REGISTER",
            EXTERNAL_DEF:"EXTERNAL_DEF",
            LABEL:"LABEL",
            UNDEFINED_LABEL:"UNDEFINED_LABEL",
            MEMBER_OF_STRUCT:"MEMBER_OF_STRUCT",
            ARGUMENT:"ARGUMENT",
            STRUCT_TAB:"STRUCT_TAB",
            MEMBER_OF_UNION:"MEMBER_OF_UNION",
            UNION_TAG:"UNION_TAG",
            TYPE_DEFINITION:"TYPE_DEFINITION",
            UNDEFINED_STATIC:"UNDEFINED_STATIC",
            ENUM_TAG:"ENUM_TAG",
            MEMBER_OF_ENUM:"MEMBER_OF_ENUM",
            REGISTER_PARAM:"REGISTER_PARAM",
            BIT_FIELD:"BIT_FIELD",
            FAR_EXTERNAL:"FAR_EXTERNAL",
            CLASS_BLOCK:"CLASS_BLOCK",
            CLASS_FUNCTION:"CLASS_FUNCTION",
            CLASS_END_OF_STRUCT:"CLASS_END_OF_STRUCT",
            CLASS_FILE:"CLASS_FILE",
            CLASS_SECTION:"CLASS_SECTION",
            CLASS_WEAK_EXTERNAL:"CLASS_WEAK_EXTERNAL",
            CLASS_CLR_TOKEN:"CLASS_CLR_TOKEN",}
    
class SymbolTypePacking:
    BTMASK = 0xF
    TMASK = 0x30
    TMASK1 = 0xC0
    TMASK2 = 0xF0
    BTSHFT = 4
    TSHIFT = 2

    NAME={BTMASK:'BTMASK',
          TMASK:'TMASK',
          TMASK1:'TMASK1',
          TMASK2:'TMASK2',
          BTSHFT:'BTSHFT',
          TSHIFT:'TSHIFT'}

class RelocationTypes:
    I386_ABSOLUTE = 0x0
    I386_DIR16 = 0x1
    I386_REL16 = 0x2
    I386_DIR32 = 0x6
    I386_DIR32NB = 0x7
    I386_SEG12 = 0x9
    I386_SECTION = 0xA
    I386_SECREL = 0xB
    I386_TOKEN = 0xC # CLR TOKEN
    I386_SECREL7 = 0xD
    I386_REL32 = 0x14

    NAME={I386_ABSOLUTE:'I386_ABSOLUTE',
          I386_DIR16:'I386_DIR16',
          I386_REL16:'I386_REL16',
          I386_DIR32:'I386_DIR32',
          I386_DIR32NB:'I386_DIR32NB',
          I386_SEG12:'I386_SEG12',
          I386_SECTION:'I386_SECTION',
          I386_SECREL:'I386_SECREL',
          I386_TOKEN:'I386_TOKEN',
          I386_SECREL7:'I386_SECREL7',
          I386_REL32:'I386_REL32',
          }




class SectionFlags:
    TYPE_NO_PAD = 0x8
    CNT_CODE = 0x20
    CNT_INITIALIZED_DATA = 0x40
    CNT_UNINITIALIZED_DATA = 0x80
    LNK_OTHER = 0x100
    LNK_INFO = 0x200
    LNK_REMOVE = 0x800
    LNK_COMDAT = 0x1000
    NO_DEFER_SPEC_EXC = 0x4000
    MEM_FARDATA = 0x8000
    MEM_PURGEABLE = 0x20000
    MEM_LOCKED = 0x40000
    MEM_PRELOAD = 0x80000
    
    ALIGN_1BYTES = 0x100000 #THESE AREN'T BOOLEAN FLAGS ARE THEY?
    ALIGN_2BYTES = 0x200000
    ALIGN_4BYTES = 0x300000
    ALIGN_8BYTES = 0x400000
    ALIGN_16BYTES = 0x500000
    ALIGN_32BYTES = 0x600000
    ALIGN_64BYTES = 0x700000
    ALIGN_128BYTES = 0x800000
    ALIGN_256BYTES = 0x900000
    ALIGN_512BYTES = 0xA00000
    ALIGN_1024BYTES = 0xB00000
    ALIGN_2048BYTES = 0xC00000
    ALIGN_4096BYTES = 0xD00000
    ALIGN_8192BYTES = 0xE00000
    ALIGN_MASK = 0xF00000 # END NONBOOL FLAGS?

    LNK_NRELOC_OVFL = 0x1000000
    MEM_DISCARDABLE = 0x2000000
    NOT_CACHED = 0x4000000
    NOT_PAGED = 0x8000000
    MEM_SHARED = 0x10000000
    MEM_EXECUTE = 0x20000000
    MEM_READ = 0x40000000
    MEM_WRITE = 0x80000000
    
    NAME = {
        TYPE_NO_PAD:'TYPE_NO_PAD',
        CNT_CODE:'CNT_CODE',
        CNT_INITIALIZED_DATA:'CNT_INITIALIZED_DATA',
        CNT_UNINITIALIZED_DATA:'CNT_UNITIALIZED_DATA',
        LNK_OTHER:'LNK_OTHER',
        LNK_INFO:'LNK_INFO',
        LNK_REMOVE:'LNK_REMOVE',
        LNK_COMDAT:'LNK_COMDAT',
        NO_DEFER_SPEC_EXC:'NO_DEFER_SPEC_EXC',
        MEM_FARDATA:'FARDATA',
        MEM_PURGEABLE:'PURGEABLE',
        MEM_LOCKED:'LOCKED',
        MEM_PRELOAD:'PRELOAD',

        LNK_NRELOC_OVFL:'LNK_NRELOC_OVFL',
        MEM_DISCARDABLE:'MEM_DISCARDABLE',
        NOT_CACHED:'NOT_CACHED',
        NOT_PAGED:'NOT_PAGED',
        MEM_SHARED:'MEM_SHARED',
        MEM_EXECUTE:'MEM_EXECUTE',
        MEM_READ:'MEM_READ',
        MEM_WRITE :'MEM_WRITE'
        }

    ALIGN_NAME = {
        ALIGN_1BYTES:'ALIGN_1BYTES',
        ALIGN_2BYTES:'ALIGN_2BYTES',
        ALIGN_4BYTES:'ALIGN_4BYTES',
        ALIGN_8BYTES:'ALIGN_8BYTES',
        ALIGN_16BYTES:'ALIGN_16BYTES',
        ALIGN_32BYTES:'ALIGN_32BYTES',
        ALIGN_64BYTES:'ALIGN_64BYTES',
        ALIGN_128BYTES:'ALIGN_128BYTES',
        ALIGN_256BYTES:'ALIGN_256BYTES',
        ALIGN_512BYTES:'ALIGN_512BYTES',
        ALIGN_1024BYTES:'ALIGN_1024BYTES',
        ALIGN_2048BYTES:'ALIGN_2048BYTES',
        ALIGN_4096BYTES:'ALIGN_4096BYTES',
        ALIGN_8192BYTES:'ALIGN_8192BYTES',
        }

