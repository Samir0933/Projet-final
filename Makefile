ENV_NAME = student_env
setup_env : 
	@echo "Setting up environment..."
	pyenv virtualenv $(ENV_NAME)
	pyenv local $(ENV_NAME)
	@echo "Environment setup complete."

install_deps : setup_env
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed."