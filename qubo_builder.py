"""
QUBO Builder for Time-Windowed TSP/VRP Optimization
Part of the Quantum-Enhanced AI Logistics Engine
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import itertools

class QUBOBuilder:
    """Builds QUBO formulations for Vehicle Routing Problems with time windows"""
    
    def __init__(self, lambda_penalty: float = 100.0):
        self.lambda_penalty = lambda_penalty
        
    def build_time_dependent_tsp_qubo(self, 
                                    time_matrix: np.ndarray,
                                    time_windows: Optional[List[Tuple[float, float]]] = None,
                                    capacity_constraints: Optional[List[float]] = None,
                                    depot_index: int = 0) -> Tuple[Dict, Dict]:
        """
        Build QUBO for time-dependent TSP with time windows
        
        Args:
            time_matrix: NxN matrix of travel times between nodes
            time_windows: List of (earliest, latest) time windows for each node
            capacity_constraints: List of capacity requirements for each node
            depot_index: Index of the depot/starting node
            
        Returns:
            Q: Dictionary mapping (var_i, var_j) -> coefficient
            var_index: Dictionary mapping (node, position) -> variable index
        """
        N = time_matrix.shape[0]
        
        # Create variable mapping: x_{i,p} = node i at position p
        var_index = {}
        idx = 0
        for i in range(N):
            for p in range(N):
                var_index[(i, p)] = idx
                idx += 1
        
        Q = defaultdict(float)
        
        # Objective: Minimize total travel time
        # sum_{p=0}^{N-1} sum_{i=0}^{N-1} sum_{j=0}^{N-1} d_{ij} * x_{i,p} * x_{j,p+1}
        for p in range(N):
            p_next = (p + 1) % N
            for i in range(N):
                for j in range(N):
                    if i == j:
                        continue
                    
                    vi = var_index[(i, p)]
                    vj = var_index[(j, p_next)]
                    Q[(vi, vj)] += time_matrix[i, j]
        
        # Constraint 1: Each node visited exactly once
        for i in range(N):
            vars_i = [var_index[(i, p)] for p in range(N)]
            
            # Quadratic penalty: sum of all pairs
            for a, b in itertools.combinations(vars_i, 2):
                Q[(a, b)] += 2 * self.lambda_penalty
            
            # Linear terms: -2 * sum of variables
            for a in vars_i:
                Q[(a, a)] += -2 * self.lambda_penalty
            
            # Constant term
            Q[('const',)] += self.lambda_penalty
        
        # Constraint 2: Each position has exactly one node
        for p in range(N):
            vars_p = [var_index[(i, p)] for i in range(N)]
            
            # Quadratic penalty
            for a, b in itertools.combinations(vars_p, 2):
                Q[(a, b)] += 2 * self.lambda_penalty
            
            # Linear terms
            for a in vars_p:
                Q[(a, a)] += -2 * self.lambda_penalty
            
            # Constant term
            Q[('const',)] += self.lambda_penalty
        
        # Time window constraints (soft penalties)
        if time_windows:
            Q = self._add_time_window_constraints(Q, var_index, time_matrix, time_windows, N)
        
        # Capacity constraints (for VRP)
        if capacity_constraints:
            Q = self._add_capacity_constraints(Q, var_index, capacity_constraints, N)
        
        return Q, var_index
    
    def _add_time_window_constraints(self, Q: Dict, var_index: Dict, 
                                   time_matrix: np.ndarray, 
                                   time_windows: List[Tuple[float, float]], 
                                   N: int) -> Dict:
        """Add time window constraints as soft penalties"""
        
        # Estimate arrival time for each position
        for i in range(N):
            if i == 0:  # Skip depot
                continue
                
            earliest, latest = time_windows[i]
            
            for p in range(N):
                # Estimate arrival time at position p
                # Simple heuristic: sum of minimum travel times for first p positions
                min_travel_time = np.min(time_matrix[time_matrix > 0]) * p
                service_time = 5.0  # Average service time per node
                estimated_arrival = min_travel_time + p * service_time
                
                # Add penalty if estimated arrival is outside time window
                if estimated_arrival < earliest:
                    # Too early - add penalty
                    vi = var_index[(i, p)]
                    Q[(vi, vi)] += self.lambda_penalty * (earliest - estimated_arrival) / 60.0
                elif estimated_arrival > latest:
                    # Too late - add penalty
                    vi = var_index[(i, p)]
                    Q[(vi, vi)] += self.lambda_penalty * (estimated_arrival - latest) / 60.0
        
        return Q
    
    def _add_capacity_constraints(self, Q: Dict, var_index: Dict, 
                                capacity_constraints: List[float], N: int) -> Dict:
        """Add vehicle capacity constraints"""
        
        # For simplicity, assume single vehicle with capacity limit
        max_capacity = 100.0  # Maximum vehicle capacity
        
        for p in range(N):
            # Calculate cumulative capacity up to position p
            for i in range(N):
                vi = var_index[(i, p)]
                capacity = capacity_constraints[i] if i < len(capacity_constraints) else 1.0
                
                # Add penalty if capacity exceeds limit
                if capacity > max_capacity:
                    Q[(vi, vi)] += self.lambda_penalty * (capacity - max_capacity) / max_capacity
        
        return Q
    
    def build_vrp_qubo(self, 
                      time_matrix: np.ndarray,
                      demands: List[float],
                      vehicle_capacity: float,
                      num_vehicles: int = 3,
                      time_windows: Optional[List[Tuple[float, float]]] = None) -> Tuple[Dict, Dict]:
        """
        Build QUBO for Vehicle Routing Problem (VRP)
        
        Args:
            time_matrix: NxN matrix of travel times
            demands: List of demand at each node
            vehicle_capacity: Capacity of each vehicle
            num_vehicles: Number of vehicles available
            time_windows: Optional time windows for each node
            
        Returns:
            Q: QUBO dictionary
            var_index: Variable mapping
        """
        N = time_matrix.shape[0]
        
        # Variables: x_{i,j,k} = vehicle k travels from node i to node j
        var_index = {}
        idx = 0
        
        for k in range(num_vehicles):
            for i in range(N):
                for j in range(N):
                    if i != j:  # No self-loops
                        var_index[(i, j, k)] = idx
                        idx += 1
        
        Q = defaultdict(float)
        
        # Objective: Minimize total travel time
        for k in range(num_vehicles):
            for i in range(N):
                for j in range(N):
                    if i != j:
                        var_ij = var_index[(i, j, k)]
                        Q[(var_ij, var_ij)] += time_matrix[i, j]
        
        # Constraint 1: Each customer visited exactly once
        for j in range(1, N):  # Skip depot
            vars_to_j = [var_index[(i, j, k)] for k in range(num_vehicles) 
                        for i in range(N) if i != j and (i, j, k) in var_index]
            
            # Quadratic penalty
            for a, b in itertools.combinations(vars_to_j, 2):
                Q[(a, b)] += 2 * self.lambda_penalty
            
            # Linear terms
            for a in vars_to_j:
                Q[(a, a)] += -2 * self.lambda_penalty
            
            Q[('const',)] += self.lambda_penalty
        
        # Constraint 2: Each vehicle leaves depot exactly once
        for k in range(num_vehicles):
            vars_from_depot = [var_index[(0, j, k)] for j in range(1, N)]
            
            for a, b in itertools.combinations(vars_from_depot, 2):
                Q[(a, b)] += 2 * self.lambda_penalty
            
            for a in vars_from_depot:
                Q[(a, a)] += -2 * self.lambda_penalty
            
            Q[('const',)] += self.lambda_penalty
        
        # Constraint 3: Capacity constraints (simplified)
        for k in range(num_vehicles):
            total_demand = sum(demands[1:])  # Exclude depot
            if total_demand > vehicle_capacity:
                # Add penalty proportional to capacity violation
                penalty = self.lambda_penalty * (total_demand - vehicle_capacity) / vehicle_capacity
                for i in range(N):
                    for j in range(1, N):
                        if i != j and (i, j, k) in var_index:
                            var_ij = var_index[(i, j, k)]
                            Q[(var_ij, var_ij)] += penalty
        
        return Q, var_index
    
    def extract_solution(self, solution: Dict, var_index: Dict, problem_type: str = 'tsp') -> List[int]:
        """
        Extract route from binary solution
        
        Args:
            solution: Dictionary mapping variable indices to binary values
            var_index: Variable mapping dictionary
            problem_type: 'tsp' or 'vrp'
            
        Returns:
            List of node indices representing the route
        """
        if problem_type == 'tsp':
            return self._extract_tsp_solution(solution, var_index)
        elif problem_type == 'vrp':
            return self._extract_vrp_solution(solution, var_index)
        else:
            raise ValueError(f"Unknown problem type: {problem_type}")
    
    def _extract_tsp_solution(self, solution: Dict, var_index: Dict) -> List[int]:
        """Extract TSP route from solution"""
        # Find which node is at each position
        position_to_node = {}
        
        for (node, pos), var_idx in var_index.items():
            if solution.get(var_idx, 0) == 1:
                position_to_node[pos] = node
        
        # Build route in order
        route = []
        for pos in sorted(position_to_node.keys()):
            route.append(position_to_node[pos])
        
        return route
    
    def _extract_vrp_solution(self, solution: Dict, var_index: Dict) -> List[List[int]]:
        """Extract VRP routes from solution"""
        routes = []
        
        # Group by vehicle
        vehicle_routes = defaultdict(list)
        
        for (i, j, k), var_idx in var_index.items():
            if solution.get(var_idx, 0) == 1:
                vehicle_routes[k].append((i, j))
        
        # Build routes for each vehicle
        for k in sorted(vehicle_routes.keys()):
            route_edges = vehicle_routes[k]
            if not route_edges:
                continue
                
            # Start from depot
            current = 0
            route = [current]
            
            while True:
                next_node = None
                for i, j in route_edges:
                    if i == current:
                        next_node = j
                        break
                
                if next_node is None or next_node == 0:  # Back to depot or no more nodes
                    break
                
                route.append(next_node)
                current = next_node
            
            if len(route) > 1:  # Only add non-empty routes
                routes.append(route)
        
        return routes

def create_sample_problem() -> Tuple[np.ndarray, List[Tuple[float, float]]]:
    """Create a sample TSP problem for testing"""
    # Sample coordinates (same as traffic simulator)
    coords = [
        (28.6139, 77.2090),  # Depot
        (28.6239, 77.2190),  # Node 1
        (28.6089, 77.2240),  # Node 2
        (28.6219, 77.2010),  # Node 3
        (28.6019, 77.2040),  # Node 4
    ]
    
    # Create time matrix (simplified)
    N = len(coords)
    time_matrix = np.zeros((N, N))
    
    for i in range(N):
        for j in range(N):
            if i != j:
                # Simple distance-based time (in minutes)
                lat1, lon1 = coords[i]
                lat2, lon2 = coords[j]
                dist = np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111  # Rough km
                time_matrix[i, j] = dist * 2  # 2 minutes per km
    
    # Time windows (earliest, latest) in minutes from start
    time_windows = [
        (0, 480),    # Depot: 0 to 8 hours
        (60, 180),   # Node 1: 1-3 hours
        (120, 240),  # Node 2: 2-4 hours
        (180, 300),  # Node 3: 3-5 hours
        (240, 360),  # Node 4: 4-6 hours
    ]
    
    return time_matrix, time_windows

if __name__ == "__main__":
    print("🧮 QUBO Builder for Quantum Route Optimization")
    print("=" * 50)
    
    # Create sample problem
    time_matrix, time_windows = create_sample_problem()
    
    print(f"Problem size: {time_matrix.shape[0]} nodes")
    print(f"Time matrix:\n{time_matrix}")
    print(f"Time windows: {time_windows}")
    
    # Build QUBO
    builder = QUBOBuilder(lambda_penalty=100.0)
    Q, var_index = builder.build_time_dependent_tsp_qubo(time_matrix, time_windows)
    
    print(f"\nQUBO created with {len(var_index)} variables")
    print(f"Number of quadratic terms: {len([k for k in Q.keys() if k != ('const',)])}")
    print(f"Constant term: {Q.get(('const',), 0)}")
    
    # Show sample QUBO terms
    print("\nSample QUBO terms:")
    count = 0
    for (i, j), coeff in Q.items():
        if i != j and count < 5:
            print(f"  Q[{i},{j}] = {coeff:.2f}")
            count += 1
