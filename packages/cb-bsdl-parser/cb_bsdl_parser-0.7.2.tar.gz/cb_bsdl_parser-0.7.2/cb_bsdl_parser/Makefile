

# tools
E := @echo


all: parser


GRAMAR_FILES = CBBsdl.g4 \
			   CBBsdlLexer.g4

ANTLR4_FILES = CBBsdlParser.py CBBsdlLexer.py CBBsdlListener.py \
			   CBBsdl.tokens  CBBsdl.interp \
			   CBBsdlLexer.tokens CBBsdlLexer.interp
# 			   .antlr


parser: $(ANTLR4_FILES)


$(ANTLR4_FILES): $(GRAMAR_FILES)
	$(E) "Generating python code from ANTLR grammar files..."
	@antlr4 -Dlanguage=Python3 $(GRAMAR_FILES)


clean:
	$(E) "Cleaning up generated files..."
	@rm -rf $(ANTLR4_FILES)
	@rm -rf __pycache__
	@rm -rf */__pycache__