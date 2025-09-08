"""
Quantum Solver Integration for Route Optimization
Part of the Quantum-Enhanced AI Logistics Engine
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import time
import json

try:
    import dimod
    from dimod import BinaryQuadraticModel
    DIMOD_AVAILABLE = True
except ImportError:
    DIMOD_AVAILABLE = False
    print("Warning: dimod not available. Using fallback solver.")

try:
    import neal
    NEAL_AVAILABLE = True
except ImportError:
    NEAL_AVAILABLE = False
    print("Warning: neal not available. Using basic solver.")

try:
    from dwave.system import LeapHybridSampler, DWaveSampler, EmbeddingComposite
    from dwave.cloud import Client
    DWAVE_AVAILABLE = True
except ImportError:
    DWAVE_AVAILABLE = False
    print("Warning: D-Wave Ocean SDK not available. Using classical solvers.")

class QuantumSolver:
    """Quantum and classical solvers for QUBO optimization"""
    
    def __init__(self, solver_type: str = 'auto'):
        self.solver_type = solver_type
        self.available_solvers = self._check_available_solvers()
        
    def _check_available_solvers(self) -> List[str]:
        """Check which solvers are available"""
        solvers = []
        
        if DWAVE_AVAILABLE:
            try:
                # Test D-Wave connection
                client = Client.from_config()
                if client.get_solvers():
                    solvers.append('dwave_hybrid')
                    solvers.append('dwave_qpu')
            except:
                pass
        
        if NEAL_AVAILABLE:
            solvers.append('neal')
        
        if DIMOD_AVAILABLE:
            solvers.append('dimod_exact')
        
        solvers.append('greedy')  # Always available
        
        return solvers
    
    def solve_qubo(self, Q: Dict, var_index: Dict, 
                   time_limit: float = 5.0,
                   num_reads: int = 100) -> Tuple[Dict, float, float]:
        """
        Solve QUBO problem using available solver
        
        Args:
            Q: QUBO dictionary
            var_index: Variable mapping
            time_limit: Maximum time in seconds
            num_reads: Number of solution attempts
            
        Returns:
            solution: Dictionary mapping variable indices to binary values
            energy: Energy of the best solution
            solve_time: Time taken to solve
        """
        start_time = time.time()
        
        if self.solver_type == 'auto':
            solver = self._get_best_solver()
        else:
            solver = self.solver_type
        
        print(f"🔧 Using solver: {solver}")
        
        if solver == 'dwave_hybrid' and 'dwave_hybrid' in self.available_solvers:
            solution, energy = self._solve_dwave_hybrid(Q, time_limit)
        elif solver == 'dwave_qpu' and 'dwave_qpu' in self.available_solvers:
            solution, energy = self._solve_dwave_qpu(Q, num_reads)
        elif solver == 'neal' and 'neal' in self.available_solvers:
            solution, energy = self._solve_neal(Q, num_reads)
        elif solver == 'dimod_exact' and 'dimod_exact' in self.available_solvers:
            solution, energy = self._solve_dimod_exact(Q)
        else:
            solution, energy = self._solve_greedy(Q, var_index)
        
        solve_time = time.time() - start_time
        
        return solution, energy, solve_time
    
    def _get_best_solver(self) -> str:
        """Get the best available solver"""
        if 'dwave_hybrid' in self.available_solvers:
            return 'dwave_hybrid'
        elif 'neal' in self.available_solvers:
            return 'neal'
        elif 'dimod_exact' in self.available_solvers:
            return 'dimod_exact'
        else:
            return 'greedy'
    
    def _solve_dwave_hybrid(self, Q: Dict, time_limit: float) -> Tuple[Dict, float]:
        """Solve using D-Wave hybrid solver"""
        try:
            bqm = BinaryQuadraticModel.from_qubo(Q)
            sampler = LeapHybridSampler()
            sampleset = sampler.sample(bqm, time_limit=time_limit)
            
            best_sample = sampleset.first.sample
            energy = sampleset.first.energy
            
            return best_sample, energy
        except Exception as e:
            print(f"D-Wave hybrid solver failed: {e}")
            return self._solve_greedy(Q, {})
    
    def _solve_dwave_qpu(self, Q: Dict, num_reads: int) -> Tuple[Dict, float]:
        """Solve using D-Wave QPU"""
        try:
            bqm = BinaryQuadraticModel.from_qubo(Q)
            sampler = DWaveSampler()
            embedding_sampler = EmbeddingComposite(sampler)
            sampleset = embedding_sampler.sample(bqm, num_reads=num_reads)
            
            best_sample = sampleset.first.sample
            energy = sampleset.first.energy
            
            return best_sample, energy
        except Exception as e:
            print(f"D-Wave QPU solver failed: {e}")
            return self._solve_greedy(Q, {})
    
    def _solve_neal(self, Q: Dict, num_reads: int) -> Tuple[Dict, float]:
        """Solve using simulated annealing (neal)"""
        try:
            bqm = BinaryQuadraticModel.from_qubo(Q)
            sampler = neal.SimulatedAnnealingSampler()
            sampleset = sampler.sample(bqm, num_reads=num_reads)
            
            best_sample = sampleset.first.sample
            energy = sampleset.first.energy
            
            return best_sample, energy
        except Exception as e:
            print(f"Neal solver failed: {e}")
            return self._solve_greedy(Q, {})
    
    def _solve_dimod_exact(self, Q: Dict) -> Tuple[Dict, float]:
        """Solve using exact solver (for small problems)"""
        try:
            bqm = BinaryQuadraticModel.from_qubo(Q)
            exact_solver = dimod.ExactSolver()
            sampleset = exact_solver.sample(bqm)
            
            best_sample = sampleset.first.sample
            energy = sampleset.first.energy
            
            return best_sample, energy
        except Exception as e:
            print(f"Exact solver failed: {e}")
            return self._solve_greedy(Q, {})
    
    def _solve_greedy(self, Q: Dict, var_index: Dict) -> Tuple[Dict, float]:
        """Fallback greedy solver"""
        # Simple greedy approach: minimize linear terms
        solution = {}
        energy = 0.0
        
        # Get all variables
        variables = set()
        for (i, j) in Q.keys():
            if i != j:
                variables.add(i)
                variables.add(j)
        
        # Initialize all variables to 0
        for var in variables:
            solution[var] = 0
        
        # Greedy assignment based on linear terms
        linear_terms = {}
        for (i, j), coeff in Q.items():
            if i == j:
                linear_terms[i] = linear_terms.get(i, 0) + coeff
        
        # Sort by linear term value (ascending)
        sorted_vars = sorted(linear_terms.items(), key=lambda x: x[1])
        
        # Assign variables greedily
        for var, coeff in sorted_vars:
            if coeff < 0:  # Negative coefficient means setting to 1 is beneficial
                solution[var] = 1
                energy += coeff
        
        # Add quadratic terms
        for (i, j), coeff in Q.items():
            if i != j and solution.get(i, 0) == 1 and solution.get(j, 0) == 1:
                energy += coeff
        
        return solution, energy

class RouteOptimizer:
    """Main route optimization engine"""
    
    def __init__(self, solver_type: str = 'auto'):
        self.solver = QuantumSolver(solver_type)
        self.optimization_history = []
        
    def optimize_route(self, 
                      time_matrix: np.ndarray,
                      time_windows: Optional[List[Tuple[float, float]]] = None,
                      problem_type: str = 'tsp',
                      **kwargs) -> Dict:
        """
        Optimize route using quantum/classical solver
        
        Args:
            time_matrix: NxN travel time matrix
            time_windows: Optional time windows for each node
            problem_type: 'tsp' or 'vrp'
            **kwargs: Additional parameters for VRP
            
        Returns:
            Dictionary with optimization results
        """
        from qubo_builder import QUBOBuilder
        
        # Build QUBO
        builder = QUBOBuilder()
        
        if problem_type == 'tsp':
            Q, var_index = builder.build_time_dependent_tsp_qubo(
                time_matrix, time_windows
            )
        elif problem_type == 'vrp':
            demands = kwargs.get('demands', [0] * time_matrix.shape[0])
            vehicle_capacity = kwargs.get('vehicle_capacity', 100.0)
            num_vehicles = kwargs.get('num_vehicles', 3)
            
            Q, var_index = builder.build_vrp_qubo(
                time_matrix, demands, vehicle_capacity, num_vehicles, time_windows
            )
        else:
            raise ValueError(f"Unknown problem type: {problem_type}")
        
        # Solve QUBO
        solution, energy, solve_time = self.solver.solve_qubo(Q, var_index)
        
        # Extract route
        route = builder.extract_solution(solution, var_index, problem_type)
        
        # Calculate metrics
        total_time = self._calculate_route_time(route, time_matrix)
        on_time_deliveries = self._calculate_on_time_deliveries(route, time_matrix, time_windows)
        
        # Store optimization history
        result = {
            'route': route,
            'total_time': total_time,
            'energy': energy,
            'solve_time': solve_time,
            'on_time_deliveries': on_time_deliveries,
            'solver_type': self.solver.solver_type,
            'problem_type': problem_type,
            'timestamp': time.time()
        }
        
        self.optimization_history.append(result)
        
        return result
    
    def _calculate_route_time(self, route: List[int], time_matrix: np.ndarray) -> float:
        """Calculate total travel time for route"""
        if len(route) < 2:
            return 0.0
        
        total_time = 0.0
        for i in range(len(route) - 1):
            total_time += time_matrix[route[i], route[i + 1]]
        
        # Return to depot if not already there
        if route[-1] != 0:
            total_time += time_matrix[route[-1], 0]
        
        return total_time
    
    def _calculate_on_time_deliveries(self, route: List[int], 
                                    time_matrix: np.ndarray,
                                    time_windows: Optional[List[Tuple[float, float]]]) -> float:
        """Calculate percentage of on-time deliveries"""
        if not time_windows or len(route) < 2:
            return 100.0
        
        on_time_count = 0
        current_time = 0.0
        
        for i, node in enumerate(route[1:], 1):  # Skip depot
            if node < len(time_windows):
                earliest, latest = time_windows[node]
                if earliest <= current_time <= latest:
                    on_time_count += 1
            
            # Add travel time to next node
            if i < len(route) - 1:
                current_time += time_matrix[node, route[i + 1]]
            else:
                current_time += time_matrix[node, 0]  # Return to depot
        
        return (on_time_count / max(1, len(route) - 1)) * 100.0
    
    def compare_with_baseline(self, 
                            time_matrix: np.ndarray,
                            baseline_route: List[int],
                            optimized_route: List[int]) -> Dict:
        """Compare optimized route with baseline"""
        baseline_time = self._calculate_route_time(baseline_route, time_matrix)
        optimized_time = self._calculate_route_time(optimized_route, time_matrix)
        
        improvement = ((baseline_time - optimized_time) / baseline_time) * 100
        
        return {
            'baseline_time': baseline_time,
            'optimized_time': optimized_time,
            'improvement_percent': improvement,
            'time_saved': baseline_time - optimized_time
        }

def create_baseline_route(time_matrix: np.ndarray) -> List[int]:
    """Create a simple baseline route (nearest neighbor)"""
    n = time_matrix.shape[0]
    unvisited = list(range(1, n))  # Exclude depot
    route = [0]  # Start at depot
    current = 0
    
    while unvisited:
        # Find nearest unvisited node
        nearest = min(unvisited, key=lambda x: time_matrix[current, x])
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return route

if __name__ == "__main__":
    print("⚛️ Quantum Solver for Route Optimization")
    print("=" * 50)
    
    # Test with sample problem
    from qubo_builder import create_sample_problem
    
    time_matrix, time_windows = create_sample_problem()
    print(f"Problem size: {time_matrix.shape[0]} nodes")
    
    # Create optimizer
    optimizer = RouteOptimizer(solver_type='auto')
    
    # Optimize route
    print("\n🔍 Optimizing route...")
    result = optimizer.optimize_route(time_matrix, time_windows, 'tsp')
    
    print(f"✅ Optimization complete!")
    print(f"Route: {result['route']}")
    print(f"Total time: {result['total_time']:.2f} minutes")
    print(f"Energy: {result['energy']:.2f}")
    print(f"Solve time: {result['solve_time']:.3f} seconds")
    print(f"Solver: {result['solver_type']}")
    print(f"On-time deliveries: {result['on_time_deliveries']:.1f}%")
    
    # Compare with baseline
    baseline_route = create_baseline_route(time_matrix)
    comparison = optimizer.compare_with_baseline(time_matrix, baseline_route, result['route'])
    
    print(f"\n📊 Comparison with baseline:")
    print(f"Baseline time: {comparison['baseline_time']:.2f} minutes")
    print(f"Optimized time: {comparison['optimized_time']:.2f} minutes")
    print(f"Improvement: {comparison['improvement_percent']:.1f}%")
    print(f"Time saved: {comparison['time_saved']:.2f} minutes")
