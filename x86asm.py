# Copyright 2004-2010 Grant T. Olson.
# See license.txt for terms.

"""
x86asm.py
---------

Ultimately create a two-pass assembler so we can assemble raw machine code.
We will also want to come up with some way to load code straight into memory
at runtime instead of just generating coff files.

I need to get the instruction tokenizer working for this to take off.
"""

from x86tokenizer import (tokenizeInst,
                          REGISTER,OPCODE,COMMA,OPERAND,
                          LBRACKET,RBRACKET,NUMBER,SYMBOL,STRING,
                          symbolRe,stringRe)

from x86inst import mnemonicDict, rb, rw, rd, instructionInstance

from tokenize import Number
import types, re

from pyasm.loggers import x86asmLogger, x86sourceLogger, x86apiLogger
class x86asmError(Exception): pass

###########################################################
## Find right instruction def based on concrete instruction
###########################################################

def possibleDefault(*toks):
    "By default, a token will just yield itself."
    first,rest = toks[0],toks[1:]
    if not rest:
        yield [first]
    else:
        i = 1
        possibleLookup = getProperLookup(*rest)
        for restMatches in possibleLookup(*rest):
            i += 1
            yldVal = [first]
            yldVal.extend(restMatches)
            yield yldVal

def possibleImmediateOrRelative(*toks):
    # TODO: can we narrow down which one this should be?
    immVals = [(OPERAND,'imm32'),(OPERAND,'imm16')]
    relVals = [(OPERAND,'rel32'),(OPERAND,'rel16')]
    first,rest = toks[0],toks[1:]
    vals = []
    
    #if it's 8 bit, try to grab smaller opcode
    if first[0] == NUMBER:
        num = eval(first[1])
        # Now 0x00000001 is imm32
        if len(first[1]) < 4 and num >= -127 and num <= 128:
            immVals.insert(0,(OPERAND,'imm8'))
            relVals.insert(0,(OPERAND,'rel8'))

       
    #lookup constant value like INT 3
    if first[0] == NUMBER:
        vals.append(first)
        
    vals.extend(immVals)
    vals.extend(relVals)    
    
    if not rest:
        for val in vals:
            yield [val]
    else:
        possibleLookup = getProperLookup(*rest)
        for val in vals:
            for restMatches in possibleLookup(*rest):
                yldVal = [val]
                yldVal.extend(restMatches)
                yield yldVal

def possibleRegister(*toks):
    """
    Registers may be hardcoded for superfast lookups, or an r or r/m value.
    We could probably optimize better with a better understanding of the environment.
        i.e. it doesn't make sense to move an r/m8 into an r32
    """    
    regName = toks[0][1]
    registerVals = [(REGISTER, '%s' % regName)]
    if regName in rb:
        registerVals.append((OPERAND,'r8'))
        registerVals.append((OPERAND, 'r/m8'))
    elif regName in rw:
        registerVals.append((OPERAND, 'r16'))
        registerVals.append((OPERAND,'r/m16'))
    elif regName in rd:
        registerVals.append((OPERAND,'r32'))
        registerVals.append((OPERAND,'r/m32'))
    else:
        raise x86asmError("Invalid Register name '%s'" % regName)

    first,rest = toks[0],toks[1:]
    if not rest:
        for val in registerVals:
            yield [val]
    else:
        possibleLookup = getProperLookup(*rest)
        for val in registerVals:
            for restMatches in possibleLookup(*rest):
                yldVal = [val]
                yldVal.extend(restMatches)
                yield yldVal

def possibleIndirect(*toks):
    """
    This is pretty much an r/m value
        i.e. it doesn't make sense to move an r/m8 into an r32
    """    
    possibleVals = []
    lbracket,operand,rest = toks[0],toks[1],toks[2:]

    if operand[0] in (NUMBER,SYMBOL):
        # TODO: CAN WE OPTIMIZE THIS?
        possibleVals.append((OPERAND,'r/m32'))
        possibleVals.append((OPERAND,'r/m16'))
        possibleVals.append((OPERAND,'r/m8'))
    elif operand[0] == REGISTER:        
        regName = operand[1]
        if rest[0][0] == RBRACKET:
            #Special case
            possibleVals.append((REGISTER, '[%s]' % regName))
        
        if regName in rb:
            possibleVals.append((OPERAND, 'r/m8'))
        elif regName in rw:
            possibleVals.append((OPERAND,'r/m16'))
        elif regName in rd:
            possibleVals.append((OPERAND,'r/m32'))
        else:
            raise x86asmError("Invalid Register name '%s'" % regName)
    
    while rest[0] != (RBRACKET, ']'):
        rest = rest[1:]
    rest = rest[1:]
    if not rest:
        for val in possibleVals:
            yield [val]
    else:
        possibleLookup = getProperLookup(*rest)
        for val in possibleVals:
            for restMatches in possibleLookup(*rest):
                yldVal = [val]
                yldVal.extend(restMatches)
                yield yldVal


possibleLookups = {
    REGISTER:possibleRegister,
    OPCODE:possibleDefault,
    COMMA:possibleDefault,
    LBRACKET:possibleIndirect,
    NUMBER:possibleImmediateOrRelative,
    SYMBOL:possibleImmediateOrRelative,}

def getProperLookup(*toks):
    return possibleLookups[toks[0][0]]

def findBestMatchTokens(toks):
    retVal = None
    for x in possibleDefault(*toks):
        y = tuple(x)
        if mnemonicDict.has_key(y):
            retVal = mnemonicDict[y]
            break
    if retVal:
        return retVal
    else:
        raise x86asmError("Unable to find match for " + `toks`)
    
def findBestMatch(s):
    toks = tokenizeInst(s)
    try:
        return findBestMatchTokens(toks)
    except x86asmError:
        raise x86asmError("Unable to find match for '%s'" % s)

def printBestMatch(s):
    print "Best match for '%s' => '%s'" % (s,findBestMatch(s).InstructionString)

##################################################################
## END OF Find right instruction def based on concrete instruction
##################################################################

class labelRef:
    def __init__(self, name):
        self.Name = name
        
class label:
    def __init__(self, name,typ=0):
        self.Name = name
        self.Address = 0x0
        self.Type = typ

class labelDict(dict):
    def __setitem__(self,key,val):
        if self.has_key(key):
            raise x86asmError("Duplicate Label Declaration '%s'" % key)
        else:
            dict.__setitem__(self,key,val)

class constDict(dict):
    def __setitem__(self,key,val):
        if self.has_key(key):
            raise x86asmError("Duplicate Constant Declaration '%s'" % key)
        else:
            dict.__setitem__(self,key, (NUMBER,val) )
            
class data:
    def __init__(self,name,dat,size=0):
        self.Name = name
        self.Data = dat
        self.Size = size
        self.Address = 0x0

class codePackage:
    def __init__(self):
        self.Code = ''
        self.CodeSymbols = []
        self.CodePatchins = []
        self.Data = ''
        self.DataSymbols = []

STDCALL, CDECL, PYTHON = range(1,4)

class procedure:
    def __init__(self,name, typ=CDECL):
        self.Name = name
        self.Address = 0x0

        self.Type = typ     
        
        self.Args = []
        self.ArgOffset = 8
        self.Locals = []
        self.LocalOffset = 0
        self.Frozen = 0
        
    def AddArg(self,name,bytes=4):
        if self.Frozen:
            raise x86asmError("Cannot add arg %s to procedure %s." \
                              "This must happen before instrutions are" \
                              "added." % (self.Name, name))
        self.Args.append( (name, self.ArgOffset, bytes) )
        self.ArgOffset += bytes

    def AddLocal(self,name,bytes=4):
        if self.Frozen:
            raise x86asmError("Cannot add arg %s to procedure %s." \
                              "This must happen before instrutions are" \
                              "added." % (self.Name, name))
        self.Locals.append( (name, self.LocalOffset, bytes) )
        self.LocalOffset += bytes

    def LookupArg(self,name):
        for x in self.Args:
            if x[0] == name:
                return ( (LBRACKET, '['), (REGISTER,'EBP'),(NUMBER, str(x[1])),
                         (RBRACKET,']') )
        return None

    def LookupLocal(self,name):
        for x in self.Locals:
            if x[0] == name:
                return ( (LBRACKET, '['), (REGISTER,'EBP'),(NUMBER, str(-(x[1]+4))),
                         (RBRACKET,']') )
        return None
       
    def LookupVar(self, name):
        retVal = self.LookupArg(name)
        if retVal is None:
            retVal = self.LookupLocal(name)
        return retVal

    def EmitProcStartCode(self, a):
        """
        Save EBP
        Copy ESP so we can use it to reference params and locals
        Subtrack 
        """
        a.AI("PUSH EBP")
        a.AI("MOV EBP, ESP")
        if self.LocalOffset:
            a.AI("SUB ESP, %s" % self.LocalOffset)

    def EmitProcEndCode(self, a):
        """
        Restore settings and RETurn
        TODO: Do we need to handle a Return value here?
        """
        if self.LocalOffset:
            a.AI("ADD ESP, %s" % self.LocalOffset)

        #check for malformed stack
        #a.AI("CMP         EBP,ESP")
        #a.AI("CALL        __chkesp")
        
        a.AI("MOV ESP, EBP")
        a.AI("POP EBP")
        
        if self.Type == STDCALL and self.ArgOffset - 8:
            #HAD ARGS AND IS A STDCALL, CLEANUP
            a.AI("RET %s" % (self.ArgOffset - 8))
        else:
            a.AI("RET")

#
# assembler directive re's
#
strRe = re.compile("\s*" + symbolRe + "\s*" + stringRe + "?$",re.DOTALL)
procRe = re.compile("\s*" + symbolRe +"\s*(?P<TYPE>STDCALL|CDECL|PYTHON)?$")
varRe = re.compile("\s*" + symbolRe + "\s*(?P<NUM>" + Number[1:] + "?$")
callRe = re.compile("\s*(%s|%s)\s*(?P<REST>.*)" % (symbolRe, stringRe))

class assembler:
    def __init__(self):
        self.Instructions = []
        self.Data = []
        self.Labels = {}
        self.Constants = constDict()
        self.CurrentProcedure = None
        self.StartAddress = 0x0
        self.DataStartAddress = 0x0
        self.inlineStringNo = 1000

    def registerLabel(self,lbl):
        if self.Labels.has_key(lbl.Name):
            raise x86asmError("Duplicate Label Registration [%s]" % lbl.Name)
        self.Labels[lbl.Name] = lbl


    #
    # Write assmebly code
    #

    def freezeProc(self):
        if self.CurrentProcedure and not self.CurrentProcedure.Frozen:
            #initialize proc
            self.CurrentProcedure.Frozen = 1
            self.CurrentProcedure.EmitProcStartCode(self)
            
    def AddInstruction(self,inst):
        self.freezeProc()
        instToks = tokenizeInst(inst)
        instToksMinusLocals = ()

        for tok in instToks:
            if tok[0] == STRING:
                # Create an inlined string
                inlineName = "inline_pyasm_string%i" % self.inlineStringNo
                escapedString = tok[1].decode("string_escape")
                self.ADStr(inlineName,escapedString)
                instToksMinusLocals += ((SYMBOL,inlineName),)
                self.inlineStringNo += 1                
            elif tok[0] != SYMBOL: # do nothing
                instToksMinusLocals += ( tok,)
            elif self.Constants.has_key(tok[1]): #replace constant
                instToksMinusLocals += (self.Constants[tok[1]],)
            elif self.CurrentProcedure:
                #look for local match
                local = self.CurrentProcedure.LookupVar(tok[1])
                if local: #found match
                    instToksMinusLocals += local
                else: # defer resolution to second pass
                    instToksMinusLocals += (tok,)
            else: # stick with local
                instToksMinusLocals = instToks
            
        self.Instructions.append(instToksMinusLocals)

    def AI(self,inst):

        self.AddInstruction(inst)

    def AddInstructionLabel(self,name,typ=0):
        lbl = label(name,typ)
        self.registerLabel(lbl)
        self.Instructions.append(lbl)

    def AIL(self,name):
        self.AddInstructionLabel(name)

    def AddData(self,name,dat):
        lbl = label(name)
        self.registerLabel(lbl)
        self.Data.append(data(name,dat,len(dat)))

    def ADStr(self,name,dat):
        self.AddData(name,dat)

    def AddProcedure(self,name,typ=STDCALL):
        if self.CurrentProcedure: # didn't emit procedure cleanup code
            raise x86asmError("Must end procedure '%s' before starting proc " \
                              " '%s'" % (self.CurrentProcedure.Name, name))
        self.AddInstructionLabel(name,typ)
        proc = procedure(name,typ)  
        self.CurrentProcedure = proc

    def AP(self,name,typ=STDCALL):
        self.AddProcedure(name,typ)

    def AddArgument(self,name,size=4):
        self.CurrentProcedure.AddArg(name,size)

    def AA(self,name,size=4):
        self.AddArgument(name,size)

    def AddLocal(self,name,size=4):
        self.CurrentProcedure.AddLocal(name,size)

    def EndProc(self):
        if self.CurrentProcedure:
            self.CurrentProcedure.EmitProcEndCode(self)
            self.CurrentProcedure = None

    def EP(self):
        self.EndProc()

    def AddConstant(self,name,val):
        self.Constants[name] = val

    def AC(self,name,val):
        self.AddConstant(name,val)
        
    #
    # end write assembly code
    #

    #
    # handle assembler directives
    #
    def getVarNameAndSize(t,s):
        matches = varRe.match(s)
        if not matches:
            raise x86asmError("Couldn't parse %s assembler directive %s" % (t,repr(s)))
        matches = matches.groupdict()
        name = matches['SYMBOL']
        if matches['NUM']:
            size = eval(matches['NUM'])
        else:
            size = 4 #default to DWORD
        return name,size
    
    def PROC(self,params):
        matches = procRe.match(params)
        if not matches:
            x86asmError("Couldn't parse PROC assembler directive %s" % repr(params))
        matches = matches.groupdict()
        
        name = matches['SYMBOL']
        
        if matches['TYPE']:
            t = matches['TYPE']
            if t == 'CDECL':
                c = CDECL
            elif t == 'STDCALL':
                c = STDCALL
            elif t == 'PYTHON':
                c = PYTHON
            else:
                raise x86asmError("Couldn't parse PROC assembler directive %s" % repr(params))
        else:
            c = CDECL
            
        self.AddProcedure(name,c)

    def ARG(self,params):
        name,size = self.getVarNameAndSize(params)
        self.AddArgument(name,size)

    def LOCAL(self,params):
        name,size = self.getVarNameAndSize(params)
        self.AddLocal(name,size)

    def ENDPROC(self,params):
        if params:
            raise x86asmError("Couldn't parse assembler directive %s" % repr(params))
        self.EndProc()

    def CALL(self,params):
        matches = callRe.match(params)
        if not matches:
            raise x86asmError("Couldn't parse assembler directive %s" % repr(params))
        matches = matches.groupdict()
        proc,rest = matches['SYMBOL'],matches['REST']
        params = []

        while rest:
            matches = callRe.match(rest).groupdict()
            if not matches:
                raise x86asmError("Couldn't parse assembler directive %s" % repr(params))
            rest = matches['REST']
            if matches['SYMBOL']:
                first = matches['SYMBOL']
            elif matches['STRING']:
                first = matches['q'] + matches['STRING'] + matches['q']
            else:
                raise x86asmError("Couldn't parse assembler directive %s" % repr(params))
            params.append(first)

        params.reverse() # push from right to left
        for param in params:
            self.AI("PUSH %s" % param)
        self.AI("CALL %s" % proc)
    
    def CHARS(self,params):
        matches = strRe.match(params)
        if not matches:
            raise x86asmError("Couldn't parse assembler directive %s" % repr(params))
        matches = matches.groupdict()
        name,s = matches['SYMBOL'], matches['STRING']
        if not (name and s):
            raise x86asmError("Couldn't parse assembler directive %s" % repr(params))
        self.ADStr(name,s.decode("string_escape"))

    def COMMENT(self,params):
        pass
    
    def dispatchDirective(self,s):
        firstSpace = s.find(' ')
        if firstSpace < 0: 
            directive,params = s[1:],''
        else:
            directive,params = s[1:firstSpace],s[firstSpace+1:]
        getattr(self,directive)(params)
        

    def dispatchStatement(self,s):
        self.AddInstruction(s)

    def DispatchString(self,s):
        x86sourceLogger.info(s.rstrip()) #don't want extra newline
        s = s.strip()
        if not s:
            pass #blank line
        elif s[0] == "!":
            self.dispatchDirective(s)
        else:
            self.dispatchStatement(s)

    def __call__(self,s):
        self.DispatchString(s)
        
    #
    # start actual compilation code
    #
    def pass1(self):
        cp = codePackage()
        newInsts = []
        newData = []

        currentAddress = self.StartAddress
        for i in self.Instructions:
            if type(i) == types.TupleType: # and instruction to lookup
                inst = findBestMatchTokens(i).GetInstance()
                inst.LoadConcreteValues(i)
                inst.Address = currentAddress
                currentAddress += inst.GetInstructionSize()
                newInsts.append(inst)
                x86asmLogger.info(inst.OpText())
                cp.CodePatchins.extend(inst.GetSymbolPatchins())
            else: # a label
                i.Address = currentAddress
                logMsg = "  %08X: %s" % (i.Address,i.Name)
                x86asmLogger.info(logMsg)
                cp.CodeSymbols.append((i.Name,i.Address,i.Type))

        currentAddress = self.DataStartAddress
        newData = []
        for d in self.Data:
            d.Address = currentAddress
            newData.append(d.Data)
            cp.DataSymbols.append( (d.Name,d.Address) )
            currentAddress += d.Size            
        cp.Code = ''.join([i.OpDataAsString() for i in newInsts])
        cp.Data = ''.join([d for d in newData])

        return cp
            
            
    def Compile(self):
        if self.CurrentProcedure:
            raise x86asmError("Never ended procedure '%s'" % self.CurrentProcedure.Name)
        return self.pass1()

def _log_header(text):
    line = "=" * len(text)
    x86sourceLogger.info(line)
    x86sourceLogger.info(text)
    x86sourceLogger.info(line)
    x86sourceLogger.info('')
        

def codePackageFromFile(fil,constCallback=None):
    try:
        filename = fil.name
    except: #stringIO objects don't have a name property
        filename = repr(fil)
        
    _log_header("COMPILING FILE %s" % filename)
    a = assembler()
    
    if constCallback:
        constCallback(a)
        
    for line in fil.readlines():
        a(line)
        
    _log_header("END COMPILE OF %s" % filename)
    return a.Compile()

def manglePythonNames(cp):
    """
    Python names need to start with a _ for STDCALL designation in
    static compilation, but names are resolved without this.  This adds
    The name mangling where appropriate.
    """
    newPatchins = []
    for patch in cp.CodePatchins:
        if patch[0].startswith("Py") or patch[0].startswith("_Py"):
            patch = ("_" + patch[0], patch[1],patch[2])
        newPatchins.append(patch)
    cp.CodePatchins = newPatchins

    return cp # even though it did it in place


if __name__ == '__main__':
    a = assembler()
    a.AP("foo")
    a.AA("bar")
    a.AA("baz")
    a.AddLocal("x")
    a.AddLocal("y")
    a.AI("MOV EAX,bar")
    a.AI("MOV EAX,baz")
    a.AI("MOV x,EAX")
    a.AI("MOV y,12")
    a.EP()

    a.Compile()    
