from Function import Function


class Protein(Function):
    '''
    Takes, as input, a list of nucleotide bases, and outputs amino acid strings
    '''
    #Name for use in help listing
    mHelpName = "protein"
    #Names which can be used to address the Function
    mNames = set(["protein","prot","amino acid"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Convert a set of neucleobases to a string of amino acids"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        codonTable = {}
        codonTable['Ala'] = ['GCU','GCC','GCA','GCG']
        codonTable['Arg'] = ['CGU','CGC','CGA','CGG','AGA','AGG']
        codonTable['Asn'] = ['AAU','AAC']
        codonTable['Cys'] = ['UGU','UGC']
        codonTable['Gln'] = ['CAA','CAG']
        codonTable['Glu'] = ['GAA','GAG']
        codonTable['Gly'] = ['GGU','GGC','GGA','GGG']
        codonTable['His'] = ['CAU','CAC']
        codonTable['Ile'] = ['AUU','AUC','AUA']
        codonTable['START'] = ['AUG']
        codonTable['Leu'] = ['UUA','UUG','CUU','CUC','CUA','CUG']
        codonTable['Lys'] = ['AAA','AAG']
        codonTable['Met'] = ['AUG']
        codonTable['Phe'] = ['UUU','UUC']
        codonTable['Pro'] = ['CCU','CCC','CCA','CCG']
        codonTable['Ser'] = ['UCU','UCC','UCA','UCG','AGU','AGC']
        codonTable['Thr'] = ['ACU','ACC','ACA','ACG']
        codonTable['Trp'] = ['UGG']
        codonTable['Tyr'] = ['UAU','UAC']
        codonTable['Val'] = ['GUU','GUC','GUA','GUG']
        codonTable['STOP'] = ['UAA','UGA','UAG']
        #Clean the string, replace Tymine with Uracil
        lineClean = line.upper().replace('T','U')
        if(not all([c in 'ACGU' for c in lineClean])):
            return "Error, invalid nucleotides."
        strand = ["..."]
        if(codonTable['START'][0] in lineClean):
            strand = ["START"]
            lineClean = lineClean.split(codonTable['START'][0])[-1]
        stop = False
        while(len(lineClean)>=3 and not stop):
            codon = lineClean[:3]
            lineClean = lineClean[3:]
            for protein in codonTable :
                if(codon in codonTable[protein]):
                    strand += [protein]
                    if(protein=="STOP"):
                        stop = True
                    break
        if(not stop):
            strand += ["..."]
        return "-".join(strand)

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set([Function.EVENT_MESSAGE])

    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.lower()
        if(len(cleanFullLine)>3):
            return None
        validChars = list("ACGUT")
        checkMessage = cleanFullLine
        for validChar in validChars:
            checkMessage = checkMessage.replace(validChar,"")
        if(checkMessage==""):
            return self.run(cleanFullLine,userObject,channelObject)
        return None

