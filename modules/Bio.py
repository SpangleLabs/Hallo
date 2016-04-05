from Function import Function


class Protein(Function):
    """
    Takes, as input, a list of nucleotide bases, and outputs amino acid strings
    """
    # Name for use in help listing
    help_name = "protein"
    # Names which can be used to address the Function
    names = {"protein", "prot", "amino acid"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Convert a set of nucleobases to a string of amino acids"

    START = 'START'
    STOP = 'STOP'
    
    def __init__(self):
        """
        Constructor
        """
        pass
    
    def run(self, line, user_obj, destination_obj=None):
        codonTable = {'Ala': ['GCU', 'GCC', 'GCA', 'GCG'],
                      'Arg': ['CGU', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
                      'Asn': ['AAU', 'AAC'],
                      'Cys': ['UGU', 'UGC'],
                      'Gln': ['CAA', 'CAG'],
                      'Glu': ['GAA', 'GAG'],
                      'Gly': ['GGU', 'GGC', 'GGA', 'GGG'],
                      'His': ['CAU', 'CAC'],
                      'Ile': ['AUU', 'AUC', 'AUA'],
                      Protein.START: ['AUG'],
                      'Leu': ['UUA', 'UUG', 'CUU', 'CUC', 'CUA', 'CUG'],
                      'Lys': ['AAA', 'AAG'],
                      'Met': ['AUG'],
                      'Phe': ['UUU', 'UUC'],
                      'Pro': ['CCU', 'CCC', 'CCA', 'CCG'],
                      'Ser': ['UCU', 'UCC', 'UCA', 'UCG', 'AGU', 'AGC'],
                      'Thr': ['ACU', 'ACC', 'ACA', 'ACG'],
                      'Trp': ['UGG'],
                      'Tyr': ['UAU', 'UAC'],
                      'Val': ['GUU', 'GUC', 'GUA', 'GUG'],
                      Protein.STOP: ['UAA', 'UGA', 'UAG']}
        # Clean the string, replace Thymine with Uracil
        lineClean = line.upper().replace('T', 'U')
        if not all([c in 'ACGU' for c in lineClean]):
            return "Error, invalid nucleotides."
        strand = ["..."]
        if codonTable[Protein.START][0] in lineClean:
            strand = [Protein.START]
            lineClean = lineClean.split(codonTable[Protein.START][0])[-1]
        stop = False
        while len(lineClean) >= 3 and not stop:
            codon = lineClean[:3]
            lineClean = lineClean[3:]
            for protein in codonTable:
                if codon in codonTable[protein]:
                    strand += [protein]
                    if protein == Protein.STOP:
                        stop = True
                    break
        if not stop:
            strand += ["..."]
        return "-".join(strand)

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        cleanFullLine = full_line.strip().upper()
        if len(cleanFullLine) < 3:
            return None
        validChars = list("ACGUT")
        checkMessage = cleanFullLine
        for validChar in validChars:
            checkMessage = checkMessage.replace(validChar, "")
        if checkMessage == "":
            return self.run(cleanFullLine, user_obj, channel_obj)
        return None
