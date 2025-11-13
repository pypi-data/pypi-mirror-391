# coordinate_system/__init__.py

from .coordinate_system import vec3, vec2
from .coordinate_system import quat
from .coordinate_system import coord3

# Differential geometry module (v3.3.0+)
from .differential_geometry import (
    # Classes
    Surface,
    Sphere,
    Torus,
    MetricTensor,
    IntrinsicGradientOperator,
    IntrinsicGradientCurvatureCalculator,

    # Main functions
    compute_intrinsic_gradient,
    compute_gaussian_curvature,
    compute_mean_curvature,
    compute_riemann_curvature,
    compute_all_curvatures,
)

# High-precision curvature computation module (v2.3.0+)
from .curvature import (
    # Classical method
    CurvatureCalculator,
    gaussian_curvature,
    mean_curvature,
    principal_curvatures,
    all_curvatures,

    # Intrinsic Gradient Operator method
    intrinsic_gradient_gaussian_curvature,
    intrinsic_gradient_mean_curvature,
    intrinsic_gradient_principal_curvatures,
    intrinsic_gradient_all_curvatures,
    compare_methods,

    # Utility functions
    derivative_5pt,
    derivative_2nd_5pt,
    richardson_extrapolation,
)

# Fourier spectral analysis module (v4.0.0+)
from .fourier_spectral import (
    # Core Fourier analysis
    FourierTransformer,
    SpectralAnalyzer,
    FrameFieldSpectrum,
    
    # GPU accelerated transforms
    GPUFourierTransformer,
    BatchCoordTransformer,
    
    # Spectral geometry operations
    spectral_intrinsic_gradient,
    spectral_curvature_calculator,
    berry_phase_calculator,
    topological_invariant_analyzer,
    
    # Utility functions
    fft2_coord_field,
    ifft2_spectrum,
    compute_spectral_density,
    radial_spectrum_average,
)

__all__ = [
    # Constants
    'ZERO3','UNITX','UNITY','UNITZ','ONE3','ONE4','ONEC',

    # Core types
    'vec3', 'vec2', 'quat', 'coord3', 'lerp',

    # Differential geometry classes (v3.3.0+)
    'Surface', 'Sphere', 'Torus',
    'MetricTensor', 'IntrinsicGradientOperator', 'IntrinsicGradientCurvatureCalculator',

    # Differential geometry functions (v3.3.0+)
    'compute_intrinsic_gradient',
    'compute_gaussian_curvature',
    'compute_mean_curvature',
    'compute_riemann_curvature',
    'compute_all_curvatures',

    # High-precision curvature module - Classical method (v2.3.0+)
    'CurvatureCalculator',
    'gaussian_curvature', 'mean_curvature',
    'principal_curvatures', 'all_curvatures',

    # Intrinsic Gradient Operator method (v2.4.0+)
    'intrinsic_gradient_gaussian_curvature',
    'intrinsic_gradient_mean_curvature',
    'intrinsic_gradient_principal_curvatures',
    'intrinsic_gradient_all_curvatures',
    'compare_methods',

    # Utility functions
    'derivative_5pt', 'derivative_2nd_5pt', 'richardson_extrapolation',

    # Fourier spectral analysis (v4.0.0+)
    'FourierTransformer', 'SpectralAnalyzer', 'FrameFieldSpectrum',
    'GPUFourierTransformer', 'BatchCoordTransformer',
    'spectral_intrinsic_gradient', 'spectral_curvature_calculator',
    'berry_phase_calculator', 'topological_invariant_analyzer',
    'fft2_coord_field', 'ifft2_spectrum', 
    'compute_spectral_density', 'radial_spectrum_average',
]

# Constants for unit vectors and zero point
ZERO3 = vec3(0.0, 0.0, 0.0)         # Zero vector (origin point)
UNITX = vec3(1.0, 0.0, 0.0)         # Unit vector in X direction  
UNITY = vec3(0.0, 1.0, 0.0)         # Unit vector in Y direction
UNITZ = vec3(0.0, 0.0, 1.0)         # Unit vector in Z direction
ONE3  = vec3(1.0, 1.0, 1.0)         # Unit scale vector (1,1,1)

# Unit quaternion (no rotation)
ONE4 = quat(1.0, 0.0, 0.0, 0.0)

# World coordinate system (the fundamental unit one in 3D space)
ONEC = coord3(ZERO3, ONE4, ONE3)

def lerp(a: vec3, b: vec3, t: float) -> vec3:
    """
    Linear interpolation between two points in 3D space
    
    The concept of interpolation embodies the metaphysical principle of 
    continuum - the smooth transition between states that preserves 
    the fundamental unity of spatial relationships
    
    Args:
        a: Starting point (thesis)
        b: End point (antithesis)  
        t: Interpolation ratio [0,1] (synthesis parameter)
        
    Returns:
        The interpolated point (synthesis)
    """
    return a + (b - a) * t

class CoordTuple(tuple):
    """
    Custom tuple subclass that supports operations with coord3 objects
    
    This class represents the metaphysical concept of 'potentiality' - 
    the tuple as pure mathematical form that can interact with the 
    actualized coordinate system (coord3) to produce new actualities
    """
    
    def __mul__(self, other):
        """Multiplication operation supporting coord3 interaction"""
        if isinstance(other, coord3):
            return self._mul_coord3(other)
        return super().__mul__(other)
    
    def __rmul__(self, other):
        """Right multiplication operation supporting coord3 interaction"""
        if isinstance(other, coord3):
            return self._mul_coord3(other)
        return super().__rmul__(other)
    
    def __truediv__(self, other):
        """Division operation supporting coord3 interaction"""
        if isinstance(other, coord3):
            return self._div_coord3(other)
        return super().__truediv__(other)
    
    def _mul_coord3(self, coord: coord3) -> tuple:
        """
        Tuple multiplication with coordinate system
        
        Represents the metaphysical operation where mathematical forms 
        (tuple) interact with actualized space (coord3) to produce 
        new spatial relationships
        """
        if len(self) != 3:
            raise ValueError("Tuple must have exactly 3 elements for spatial operations")
        
        x, y, z = self
        scale_vec = vec3(x, y, z)
        result = scale_vec * coord
        return (result.x, result.y, result.z)
    
    def _div_coord3(self, coord: coord3) -> tuple:
        """
        Tuple division with coordinate system
        
        The inverse operation of multiplication, representing the 
        decomposition of spatial relationships into their mathematical 
        components
        """
        if len(self) != 3:
            raise ValueError("Tuple must have exactly 3 elements for spatial operations")
        
        x, y, z = self
        # Check for division by zero (preservation of metaphysical integrity)
        if x == 0 or y == 0 or z == 0:
            raise ZeroDivisionError("Division by zero violates the principle of continuity")
        
        scale_vec = vec3(x, y, z)
        result = scale_vec / coord
        return (result.x, result.y, result.z)

# Store original coord3 operators for metaphysical preservation
_original_coord3_mul = coord3.__mul__
_original_coord3_rmul = coord3.__rmul__
_original_coord3_truediv = getattr(coord3, '__truediv__', None)

def _new_coord3_mul(self, other):
    """
    Enhanced multiplication operator for coord3
    
    Enables interaction between actualized coordinate systems (coord3) 
    and mathematical forms (tuples), embodying the Aristotelian concept 
    of actuality interacting with potentiality
    """
    if isinstance(other, tuple):
        # Transform pure form (tuple) into operational entity (CoordTuple)
        other = CoordTuple(other)
        return other * self
    return _original_coord3_mul(self, other)

def _new_coord3_rmul(self, other):
    """
    Enhanced right multiplication operator for coord3
    
    The commutative property in spatial operations reflects the 
    metaphysical principle of reciprocity in relationships
    """
    if isinstance(other, tuple):
        other = CoordTuple(other)
        return other * self
    return _original_coord3_rmul(self, other)

def _new_coord3_truediv(self, other):
    """
    Enhanced division operator for coord3
    
    Division represents the analytical decomposition of spatial 
    relationships, revealing the underlying mathematical structure
    """
    if isinstance(other, tuple):
        other = CoordTuple(other)
        return other / self
    if _original_coord3_truediv:
        return _original_coord3_truediv(self, other)
    raise TypeError(f"unsupported operand type(s) for /: 'coord3' and {type(other).__name__}")

# Apply metaphysical enhancements to coord3 operators
coord3.__mul__ = _new_coord3_mul
coord3.__rmul__ = _new_coord3_rmul
coord3.__truediv__ = _new_coord3_truediv