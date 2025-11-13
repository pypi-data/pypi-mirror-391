import pytest
import numpy as np
from vizgrad import Value


class TestBasicOperations:
    """Test basic arithmetic operations"""
    
    def test_addition(self):
        x = Value(2.0)
        y = Value(3.0)
        z = x + y
        assert z.data == 5.0
        
        z.backward()
        assert x.grad == 1.0
        assert y.grad == 1.0
    
    def test_multiplication(self):
        x = Value(2.0)
        y = Value(3.0)
        z = x * y
        assert z.data == 6.0
        
        z.backward()
        assert x.grad == 3.0
        assert y.grad == 2.0
    
    def test_subtraction(self):
        x = Value(5.0)
        y = Value(3.0)
        z = x - y
        assert z.data == 2.0
        
        z.backward()
        assert x.grad == 1.0
        assert y.grad == -1.0
    
    def test_division(self):
        x = Value(6.0)
        y = Value(2.0)
        z = x / y
        assert z.data == 3.0
        
        z.backward()
        assert x.grad == 0.5
        assert y.grad == -1.5
    
    def test_power_scalar(self):
        x = Value(2.0)
        z = x ** 3
        assert z.data == 8.0
        
        z.backward()
        assert x.grad == 12.0  # 3 * 2^2
    
    def test_power_value(self):
        x = Value(2.0)
        y = Value(3.0)
        z = x ** y
        assert z.data == 8.0
        
        z.backward()
        assert np.isclose(x.grad, 12.0)  # 3 * 2^2
        assert np.isclose(y.grad, 8.0 * np.log(2))
    
    def test_negation(self):
        x = Value(5.0)
        z = -x
        assert z.data == -5.0
        
        z.backward()
        assert x.grad == -1.0
    
    def test_reverse_operations(self):
        x = Value(3.0)
        
        # radd
        z1 = 5 + x
        assert z1.data == 8.0
        
        # rsub
        z2 = 5 - x
        assert z2.data == 2.0
        
        # rmul
        z3 = 5 * x
        assert z3.data == 15.0
        
        # rtruediv
        z4 = 6 / x
        assert z4.data == 2.0


class TestActivationFunctions:
    """Test activation functions"""
    
    def test_relu(self):
        x = Value([-2.0, 0.0, 2.0])
        y = x.relu()
        assert np.array_equal(y.data, [0.0, 0.0, 2.0])
        
        y.backward(gradient=np.ones(3))
        assert np.array_equal(x.grad, [0.0, 0.0, 1.0])
    
    def test_tanh(self):
        x = Value(0.0)
        y = x.tanh()
        assert np.isclose(y.data, 0.0)
        
        y.backward()
        assert np.isclose(x.grad, 1.0)  # tanh'(0) = 1
    
    def test_sigmoid(self):
        x = Value(0.0)
        y = x.sigmoid()
        assert np.isclose(y.data, 0.5)
        
        y.backward()
        assert np.isclose(x.grad, 0.25)  # sigmoid(0) * (1 - sigmoid(0))
    
    def test_exp(self):
        x = Value(1.0)
        y = x.exp()
        assert np.isclose(y.data, np.e)
        
        y.backward()
        assert np.isclose(x.grad, np.e)
    
    def test_log(self):
        x = Value(np.e)
        y = x.log()
        assert np.isclose(y.data, 1.0)
        
        y.backward()
        assert np.isclose(x.grad, 1.0 / np.e)
    
    def test_abs(self):
        x = Value(-5.0)
        y = x.abs()
        assert y.data == 5.0
        
        y.backward()
        assert x.grad == -1.0
    
    def test_sin(self):
        x = Value(0.0)
        y = x.sin()
        assert np.isclose(y.data, 0.0)
        
        y.backward()
        assert np.isclose(x.grad, 1.0)  # cos(0) = 1
    
    def test_cos(self):
        x = Value(0.0)
        y = x.cos()
        assert np.isclose(y.data, 1.0)
        
        y.backward()
        assert np.isclose(x.grad, 0.0)  # -sin(0) = 0
    
    def test_tan(self):
        x = Value(0.0)
        y = x.tan()
        assert np.isclose(y.data, 0.0)
        
        y.backward()
        assert np.isclose(x.grad, 1.0)  # 1/cos^2(0) = 1


class TestMatrixOperations:
    """Test matrix and tensor operations"""
    
    def test_matmul_2d(self):
        A = Value([[1, 2], [3, 4]])
        B = Value([[5, 6], [7, 8]])
        C = A @ B
        
        expected = np.array([[19, 22], [43, 50]])
        assert np.array_equal(C.data, expected)
        
        C.backward(gradient=np.ones((2, 2)))
        assert np.array_equal(A.grad, np.array([[11, 15], [11, 15]]))
        assert np.array_equal(B.grad, np.array([[4, 4], [6, 6]]))
    
    def test_transpose(self):
        x = Value([[1, 2], [3, 4]])
        y = x.transpose()
        
        assert np.array_equal(y.data, [[1, 3], [2, 4]])
        
        y.backward(gradient=np.ones((2, 2)))
        assert np.array_equal(x.grad, np.ones((2, 2)))
    
    def test_transpose_property(self):
        x = Value([[1, 2], [3, 4]])
        y = x.T
        assert np.array_equal(y.data, [[1, 3], [2, 4]])
    
    def test_reshape(self):
        x = Value([1, 2, 3, 4])
        y = x.reshape((2, 2))
        
        assert y.shape == (2, 2)
        assert np.array_equal(y.data, [[1, 2], [3, 4]])
        
        y.backward(gradient=np.ones((2, 2)))
        assert np.array_equal(x.grad, np.ones(4))
    
    def test_sum_no_axis(self):
        x = Value([[1, 2], [3, 4]])
        y = x.sum()
        
        assert y.data == 10.0
        
        y.backward()
        assert np.array_equal(x.grad, np.ones((2, 2)))
    
    def test_sum_with_axis(self):
        x = Value([[1, 2], [3, 4]])
        y = x.sum(axis=0)
        
        assert np.array_equal(y.data, [4, 6])
        
        y.backward(gradient=np.ones(2))
        assert np.array_equal(x.grad, np.ones((2, 2)))
    
    def test_mean(self):
        x = Value([[1, 2], [3, 4]])
        y = x.mean()
        
        assert y.data == 2.5
        
        y.backward()
        assert np.allclose(x.grad, np.ones((2, 2)) * 0.25)
    
    def test_softmax(self):
        x = Value([1.0, 2.0, 3.0])
        y = x.softmax()
        
        # Check probabilities sum to 1
        assert np.isclose(np.sum(y.data), 1.0)
        
        # Check all positive
        assert np.all(y.data > 0)
        
        y.backward(gradient=np.ones(3))
        # Gradient should sum to 0 for softmax
        assert np.isclose(np.sum(x.grad), 0.0, atol=1e-7)
    
    def test_log_softmax(self):
        x = Value([1.0, 2.0, 3.0])
        y = x.log_softmax()
        
        # Check equals log(softmax(x))
        expected = np.log(x.softmax().data)
        assert np.allclose(y.data, expected)


class TestIndexingAndStacking:
    """Test indexing and stacking operations"""
    
    def test_getitem(self):
        x = Value([1, 2, 3, 4])
        y = x[1:3]
        
        assert np.array_equal(y.data, [2, 3])
        
        y.backward(gradient=np.ones(2))
        assert np.array_equal(x.grad, [0, 1, 1, 0])
    
    def test_stack(self):
        x = Value([1, 2])
        y = Value([3, 4])
        z = Value.stack([x, y])
        
        assert np.array_equal(z.data, [[1, 2], [3, 4]])
        
        z.backward(gradient=np.ones((2, 2)))
        assert np.array_equal(x.grad, [1, 1])
        assert np.array_equal(y.grad, [1, 1])
    
    def test_concatenate(self):
        x = Value([1, 2])
        y = Value([3, 4])
        z = Value.concatenate([x, y])
        
        assert np.array_equal(z.data, [1, 2, 3, 4])
        
        z.backward(gradient=np.ones(4))
        assert np.array_equal(x.grad, [1, 1])
        assert np.array_equal(y.grad, [1, 1])
    
    def test_sum_values(self):
        values = [Value(1.0), Value(2.0), Value(3.0)]
        result = Value.sum_values(values)
        assert result.data == 6.0
    
    def test_mean_values(self):
        values = [Value(1.0), Value(2.0), Value(3.0)]
        result = Value.mean_values(values)
        assert result.data == 2.0


class TestGradientComputation:
    """Test gradient computation and backpropagation"""
    
    def test_simple_chain(self):
        x = Value(2.0)
        y = x * 3
        z = y + 5
        w = z ** 2
        
        w.backward()
        
        # dw/dx = dw/dz * dz/dy * dy/dx = 2*z * 1 * 3 = 2*11*3 = 66
        assert x.grad == 66.0
    
    def test_multiple_paths(self):
        x = Value(2.0)
        y = x * x  # y = x^2
        z = x + y  # z = x + x^2
        
        z.backward()
        
        # dz/dx = 1 + 2x = 1 + 4 = 5
        assert x.grad == 5.0
    
    def test_zero_grad(self):
        x = Value(2.0)
        y = x * 3
        
        y.backward()
        assert x.grad == 3.0
        
        x.zero_grad()
        y.zero_grad()
        assert x.grad == 0.0
        assert y.grad == 0.0
    
    def test_non_scalar_backward_requires_gradient(self):
        x = Value([1, 2, 3])
        y = x * 2
        
        with pytest.raises(ValueError):
            y.backward()  # Should raise - need gradient for non-scalar
    
    def test_non_scalar_backward_with_gradient(self):
        x = Value([1, 2, 3])
        y = x * 2
        
        y.backward(gradient=np.array([1, 1, 1]))
        assert np.array_equal(x.grad, [2, 2, 2])


class TestVisualizationUtilities:
    """Test visualization helper methods"""
    
    def test_depends_on(self):
        x = Value(2.0)
        y = Value(3.0)
        z = x * 2 + y
        w = y * 3
        
        assert z.depends_on(x)
        assert z.depends_on(y)
        assert not w.depends_on(x)
        assert w.depends_on(y)
    
    def test_recompute_with_value(self):
        x = Value(2.0)
        y = x ** 2 + 3 * x
        
        # Original: 2^2 + 3*2 = 10
        assert y.data == 10.0
        
        # Recompute with x=3: 3^2 + 3*3 = 18
        new_val = y.recompute_with_value(x, 3.0)
        assert new_val == 18.0
        
        # Original should be unchanged
        assert y.data == 10.0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_division_by_zero(self):
        x = Value(5.0)
        y = Value(0.0)
        
        with pytest.raises(ZeroDivisionError):
            z = x / y
    
    def test_log_of_negative(self):
        x = Value(-1.0)
        
        with pytest.raises(ValueError):
            y = x.log()
    
    def test_power_negative_base_value_exponent(self):
        x = Value(-2.0)
        y = Value(2.0)
        
        with pytest.raises(ValueError):
            z = x ** y
    
    def test_empty_stack(self):
        with pytest.raises(ValueError):
            Value.stack([])
    
    def test_empty_concatenate(self):
        with pytest.raises(ValueError):
            Value.concatenate([])


class TestBroadcasting:
    """Test broadcasting behavior"""
    
    def test_scalar_array_addition(self):
        x = Value(5.0)
        y = Value([1, 2, 3])
        z = x + y
        
        assert np.array_equal(z.data, [6, 7, 8])
        
        z.backward(gradient=np.ones(3))
        assert x.grad == 3.0  # Sum of gradients
        assert np.array_equal(y.grad, [1, 1, 1])
    
    def test_broadcast_multiplication(self):
        x = Value([[1], [2], [3]])  # (3, 1)
        y = Value([1, 2, 3])         # (3,)
        z = x * y
        
        expected = np.array([[1, 2, 3], [2, 4, 6], [3, 6, 9]])
        assert np.array_equal(z.data, expected)


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_shape_property(self):
        x = Value([[1, 2], [3, 4]])
        assert x.shape == (2, 2)
    
    def test_repr(self):
        x = Value(5.0)
        repr_str = repr(x)
        assert "Value" in repr_str
        assert "5.0" in repr_str
    
    def test_equality(self):
        x = Value([1, 2, 3])
        y = Value([1, 2, 3])
        z = Value([1, 2, 4])
        
        assert x == y
        assert x != z
    
    def test_comparison_operators(self):
        x = Value(5.0)
        y = Value(3.0)
        
        assert x > y
        assert y < x
        assert x >= y
        assert y <= x


if __name__ == "__main__":
    pytest.main([__file__, "-v"])