#!/usr/bin/env python3
"""
PVZ AI - Q-Learning Version
Uses Q-Learning table to learn optimal actions
"""

import pygame
import random
import time
import math
import json
import numpy as np

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("PVZ Q-Learning AI")

# Import base game
try:
    exec(open('/home/vboxuser/.openclaw/workspace/pvz_learning_ai.py').read())
except Exception as e:
    print(f"Error loading game: {e}")
    import sys
    sys.exit(1)

class QLearningAgent:
    """Q-Learning Agent for PVZ"""
    
    def __init__(self):
        # Q-table: state -> action values
        self.q_table = {}
        
        # Learning parameters
        self.learning_rate = 0.1  # Alpha
        self.discount_factor = 0.95  # Gamma
        self.epsilon = 0.3  # Epsilon-greedy exploration rate
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        
        # State discretization
        self.sun_bins = [0, 50, 150, 300, 500]  # Sun ranges
        self.zombie_bins = [0, 1, 3, 5, 10]  # Zombie count ranges
        self.wave_bins = [1, 3, 5, 10]  # Wave ranges
        
        # Actions
        self.actions = [
            'wait',
            'collect_sun',
            'place_sunflower_back',
            'place_sunflower_mid',
            'place_peashooter_back',
            'place_peashooter_mid',
            'place_wallnut_front'
        ]
        
        # Statistics
        self.state_visits = {}
        self.total_rewards = 0
        self.episodes = 0
        
        # Load if exists
        self.load()
    
    def get_state(self, game_state):
        """Discretize continuous state into bins"""
        sun = game_state['sun']
        zombies = len([z for z in game_state['zombies'] if not z.dying])
        wave = game_state['wave']
        
        # Bin the values
        sun_bin = min(i for i, val in enumerate(self.sun_bins) if sun < val)
        zombie_bin = min(i for i, val in enumerate(self.zombie_bins) if zombies < val)
        wave_bin = min(i for i, val in enumerate(self.wave_bins) if wave < val)
        
        # Count plants by row
        plant_counts = [0] * 5
        for plant in game_state['plants']:
            plant_counts[plant.row] += 1
        
        return (sun_bin, zombie_bin, wave_bin, tuple(plant_counts))
    
    def get_q_values(self, state):
        """Get Q-values for all actions in a state"""
        if state not in self.q_table:
            # Initialize with small random values
            self.q_table[state] = {action: random.uniform(-0.1, 0.1) for action in self.actions}
        
        return self.q_table[state]
    
    def choose_action(self, state, available_actions):
        """Epsilon-greedy action selection"""
        if random.random() < self.epsilon:
            # Explore: random action
            return random.choice(available_actions)
        else:
            # Exploit: best action
            q_values = self.get_q_values(state)
            available_q = {a: q_values[a] for a in available_actions}
            return max(available_q, key=available_q.get)
    
    def update_q(self, state, action, reward, next_state):
        """Q-Learning update rule"""
        current_q = self.get_q_values(state)[action]
        max_next_q = max(self.get_q_values(next_state).values())
        
        # Q(s,a) = Q(s,a) + alpha * [reward + gamma * max(Q(s',a')) - Q(s,a)]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        
        self.q_table[state][action] = new_q
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def get_available_actions(self, game_state):
        """Get actions available in current state"""
        actions = ['wait']
        
        sun = game_state['sun']
        grid = game_state['grid']
        plants = game_state['plants']
        
        # Can collect sun?
        if any(s.active for s in game_state['suns']):
            actions.append('collect_sun')
        
        # Plant actions
        if sun >= 50:
            # Find empty spots
            for col in range(2):  # Back columns
                for row in range(5):
                    if grid[col][row] is None:
                        actions.append('place_sunflower_back')
                        break
                else:
                    break
        
        if sun >= 100:
            for col in range(2, 5):  # Mid columns
                for row in range(5):
                    if grid[col][row] is None:
                        actions.append('place_peashooter_mid')
                        break
                else:
                    break
        
        if sun >= 50:
            for col in range(6, 8):  # Front columns
                for row in range(5):
                    if grid[col][row] is None:
                        actions.append('place_wallnut_front')
                        break
                else:
                    break
        
        return list(set(actions))  # Remove duplicates
    
    def calculate_reward(self, game_state, action, next_game_state):
        """Calculate reward for an action"""
        reward = 0
        
        # Basic reward/penalties
        if action == 'wait':
            reward = -0.1  # Small penalty for waiting
        elif action == 'collect_sun':
            reward = 1.0
        elif action.startswith('place_'):
            reward = 0.5
            # Bonus for placing in good positions
            if 'sunflower' in action and 'back' in action:
                reward += 0.3
            if 'peashooter' in action and 'mid' in action:
                reward += 0.3
        
        # Check if zombie was damaged
        old_zombies = len([z for z in game_state['zombies'] if not z.dying])
        new_zombies = len([z for z in next_game_state['zombies'] if not z.dying])
        if new_zombies < old_zombies:
            reward += 2.0  # Bonus for damaging zombies
        
        # Penalty if plant died
        old_plants = len(game_state['plants'])
        new_plants = len(next_game_state['plants'])
        if new_plants < old_plants:
            reward -= 1.0
        
        # Check if game progressed
        if next_game_state['wave'] > game_state['wave']:
            reward += 5.0  # Wave completion bonus
        
        # Game over penalty
        if next_game_state.get('game_over', False):
            reward = -50.0
        
        # Progress reward
        total_waves = (next_game_state['level'] - 1) * 5 + next_game_state['wave']
        reward += total_waves * 0.1
        
        return reward
    
    def save(self):
        """Save Q-table"""
        # Convert tuple keys to strings for JSON
        serializable = {}
        for state, actions in self.q_table.items():
            state_str = str(state)
            serializable[state_str] = actions
        
        data = {
            'q_table': serializable,
            'epsilon': self.epsilon,
            'episodes': self.episodes
        }
        
        with open('q_learning_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load Q-table"""
        if os.path.exists('q_learning_data.json'):
            try:
                with open('q_learning_data.json', 'r') as f:
                    data = json.load(f)
                    
                # Convert string keys back to tuples
                self.q_table = {}
                for state_str, actions in data['q_table'].items():
                    self.q_table[eval(state_str)] = actions
                
                self.epsilon = data.get('epsilon', 0.3)
                self.episodes = data.get('episodes', 0)
                print(f"Loaded Q-Learning agent: {len(self.q_table)} states, epsilon={self.epsilon:.3f}")
            except Exception as e:
                print(f"Could not load Q-table: {e}")

# Use Q-Learning agent in game
class QLearningGame(Game):
    """Game wrapper for Q-Learning"""
    
    def __init__(self):
        super().__init__()
        self.q_agent = QLearningAgent()
        self.previous_state = None
        self.previous_action = None
    
    def auto_play_ai_decide(self):
        """Q-Learning decision making"""
        if self.game_over or self.paused:
            return
        
        current_time = time.time()
        if current_time - self.last_ai_action < self.ai_action_interval:
            return
        
        self.last_ai_action = current_time
        
        # Get current state
        game_state = {
            'sun': self.sun_count,
            'zombies': self.zombies,
            'plants': self.plants,
            'grid': self.grid,
            'suns': self.suns,
            'wave': self.wave,
            'level': self.level
        }
        
        state = self.q_agent.get_state(game_state)
        available_actions = self.q_agent.get_available_actions(game_state)
        
        # Choose and execute action
        action = self.q_agent.choose_action(state, available_actions)
        
        # Execute action and calculate reward
        next_game_state = self._simulate_action(action, game_state)
        
        if self.previous_state is not None:
            reward = self.q_agent.calculate_reward(
                {k: game_state[k] for k in ['sun', 'zombies', 'plants', 'grid', 'suns', 'wave', 'level']},
                self.previous_action,
                {k: next_game_state[k] for k in ['sun', 'zombies', 'plants', 'grid', 'suns', 'wave', 'level', 'game_over']}
            )
            self.q_agent.update_q(self.previous_state, self.previous_action, reward, state)
        
        self.previous_state = state
        self.previous_action = action
        
        # Actually execute the action
        self._execute_action(action, game_state)
        
        # Decay exploration
        self.q_agent.decay_epsilon()
        
        # Log
        if random.random() < 0.1:  # Log 10% of actions
            self.ai_log(f"Q: {action[:15]}... | e={self.q_agent.epsilon:.2f}")
    
    def _simulate_action(self, action, game_state):
        """Simulate action result for reward calculation"""
        # Simplified simulation - just return current state
        return {k: game_state[k] for k in ['sun', 'zombies', 'plants', 'grid', 'suns', 'wave', 'level', 'game_over']}
    
    def _execute_action(self, action, game_state):
        """Execute the chosen action"""
        if action == 'wait':
            pass  # Do nothing
        elif action == 'collect_sun':
            for sun in self.suns[:]:
                if sun.active:
                    self.sun_count += sun.value
                    self.suns.remove(sun)
                    break
        elif action.startswith('place_'):
            # Parse action
            if 'sunflower_back' in action:
                plant_type = 'sunflower'
                cols, rows = range(2), range(5)
            elif 'peashooter_mid' in action:
                plant_type = 'peashooter'
                cols, rows = range(2, 5), range(5)
            elif 'wallnut_front' in action:
                plant_type = 'wallnut'
                cols, rows = range(6, 8), range(5)
            else:
                return
            
            # Find first empty spot
            for col in cols:
                for row in rows:
                    if self.grid[col][row] is None:
                        self._place_plant(col, row, plant_type)
                        return

# Run Q-Learning training
def run_q_learning_training(games=100):
    """Run Q-Learning training"""
    
    print("="*70)
    print(" " * 20 + "Q-LEARNING TRAINING" + " " * 20)
    print("="*70)
    print(f"Training for {games} episodes")
    print("Features:")
    print("  - Q-Table with state discretization")
    print("  - Epsilon-greedy exploration")
    print("  - Reward-based learning")
    print("="*70)
    
    game = QLearningGame()
    
    for episode in range(games):
        # Reset game
        game = QLearningGame()
        game.auto_play = True
        game.game_over = False
        game._reset_game()
        
        # Run one episode
        step = 0
        while not game.game_over and step < 1000:  # Max steps per episode
            game.auto_play_ai_decide()
            game.update()
            step += 1
            
            if step % 100 == 0:
                print(f"Episode {episode+1}/{games}: Step {step}, Epsilon: {game.q_agent.epsilon:.3f}, "
                      f"Q-table size: {len(game.q_agent.q_table)}")
        
        # Update agent
        game.q_agent.episodes += 1
        game.q_agent.save()
        
        # Log result
        total_waves = (game.level - 1) * 5 + game.current_level_waves
        print(f"Episode {episode+1}: {total_waves} waves completed | "
              f"Q-states: {len(game.q_agent.q_table)} | "
              f"Epsilon: {game.q_agent.epsilon:.3f}")
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    game.q_agent.save()
    
    # Show top Q-values for some states
    print("\nSample Q-Values:")
    state_count = 0
    for state, actions in list(game.q_agent.items())[:10]:
        print(f"  State {state}:")
        for action, value in sorted(actions.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"    {action}: {value:.3f}")
        state_count += 1
        if state_count >= 5:
            break

if __name__ == "__main__":
    run_q_learning_training(games=100)
