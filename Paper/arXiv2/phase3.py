# GRAND UNIFICATION OF GIANTS PHASES 1, 2, and 3

# === Phase 1 & 2 ===

import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.integrate import solve_ivp

np.random.seed(42)

class DualHorizonSystem:
    r"""
    Simulates a dual-horizon system with both Black Hole-like (internal/dissipative)
    and White Hole-like (external/generative) dynamics.
    """

    def __init__(self, dimension=10, internal_horizon=0.5, external_horizon=0.5,
                 dissipation_rate=0.1, generation_rate=0.1,
                 initial_state=None, bounded_capacity=1.0):
        self.dimension = dimension
        self.internal_horizon = internal_horizon
        self.external_horizon = external_horizon
        self.dissipation_rate = dissipation_rate
        self.generation_rate = generation_rate
        self.bounded_capacity = bounded_capacity

        if initial_state is None:
            self.state = np.random.normal(0, 1, dimension)
            self.state = self.state / np.linalg.norm(self.state) * bounded_capacity / 2
        else:
            self.state = initial_state

        self.history = [np.copy(self.state)]
        self.entropy_history = [self.calculate_entropy()]
        self.complexity_history = [self.calculate_complexity()]
        self.novelty_history = [0]
        self.time_points = [0]

    def calculate_entropy(self):
        norm_state = np.abs(self.state) / (np.sum(np.abs(self.state)) + 1e-10)
        entropy = -np.sum(norm_state * np.log2(norm_state + 1e-10))
        return entropy / np.log2(self.dimension)

    def calculate_complexity(self):
        s = self.calculate_entropy()
        return 4 * s * (1 - s)

    def generate_novelty(self, t):
        if self.external_horizon <= 0:
            return np.zeros(self.dimension)

        novelty = np.sin(t * np.arange(1, self.dimension + 1) / self.dimension)
        novelty_norm = np.linalg.norm(novelty)
        if novelty_norm < 1e-8:
            return np.zeros(self.dimension)
        return novelty / novelty_norm * self.generation_rate * self.external_horizon

    def dissipate(self):
        return -self.state * self.dissipation_rate * self.internal_horizon

    def system_dynamics(self, t, y):
        state = y.reshape(self.dimension)
        novelty = self.generate_novelty(t)
        dissipation = -state * self.dissipation_rate * self.internal_horizon
        dydt = novelty + dissipation

        dydt_norm = np.linalg.norm(dydt)
        if dydt_norm > self.bounded_capacity:
            dydt = dydt * (self.bounded_capacity / dydt_norm)

        return dydt.flatten()

    def simulate(self, duration=100.0, steps=1000):
        t_span = (0, duration)
        t_eval = np.linspace(0, duration, steps)
        y0 = self.state.flatten()

        solution = solve_ivp(
            self.system_dynamics,
            t_span,
            y0,
            t_eval=t_eval,
            method='RK45'
        )

        times = solution.t
        states = solution.y.T

        entropies = []
        complexities = []
        novelties = []

        for i in range(len(times)):
            self.state = states[i].reshape(self.dimension)
            entropies.append(self.calculate_entropy())
            complexities.append(self.calculate_complexity())
            if i > 0:
                novelty = np.linalg.norm(states[i] - states[i - 1])
                novelties.append(novelty)
            else:
                novelties.append(0)
            self.history.append(np.copy(self.state))

        self.time_points = times
        self.entropy_history = entropies
        self.complexity_history = complexities
        self.novelty_history = novelties

        return times, states

def run_sweep_and_export():
    print("Starting reflective sweep...")
    dims = [5, 10, 25]
    h_values = np.linspace(0, 1, 6)
    init_states = ['low_entropy', 'mid_entropy', 'high_entropy']

    with open("reflective_sweep_results.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["dimension", "h_plus", "h_minus", "init_type",
                         "final_entropy", "final_complexity", "reflective_closure"])

        for dim in dims:
            for h_plus in h_values:
                for h_minus in h_values:
                    for init_type in init_states:
                        if init_type == 'low_entropy':
                            init = np.zeros(dim)
                            init[0] = 1.0
                        elif init_type == 'high_entropy':
                            init = np.random.normal(0, 1, dim)
                        else:
                            init = np.random.uniform(-1, 1, dim)
                        init = init / (np.linalg.norm(init) + 1e-8) * 0.5

                        system = DualHorizonSystem(
                            dimension=dim,
                            internal_horizon=h_minus,
                            external_horizon=h_plus,
                            dissipation_rate=0.1,
                            generation_rate=0.1,
                            initial_state=init,
                            bounded_capacity=1.0
                        )

                        system.simulate(duration=100.0, steps=1000)
                        entropy = system.entropy_history[-1]
                        complexity = system.complexity_history[-1]
                        reflective_closure = h_plus > 0 and h_minus > 0

                        writer.writerow([dim, h_plus, h_minus, init_type,
                                         round(entropy, 4), round(complexity, 4), reflective_closure])
    print("Reflective sweep complete. Output written to reflective_sweep_results.csv.")

class ReflectiveField:
    def __init__(self, grid_shape=(10, 10), vector_dim=5,
                 h_plus=0.5, h_minus=0.5, alpha=0.2, gen_rate=0.1, diss_rate=0.1):
        self.grid_shape = grid_shape
        self.vector_dim = vector_dim
        self.h_plus = h_plus
        self.h_minus = h_minus
        self.alpha = alpha
        self.gen_rate = gen_rate
        self.diss_rate = diss_rate
        self.grid = np.random.normal(0, 1, grid_shape + (vector_dim,))
        self.grid /= np.linalg.norm(self.grid, axis=-1, keepdims=True) + 1e-8
        self.history = [self.grid.copy()]

    def generate_novelty(self, t):
        sine_wave = np.sin(t * np.arange(1, self.vector_dim + 1) / self.vector_dim)
        norm = np.linalg.norm(sine_wave)
        return sine_wave / norm * self.gen_rate * self.h_plus if norm > 1e-8 else np.zeros(self.vector_dim)

    def dissipate(self, state):
        return -state * self.diss_rate * self.h_minus

    def neighbor_mean(self, grid, i, j):
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = i + dx, j + dy
            if 0 <= ni < self.grid_shape[0] and 0 <= nj < self.grid_shape[1]:
                neighbors.append(grid[ni, nj])
        return np.mean(neighbors, axis=0) if neighbors else np.zeros(self.vector_dim)

    def step(self, t):
        new_grid = np.zeros_like(self.grid)
        novelty = self.generate_novelty(t)
        for i in range(self.grid_shape[0]):
            for j in range(self.grid_shape[1]):
                state = self.grid[i, j]
                diss = self.dissipate(state)
                neigh = self.neighbor_mean(self.grid, i, j)
                update = state + novelty + diss + self.alpha * (neigh - state)
                norm = np.linalg.norm(update)
                new_grid[i, j] = update / norm if norm > 1e-8 else update
        self.grid = new_grid
        self.history.append(self.grid.copy())

    def run(self, steps=50):
        for t in range(steps):
            self.step(t)

    def plot_entropy_map(self, step=-1):
        grid = self.history[step]
        entropy = -np.sum(np.abs(grid) * np.log2(np.abs(grid) + 1e-10), axis=-1)
        entropy /= np.log2(self.vector_dim)
        plt.figure(figsize=(6, 5))
        plt.imshow(entropy, cmap='plasma', origin='lower')
        plt.colorbar(label='Normalized Entropy')
        plt.title(f"Entropy Map at Step {step if step >= 0 else len(self.history)-1}")
        plt.xlabel("j")
        plt.ylabel("i")
        plt.tight_layout()
        plt.savefig("phase2_entropy_map.png", dpi=300)
        plt.close()


    print("\nRunning Phase 1 Dual Horizon Sweep...")
    run_sweep_and_export()


# === Phase 3 ===
"""
Enhanced Implementation of Phase 3 of the Giants Framework

This implementation adds the Mutually Assured Progress (MAP) mechanism to the multi-agent
reflective field, enabling trust propagation and symbiotic cognition between agents.

Key additions:
- Trust network between agents
- MAP calculation based on state trajectory alignment and entropy stabilization
- Visualization of agent clusters and trust networks
- Metrics for measuring emergent alignment
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba

class ReflectiveAgent:
    def __init__(self, position, vector_dim=5):
        self.position = position  # (i, j) position in grid
        self.state = np.random.normal(0, 1, vector_dim)
        self.state = self.state / (np.linalg.norm(self.state) + 1e-10)  # Normalize
        self.vector_dim = vector_dim
        self.history = [self.state.copy()]
        self.entropy_trace = []
        self.trust_network = {}  # Maps (i,j) -> trust value
        
    def entropy(self):
        """Calculate normalized entropy of the agent's state vector"""
        norm = np.abs(self.state) / (np.sum(np.abs(self.state)) + 1e-10)
        s = -np.sum(norm * np.log2(norm + 1e-10))
        return s / np.log2(self.vector_dim)
    
    def state_derivative(self):
        """Calculate rate of change in state vector"""
        if len(self.history) < 2:
            return np.zeros(self.vector_dim)
        return self.history[-1] - self.history[-2]
    
    def entropy_derivative(self):
        """Calculate rate of change in entropy"""
        if len(self.entropy_trace) < 2:
            return 0
        return self.entropy_trace[-1] - self.entropy_trace[-2]
        
    def update_state(self, novelty, dissipation, neighbor_influences):
        """
        Update agent state based on:
        - External novelty signal
        - Internal dissipation (decay)
        - Weighted influences from neighbors based on trust
        """
        # Combine all influences
        total_influence = novelty + dissipation
        for neighbor_state, trust in neighbor_influences:
            influence = trust * (neighbor_state - self.state)
            total_influence += influence
            
        # Apply influence to update state
        next_state = self.state + total_influence
        
        # Normalize to maintain bounded representation
        norm = np.linalg.norm(next_state)
        self.state = next_state / norm if norm > 1e-8 else next_state
        
        # Record history
        self.history.append(self.state.copy())
        self.entropy_trace.append(self.entropy())

class MultiAgentReflectiveField:
    def __init__(self, shape=(10, 10), vector_dim=5):
        self.shape = shape
        self.vector_dim = vector_dim
        # Initialize grid with agents that know their positions
        self.grid = [[ReflectiveAgent((i, j), vector_dim) for j in range(shape[1])] for i in range(shape[0])]
        self.steps = 0
        self.global_entropy_history = []
        self.alignment_history = []
        
    def calculate_MAP(self, agent1, agent2):
        """
        Calculate Mutually Assured Progress between two agents
        MAP_ij(t) = f(∂Φ_i/∂t, ∂Φ_j/∂t, ∂S_i/∂t, ∂S_j/∂t)
        
        Higher values indicate agents are moving in aligned directions
        both in state space and entropy dynamics
        """
        # Get state derivatives
        d_state_i = agent1.state_derivative()
        d_state_j = agent2.state_derivative()
        
        # Get entropy derivatives
        d_entropy_i = agent1.entropy_derivative()
        d_entropy_j = agent2.entropy_derivative()
        
        # Calculate state alignment (cosine similarity)
        state_alignment = np.dot(d_state_i, d_state_j) / (
            np.linalg.norm(d_state_i) * np.linalg.norm(d_state_j) + 1e-10)
            
        # Calculate entropy alignment (both increasing or both decreasing)
        entropy_alignment = np.sign(d_entropy_i) * np.sign(d_entropy_j)
        
        # Combine into MAP score
        # When agents move in similar directions AND have similar entropy changes,
        # they are considered to be progressing together
        map_score = 0.7 * state_alignment + 0.3 * entropy_alignment
        
        # Bound between 0 and 1 for use as trust value
        return (map_score + 1) / 2

    def update_trust_networks(self):
        """Update trust relationships between all neighboring agents"""
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                agent = self.grid[i][j]
                agent.trust_network = {}  # Reset trust network
                
                # Check each neighbor
                for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.shape[0] and 0 <= nj < self.shape[1]:
                        neighbor = self.grid[ni][nj]
                        
                        # Calculate MAP between this agent and its neighbor
                        if len(agent.history) > 1:  # Need history to calculate derivatives
                            trust = self.calculate_MAP(agent, neighbor)
                            agent.trust_network[(ni, nj)] = trust
                        else:
                            # Initial trust is neutral
                            agent.trust_network[(ni, nj)] = 0.5

    def get_neighbor_influences(self, i, j):
        """Get states and trust values of neighboring agents"""
        agent = self.grid[i][j]
        influences = []
        
        for pos, trust in agent.trust_network.items():
            ni, nj = pos
            neighbor = self.grid[ni][nj]
            influences.append((neighbor.state, trust))
            
        return influences

    def calculate_global_entropy(self):
        """Calculate system-wide entropy"""
        entropies = [self.grid[i][j].entropy() for i in range(self.shape[0]) 
                    for j in range(self.shape[1])]
        return np.mean(entropies)
    
    def calculate_alignment(self):
        """Measure overall alignment of agent states"""
        all_states = [self.grid[i][j].state for i in range(self.shape[0]) 
                     for j in range(self.shape[1])]
        
        # Convert to array for easier calculation
        states_array = np.array(all_states)
        
        # Calculate average pairwise cosine similarity
        dot_products = np.dot(states_array, states_array.T)
        norms = np.linalg.norm(states_array, axis=1)
        norm_matrix = np.outer(norms, norms)
        
        # Get average similarity, excluding self-similarity
        n = states_array.shape[0]
        total_similarity = np.sum(dot_products / (norm_matrix + 1e-10)) - n  # Subtract diagonal
        avg_similarity = total_similarity / (n * (n - 1))
        
        return avg_similarity
        
    def run(self, timesteps=100):
        """Run the simulation for a specified number of timesteps"""
        for t in range(timesteps):
            # Generate novelty signal (same for all agents)
            novelty = np.sin(t * np.arange(1, self.vector_dim + 1) / self.vector_dim)
            novelty /= np.linalg.norm(novelty) + 1e-10
            novelty *= 0.05  # Reduced strength for more stable dynamics
            
            # Update trust networks based on previous states
            if t > 0:
                self.update_trust_networks()
            
            # Update each agent
            for i in range(self.shape[0]):
                for j in range(self.shape[1]):
                    agent = self.grid[i][j]
                    dissipation = -agent.state * 0.05  # Reduced dissipation
                    neighbor_influences = self.get_neighbor_influences(i, j)
                    agent.update_state(novelty, dissipation, neighbor_influences)
            
            # Track global metrics
            self.global_entropy_history.append(self.calculate_global_entropy())
            self.alignment_history.append(self.calculate_alignment())
            self.steps += 1
            
            # Optional progress output
            if t % 10 == 0 or t == timesteps - 1:
                print(f"Step {t}: Global Entropy = {self.global_entropy_history[-1]:.4f}, "
                      f"Alignment = {self.alignment_history[-1]:.4f}")

    def visualize_state_space(self, dims=(0, 1, 2)):
        """Visualize agent states in 3D state space for specified dimensions"""
        if self.vector_dim < 3:
            print("Vector dimension too small for 3D visualization")
            return
            
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Get trust-based communities for coloring
        communities = self.detect_communities()
        
        # Define colors for communities
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        
        # Plot each agent as a point in state space
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                agent = self.grid[i][j]
                x, y, z = [agent.state[dim] for dim in dims]
                
                # Color based on community
                community_id = communities.get((i, j), 0)
                color = colors[community_id % len(colors)]
                
                ax.scatter(x, y, z, c=color, marker='o')
                
                # Draw lines to trusted neighbors
                for pos, trust in agent.trust_network.items():
                    if trust > 0.7:  # Only show strong trust connections
                        ni, nj = pos
                        neighbor = self.grid[ni][nj]
                        nx, ny, nz = [neighbor.state[dim] for dim in dims]
                        ax.plot([x, nx], [y, ny], [z, nz], 'k-', alpha=0.3)
        
        ax.set_xlabel(f'Dimension {dims[0]}')
        ax.set_ylabel(f'Dimension {dims[1]}')
        ax.set_zlabel(f'Dimension {dims[2]}')
        ax.set_title('Agent States in Vector Space')
        plt.tight_layout()
        plt.savefig("phase3_metrics.png", dpi=300)
        plt.close()
    
    def visualize_metrics(self):
        """Visualize the evolution of global metrics over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # Plot global entropy
        ax1.plot(range(self.steps), self.global_entropy_history, 'b-')
        ax1.set_ylabel('Global Entropy')
        ax1.set_title('System Evolution Metrics')
        
        # Plot alignment
        ax2.plot(range(self.steps), self.alignment_history, 'r-')
        ax2.set_ylabel('Agent Alignment')
        ax2.set_xlabel('Time Steps')
        
        plt.tight_layout()
        plt.savefig("phase3_state_space.png", dpi=300)
        plt.close()
    
    def visualize_trust_network(self):
        """Visualize the trust network between agents"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw agents as grid of points
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                ax.scatter(i, j, c='b', s=100)
                
                # Draw trust connections
                agent = self.grid[i][j]
                for pos, trust in agent.trust_network.items():
                    ni, nj = pos
                    # Thickness and color based on trust
                    lw = trust * 3
                    color = to_rgba('green', alpha=trust)
                    if lw > 0.5:  # Only show significant trust
                        ax.plot([i, ni], [j, nj], c=color, lw=lw)
        
        ax.set_xlim(-1, self.shape[0])
        ax.set_ylim(-1, self.shape[1])
        ax.set_xticks(range(self.shape[0]))
        ax.set_yticks(range(self.shape[1]))
        ax.set_title('Trust Network Between Agents')
        ax.grid(True)
        plt.tight_layout()
        plt.savefig("phase3_trust_network.png", dpi=300)
        plt.close()
    
    def detect_communities(self):
        """
        Simple community detection based on trust thresholds
        Returns a dictionary mapping positions to community IDs
        """
        # Initialize each agent as its own community
        communities = {(i, j): -1 for i in range(self.shape[0]) for j in range(self.shape[1])}
        visited = set()
        
        def dfs(i, j, community_id):
            """Depth-first search to find connected trust communities"""
            if (i, j) in visited:
                return
                
            visited.add((i, j))
            communities[(i, j)] = community_id
            
            # Add strongly trusted neighbors to same community
            agent = self.grid[i][j]
            for pos, trust in agent.trust_network.items():
                if trust > 0.6:  # Trust threshold for community membership
                    ni, nj = pos
                    dfs(ni, nj, community_id)
        
        # Find communities
        community_id = 0
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if (i, j) not in visited:
                    dfs(i, j, community_id)
                    community_id += 1
                    
        return communities

# === Runtime Phase Selector ===

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], default=3,
                        help="Which phase of the simulation to run (1, 2, or 3)")
    args = parser.parse_args()

    if args.phase == 1:
        print("Running Phase 1: Dual Horizon Sweep")
        run_sweep_and_export()
    elif args.phase == 2:
        print("Running Phase 2: Distributed Reflective Field")
        sim = ReflectiveField()
        sim.run(steps=50)
        sim.plot_entropy_map()
    else:
        print("Running Phase 3: Multi-Agent Reflective Field with MAP")
        field = MultiAgentReflectiveField(shape=(8, 8), vector_dim=5)
        field.run(timesteps=100)
        field.visualize_metrics()
        field.visualize_trust_network()
        field.visualize_state_space()
