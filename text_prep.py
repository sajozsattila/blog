
# coding: utf-8

# In[ ]:


import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formater = logging.Formatter('[%(asctime)s][%(levelname)s][%(processName)s] %(message)s')
std = logging.StreamHandler()
std.setFormatter(formater)



        

# general class for prep the text before loading in model
# Arguments
#   * text -- The original text array which we want to prep
#   * memoryopt -- Bollean, do we delete the middle step data, due to optimalise the memory usage
class TextPrep():
    def __init__(self, text, memoryopt=True):
        # test the text is itterable
        try:
            _ = (e for e in text)
        except TypeError as e:
            logging.exception(str(text)+" is not iterable")
            raise RuntimeError(str(text)+" is not iterable") from error
        
        self.text = tuple(text)
        self.memoryopt = memoryopt
        self.version = '1.0.0'
        self.length = len(self.text)
    
    # version 1.0.0
    # steaming the text
    def steaming(self, text):
        
        steamed = []
        for pos in text:
            # numbers drop
            if pos[1] == 'CD':
                continue
            
            w = pos[0]
            if len(w) > 0:
                # remove stops
                if w in self.stops:
                    continue
                # drop words symboles
                if w in self.drop:
                    continue
                # bugfix 'is" -> "i"
                if w == 'is':
                    steamed.append( (w.lower(), pos[1]) )
                    continue
                
                s = self.hobj.stem(w)
                if len(s) > 0:
                    if s[0].decode('unicode_escape') in self.stops:
                        continue
                    steamed.append( ( s[0].decode('unicode_escape'), pos[1] ) )
                else:
                    steamed.append( (w.lower(), pos[1]) )
        return( steamed )  
    
    # generate a text
    def run(self):
        import hunspell
        self.hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')
        from nltk.corpus import stopwords
        # words which we not interest
        self.drop = set(["(", ")", ",", ".", "%", ":", ";", "—", '”', '“' ])
        self.stops = set(stopwords.words("english")) 
        
        # breaking to sentence        
        from nltk import word_tokenize, pos_tag, sent_tokenize
        if not self.memoryopt:
            import copy
            self.text_original = copy.copy(self.text )
        self.text_tokenized = []
        for a in range(len(self.text)):
            thisabs = []
            for s in sent_tokenize(self.text[a]):
                thisabs.append(pos_tag(word_tokenize(s)))
            self.text_tokenized.append(thisabs)
        self.text = tuple(self.text_tokenized)
        
        # steaming
        self.text_steamed = []
        for a in self.text_tokenized:
            thisa = []
            for s in a:
                thisa.append(self.steaming(s))
            self.text_steamed.append(thisa)
        self.text = tuple(self.text_steamed)
        if self.memoryopt:
            self.text_tokenized = "Dropped due to the memoryopt settings."
            
        # join back to text
        self.text_final = []
        for a in range(len(self.text_steamed)):
            newa = []
            for s in self.text_steamed[a]:
                for w in s:
                    newa.append(w[0])
            self.text_final.append( " ".join(newa) )
        self.text = tuple(self.text_final)
        if self.memoryopt:
            self.text_steamed = "Dropped due to the memoryopt settings."
            self.text_final = "Dropped due to the memoryopt settings."
 
    # merge -- add new text to the original text
    # Arguments
    #   text -- the text which we merging in
    #   front -- Bool, the new text it is going on the front of the old (True) or to the end (False)
    def merge(self, text, front=True):
        # test the text is itterable
        try:
            _ = (e for e in text)
        except TypeError as e:
            msg = str(text)+" is not iterable"
            logging.exception(msg)
            raise RuntimeError(msg) from error
            
        if len(text) != self.length:
            msg = "The two text should be same length! But the new is "+str(text)+" comparing to the "+str(self.length)+"!"
            logging.exception(msg)
            raise RuntimeError(msg) from error
            
        new = []
        if front:
            for i in range(self.length):
                new.append(text[i] + " " + self.text[i])
        self.text = tuple(new)
    
    # function to return tagged doc for Gensim Doc2Vec
    # Arguments
    #   * labels -- the label of the doc, if we use a pretraned model we need to be sure it is not in already
    #   * tags -- extra tags for the doc
    def read_corpus(self, labels, tokens_only=False, tags = None ):
        import gensim
        for i in range(self.length):
            line = self.text[i]
        
            if tokens_only:
                if tags is None:
                    yield gensim.utils.simple_preprocess(line)
                else:
                    yield gensim.utils.simple_preprocess(line, tags[i])
            else:
                if tags is None:
                    yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [labels[i]])
                else:
                    yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), tags[i]+[labels[i]])
                    



