# coordinate_system/fourier_spectral.py

import numpy as np
from typing import List, Tuple, Dict, Optional, Union, Any
from dataclasses import dataclass
from .coordinate_system import coord3, vec3, quat

# GPU availability check with proper error handling
try:
    import cupy as cp
    import cupyx.scipy.fft as cufft
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    # Create dummy types for type checking when GPU is not available
    class DummyCP:
        ndarray = np.ndarray
        def asarray(self, *args, **kwargs):
            raise RuntimeError("CuPy not available")
        def matmul(self, *args, **kwargs):
            raise RuntimeError("CuPy not available")
    cp = DummyCP()
    cufft = None

@dataclass
class FrameFieldSpectrum:
    """Fourier spectrum representation of coordinate frame field"""
    ux_spectrum: np.ndarray  # Fourier coefficients for x-axis basis vectors
    uy_spectrum: np.ndarray  # Fourier coefficients for y-axis basis vectors  
    uz_spectrum: np.ndarray  # Fourier coefficients for z-axis basis vectors
    origin_spectrum: np.ndarray  # Fourier coefficients for origin positions
    frequencies: Tuple[np.ndarray, np.ndarray]  # Frequency grids (kx, ky)
    
    def __post_init__(self):
        """Validate spectrum data dimension consistency"""
        shapes = [self.ux_spectrum.shape, self.uy_spectrum.shape, 
                 self.uz_spectrum.shape, self.origin_spectrum.shape]
        if not all(shape == shapes[0] for shape in shapes):
            raise ValueError("All spectrum components must have the same dimensions")

class FourierTransformer:
    """Base Fourier transformer class"""
    
    def __init__(self, grid_size: Tuple[int, int] = (64, 64)):
        self.grid_size = grid_size
        self.ny, self.nx = grid_size
        
    def coord_field_to_tensor(self, coord_field: List[List[coord3]]) -> np.ndarray:
        """Convert coordinate field to tensor representation"""
        # Validate grid dimensions
        actual_ny = len(coord_field)
        actual_nx = len(coord_field[0]) if actual_ny > 0 else 0
        
        if actual_ny != self.ny or actual_nx != self.nx:
            raise ValueError(f"Coordinate field dimensions ({actual_ny}x{actual_nx}) "
                           f"do not match expected grid size ({self.ny}x{self.nx})")
        
        tensor_field = np.zeros((self.ny, self.nx, 12), dtype=np.float64)
        
        for i in range(self.ny):
            for j in range(self.nx):
                coord = coord_field[i][j]
                # Position (3), basis vectors (9)
                tensor_field[i, j, 0:3] = [coord.o.x, coord.o.y, coord.o.z]
                tensor_field[i, j, 3:6] = [coord.ux.x, coord.ux.y, coord.ux.z]
                tensor_field[i, j, 6:9] = [coord.uy.x, coord.uy.y, coord.uy.z]
                tensor_field[i, j, 9:12] = [coord.uz.x, coord.uz.y, coord.uz.z]
                
        return tensor_field
    
    def fft2_coord_field(self, coord_field: List[List[coord3]]) -> FrameFieldSpectrum:
        """Perform 2D Fourier transform on coordinate field"""
        tensor_field = self.coord_field_to_tensor(coord_field)
        
        # Separate components
        origin_field = tensor_field[..., 0:3]  # Position field
        ux_field = tensor_field[..., 3:6]      # x-axis basis field
        uy_field = tensor_field[..., 6:9]      # y-axis basis field
        uz_field = tensor_field[..., 9:12]     # z-axis basis field
        
        # Fourier transform
        origin_spectrum = np.fft.fft2(origin_field, axes=(0, 1))
        ux_spectrum = np.fft.fft2(ux_field, axes=(0, 1))
        uy_spectrum = np.fft.fft2(uy_field, axes=(0, 1))
        uz_spectrum = np.fft.fft2(uz_field, axes=(0, 1))
        
        # Frequency grids
        kx = np.fft.fftfreq(self.nx)
        ky = np.fft.fftfreq(self.ny)
        
        return FrameFieldSpectrum(
            ux_spectrum=ux_spectrum,
            uy_spectrum=uy_spectrum,
            uz_spectrum=uz_spectrum,
            origin_spectrum=origin_spectrum,
            frequencies=(kx, ky)
        )
    
    def ifft2_spectrum(self, spectrum: FrameFieldSpectrum) -> List[List[coord3]]:
        """Inverse Fourier transform to reconstruct coordinate field"""
        # Inverse transform each component
        origin_field = np.fft.ifft2(spectrum.origin_spectrum, axes=(0, 1)).real
        ux_field = np.fft.ifft2(spectrum.ux_spectrum, axes=(0, 1)).real
        uy_field = np.fft.ifft2(spectrum.uy_spectrum, axes=(0, 1)).real
        uz_field = np.fft.ifft2(spectrum.uz_spectrum, axes=(0, 1)).real
        
        # Reconstruct coordinate field
        coord_field = []
        for i in range(self.ny):
            row = []
            for j in range(self.nx):
                o = vec3(origin_field[i, j, 0], origin_field[i, j, 1], origin_field[i, j, 2])
                ux = vec3(ux_field[i, j, 0], ux_field[i, j, 1], ux_field[i, j, 2])
                uy = vec3(uy_field[i, j, 0], uy_field[i, j, 1], uy_field[i, j, 2])
                uz = vec3(uz_field[i, j, 0], uz_field[i, j, 1], uz_field[i, j, 2])
                
                # Create coordinate system (using unit quaternion, unit scale)
                coord = coord3(o, quat(1, 0, 0, 0), vec3(1, 1, 1))
                coord.ux, coord.uy, coord.uz = ux, uy, uz
                row.append(coord)
            coord_field.append(row)
            
        return coord_field

class GPUFourierTransformer(FourierTransformer):
    """GPU-accelerated Fourier transformer"""
    
    def __init__(self, grid_size: Tuple[int, int] = (64, 64)):
        super().__init__(grid_size)
        if not GPU_AVAILABLE:
            raise RuntimeError("CuPy not available. GPU acceleration requires CuPy installation.")
    
    def fft2_coord_field(self, coord_field: List[List[coord3]]) -> FrameFieldSpectrum:
        """GPU-accelerated Fourier transform of coordinate field"""
        tensor_field = self.coord_field_to_tensor(coord_field)
        
        # Transfer to GPU
        tensor_field_gpu = cp.asarray(tensor_field)
        
        # Separate components
        origin_field = tensor_field_gpu[..., 0:3]
        ux_field = tensor_field_gpu[..., 3:6]
        uy_field = tensor_field_gpu[..., 6:9]
        uz_field = tensor_field_gpu[..., 9:12]
        
        # GPU Fourier transform
        origin_spectrum = cufft.fft2(origin_field, axes=(0, 1))
        ux_spectrum = cufft.fft2(ux_field, axes=(0, 1))
        uy_spectrum = cufft.fft2(uy_field, axes=(0, 1))
        uz_spectrum = cufft.fft2(uz_field, axes=(0, 1))
        
        # Transfer back to CPU
        origin_spectrum = cp.asnumpy(origin_spectrum)
        ux_spectrum = cp.asnumpy(ux_spectrum)
        uy_spectrum = cp.asnumpy(uy_spectrum)
        uz_spectrum = cp.asnumpy(uz_spectrum)
        
        kx = np.fft.fftfreq(self.nx)
        ky = np.fft.fftfreq(self.ny)
        
        return FrameFieldSpectrum(
            ux_spectrum=ux_spectrum,
            uy_spectrum=uy_spectrum,
            uz_spectrum=uz_spectrum,
            origin_spectrum=origin_spectrum,
            frequencies=(kx, ky)
        )
    
    def ifft2_spectrum(self, spectrum: FrameFieldSpectrum) -> List[List[coord3]]:
        """GPU-accelerated inverse Fourier transform"""
        # Transfer to GPU
        origin_spectrum_gpu = cp.asarray(spectrum.origin_spectrum)
        ux_spectrum_gpu = cp.asarray(spectrum.ux_spectrum)
        uy_spectrum_gpu = cp.asarray(spectrum.uy_spectrum)
        uz_spectrum_gpu = cp.asarray(spectrum.uz_spectrum)
        
        # GPU inverse transform
        origin_field = cufft.ifft2(origin_spectrum_gpu, axes=(0, 1)).real
        ux_field = cufft.ifft2(ux_spectrum_gpu, axes=(0, 1)).real
        uy_field = cufft.ifft2(uy_spectrum_gpu, axes=(0, 1)).real
        uz_field = cufft.ifft2(uz_spectrum_gpu, axes=(0, 1)).real
        
        # Transfer back to CPU
        origin_field = cp.asnumpy(origin_field)
        ux_field = cp.asnumpy(ux_field)
        uy_field = cp.asnumpy(uy_field)
        uz_field = cp.asnumpy(uz_field)
        
        # Reconstruct coordinate field
        coord_field = []
        for i in range(self.ny):
            row = []
            for j in range(self.nx):
                o = vec3(origin_field[i, j, 0], origin_field[i, j, 1], origin_field[i, j, 2])
                ux = vec3(ux_field[i, j, 0], ux_field[i, j, 1], ux_field[i, j, 2])
                uy = vec3(uy_field[i, j, 0], uy_field[i, j, 1], uy_field[i, j, 2])
                uz = vec3(uz_field[i, j, 0], uz_field[i, j, 1], uz_field[i, j, 2])
                
                coord = coord3(o, quat(1, 0, 0, 0), vec3(1, 1, 1))
                coord.ux, coord.uy, coord.uz = ux, uy, uz
                row.append(coord)
            coord_field.append(row)
            
        return coord_field

class BatchCoordTransformer:
    """Batch coordinate transformer (GPU accelerated)"""
    
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
        self.gpu_available = GPU_AVAILABLE
    
    def batch_coord_transform(self, coords: List[coord3], 
                            transformations: List[coord3]) -> List[coord3]:
        """Batch coordinate transformation"""
        if len(coords) != len(transformations):
            raise ValueError("Number of coordinates and transformations must match")
            
        if self.gpu_available and len(coords) > 100:
            return self._gpu_batch_transform(coords, transformations)
        else:
            return self._cpu_batch_transform(coords, transformations)
    
    def _cpu_batch_transform(self, coords: List[coord3], 
                           transformations: List[coord3]) -> List[coord3]:
        """CPU batch transformation"""
        results = []
        for coord, transform in zip(coords, transformations):
            results.append(coord * transform)
        return results
    
    def _gpu_batch_transform(self, coords: List[coord3], 
                           transformations: List[coord3]) -> List[coord3]:
        """GPU batch transformation"""
        if not self.gpu_available:
            return self._cpu_batch_transform(coords, transformations)
            
        # Convert coordinate data to tensors
        coord_tensors = self._coords_to_tensor_batch(coords)
        transform_tensors = self._coords_to_tensor_batch(transformations)
        
        # Transfer to GPU and perform batch matrix operations
        coord_tensors_gpu = cp.asarray(coord_tensors)
        transform_tensors_gpu = cp.asarray(transform_tensors)
        
        # Execute batch coordinate multiplication
        result_tensors_gpu = self._gpu_coord_multiply(coord_tensors_gpu, transform_tensors_gpu)
        
        # Transfer back to CPU and reconstruct coordinates
        result_tensors = cp.asnumpy(result_tensors_gpu)
        return self._tensor_batch_to_coords(result_tensors)
    
    def _coords_to_tensor_batch(self, coords: List[coord3]) -> np.ndarray:
        """Convert batch coordinates to tensors"""
        batch_size = len(coords)
        tensors = np.zeros((batch_size, 4, 4), dtype=np.float64)
        
        for i, coord in enumerate(coords):
            # Build 4x4 homogeneous transformation matrix
            tensors[i, 0, 0:3] = [coord.ux.x, coord.uy.x, coord.uz.x]
            tensors[i, 1, 0:3] = [coord.ux.y, coord.uy.y, coord.uz.y]
            tensors[i, 2, 0:3] = [coord.ux.z, coord.uy.z, coord.uz.z]
            tensors[i, 3, 0:3] = [coord.o.x, coord.o.y, coord.o.z]
            tensors[i, 3, 3] = 1.0
            
        return tensors
    
    def _tensor_batch_to_coords(self, tensors: np.ndarray) -> List[coord3]:
        """Convert tensor batch to coordinates"""
        coords = []
        for i in range(tensors.shape[0]):
            matrix = tensors[i]
            o = vec3(matrix[3, 0], matrix[3, 1], matrix[3, 2])
            ux = vec3(matrix[0, 0], matrix[1, 0], matrix[2, 0])
            uy = vec3(matrix[0, 1], matrix[1, 1], matrix[2, 1])
            uz = vec3(matrix[0, 2], matrix[1, 2], matrix[2, 2])
            
            coord = coord3(o, quat(1, 0, 0, 0), vec3(1, 1, 1))
            coord.ux, coord.uy, coord.uz = ux, uy, uz
            coords.append(coord)
            
        return coords
    
    def _gpu_coord_multiply(self, A: Any, B: Any) -> Any:
        """Batch coordinate multiplication on GPU"""
        if not self.gpu_available:
            # Fallback to CPU implementation
            A_np = A if isinstance(A, np.ndarray) else cp.asnumpy(A)
            B_np = B if isinstance(B, np.ndarray) else cp.asnumpy(B)
            return np.matmul(A_np, B_np)
        
        # GPU matrix multiplication
        return cp.matmul(A, B)

class SpectralAnalyzer:
    """Spectral geometry analyzer"""
    
    def __init__(self, transformer: FourierTransformer = None):
        self.transformer = transformer or FourierTransformer()
    
    def compute_spectral_density(self, spectrum: FrameFieldSpectrum) -> np.ndarray:
        """Compute spectral energy density"""
        energy_density = (np.abs(spectrum.ux_spectrum)**2 + 
                         np.abs(spectrum.uy_spectrum)**2 + 
                         np.abs(spectrum.uz_spectrum)**2)
        return np.mean(energy_density, axis=-1)  # Average over vector components
    
    def radial_spectrum_average(self, spectrum: FrameFieldSpectrum) -> Tuple[np.ndarray, np.ndarray]:
        """Radial spectrum average (ShapeDNA)"""
        kx, ky = spectrum.frequencies
        k_mag = np.sqrt(kx[:, None]**2 + ky[None, :]**2)
        
        spectral_density = self.compute_spectral_density(spectrum)
        
        # Radial binning
        k_max = np.max(k_mag)
        k_bins = np.linspace(0, k_max, 50)
        radial_avg = np.zeros_like(k_bins)
        
        for i, k_val in enumerate(k_bins[:-1]):
            mask = (k_mag >= k_bins[i]) & (k_mag < k_bins[i+1])
            if np.any(mask):
                radial_avg[i] = np.mean(spectral_density[mask])
        
        return k_bins, radial_avg

# Convenience functions
def fft2_coord_field(coord_field: List[List[coord3]], 
                    grid_size: Tuple[int, int] = (64, 64),
                    use_gpu: bool = False) -> FrameFieldSpectrum:
    """2D Fourier transform of coordinate field"""
    if use_gpu and GPU_AVAILABLE:
        transformer = GPUFourierTransformer(grid_size)
    else:
        transformer = FourierTransformer(grid_size)
    return transformer.fft2_coord_field(coord_field)

def ifft2_spectrum(spectrum: FrameFieldSpectrum, 
                  use_gpu: bool = False) -> List[List[coord3]]:
    """Inverse Fourier transform to reconstruct coordinate field"""
    if use_gpu and GPU_AVAILABLE:
        transformer = GPUFourierTransformer()
    else:
        transformer = FourierTransformer()
    return transformer.ifft2_spectrum(spectrum)

def compute_spectral_density(spectrum: FrameFieldSpectrum) -> np.ndarray:
    """Compute spectral energy density"""
    analyzer = SpectralAnalyzer()
    return analyzer.compute_spectral_density(spectrum)

def radial_spectrum_average(spectrum: FrameFieldSpectrum) -> Tuple[np.ndarray, np.ndarray]:
    """Radial spectrum average"""
    analyzer = SpectralAnalyzer()
    return analyzer.radial_spectrum_average(spectrum)

# Placeholder functions - to be implemented in complete version
def spectral_intrinsic_gradient(spectrum: FrameFieldSpectrum) -> FrameFieldSpectrum:
    """Intrinsic gradient calculation in spectral space"""
    # Implement intrinsic gradient operator in spectral space
    return spectrum

def spectral_curvature_calculator(spectrum: FrameFieldSpectrum) -> Dict:
    """Spectral curvature calculation"""
    # Implement curvature calculation based on spectrum
    return {}

def berry_phase_calculator(spectrum: FrameFieldSpectrum) -> float:
    """Berry phase calculation"""
    # Implement topological invariant calculation
    return 0.0

def topological_invariant_analyzer(spectrum: FrameFieldSpectrum) -> Dict:
    """Topological invariant analysis"""
    # Implement complete topological analysis
    return {}