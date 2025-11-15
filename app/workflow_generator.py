"""
Generate GitHub Actions workflow files for different tech stacks.
"""
import logging
from typing import Any

logger = logging.getLogger("app.workflow_generator")

# Backend API URL - should be configurable via environment variable
BACKEND_API_URL = "http://localhost:8000"  # Default, should be overridden via env


def generate_workflow(
	tech_stack: str,
	test_case_path: str = "test_case.json",
	backend_api_url: str | None = None,
) -> str:
	"""
	Generate GitHub Actions workflow YAML content based on tech stack.
	
	Args:
		tech_stack: One of "springboot_maven", "nodejs_express", "python_flask"
		test_case_path: Path to test case JSON file in repository
		backend_api_url: Backend API URL to send test results to
	
	Returns:
		YAML content for GitHub Actions workflow
	"""
	api_url = backend_api_url or BACKEND_API_URL

	if tech_stack == "springboot_maven":
		return _generate_springboot_workflow(test_case_path, api_url)
	elif tech_stack == "nodejs_express":
		return _generate_nodejs_workflow(test_case_path, api_url)
	elif tech_stack == "python_flask":
		return _generate_python_flask_workflow(test_case_path, api_url)
	else:
		raise ValueError(f"Unsupported tech_stack: {tech_stack}")


def _generate_springboot_workflow(test_case_path: str, backend_api_url: str) -> str:
	"""Generate workflow for Spring Boot Maven projects."""
	return f"""name: API Test

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven
      
      - name: Build application
        run: mvn clean package -DskipTests
      
      - name: Start application
        run: |
          java -jar target/*.jar &
          sleep 30
        env:
          SPRING_PROFILES_ACTIVE: test
      
      - name: Wait for application to be ready
        run: |
          timeout=60
          elapsed=0
          while ! curl -f http://localhost:8080/health 2>/dev/null; do
            if [ $elapsed -ge $timeout ]; then
              echo "Application failed to start"
              exit 1
            fi
            sleep 2
            elapsed=$((elapsed + 2))
          done
      
      - name: Run API tests
        id: test
        run: |
          python3 -m pip install requests
          python3 << 'EOF'
          import json
          import requests
          import sys
          
          # Load test case
          with open('{test_case_path}', 'r') as f:
              test_case = json.load(f)
          
          # Run tests (simplified - should be replaced with actual test runner)
          results = {{"status": "success", "tests": []}}
          
          # Send results to backend
          try:
              response = requests.post(
                  '{backend_api_url}/repos/test-results',
                  json={{"test_results": results}},
                  timeout=30
              )
              response.raise_for_status()
              print("Test results sent successfully")
          except Exception as e:
              print(f"Failed to send results: {{e}}")
              sys.exit(1)
          EOF
      
      - name: Stop application
        if: always()
        run: pkill -f "java -jar"
"""


def _generate_nodejs_workflow(test_case_path: str, backend_api_url: str) -> str:
	"""Generate workflow for Node.js Express projects."""
	return f"""name: API Test

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm install
      
      - name: Start application
        run: |
          npm start &
          sleep 10
        env:
          NODE_ENV: test
          PORT: 3000
      
      - name: Wait for application to be ready
        run: |
          timeout=60
          elapsed=0
          while ! curl -f http://localhost:3000/health 2>/dev/null; do
            if [ $elapsed -ge $timeout ]; then
              echo "Application failed to start"
              exit 1
            fi
            sleep 2
            elapsed=$((elapsed + 2))
          done
      
      - name: Run API tests
        id: test
        run: |
          python3 -m pip install requests
          python3 << 'EOF'
          import json
          import requests
          import sys
          
          # Load test case
          with open('{test_case_path}', 'r') as f:
              test_case = json.load(f)
          
          # Run tests (simplified - should be replaced with actual test runner)
          results = {{"status": "success", "tests": []}}
          
          # Send results to backend
          try:
              response = requests.post(
                  '{backend_api_url}/repos/test-results',
                  json={{"test_results": results}},
                  timeout=30
              )
              response.raise_for_status()
              print("Test results sent successfully")
          except Exception as e:
              print(f"Failed to send results: {{e}}")
              sys.exit(1)
          EOF
      
      - name: Stop application
        if: always()
        run: pkill -f "node"
"""


def _generate_python_flask_workflow(test_case_path: str, backend_api_url: str) -> str:
	"""Generate workflow for Python Flask projects."""
	return f"""name: API Test

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Start application
        run: |
          python app.py &
          sleep 10
        env:
          FLASK_ENV: test
          FLASK_PORT: 5000
      
      - name: Wait for application to be ready
        run: |
          timeout=60
          elapsed=0
          while ! curl -f http://localhost:5000/health 2>/dev/null; do
            if [ $elapsed -ge $timeout ]; then
              echo "Application failed to start"
              exit 1
            fi
            sleep 2
            elapsed=$((elapsed + 2))
          done
      
      - name: Run API tests
        id: test
        run: |
          pip install requests
          python3 << 'EOF'
          import json
          import requests
          import sys
          
          # Load test case
          with open('{test_case_path}', 'r') as f:
              test_case = json.load(f)
          
          # Run tests (simplified - should be replaced with actual test runner)
          results = {{"status": "success", "tests": []}}
          
          # Send results to backend
          try:
              response = requests.post(
                  '{backend_api_url}/repos/test-results',
                  json={{"test_results": results}},
                  timeout=30
              )
              response.raise_for_status()
              print("Test results sent successfully")
          except Exception as e:
              print(f"Failed to send results: {{e}}")
              sys.exit(1)
          EOF
      
      - name: Stop application
        if: always()
        run: pkill -f "python.*app.py"
"""

