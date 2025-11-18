"""
Tests for CVE Database Integration
Week 1 Day 3: CVE Database Testing
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from alprina_cli.agents.cicd_guardian.cve_database import (
    CVEDatabase,
    CVEEntry,
    get_cve_database
)


class TestCVEEntry:
    """Test CVE Entry data class"""

    def test_cve_entry_creation(self):
        """Test creating a CVE entry"""
        cve = CVEEntry(
            cve_id="CVE-2020-15228",
            title="Test CVE",
            description="Test description",
            severity="high",
            affected_actions=["actions/checkout@v2"],
            affected_versions=["<= 2.3.4"],
            fixed_versions=[">= 2.4.0"],
            references=["https://example.com"],
            published_date="2020-10-19",
            last_modified="2024-01-15"
        )

        assert cve.cve_id == "CVE-2020-15228"
        assert cve.severity == "high"
        assert len(cve.affected_actions) == 1

    def test_cve_matches_action(self):
        """Test CVE action matching"""
        cve = CVEEntry(
            cve_id="TEST-001",
            title="Test",
            description="Test",
            severity="high",
            affected_actions=["actions/checkout@v2"],
            affected_versions=["<= 2.3.4"],
            fixed_versions=[">= 2.4.0"],
            references=[],
            published_date="2020-01-01",
            last_modified="2020-01-01"
        )

        # Should match action name
        assert cve.matches_action("actions/checkout")
        assert cve.matches_action("actions/checkout", "v2")

        # Should not match different action
        assert not cve.matches_action("actions/setup-node")


class TestCVEDatabase:
    """Test CVE Database functionality"""

    def test_database_initialization(self):
        """Test database initializes with bootstrap data"""
        db = CVEDatabase()
        assert len(db.cves) > 0
        assert "GHSL-2024-313" in db.cves

    def test_search_by_cve_id(self):
        """Test searching by CVE ID"""
        db = CVEDatabase()
        results = db.search(cve_id="GHSL-2024-313")

        assert len(results) == 1
        assert results[0].cve_id == "GHSL-2024-313"
        assert results[0].severity == "critical"

    def test_search_by_severity(self):
        """Test searching by severity"""
        db = CVEDatabase()
        critical_cves = db.search(severity="critical")

        assert len(critical_cves) > 0
        for cve in critical_cves:
            assert cve.severity == "critical"

    def test_search_by_action_name(self):
        """Test searching by action name"""
        db = CVEDatabase()
        checkout_cves = db.search(action_name="actions/checkout")

        assert len(checkout_cves) > 0
        # Should find CVE-2020-15228 and potentially others
        assert any(cve.cve_id == "CVE-2020-15228" for cve in checkout_cves)

    def test_get_specific_cve(self):
        """Test getting specific CVE"""
        db = CVEDatabase()
        cve = db.get_cve("GHSL-2024-313")

        assert cve is not None
        assert cve.title == "Public PPE (3PE) - Untrusted Code Execution in Pull Requests"
        assert "23,000+" in cve.description

    def test_get_statistics(self):
        """Test database statistics"""
        db = CVEDatabase()
        stats = db.get_statistics()

        assert "total" in stats
        assert "critical" in stats
        assert "high" in stats
        assert "medium" in stats
        assert "low" in stats

        assert stats["total"] > 0
        assert stats["critical"] + stats["high"] + stats["medium"] + stats["low"] == stats["total"]

    def test_singleton_pattern(self):
        """Test that get_cve_database returns singleton"""
        db1 = get_cve_database()
        db2 = get_cve_database()

        assert db1 is db2

    def test_cve_to_dict(self):
        """Test CVE entry serialization"""
        db = CVEDatabase()
        cve = db.get_cve("GHSL-2024-313")

        cve_dict = cve.to_dict()

        assert isinstance(cve_dict, dict)
        assert cve_dict["cve_id"] == "GHSL-2024-313"
        assert "affected_actions" in cve_dict
        assert "references" in cve_dict

    def test_bootstrap_known_cves(self):
        """Test that bootstrap includes all known CVEs"""
        db = CVEDatabase()

        # Check for key CVEs that should be in bootstrap
        required_cves = [
            "GHSL-2024-313",  # Public PPE pattern
            "CVE-2020-15228",  # actions/checkout
            "CVE-2021-22573",  # actions/cache
            "CVE-2023-33968",  # actions/github-script
            "ALPRINA-WORKFLOW-RUN-001",  # workflow_run
            "ALPRINA-PR-TARGET-001",  # pull_request_target
        ]

        for cve_id in required_cves:
            cve = db.get_cve(cve_id)
            assert cve is not None, f"Missing required CVE: {cve_id}"

    def test_cache_persistence(self, tmp_path):
        """Test that cache persists between instances"""
        cache_dir = tmp_path / "cve_cache"

        # Create first instance
        db1 = CVEDatabase(cache_dir=cache_dir)
        initial_count = len(db1.cves)

        # Create second instance (should load from cache)
        db2 = CVEDatabase(cache_dir=cache_dir)

        assert len(db2.cves) == initial_count
        assert "GHSL-2024-313" in db2.cves


class TestCVEIntegrationWithCICDGuardian:
    """Test CVE database integration with CI/CD Guardian agent"""

    def test_parse_action_reference(self):
        """Test parsing action references"""
        from alprina_cli.agents.cicd_guardian.cicd_guardian import PipelineGuardianAgent

        agent = PipelineGuardianAgent()

        # Test standard action reference
        name, version = agent._parse_action_reference("actions/checkout@v2")
        assert name == "actions/checkout"
        assert version == "v2"

        # Test action with commit SHA
        name, version = agent._parse_action_reference("actions/checkout@a81bbbf8298c0fa03ea29cdc473d45769f953675")
        assert name == "actions/checkout"
        assert version == "a81bbbf8298c0fa03ea29cdc473d45769f953675"

        # Test docker image
        name, version = agent._parse_action_reference("docker://alpine:3.10")
        assert name == "docker://alpine"
        assert version == "3.10"

        # Test action without version
        name, version = agent._parse_action_reference("actions/checkout")
        assert name == "actions/checkout"
        assert version is None

    def test_check_actions_against_cve_database(self):
        """Test checking workflow actions against CVE database"""
        from alprina_cli.agents.cicd_guardian.cicd_guardian import PipelineGuardianAgent

        agent = PipelineGuardianAgent()

        # Workflow with vulnerable action
        workflow = {
            'on': ['push'],
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v2'  # Vulnerable version
                        },
                        {
                            'uses': 'actions/cache@v2.1.6'  # Vulnerable version
                        }
                    ]
                }
            }
        }

        vulns = agent._check_actions_against_cve_database(workflow, 'test.yml')

        # Should detect CVE-2020-15228 for actions/checkout@v2
        # Should detect CVE-2021-22573 for actions/cache@v2.1.6
        assert len(vulns) >= 2

        cve_ids = [v.cve_id for v in vulns]
        assert "CVE-2020-15228" in cve_ids
        assert "CVE-2021-22573" in cve_ids

    def test_full_workflow_analysis_with_cve(self):
        """Test full workflow analysis including CVE checks"""
        from alprina_cli.agents.cicd_guardian.cicd_guardian import PipelineGuardianAgent

        agent = PipelineGuardianAgent()

        # Create workflow with multiple vulnerabilities
        workflow = {
            'on': {
                'pull_request_target': {},  # Public PPE vulnerability
            },
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v2',  # CVE-2020-15228
                            'with': {
                                'ref': '${{ github.event.pull_request.head.sha }}'
                            }
                        },
                        {
                            'run': 'echo ${{ github.event.pull_request.title }}'  # Public PPE
                        }
                    ]
                }
            }
        }

        vulns = agent._analyze_github_actions(workflow, 'test.yml')

        # Should detect:
        # 1. Public PPE (GHSL-2024-313)
        # 2. CVE-2020-15228 (actions/checkout@v2)
        # 3. pull_request_target pattern (ALPRINA-PR-TARGET-001)

        assert len(vulns) >= 2  # At least PPE and checkout CVE

        # Check for critical vulnerabilities
        critical_vulns = [v for v in vulns if v.severity == "critical"]
        assert len(critical_vulns) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
