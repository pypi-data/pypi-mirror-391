
CB_BSDL_TOOL_DIR := ./cb_bsdl_tools
TEST_DIR := ./test


PYFILES := $(wildcard $(CB_BSDL_TOOL_DIR)/*.py) \
		   ./cb_bsdl_parser/cb_bsdl.py \
		   ./cb_bsdl_parser/__init__.py \
 		   $(wildcard $(TEST_DIR)/*.py)

show_files:
	@echo "Python files to be checked:"
	@echo "$(PYFILES)"

BUILD_DIR := ./dist

# tools
E := @echo
PYCODESTYLE := pycodestyle
PYCODESTYLE_FLAGS := --show-source --show-pep8 --max-line-length=100 #--ignore=E501,E228,E722

AUTOPEP8 := autopep8
AUTOPEP8_FLAGS := --in-place --max-line-length=1000

FLAKE8 := flake8
FLAKE8_FLAGS := --show-source  --ignore=E501,E228,E722

BANDIT := bandit
BANDIT_FLAGS := --format custom --msg-template \
    "{abspath}:{line}: {test_id}[bandit]: {severity}: {msg}" \
	-c pyproject.toml


HATCH := hatch



all: parser doc

doc: badges


check: pycodestyle flake8 bandit

pycodestyle: $(patsubst %.py,%.pycodestyle,$(PYFILES))

%.pycodestyle:
	$(E) $(PYCODESTYLE) checking $*.py
	@$(AUTOPEP8) $(AUTOPEP8_FLAGS) $*.py
	@$(PYCODESTYLE) $(PYCODESTYLE_FLAGS) $*.py


flake8: $(patsubst %.py,%.flake8,$(PYFILES))

%.flake8:
	$(E) flake8 checking $*.py
	@$(FLAKE8) $(FLAKE8_FLAGS) $*.py


bandit: $(patsubst %.py,%.bandit,$(PYFILES))

%.bandit:
	$(E) bandit checking $*.py
	@$(BANDIT) $(BANDIT_FLAGS) $*.py




COV_RESULT:= ./reports/junit/junit.xml
COV_REPORT:= ./reports/coverage_html/index.html ./reports/coverage/coverage.xml
DOC_BADGES:= ./doc/tests-badge.svg ./doc/coverage-badge.svg


parser:
	make -C ./cb_bsdl_parser/

test: $(COV_RESULT)
$(COV_RESULT): $(PYFILES)
	coverage run  -m  \
		pytest -rP   --junit-xml=./reports/junit/junit.xml


cov_report: $(COV_REPORT)
$(COV_REPORT): $(COV_RESULT)
	coverage report -m
	coverage html -d ./reports/coverage_html
	coverage xml -o ./reports/coverage/coverage.xml


badges: $(DOC_BADGES)
$(DOC_BADGES): $(COV_RESULT) $(COV_REPORT)
	@echo "Generating coverage badge..."
	@genbadge tests --output-file ./doc/tests-badge.svg
	@genbadge coverage --output-file ./doc/coverage-badge.svg


build: parser
	@$(E) Building the package...
	$(HATCH) build


install: build
	@$(E) Installing the package...
	@pip install dist/cb_bsdl_parser*.whl --force-reinstall


clean:
	@$(E) Cleaning up...
	@rm -f *.log *.log.*
	@rm -f ./bsdl_file_db/*.log  ./bsdl_file_db/*.log.*  ./test/bsdl_files/*.log  ./test/bsdl_files/*.log.*
	@rm -rf __pycache__
	@rm -rf */__pycache__
	@rm -rf ./$(BUILD_DIR)
	@rm -rf ./reports/
	@rm -f ./.coverage


mr_proper: clean
	make -C ./cb_bsdl_parser/ clean