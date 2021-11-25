ROOT_DIR:= ./
SRC_DIR:= ./src
VENV_BIN_DIR:= "sabicenv/bin"
CMD_FROM_VENV:="$(VENV_BIN_DIR)/activate"

define create-venv
pip install virtualenv
python3 -m virtualenv sabicenv
endef

venv:
	@$(create-venv);

requirements:
	echo "Installing all the dependencies"
	pip install -r requirements.txt

freeze:
	echo "freezing the current directory to update requirements.txt"
	pip freeze >requirements.txt

clear_cache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo|.pytest_cache)" | xargs rm -rf

	