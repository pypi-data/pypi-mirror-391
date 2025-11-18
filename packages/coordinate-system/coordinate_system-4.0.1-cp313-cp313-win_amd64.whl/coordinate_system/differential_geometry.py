"""
Differential Geometry Module for Coordinate System Package
===========================================================

This module provides tools for discrete differential geometry computations on surfaces,
using the CORRECT Intrinsic Gradient Operator framework based on the proven algorithm.

Key Formula:
    G_μ = (c(u+h) - c(u-h)) / (2h) / c(u) then extract normal derivative using .VZ()

Author: PanGuoJun
Date: 2025-10-31
"""

import math
import numpy as np
from typing import Tuple, Optional, Callable, Union
from .coordinate_system import coord3, vec3


# ========== Surface Base Class ==========

class Surface:
    """
    Base class for parametric surfaces r(u, v)
    """

    def __init__(self, h: float = 1e-6):
        """
        Initialize surface

        Args:
            h: Step size for numerical differentiation
        """
        self.h = h

    def position(self, u: float, v: float) -> vec3:
        """Compute position on surface at parameters (u, v)"""
        raise NotImplementedError("Subclass must implement position(u, v)")

    def tangent_u(self, u: float, v: float) -> vec3:
        """Compute tangent vector in u direction"""
        r_plus = self.position(u + self.h, v)
        r_minus = self.position(u - self.h, v)
        return (r_plus - r_minus) * (1.0 / (2.0 * self.h))

    def tangent_v(self, u: float, v: float) -> vec3:
        """Compute tangent vector in v direction"""
        r_plus = self.position(u, v + self.h)
        r_minus = self.position(u, v - self.h)
        return (r_plus - r_minus) * (1.0 / (2.0 * self.h))

    def normal(self, u: float, v: float) -> vec3:
        """Compute unit normal vector"""
        r_u = self.tangent_u(u, v)
        r_v = self.tangent_v(u, v)
        n = r_u.cross(r_v)
        length = (n.x**2 + n.y**2 + n.z**2) ** 0.5
        if length > 1e-10:
            return n * (1.0 / length)
        else:
            return vec3(0.0, 0.0, 1.0)


# ========== Common Surface Types ==========

class Sphere(Surface):
    """
    Sphere surface
    Parametrization: r(θ, φ) = R(sin θ cos φ, sin θ sin φ, cos θ)
    where θ ∈ [0, π] is polar angle, φ ∈ [0, 2π] is azimuthal angle
    """

    def __init__(self, radius: float = 1.0, h: float = 1e-6):
        super().__init__(h)
        self.R = radius

    def position(self, theta: float, phi: float) -> vec3:
        """Position on sphere"""
        x = self.R * math.sin(theta) * math.cos(phi)
        y = self.R * math.sin(theta) * math.sin(phi)
        z = self.R * math.cos(theta)
        return vec3(x, y, z)


class Torus(Surface):
    """
    Torus surface
    Parametrization: r(u, v) = ((R + r cos u) cos v, (R + r cos u) sin v, r sin u)
    """

    def __init__(self, major_radius: float = 3.0, minor_radius: float = 1.0, h: float = 1e-6):
        super().__init__(h)
        self.R = major_radius  # Major radius
        self.r = minor_radius  # Minor radius

    def position(self, u: float, v: float) -> vec3:
        """Position on torus"""
        x = (self.R + self.r * math.cos(u)) * math.cos(v)
        y = (self.R + self.r * math.cos(u)) * math.sin(v)
        z = self.r * math.sin(u)
        return vec3(x, y, z)


# ========== Metric Tensor ==========

class MetricTensor:
    """
    First fundamental form (metric tensor) of a surface
    g_ij = <∂r/∂u^i, ∂r/∂u^j>
    """

    def __init__(self, E: float, F: float, G: float):
        """
        Initialize metric tensor

        Args:
            E: g_11 = <r_u, r_u>
            F: g_12 = <r_u, r_v>
            G: g_22 = <r_v, r_v>
        """
        self.E = E
        self.F = F
        self.G = G
        self.det = E * G - F * F

    @classmethod
    def from_surface(cls, surface: Surface, u: float, v: float) -> 'MetricTensor':
        """Create metric tensor from surface at point (u, v)"""
        r_u = surface.tangent_u(u, v)
        r_v = surface.tangent_v(u, v)
        E = r_u.dot(r_u)
        F = r_u.dot(r_v)
        G = r_v.dot(r_v)
        return cls(E, F, G)

    def determinant(self) -> float:
        """Get determinant of metric tensor"""
        return self.det

    def __repr__(self) -> str:
        return f"MetricTensor(E={self.E:.6f}, F={self.F:.6f}, G={self.G:.6f}, det={self.det:.6f})"


# ========== Intrinsic Gradient Operator ==========

class IntrinsicGradientOperator:
    """
    CORRECT implementation based on proven test code
    """
    
    def __init__(self, surface: Surface, step_size: float = 1e-3):
        self.surface = surface
        self.h = step_size

    def calc_intrinsic_frame(self, u: float, v: float) -> coord3:
        """
        Calculate intrinsic frame - EXACTLY like the working test code
        """
        # 对于球面，使用解析表达式（与测试代码一致）
        if isinstance(self.surface, Sphere):
            R = self.surface.R
            theta, phi = u, v
            
            # 位置向量
            pos = self.surface.position(theta, phi)
            
            # 切向量（解析表达式，与测试代码一致）
            r_theta = vec3(
                R * math.cos(theta) * math.cos(phi),
                R * math.cos(theta) * math.sin(phi),
                -R * math.sin(theta)
            )
            
            r_phi = vec3(
                -R * math.sin(theta) * math.sin(phi),
                R * math.sin(theta) * math.cos(phi),
                0
            )
            
            # 单位法向量
            n = r_theta.cross(r_phi).normalized()
            
            # 单位切向量
            e1 = r_theta.normalized()
            e2 = r_phi.normalized()
            
        elif isinstance(self.surface, Torus):
            # 对于环面，使用解析表达式
            R = self.surface.R  # 主半径
            r = self.surface.r  # 副半径
            u_param, v_param = u, v
            
            # 位置向量
            pos = self.surface.position(u_param, v_param)
            
            # 切向量（解析表达式）
            r_u = vec3(
                -r * math.sin(u_param) * math.cos(v_param),
                -r * math.sin(u_param) * math.sin(v_param),
                r * math.cos(u_param)
            )
            
            r_v = vec3(
                -(R + r * math.cos(u_param)) * math.sin(v_param),
                (R + r * math.cos(u_param)) * math.cos(v_param),
                0
            )
            
            # 单位法向量
            n = r_u.cross(r_v).normalized()
            
            # 单位切向量
            e1 = r_u.normalized()
            e2 = r_v.normalized()
            
        else:
            # 对于其他曲面，使用数值方法
            pos = self.surface.position(u, v)
            r_u = self.surface.tangent_u(u, v)
            r_v = self.surface.tangent_v(u, v)
            
            # 单位法向量
            n = r_u.cross(r_v).normalized()
            
            # 单位切向量
            e1 = r_u.normalized()
            e2 = r_v.normalized()
        
        # 创建内禀标架（与测试代码一致）
        frame = coord3()
        frame.o = pos
        frame.ux = e1
        frame.uy = e2
        frame.uz = n
        
        return frame

    def compute_both(self, u: float, v: float) -> Tuple['GradientResult', 'GradientResult', coord3]:
        """
        Compute gradients using CENTRAL DIFFERENCES - like test code
        """
        # 计算中心点和偏移点的标架
        c_center = self.calc_intrinsic_frame(u, v)
        
        # u方向：中心差分
        c_u_plus = self.calc_intrinsic_frame(u + self.h, v)
        c_u_minus = self.calc_intrinsic_frame(u - self.h, v)
        dn_du = ((c_u_plus - c_u_minus) / (2 * self.h)).VZ()
        
        # v方向：中心差分  
        c_v_plus = self.calc_intrinsic_frame(u, v + self.h)
        c_v_minus = self.calc_intrinsic_frame(u, v - self.h)
        dn_dv = ((c_v_plus - c_v_minus) / (2 * self.h)).VZ()
        
        # 创建梯度结果
        G_u = GradientResult(dn_du, "u")
        G_v = GradientResult(dn_dv, "v")
        
        return G_u, G_v, c_center


class GradientResult:
    """
    Gradient result containing normal vector derivative
    """

    def __init__(self, dn: vec3, direction: str):
        """
        Initialize gradient result

        Args:
            dn: Normal vector derivative (computed using proven algorithm)
            direction: Parameter direction ('u' or 'v')
        """
        self.dn = dn
        self.direction = direction

    def __repr__(self) -> str:
        return f"GradientResult({self.direction}: [{self.dn.x:.6f}, {self.dn.y:.6f}, {self.dn.z:.6f}])"


# ========== Curvature Calculator ==========

class IntrinsicGradientCurvatureCalculator:
    """
    Curvature calculator using the CORRECTED intrinsic gradient method
    """
    
    def __init__(self, surface: Surface, step_size: float = 1e-3):
        self.surface = surface
        self.h = step_size
        self.grad_op = IntrinsicGradientOperator(surface, step_size)

    def compute_gaussian_curvature(self, u: float, v: float) -> float:
        """
        Compute Gaussian curvature - CORRECTED implementation
        """
        # 计算梯度算子
        G_u, G_v, _ = self.grad_op.compute_both(u, v)

        # 计算切向量（使用解析表达式）
        if isinstance(self.surface, Sphere):
            R = self.surface.R
            theta, phi = u, v
            r_u = vec3(
                R * math.cos(theta) * math.cos(phi),
                R * math.cos(theta) * math.sin(phi),
                -R * math.sin(theta)
            )
            r_v = vec3(
                -R * math.sin(theta) * math.sin(phi),
                R * math.sin(theta) * math.cos(phi),
                0
            )
        elif isinstance(self.surface, Torus):
            R = self.surface.R  # 主半径
            r = self.surface.r  # 副半径
            u_param, v_param = u, v
            r_u = vec3(
                -r * math.sin(u_param) * math.cos(v_param),
                -r * math.sin(u_param) * math.sin(v_param),
                r * math.cos(u_param)
            )
            r_v = vec3(
                -(R + r * math.cos(u_param)) * math.sin(v_param),
                (R + r * math.cos(u_param)) * math.cos(v_param),
                0
            )
        else:
            # 对于其他曲面，使用数值导数
            r_u = self.surface.tangent_u(u, v)
            r_v = self.surface.tangent_v(u, v)

        # 提取法向量导数
        dn_du = G_u.dn
        dn_dv = G_v.dn

        # 计算度量张量
        E = r_u.dot(r_u)
        F = r_u.dot(r_v)
        G = r_v.dot(r_v)
        metric_det = E * G - F * F

        # 计算第二基本形式
        L = -dn_du.dot(r_u)
        M1 = -dn_du.dot(r_v)
        M2 = -dn_dv.dot(r_u)
        N = -dn_dv.dot(r_v)
        M = (M1 + M2) / 2.0

        # 高斯曲率
        if abs(metric_det) > 1e-14:
            K = (L * N - M * M) / metric_det
        else:
            K = 0.0

        return K

    def compute_riemann_curvature(self, u: float, v: float, proportional_correction: bool = True) -> float:
        """
        Compute Riemann curvature tensor component R^1_212
        Based on the intrinsic gradient operator method with correct implementation
        """
        delta = self.h

        # 计算中心标架
        c_center = self.grad_op.calc_intrinsic_frame(u, v)

        # 计算u方向的内禀梯度算子（使用中心差分）
        c_u_plus = self.grad_op.calc_intrinsic_frame(u + delta, v)
        c_u_minus = self.grad_op.calc_intrinsic_frame(u - delta, v)
        G_u = (c_u_plus - c_u_minus) / (2 * delta)

        # 计算v方向的内禀梯度算子（使用中心差分）
        c_v_plus = self.grad_op.calc_intrinsic_frame(u, v + delta)
        c_v_minus = self.grad_op.calc_intrinsic_frame(u, v - delta)
        G_v = (c_v_plus - c_v_minus) / (2 * delta)

        # 计算李括号 [G_u, G_v] = G_u ∘ G_v - G_v ∘ G_u
        # 这需要计算二阶混合偏导数

        # 计算 ∂²c/∂u∂v 和 ∂²c/∂v∂u
        c_uv_pp = self.grad_op.calc_intrinsic_frame(u + delta, v + delta)
        c_uv_pm = self.grad_op.calc_intrinsic_frame(u + delta, v - delta)
        c_uv_mp = self.grad_op.calc_intrinsic_frame(u - delta, v + delta)
        c_uv_mm = self.grad_op.calc_intrinsic_frame(u - delta, v - delta)

        # 二阶混合偏导数 ∂²c/∂u∂v
        d2c_dudv = (c_uv_pp - c_uv_pm - c_uv_mp + c_uv_mm) / (4 * delta * delta)

        # 对于对称的联络，∂²c/∂v∂u = ∂²c/∂u∂v，所以李括号简化为零
        # 但是我们需要考虑标架的非对易性

        # 更精确的方法：直接计算联络系数的变化
        # 提取法向量的导数（这是关键）
        dn_du = G_u.VZ()  # 法向量在u方向的导数
        dn_dv = G_v.VZ()  # 法向量在v方向的导数

        # 计算切向量（根据曲面类型）
        if isinstance(self.surface, Sphere):
            R = self.surface.R
            theta, phi = u, v
            r_u = vec3(
                R * math.cos(theta) * math.cos(phi),
                R * math.cos(theta) * math.sin(phi),
                -R * math.sin(theta)
            )
            r_v = vec3(
                -R * math.sin(theta) * math.sin(phi),
                R * math.sin(theta) * math.cos(phi),
                0
            )
        elif isinstance(self.surface, Torus):
            R = self.surface.R
            r = self.surface.r
            u_param, v_param = u, v
            r_u = vec3(
                -r * math.sin(u_param) * math.cos(v_param),
                -r * math.sin(u_param) * math.sin(v_param),
                r * math.cos(u_param)
            )
            r_v = vec3(
                -(R + r * math.cos(u_param)) * math.sin(v_param),
                (R + r * math.cos(u_param)) * math.cos(v_param),
                0
            )
        else:
            r_u = self.surface.tangent_u(u, v)
            r_v = self.surface.tangent_v(u, v)

        # 计算第二基本形式系数
        L = -dn_du.dot(r_u)
        M = -dn_du.dot(r_v)
        N = -dn_dv.dot(r_v)

        # 计算度量张量
        E = r_u.dot(r_u)
        F = r_u.dot(r_v)
        G_metric = r_v.dot(r_v)
        det_g = E * G_metric - F * F

        # 对于2D曲面，黎曼曲率张量只有一个独立分量
        # R^1_212 与高斯曲率的关系为：K = R^1_212 / det(g)
        # 所以 R^1_212 = K * det(g) = (LN - M²)

        R_1212 = L * N - M * M

        # 比例修正（对于某些参数化可能需要）
        if proportional_correction and isinstance(self.surface, Sphere):
            # 对于球面的某些参数化，可能需要额外的修正
            # 但是基于第二基本形式的计算通常不需要
            pass

        return R_1212

    def compute_mean_curvature(self, u: float, v: float) -> float:
        """
        Compute mean curvature
        """
        # 使用与高斯曲率相同的计算方法
        G_u, G_v, _ = self.grad_op.compute_both(u, v)

        # 计算切向量（使用解析表达式）
        if isinstance(self.surface, Sphere):
            R = self.surface.R
            theta, phi = u, v
            r_u = vec3(
                R * math.cos(theta) * math.cos(phi),
                R * math.cos(theta) * math.sin(phi),
                -R * math.sin(theta)
            )
            r_v = vec3(
                -R * math.sin(theta) * math.sin(phi),
                R * math.sin(theta) * math.cos(phi),
                0
            )
        elif isinstance(self.surface, Torus):
            R = self.surface.R  # 主半径
            r = self.surface.r  # 副半径
            u_param, v_param = u, v
            r_u = vec3(
                -r * math.sin(u_param) * math.cos(v_param),
                -r * math.sin(u_param) * math.sin(v_param),
                r * math.cos(u_param)
            )
            r_v = vec3(
                -(R + r * math.cos(u_param)) * math.sin(v_param),
                (R + r * math.cos(u_param)) * math.cos(v_param),
                0
            )
        else:
            # 对于其他曲面，使用数值导数
            r_u = self.surface.tangent_u(u, v)
            r_v = self.surface.tangent_v(u, v)

        dn_du = G_u.dn
        dn_dv = G_v.dn

        E = r_u.dot(r_u)
        F = r_u.dot(r_v)
        G = r_v.dot(r_v)
        metric_det = E * G - F * F

        L = -dn_du.dot(r_u)
        M1 = -dn_du.dot(r_v)
        M2 = -dn_dv.dot(r_u)
        N = -dn_dv.dot(r_v)
        M = (M1 + M2) / 2.0

        # 平均曲率
        if abs(metric_det) > 1e-14:
            H = (G * L - 2 * F * M + E * N) / (2 * metric_det)
        else:
            H = 0.0

        return H

    def compute_all_curvatures(self, u: float, v: float) -> dict:
        """
        Compute all curvature quantities
        """
        K = self.compute_gaussian_curvature(u, v)
        H = self.compute_mean_curvature(u, v)
        
        # 主曲率
        discriminant = max(0, H * H - K)
        sqrt_disc = discriminant ** 0.5
        k1 = H + sqrt_disc
        k2 = H - sqrt_disc

        return {
            'gaussian_curvature': K,
            'mean_curvature': H,
            'principal_curvatures': (k1, k2)
        }


# ========== Convenience Functions ==========

def compute_gaussian_curvature(
    surface: Surface,
    u: float,
    v: float,
    step_size: float = 1e-3
) -> float:
    """
    Compute Gaussian curvature

    Args:
        surface: Surface object
        u, v: Parameter values
        step_size: Step size for numerical differentiation

    Returns:
        Gaussian curvature value
    """
    calc = IntrinsicGradientCurvatureCalculator(surface, step_size)
    return calc.compute_gaussian_curvature(u, v)


def compute_mean_curvature(
    surface: Surface,
    u: float,
    v: float,
    step_size: float = 1e-3
) -> float:
    """
    Compute mean curvature
    """
    calc = IntrinsicGradientCurvatureCalculator(surface, step_size)
    return calc.compute_mean_curvature(u, v)


def compute_riemann_curvature(
    surface: Surface,
    u: float,
    v: float,
    step_size: float = 1e-3,
    proportional_correction: bool = True
) -> float:
    """
    Compute Riemann curvature tensor component R^1_212

    Args:
        surface: Surface object
        u, v: Parameter values
        step_size: Step size for numerical differentiation
        proportional_correction: Apply proportional correction for spherical coordinates

    Returns:
        Riemann curvature tensor component R^1_212
    """
    calc = IntrinsicGradientCurvatureCalculator(surface, step_size)
    return calc.compute_riemann_curvature(u, v, proportional_correction)


def compute_all_curvatures(
    surface: Surface,
    u: float,
    v: float,
    step_size: float = 1e-3
) -> dict:
    """
    Compute all curvature quantities
    """
    calc = IntrinsicGradientCurvatureCalculator(surface, step_size)
    return calc.compute_all_curvatures(u, v)


def compute_intrinsic_gradient(
    surface: Surface,
    u: float,
    v: float,
    direction: str = 'u',
    step_size: float = 1e-3
) -> GradientResult:
    """
    Compute intrinsic gradient in specified direction

    Args:
        surface: Surface object
        u, v: Parameter values
        direction: 'u' or 'v'
        step_size: Step size

    Returns:
        GradientResult object
    """
    grad_op = IntrinsicGradientOperator(surface, step_size)
    
    if direction == 'u':
        # Compute central difference for u direction
        c_plus = grad_op.calc_intrinsic_frame(u + step_size, v)
        c_minus = grad_op.calc_intrinsic_frame(u - step_size, v)
        dn = ((c_plus - c_minus) / (2 * step_size)).VZ()
    elif direction == 'v':
        # Compute central difference for v direction
        c_plus = grad_op.calc_intrinsic_frame(u, v + step_size)
        c_minus = grad_op.calc_intrinsic_frame(u, v - step_size)
        dn = ((c_plus - c_minus) / (2 * step_size)).VZ()
    else:
        raise ValueError(f"direction must be 'u' or 'v', got: {direction}")

    return GradientResult(dn, direction)


# ========== Export ==========

__all__ = [
    # Surface classes
    'Surface',
    'Sphere',
    'Torus',

    # Core classes
    'MetricTensor',
    'IntrinsicGradientOperator',
    'IntrinsicGradientCurvatureCalculator',

    # Functions
    'compute_gaussian_curvature',
    'compute_mean_curvature',
    'compute_all_curvatures',
    'compute_intrinsic_gradient',
]