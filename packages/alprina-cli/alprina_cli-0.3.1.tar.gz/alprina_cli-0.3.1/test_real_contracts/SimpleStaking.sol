// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SimpleStaking
 * @dev Staking contract with intentional gas inefficiencies
 */
contract SimpleStaking {
    address public stakingToken;  // Could be immutable
    address public rewardToken;   // Could be immutable
    address public owner;         // Could be immutable

    uint256 public rewardRate = 100;  // Could be constant or immutable
    uint256 public totalStaked;

    struct UserInfo {
        uint256 amount;
        uint256 rewardDebt;
        uint256 pendingRewards;
    }

    mapping(address => UserInfo) public userInfo;
    address[] public stakers;

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);

    constructor(address _stakingToken, address _rewardToken) {
        owner = msg.sender;
        stakingToken = _stakingToken;
        rewardToken = _rewardToken;
    }

    // Stake tokens
    function stake(uint256 amount) public {
        require(amount > 0, "Cannot stake 0");

        UserInfo storage user = userInfo[msg.sender];

        // Update rewards before changing stake
        _updateRewards(msg.sender);

        // Multiple storage writes
        user.amount = user.amount + amount;
        totalStaked = totalStaked + amount;

        // Add to stakers array if first stake
        if (user.amount == amount) {
            stakers.push(msg.sender);
        }

        emit Staked(msg.sender, amount);
    }

    // Withdraw staked tokens
    function withdraw(uint256 amount) public {
        UserInfo storage user = userInfo[msg.sender];
        require(user.amount >= amount, "Insufficient balance");

        _updateRewards(msg.sender);

        user.amount = user.amount - amount;
        totalStaked = totalStaked - amount;

        emit Withdrawn(msg.sender, amount);
    }

    // Claim rewards
    function claimRewards() public {
        _updateRewards(msg.sender);

        UserInfo storage user = userInfo[msg.sender];
        uint256 reward = user.pendingRewards;
        require(reward > 0, "No rewards");

        user.pendingRewards = 0;
        emit RewardPaid(msg.sender, reward);
    }

    // Update rewards for a user
    function _updateRewards(address account) private {
        UserInfo storage user = userInfo[account];

        if (user.amount > 0) {
            // Inefficient calculation without caching
            uint256 newReward = (user.amount * rewardRate) / 1000;
            user.pendingRewards = user.pendingRewards + newReward;
        }
    }

    // Distribute rewards to all stakers (very inefficient)
    function distributeRewardsToAll() public {
        require(msg.sender == owner, "Only owner");

        // Loop reading array.length every iteration
        for (uint256 i = 0; i < stakers.length; i++) {
            address staker = stakers[i];
            UserInfo storage user = userInfo[staker];

            if (user.amount > 0) {
                uint256 reward = (user.amount * rewardRate) / 1000;
                user.pendingRewards = user.pendingRewards + reward;
            }
        }
    }

    // Emergency withdraw (unchecked math opportunity)
    function emergencyWithdraw() public {
        UserInfo storage user = userInfo[msg.sender];
        uint256 amount = user.amount;

        user.amount = 0;
        user.rewardDebt = 0;
        user.pendingRewards = 0;
        totalStaked = totalStaked - amount;

        emit Withdrawn(msg.sender, amount);
    }

    // View pending rewards (inefficient)
    function pendingReward(address account) public view returns (uint256) {
        UserInfo storage user = userInfo[account];

        // Multiple reads without caching
        if (user.amount > 0) {
            uint256 newReward = (user.amount * rewardRate) / 1000;
            return user.pendingRewards + newReward;
        }

        return user.pendingRewards;
    }

    // Get total number of stakers
    function getTotalStakers() public view returns (uint256) {
        return stakers.length;
    }

    // Update reward rate
    function setRewardRate(uint256 newRate) public {
        require(msg.sender == owner, "Only owner");
        rewardRate = newRate;
    }
}
