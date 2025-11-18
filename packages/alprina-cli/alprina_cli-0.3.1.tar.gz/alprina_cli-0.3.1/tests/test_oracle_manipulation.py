"""
Tests for Enhanced Oracle Manipulation Detection
Week 2 Day 1: Oracle Manipulation Testing
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from alprina_cli.agents.web3_auditor.solidity_analyzer import (
    SolidityStaticAnalyzer,
    VulnerabilityType
)


class TestOracleManipulationDetection:
    """Test enhanced oracle manipulation detection patterns"""

    def setup_method(self):
        """Initialize analyzer for each test"""
        self.analyzer = SolidityStaticAnalyzer()

    def test_detect_chainlink_staleness_missing(self):
        """Test detection of Chainlink oracle without staleness check"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract VulnerablePrice {
            AggregatorV3Interface priceFeed;

            function getPrice() public view returns (uint256) {
                (, int price,,,) = priceFeed.latestRoundData();
                // Missing: updatedAt staleness check
                return uint256(price);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]
        assert len(oracle_vulns) >= 1

        # Should detect missing staleness check
        staleness_vulns = [v for v in oracle_vulns if 'staleness' in v.title.lower()]
        assert len(staleness_vulns) >= 1
        assert staleness_vulns[0].severity == "high"
        assert "updatedAt" in staleness_vulns[0].remediation

    def test_chainlink_with_staleness_check_safe(self):
        """Test that proper staleness check is recognized as safe"""
        safe_code = """
        pragma solidity ^0.8.0;

        contract SafePrice {
            AggregatorV3Interface priceFeed;

            function getPrice() public view returns (uint256) {
                (, int price,, uint256 updatedAt,) = priceFeed.latestRoundData();
                require(block.timestamp - updatedAt < 3600, "Stale price");
                require(price > 0, "Invalid price");
                return uint256(price);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(safe_code, "test.sol")

        # Should have far fewer vulnerabilities
        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]
        staleness_vulns = [v for v in oracle_vulns if 'staleness' in v.title.lower()]

        # Should not detect staleness issue
        assert len(staleness_vulns) == 0

    def test_detect_single_oracle_source(self):
        """Test detection of single oracle source without aggregation"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract SingleOracle {
            AggregatorV3Interface priceFeed;

            function calculateValue() public view returns (uint256) {
                (, int price,,,) = priceFeed.latestRoundData();
                return uint256(price) * 1000;
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect single oracle usage
        single_oracle_vulns = [v for v in oracle_vulns if 'single oracle' in v.title.lower()]
        assert len(single_oracle_vulns) >= 1
        assert "multi-oracle" in single_oracle_vulns[0].remediation.lower()

    def test_detect_uniswap_spot_price_vulnerability(self):
        """Test detection of UniswapV2 spot price usage (flash loan vulnerable)"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract UniswapSpotPrice {
            IUniswapV2Router02 router;

            function getTokenPrice() public view returns (uint256) {
                address[] memory path = new address[](2);
                path[0] = tokenA;
                path[1] = tokenB;

                uint256[] memory amounts = router.getAmountsOut(1e18, path);
                return amounts[1];  // Using spot price - VULNERABLE!
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect Uniswap spot price vulnerability
        spot_price_vulns = [v for v in oracle_vulns if 'spot price' in v.title.lower()]
        assert len(spot_price_vulns) >= 1
        assert spot_price_vulns[0].severity == "critical"
        assert "flash loan" in spot_price_vulns[0].description.lower()
        assert "TWAP" in spot_price_vulns[0].remediation

    def test_uniswap_with_twap_safe(self):
        """Test that UniswapV3 TWAP is recognized as safer"""
        safer_code = """
        pragma solidity ^0.8.0;

        contract TWAPPrice {
            IUniswapV3Pool pool;

            function getTokenPrice() public view returns (uint256) {
                uint32[] memory secondsAgos = new uint32[](2);
                secondsAgos[0] = 1800;  // 30 minutes ago
                secondsAgos[1] = 0;     // now

                (int56[] memory tickCumulatives,) = pool.observe(secondsAgos);
                // Calculate TWAP from tickCumulatives
                return calculateTWAP(tickCumulatives);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(safer_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should not detect spot price vulnerability (TWAP is present)
        spot_price_vulns = [v for v in oracle_vulns if 'spot price' in v.title.lower()]
        assert len(spot_price_vulns) == 0

    def test_detect_pool_reserve_manipulation(self):
        """Test detection of direct pool reserve usage"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract ReservePrice {
            IUniswapV2Pair pair;

            function calculatePrice() public view returns (uint256) {
                (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
                uint256 price = (reserve1 * 1e18) / reserve0;
                return price;  // CRITICAL: Using reserves directly!
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect reserve manipulation vulnerability
        reserve_vulns = [v for v in oracle_vulns if 'reserve' in v.title.lower()]
        assert len(reserve_vulns) >= 1
        assert reserve_vulns[0].severity == "critical"
        assert "flash loan" in reserve_vulns[0].description.lower()

    def test_detect_missing_price_bounds(self):
        """Test detection of missing price bounds validation"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract NoBounds {
            AggregatorV3Interface priceFeed;

            function executeSwap(uint256 amount) public {
                (, int price,,,) = priceFeed.latestRoundData();
                uint256 value = uint256(price) * amount;
                // Missing: MIN_PRICE and MAX_PRICE checks
                _processSwap(value);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect missing bounds validation
        bounds_vulns = [v for v in oracle_vulns if 'bounds' in v.title.lower()]
        assert len(bounds_vulns) >= 1
        assert bounds_vulns[0].severity in ["medium", "high"]
        assert "MIN_PRICE" in bounds_vulns[0].remediation or "MAX_PRICE" in bounds_vulns[0].remediation

    def test_detect_missing_oracle_failure_handling(self):
        """Test detection of oracle calls without try/catch"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract NoErrorHandling {
            AggregatorV3Interface priceFeed;

            function getPrice() public view returns (uint256) {
                // Missing: try/catch for oracle failure
                (, int price,,,) = priceFeed.latestRoundData();
                return uint256(price);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect missing error handling
        error_handling_vulns = [v for v in oracle_vulns if 'failure' in v.title.lower() or 'error' in v.title.lower()]
        assert len(error_handling_vulns) >= 1
        assert "try" in error_handling_vulns[0].remediation.lower()
        assert "catch" in error_handling_vulns[0].remediation.lower()

    def test_oracle_with_error_handling_safe(self):
        """Test that try/catch error handling is recognized"""
        safer_code = """
        pragma solidity ^0.8.0;

        contract WithErrorHandling {
            AggregatorV3Interface priceFeed;

            function getPrice() public view returns (uint256) {
                try priceFeed.latestRoundData() returns (
                    uint80,
                    int price,
                    uint,
                    uint,
                    uint80
                ) {
                    return uint256(price);
                } catch {
                    revert("Oracle failure");
                }
            }
        }
        """

        vulns = self.analyzer.analyze_contract(safer_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should not detect error handling issue
        error_handling_vulns = [v for v in oracle_vulns if 'failure' in v.title.lower()]
        assert len(error_handling_vulns) == 0

    def test_comprehensive_vulnerable_contract(self):
        """Test comprehensive detection on highly vulnerable contract"""
        highly_vulnerable_code = """
        pragma solidity ^0.8.0;

        contract HighlyVulnerable {
            AggregatorV3Interface chainlinkFeed;
            IUniswapV2Router02 uniswapRouter;
            IUniswapV2Pair pair;

            // VULNERABILITY 1: No staleness check
            // VULNERABILITY 2: No price validation
            // VULNERABILITY 3: Single oracle source
            // VULNERABILITY 4: No error handling
            function getChainlinkPrice() public view returns (uint256) {
                (, int price,,,) = chainlinkFeed.latestRoundData();
                return uint256(price);
            }

            // VULNERABILITY 5: Uniswap spot price (flash loan vulnerable)
            // VULNERABILITY 6: No TWAP
            function getUniswapPrice() public view returns (uint256) {
                address[] memory path = new address[](2);
                uint256[] memory amounts = uniswapRouter.getAmountsOut(1e18, path);
                return amounts[1];
            }

            // VULNERABILITY 7: Direct reserve usage (CRITICAL)
            function getReservePrice() public view returns (uint256) {
                (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
                uint256 price = (reserve1 * 1e18) / reserve0;
                return price;
            }

            // VULNERABILITY 8: No bounds validation
            function executeWithPrice(uint256 amount) public {
                uint256 price = getChainlinkPrice();
                uint256 value = price * amount;
                _execute(value);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(highly_vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect multiple vulnerabilities
        assert len(oracle_vulns) >= 5  # At least 5 distinct issues

        # Should detect critical vulnerabilities
        critical_vulns = [v for v in oracle_vulns if v.severity == "critical"]
        assert len(critical_vulns) >= 1

        # Should detect high severity vulnerabilities
        high_vulns = [v for v in oracle_vulns if v.severity == "high"]
        assert len(high_vulns) >= 1

    def test_safe_multi_oracle_contract(self):
        """Test that properly secured contract has minimal issues"""
        safe_code = """
        pragma solidity ^0.8.0;

        contract SafeOracleUsage {
            AggregatorV3Interface chainlinkFeed;
            IUniswapV3Pool uniV3Pool;

            uint256 constant MIN_PRICE = 1e6;
            uint256 constant MAX_PRICE = 1e12;
            uint256 constant STALENESS_THRESHOLD = 3600;

            function getAggregatedPrice() public view returns (uint256) {
                // Get Chainlink price with all validations
                uint256 chainlinkPrice = getChainlinkPrice();

                // Get UniswapV3 TWAP price
                uint256 twapPrice = getTWAPPrice();

                // Compare and validate deviation
                require(
                    abs(chainlinkPrice, twapPrice) * 100 / chainlinkPrice < 10,
                    "Price deviation too high"
                );

                // Return average
                return (chainlinkPrice + twapPrice) / 2;
            }

            function getChainlinkPrice() internal view returns (uint256) {
                try chainlinkFeed.latestRoundData() returns (
                    uint80 roundId,
                    int price,
                    uint,
                    uint updatedAt,
                    uint80 answeredInRound
                ) {
                    require(updatedAt > 0, "Invalid updatedAt");
                    require(block.timestamp - updatedAt < STALENESS_THRESHOLD, "Stale price");
                    require(answeredInRound >= roundId, "Stale round");
                    require(price > 0, "Invalid price");
                    require(uint256(price) >= MIN_PRICE && uint256(price) <= MAX_PRICE, "Price out of bounds");
                    return uint256(price);
                } catch {
                    revert("Chainlink oracle failure");
                }
            }

            function getTWAPPrice() internal view returns (uint256) {
                uint32[] memory secondsAgos = new uint32[](2);
                secondsAgos[0] = 1800;  // 30 minutes
                secondsAgos[1] = 0;

                (int56[] memory tickCumulatives,) = uniV3Pool.observe(secondsAgos);
                return calculateTWAP(tickCumulatives);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(safe_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should have very few or no oracle vulnerabilities
        # The safe contract implements all best practices
        critical_vulns = [v for v in oracle_vulns if v.severity == "critical"]
        assert len(critical_vulns) == 0  # No critical issues

        high_vulns = [v for v in oracle_vulns if v.severity == "high"]
        assert len(high_vulns) == 0  # No high issues

    def test_real_world_exploit_pattern_moby(self):
        """Test detection of Moby-style exploit pattern (Jan 2025)"""
        moby_pattern = """
        pragma solidity ^0.8.0;

        contract MobyVulnerable {
            IUniswapV2Router02 router;

            function liquidate(address token, uint256 amount) public {
                // Get current price from Uniswap (spot price)
                address[] memory path = new address[](2);
                uint256[] memory amounts = router.getAmountsOut(amount, path);
                uint256 collateralValue = amounts[1];

                // Execute liquidation based on manipulable price
                _executeLiquidation(collateralValue);
            }
        }
        """

        vulns = self.analyzer.analyze_contract(moby_pattern, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # Should detect spot price vulnerability
        spot_vulns = [v for v in oracle_vulns if 'spot' in v.title.lower() or 'flash loan' in v.description.lower()]
        assert len(spot_vulns) >= 1
        assert spot_vulns[0].severity == "critical"

    def test_confidence_scores(self):
        """Test that confidence scores are reasonable"""
        vulnerable_code = """
        pragma solidity ^0.8.0;

        contract TestConfidence {
            AggregatorV3Interface feed;
            IUniswapV2Pair pair;

            function getPrice1() public view returns (uint256) {
                (, int price,,,) = feed.latestRoundData();
                return uint256(price);
            }

            function getPrice2() public view returns (uint256) {
                (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
                return (reserve1 * 1e18) / reserve0;
            }
        }
        """

        vulns = self.analyzer.analyze_contract(vulnerable_code, "test.sol")

        oracle_vulns = [v for v in vulns if v.vulnerability_type == VulnerabilityType.ORACLE_MANIPULATION]

        # All vulnerabilities should have confidence scores
        for vuln in oracle_vulns:
            assert vuln.confidence > 0
            assert vuln.confidence <= 100

            # Critical vulnerabilities should have high confidence
            if vuln.severity == "critical":
                assert vuln.confidence >= 85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
