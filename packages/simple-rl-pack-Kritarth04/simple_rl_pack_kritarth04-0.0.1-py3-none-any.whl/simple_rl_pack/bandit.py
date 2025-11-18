# src/simple_rl_pack/bandit.py
import random

class EpsilonGreedyBandit:
    """
    A simple Multi-Armed Bandit solver using the Epsilon-Greedy algorithm.
    
    This class represents a set of 'arms' (like slot machines) and
    learns which one gives the best reward over time.
    """
    
    def __init__(self, num_arms: int, epsilon: float = 0.1):
        """
        Initializes the bandit.
        
        Args:
            num_arms (int): The number of arms (actions) available.
            epsilon (float): The probability of 'exploring' (choosing a 
                             random arm) instead of 'exploiting' (choosing
                             the current best arm). Must be between 0 and 1.
        """
        if not 0 <= epsilon <= 1:
            raise ValueError("Epsilon must be between 0 and 1")
        if num_arms <= 0:
            raise ValueError("Number of arms must be positive")
            
        self.num_arms = num_arms
        self.epsilon = epsilon
        
        # Stores the estimated value (average reward) of each arm
        self.q_values = [0.0] * num_arms
        # Stores the number of times each arm has been pulled
        self.action_counts = [0] * num_arms

    def select_action(self) -> int:
        """
        Selects an arm to pull using the Epsilon-Greedy strategy.
        
        Returns:
            int: The index of the arm to pull (0 to num_arms-1).
        """
        if random.random() < self.epsilon:
            # --- Explore ---
            # Choose a random arm
            return random.randrange(self.num_arms)
        else:
            # --- Exploit ---
            # Choose the arm with the highest Q-value
            # We break ties randomly
            max_q = max(self.q_values)
            best_arms = [i for i, q in enumerate(self.q_values) if q == max_q]
            return random.choice(best_arms)

    def update_value(self, arm: int, reward: float):
        """
        Updates the value of the arm that was pulled based on the reward.
        
        Args:
            arm (int): The index of the arm that was pulled.
            reward (float): The reward received from pulling that arm.
        """
        if not 0 <= arm < self.num_arms:
            raise ValueError(f"Invalid arm {arm}. Must be 0-{self.num_arms - 1}")
            
        self.action_counts[arm] += 1
        n = self.action_counts[arm]
        old_q = self.q_values[arm]
        
        # Update rule using incremental average:
        # Q_n = Q_{n-1} + (1/n) * (R_n - Q_{n-1})
        new_q = old_q + (1.0 / n) * (reward - old_q)
        self.q_values[arm] = new_q

    def get_best_arm(self) -> int:
        """Returns the arm with the current highest estimated value."""
        return self.q_values.index(max(self.q_values))