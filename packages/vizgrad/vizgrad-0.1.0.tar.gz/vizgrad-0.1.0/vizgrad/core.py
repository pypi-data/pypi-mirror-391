import math
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Set, List, Dict


class ValueVisualization:
    """Registry for forward operations used in visualization."""
    
    # Consolidated forward operations
    FORWARD_OPS = {
        'add': lambda ops: ops[0].data + ops[1].data,
        'mul': lambda ops: ops[0].data * ops[1].data,
        'neg': lambda ops: -ops[0].data,
        'log': lambda ops: np.log(ops[0].data),
        'tanh': lambda ops: np.tanh(ops[0].data),
        'abs': lambda ops: np.abs(ops[0].data),
        'relu': lambda ops: np.maximum(0, ops[0].data),
        'exp': lambda ops: np.exp(ops[0].data),
        'sin': lambda ops: np.sin(ops[0].data),
        'cos': lambda ops: np.cos(ops[0].data),
        'tan': lambda ops: np.tan(ops[0].data),
        'pow_value': lambda ops: ops[0].data ** ops[1].data,
        'matmul': lambda ops: ops[0].data @ ops[1].data,
    }
    
    # Operations with parameters
    @staticmethod
    def forward_with_params(op_name, operands, **params):
        """Execute forward operations that require parameters."""
        ops_map = {
            'pow_scalar': lambda: operands[0].data ** params['exponent'],
            'transpose': lambda: np.transpose(operands[0].data, params['axes']),
            'sum': lambda: np.sum(operands[0].data, axis=params['axis'], keepdims=params['keepdims']),
            'mean': lambda: np.mean(operands[0].data, axis=params['axis'], keepdims=params['keepdims']),
            'reshape': lambda: operands[0].data.reshape(params['shape']),
            'softmax': lambda: ValueVisualization._softmax(operands[0].data, params['axis']),
            'log_softmax': lambda: ValueVisualization._log_softmax(operands[0].data, params['axis']),
            'getitem': lambda: operands[0].data[params['key']],
            'stack': lambda: np.stack([v.data for v in operands], axis=params['axis']),
            'concatenate': lambda: np.concatenate([v.data for v in operands], axis=params['axis']),
        }
        return ops_map[op_name]()
    
    @staticmethod
    def _softmax(x, axis):
        x_max = np.max(x, axis=axis, keepdims=True)
        exp_shifted = np.exp(x - x_max)
        return exp_shifted / np.sum(exp_shifted, axis=axis, keepdims=True)
    
    @staticmethod
    def _log_softmax(x, axis):
        x_max = np.max(x, axis=axis, keepdims=True)
        shifted = x - x_max
        return shifted - np.log(np.sum(np.exp(shifted), axis=axis, keepdims=True))


class Value:
    
    def __init__(self, data, _children=(), _op='leaf', name=None):
        self.data = np.array(data, dtype=np.float64) if not isinstance(data, np.ndarray) else data.astype(np.float64)
        self._prev = set(_children)
        self._backward = lambda: None
        self.grad = np.zeros_like(self.data)
        self._operation = _op
        self.name = name
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _unbroadcast(self, grad, target_shape):
        """Unbroadcast gradient back to target shape."""
        if target_shape == ():
            return np.sum(grad)
        
        # Sum over added dimensions
        for _ in range(grad.ndim - len(target_shape)):
            grad = grad.sum(axis=0)
        
        # Sum over broadcasted dimensions
        for i, (grad_dim, target_dim) in enumerate(zip(grad.shape, target_shape)):
            if target_dim == 1 and grad_dim > 1:
                grad = grad.sum(axis=i, keepdims=True)
        
        return grad.reshape(target_shape)
    
    def _to_value(self, other):
        """Convert other to Value if needed."""
        return other if isinstance(other, Value) else Value(other)
    
    def _create_unary_op(self, forward_fn, backward_fn, op_name):
        """Generic unary operation creator."""
        result = forward_fn(self.data)
        out = Value(result, (self,), _op=op_name)
        
        def _backward():
            grad = backward_fn(self.data, result) * out.grad
            self.grad += self._unbroadcast(grad, self.data.shape)
        
        out._backward = _backward
        return out
    
    def _create_binary_op(self, other, forward_fn, self_grad_fn, other_grad_fn, op_name):
        """Generic binary operation creator."""
        other = self._to_value(other)
        result = forward_fn(self.data, other.data)
        out = Value(result, (self, other), _op=op_name)
        
        def _backward():
            self.grad += self._unbroadcast(self_grad_fn(out.grad, other.data), self.data.shape)
            other.grad += other._unbroadcast(other_grad_fn(out.grad, self.data), other.data.shape)
        
        out._backward = _backward
        return out
    
    def _reduce_op(self, op_fn, op_name, axis=None, keepdims=False, scale_factor=None):
        """Generic reduction operation (sum, mean)."""
        result = op_fn(self.data, axis=axis, keepdims=keepdims)
        out = Value(result, (self,), _op=op_name)
        out._op_params = {'axis': axis, 'keepdims': keepdims}
        
        def _backward():
            if axis is None:
                n = scale_factor(self.data.size) if scale_factor else 1
                grad = np.full_like(self.data, out.grad / n)
            else:
                axes = [axis] if isinstance(axis, int) else list(axis)
                axes = [ax if ax >= 0 else ax + self.data.ndim for ax in axes]
                
                n = scale_factor(np.prod([self.data.shape[ax] for ax in axes])) if scale_factor else 1
                
                if not keepdims:
                    expanded_shape = list(out.grad.shape)
                    for ax in sorted(axes):
                        expanded_shape.insert(ax, 1)
                    reshaped_grad = out.grad.reshape(expanded_shape)
                    grad = np.broadcast_to(reshaped_grad / n, self.data.shape)
                else:
                    grad = np.broadcast_to(out.grad / n, self.data.shape)
            
            self.grad += grad
        
        out._backward = _backward
        return out
    
    # =========================================================================
    # ARITHMETIC OPERATIONS
    # =========================================================================
    
    def __add__(self, other):
        return self._create_binary_op(other, 
            lambda a, b: a + b,
            lambda g, b: g,
            lambda g, a: g,
            'add')
    
    def __mul__(self, other):
        return self._create_binary_op(other,
            lambda a, b: a * b,
            lambda g, b: g * b,
            lambda g, a: g * a,
            'mul')
    
    def __pow__(self, other):
        if isinstance(other, (int, float)):
            out = Value(self.data**other, (self,), _op='pow_scalar')
            out._op_params = {'exponent': other}
            
            def _backward():
                grad = (other * self.data**(other-1)) * out.grad
                self.grad += self._unbroadcast(grad, self.data.shape)
            out._backward = _backward
            return out
        
        elif isinstance(other, Value):
            if np.any(self.data <= 0):
                raise ValueError("Base must be positive for Value^Value operations")
            
            result = self.data ** other.data
            out = Value(result, (self, other), _op='pow_value')
            
            def _backward():
                self.grad += self._unbroadcast((other.data * self.data**(other.data - 1)) * out.grad, self.data.shape)
                other.grad += other._unbroadcast((result * np.log(self.data)) * out.grad, other.data.shape)
            
            out._backward = _backward
            return out
    
    def __neg__(self):
        out = Value(-self.data, (self,), _op='neg')
        out._backward = lambda: self.grad.__iadd__(-out.grad)
        return out
    
    def __sub__(self, other):
        return self + (-other)
    
    def __truediv__(self, other):
        other = self._to_value(other)
        if np.any(other.data == 0):
            raise ZeroDivisionError("Division by zero in Value object")
        return self * other**-1
    
    # Reverse operations
    __radd__ = __add__
    __rmul__ = __mul__
    __rsub__ = lambda self, other: other + (-self)
    __rtruediv__ = lambda self, other: other * self**-1
    
    # =========================================================================
    # ACTIVATION FUNCTIONS
    # =========================================================================
    
    def log(self):
        if np.any(self.data <= 0):
            raise ValueError("Cannot take log of non-positive number")
        return self._create_unary_op(np.log, lambda x, _: 1.0 / x, 'log')
    
    def exp(self):
        return self._create_unary_op(np.exp, lambda _, r: r, 'exp')
    
    def tanh(self):
        return self._create_unary_op(np.tanh, lambda _, r: 1 - r**2, 'tanh')
    
    def sigmoid(self):
        def forward(x):
            return np.where(x >= 0, 1 / (1 + np.exp(-x)), np.exp(x) / (1 + np.exp(x)))
        return self._create_unary_op(forward, lambda _, r: r * (1 - r), 'sigmoid')
    
    def relu(self):
        return self._create_unary_op(lambda x: np.maximum(0, x), lambda x, _: (x > 0).astype(np.float64), 'relu')
    
    def abs(self):
        return self._create_unary_op(np.abs, lambda x, _: np.sign(x), 'abs')
    
    def sin(self):
        return self._create_unary_op(np.sin, lambda x, _: np.cos(x), 'sin')
    
    def cos(self):
        return self._create_unary_op(np.cos, lambda x, _: -np.sin(x), 'cos')
    
    def tan(self):
        return self._create_unary_op(np.tan, lambda x, _: 1 / np.cos(x)**2, 'tan')
    
    # =========================================================================
    # MATRIX OPERATIONS
    # =========================================================================
    
    def transpose(self, axes=None):
        out = Value(np.transpose(self.data, axes), (self,), _op='transpose')
        out._op_params = {'axes': axes}
        
        def _backward():
            inv_axes = np.argsort(axes) if axes else None
            grad = np.transpose(out.grad, inv_axes) if axes else np.transpose(out.grad)
            self.grad += grad
        
        out._backward = _backward
        return out
    
    def matmul(self, other):
        other = self._to_value(other)
        out = Value(self.data @ other.data, (self, other), _op='matmul')
        
        def _backward():
            if self.data.ndim == 1 and other.data.ndim == 1:
                self.grad += out.grad * other.data
                other.grad += out.grad * self.data
            elif self.data.ndim == 2 and other.data.ndim == 1:
                self.grad += np.outer(out.grad, other.data)
                other.grad += self.data.T @ out.grad
            elif self.data.ndim == 1 and other.data.ndim == 2:
                self.grad += out.grad @ other.data.T
                other.grad += np.outer(self.data, out.grad)
            else:
                self.grad += out.grad @ other.data.T
                other.grad += self.data.T @ out.grad
        
        out._backward = _backward
        return out
    
    __matmul__ = matmul
    __rmatmul__ = lambda self, other: self._to_value(other).matmul(self)
    
    @property
    def T(self):
        return self.transpose()
    
    # =========================================================================
    # REDUCTION OPERATIONS
    # =========================================================================
    
    def sum(self, axis=None, keepdims=False):
        return self._reduce_op(np.sum, 'sum', axis, keepdims)
    
    def mean(self, axis=None, keepdims=False):
        return self._reduce_op(np.mean, 'mean', axis, keepdims, scale_factor=lambda n: n)
    
    def reshape(self, shape):
        out = Value(self.data.reshape(shape), (self,), _op='reshape')
        out._op_params = {'shape': shape}
        out._backward = lambda: self.grad.__iadd__(out.grad.reshape(self.data.shape))
        return out
    
    def softmax(self, axis=-1):
        x_max = np.max(self.data, axis=axis, keepdims=True)
        shifted = self.data - x_max
        exp_shifted = np.exp(shifted)
        result = exp_shifted / np.sum(exp_shifted, axis=axis, keepdims=True)
        
        out = Value(result, (self,), _op='softmax')
        out._op_params = {'axis': axis}
        
        def _backward():
            s_dot_grad = np.sum(result * out.grad, axis=axis, keepdims=True)
            grad = result * (out.grad - s_dot_grad)
            self.grad += self._unbroadcast(grad, self.data.shape)
        
        out._backward = _backward
        return out
    
    def log_softmax(self, axis=-1):
        x_max = np.max(self.data, axis=axis, keepdims=True)
        shifted = self.data - x_max
        result = shifted - np.log(np.sum(np.exp(shifted), axis=axis, keepdims=True))
        
        out = Value(result, (self,), _op='log_softmax')
        out._op_params = {'axis': axis}
        
        def _backward():
            softmax_vals = np.exp(result)
            grad = out.grad - softmax_vals * np.sum(out.grad, axis=axis, keepdims=True)
            self.grad += self._unbroadcast(grad, self.data.shape)
        
        out._backward = _backward
        return out
    
    # =========================================================================
    # INDEXING AND STACKING
    # =========================================================================
    
    def __getitem__(self, key):
        out = Value(self.data[key], (self,), _op='getitem')
        out._op_params = {'key': key}
        
        def _backward():
            grad = np.zeros_like(self.data)
            grad[key] = out.grad
            self.grad += grad
        
        out._backward = _backward
        return out
    
    @staticmethod
    def stack(values, axis=0):
        values = list(values)
        if not values:
            raise ValueError("Cannot stack empty list")
        
        stacked_data = np.stack([v.data for v in values], axis=axis)
        out = Value(stacked_data, tuple(values), _op='stack')
        out._op_params = {'axis': axis}
        
        def _backward():
            grad_list = np.split(out.grad, len(values), axis=axis)
            for val, grad in zip(values, grad_list):
                val.grad += np.squeeze(grad, axis=axis)
        
        out._backward = _backward
        return out
    
    @staticmethod
    def concatenate(values, axis=0):
        values = list(values)
        if not values:
            raise ValueError("Cannot concatenate empty list")
        
        concat_data = np.concatenate([v.data for v in values], axis=axis)
        out = Value(concat_data, tuple(values), _op='concatenate')
        out._op_params = {'axis': axis}
        
        def _backward():
            split_indices = np.cumsum([v.shape[axis] for v in values[:-1]])
            grad_list = np.split(out.grad, split_indices, axis=axis)
            for val, grad in zip(values, grad_list):
                val.grad += grad
        
        out._backward = _backward
        return out
    
    @staticmethod
    def sum_values(values):
        values = list(values)
        return sum(values[1:], values[0]) if values else Value(0.0)
    
    @staticmethod
    def mean_values(values):
        values = list(values)
        return Value.sum_values(values) / len(values) if values else Value(0.0)
    
    # =========================================================================
    # GRADIENT OPERATIONS
    # =========================================================================
    
    def _build_topo(self):
        """Build topological order of computation graph."""
        topo, visited = [], set()
        def visit(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    visit(child)
                topo.append(v)
        visit(self)
        return topo
    
    def backward(self, gradient=None):
        """Compute gradients via backpropagation."""
        # Initialize gradient
        if gradient is not None:
            self.grad = gradient
        elif self.data.size == 1:
            self.grad = np.ones_like(self.data)
        else:
            raise ValueError(f"For non-scalar outputs with shape {self.data.shape}, "
                           f"gradient must be provided. Expected shape: {self.data.shape}")
        
        # Backpropagate
        for node in reversed(self._build_topo()):
            node._backward()
    
    def zero_grad(self):
        """Zero out gradients in the computation graph."""
        for node in self._build_topo():
            node.grad = np.zeros_like(node.data)
    
    # =========================================================================
    # VISUALIZATION METHODS
    # =========================================================================
    
    def _analyze_dependencies(self, variable):
        """Single-pass dependency analysis returning dependencies and topological order."""
        dependencies = set()
        topo_order = []
        visited = set()
        
        def traverse(node):
            if node in visited:
                return node in dependencies
            visited.add(node)
            
            if node is variable:
                dependencies.add(node)
                return True
            
            has_dep = any(traverse(parent) for parent in node._prev)
            if has_dep:
                dependencies.add(node)
                topo_order.append(node)
            
            return has_dep
        
        traverse(self)
        return dependencies, topo_order
    
    def depends_on(self, variable) -> bool:
        """Check if this Value depends on the given variable."""
        deps, _ = self._analyze_dependencies(variable)
        return len(deps) > 0
    
    def recompute_with_value(self, variable, new_value) -> np.ndarray:
        """Recompute the output with variable set to new_value."""
        dependencies, recompute_order = self._analyze_dependencies(variable)
        
        if not dependencies:
            return self.data.copy()
        
        value_map = {variable: np.array(new_value, dtype=np.float64)}
        
        for node in recompute_order:
            if node is variable:
                continue
            
            if node._operation == 'leaf':
                value_map[node] = node.data
                continue
            
            # Create temporary Value objects with new data
            operands = []
            for operand in node._prev:
                temp_val = type(node).__new__(type(node))
                temp_val.data = value_map.get(operand, operand.data)
                operands.append(temp_val)
            
            # Execute forward operation
            if hasattr(node, '_op_params'):
                new_data = ValueVisualization.forward_with_params(node._operation, operands, **node._op_params)
            elif node._operation in ValueVisualization.FORWARD_OPS:
                new_data = ValueVisualization.FORWARD_OPS[node._operation](operands)
            else:
                raise ValueError(f"Unknown operation: {node._operation}")
            
            value_map[node] = new_data
        
        return value_map[self]
    
    def visualize(self, variable, range_scale: float = 2.0, num_points: int = 100,
                  figsize: Tuple[int, int] = (11, 6), show_tangent: bool = True,
                  title: Optional[str] = None):
        """Visualize this Value as a function of the given variable (single frame, dark mode)."""
        # Validation
        if not hasattr(variable, '_operation') or variable._operation != 'leaf':
            raise ValueError("Can only visualize with respect to leaf variables")
        
        if not self.depends_on(variable):
            raise ValueError("Output doesn't depend on the given variable")
        
        if variable.data.size != 1 or self.data.size != 1:
            raise ValueError("Can only visualize scalar variables and outputs")
        
        # Get current values
        current_var = float(variable.data)
        current_output = float(self.data)
        current_grad = float(variable.grad)
        
        # Sample the function
        var_range = np.linspace(current_var - range_scale, current_var + range_scale, num_points)
        output_values = np.array([float(self.recompute_with_value(variable, v)) for v in var_range])
        
        # Create dark mode plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#0d0d0d')
        
        # Plot function with gradient color
        ax.plot(var_range, output_values, color='#00d9ff', linewidth=2.5, label='Function', alpha=0.9)
        ax.plot(current_var, current_output, 'o', color='#ff006e', markersize=12, 
                label=f'Current ({current_var:.3f}, {current_output:.3f})', zorder=5)
        
        if show_tangent:
            tangent = current_output + current_grad * (var_range - current_var)
            ax.plot(var_range, tangent, '--', color='#8338ec', linewidth=2, 
                    label=f'Tangent (slope={current_grad:.3f})', alpha=0.8)
        
        # Labels
        var_name = variable.name or 'variable'
        output_name = self.name or 'output'
        ax.set_xlabel(var_name, fontsize=13, color='#e0e0e0')
        ax.set_ylabel(output_name, fontsize=13, color='#e0e0e0')
        ax.set_title(title or f'{output_name} as a function of {var_name}', 
                     fontsize=15, color='#ffffff', pad=20)
        ax.grid(True, alpha=0.15, color='#404040')
        ax.legend(fontsize=11, facecolor='#1a1a1a', edgecolor='#404040')
        
        # Gradient info box
        info_text = f'∇ d{output_name}/d{var_name} = {current_grad:.4f}'
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.8, edgecolor='#404040'),
                fontsize=11, color='#00d9ff')
        
        plt.tight_layout()
        plt.show()
        return fig, ax
    
    def visualize_sequence(self, variable, history: List[float], range_scale: float = 2.0, 
                          num_points: int = 100, figsize: Tuple[int, int] = (11, 7),
                          show_tangent: bool = True, title: Optional[str] = None):
        """
        Interactive visualization showing optimization trajectory with slider.
        
        Args:
            variable: The leaf Value to vary
            history: List of variable values over time (e.g., from optimization steps)
            range_scale: How far to extend x-axis beyond history min/max
            num_points: Number of points to sample for function
            figsize: Figure size
            show_tangent: Whether to show tangent lines
            title: Optional plot title
        """
        from matplotlib.widgets import Slider
        
        # Validation
        if not hasattr(variable, '_operation') or variable._operation != 'leaf':
            raise ValueError("Can only visualize with respect to leaf variables")
        
        if not self.depends_on(variable):
            raise ValueError("Output doesn't depend on the given variable")
        
        if variable.data.size != 1 or self.data.size != 1:
            raise ValueError("Can only visualize scalar variables and outputs")
        
        if len(history) < 2:
            raise ValueError("History must contain at least 2 points")
        
        history = np.array(history)
        
        # Compute static bounds from full history
        x_min = np.min(history) - range_scale
        x_max = np.max(history) + range_scale
        var_range = np.linspace(x_min, x_max, num_points)
        
        # Pre-compute function values and gradients for entire trajectory
        trajectory_data = []
        for var_val in history:
            output_val = float(self.recompute_with_value(variable, var_val))
            
            # Compute gradient at this point
            temp_var = Value(var_val, name=variable.name)
            temp_output = self.recompute_with_value(variable, var_val)
            temp_result = Value(temp_output)
            
            # Numerical gradient
            eps = 1e-7
            f_plus = self.recompute_with_value(variable, var_val + eps)
            f_minus = self.recompute_with_value(variable, var_val - eps)
            grad = (f_plus - f_minus) / (2 * eps)
            
            trajectory_data.append({
                'var_val': var_val,
                'output_val': output_val,
                'grad': float(grad)
            })
        
        # Compute full function over range
        output_values = np.array([float(self.recompute_with_value(variable, v)) for v in var_range])
        
        # Compute static y-bounds
        all_outputs = [d['output_val'] for d in trajectory_data]
        y_margin = (np.max(all_outputs) - np.min(all_outputs)) * 0.1
        y_min = min(np.min(output_values), np.min(all_outputs)) - y_margin
        y_max = max(np.max(output_values), np.max(all_outputs)) + y_margin
        
        # Create dark mode plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#0d0d0d')
        plt.subplots_adjust(bottom=0.15)
        
        # Plot static elements
        ax.plot(var_range, output_values, color='#00d9ff', linewidth=2.5, 
                label='Function', alpha=0.7, zorder=1)
        
        # Plot full trajectory as faded line
        traj_x = [d['var_val'] for d in trajectory_data]
        traj_y = [d['output_val'] for d in trajectory_data]
        ax.plot(traj_x, traj_y, 'o-', color='#404040', linewidth=1, 
                markersize=4, alpha=0.4, label='Full trajectory', zorder=2)
        
        # Dynamic elements (will be updated)
        point_plot, = ax.plot([], [], 'o', color='#ff006e', markersize=14, zorder=5)
        tangent_plot, = ax.plot([], [], '--', color='#8338ec', linewidth=2, alpha=0.8, zorder=3)
        
        # Labels
        var_name = variable.name or 'variable'
        output_name = self.name or 'output'
        ax.set_xlabel(var_name, fontsize=13, color='#e0e0e0')
        ax.set_ylabel(output_name, fontsize=13, color='#e0e0e0')
        ax.set_title(title or f'{output_name} optimization trajectory', 
                     fontsize=15, color='#ffffff', pad=20)
        
        # Set static bounds
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        ax.grid(True, alpha=0.15, color='#404040')
        ax.legend(fontsize=10, facecolor='#1a1a1a', edgecolor='#404040', loc='upper right')
        
        # Info text box
        info_box = ax.text(0.02, 0.98, '', transform=ax.transAxes, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.8, edgecolor='#404040'),
                          fontsize=11, color='#00d9ff')
        
        # Slider
        ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03], facecolor='#2a2a2a')
        slider = Slider(ax_slider, 'Step', 0, len(history) - 1, valinit=0, 
                       valstep=1, color='#00d9ff')
        
        def update(val):
            step = int(slider.val)
            data = trajectory_data[step]
            
            # Update point
            point_plot.set_data([data['var_val']], [data['output_val']])
            
            # Update tangent
            if show_tangent:
                tangent_y = data['output_val'] + data['grad'] * (var_range - data['var_val'])
                tangent_plot.set_data(var_range, tangent_y)
            else:
                tangent_plot.set_data([], [])
            
            # Update info text
            info_text = (f'Step: {step}/{len(history)-1}\n'
                        f'{var_name} = {data["var_val"]:.4f}\n'
                        f'{output_name} = {data["output_val"]:.4f}\n'
                        f'∇ = {data["grad"]:.4f}')
            info_box.set_text(info_text)
            
            fig.canvas.draw_idle()
        
        slider.on_changed(update)
        
        # Initialize with first frame
        update(0)
        
        plt.show()
        return fig, ax, slider
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    @property
    def shape(self):
        return self.data.shape
    
    def __repr__(self):
        return f"Value(data={self.data}, shape={self.data.shape})"
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        return np.array_equal(self.data, self._to_value(other).data)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return np.all(self.data < self._to_value(other).data)
    
    def __le__(self, other):
        return np.all(self.data <= self._to_value(other).data)
    
    def __gt__(self, other):
        return np.all(self.data > self._to_value(other).data)
    
    def __ge__(self, other):
        return np.all(self.data >= self._to_value(other).data)

