"""
各种传感器之间的坐标转化功能
"""

import numpy as np
from typing import Union


class Lidar2Motor_1XXG:
    """
    手持电机1XXG系列 LiDAR点云外参转换类
    
    坐标系转换：Lidar -> Motor -> Motor-old_offset -> Motor+new_offset -> lidar
    用于将点云从旧外参坐标系转换到新外参坐标系
    自动根据数据规模选择最优计算方法（循环或向量化）
    """
    
    def __init__(self, vectorize_threshold: int = 100):
        """
        初始化转换器
        
        参数：
            vectorize_threshold: 向量化计算的阈值，当点云数量超过此值时使用向量化计算
                               默认100个点
        """
        self.vectorize_threshold = vectorize_threshold
    
    def cal_new_offset_matrix(
        self,
        points: np.ndarray,
        old_offset: np.ndarray,
        new_offset: np.ndarray,
        motor_angles: Union[np.ndarray, float]
    ) -> np.ndarray:
        """
        计算新外参下的点云坐标
        
        转换步骤：
        1. 先绕Z轴旋转 -motor_angle（回到原点坐标系）
        2. 减去旧offset old_offset（回到LiDAR原始坐标）
        3. 加上新offset new_offset（应用新外参）
        4. 最后绕Z轴旋转 +motor_angle（回到旋转后的坐标系）
        
        参数：
            points: 输入点云坐标，numpy数组
                   - 单点：shape为(3,)，[x, y, z]
                   - 多点：shape为(N, 3)，每行是[x, y, z]
                   单位：米
            old_offset: 旧外参offset向量，numpy数组，shape为(3,)，[ox, oy, oz]
                            单位：米
            new_offset: 新外参offset向量，numpy数组，shape为(3,)，[ox, oy, oz]
                            单位：米
            motor_angles: 电机旋转角度，单位：度
                         - 单个角度（float）：所有点使用相同角度
                         - numpy数组，shape为(N,)：每个点对应一个角度
        
        返回：
            np.ndarray: 转换后的点云坐标
                       - 输入单点时返回shape为(3,)
                       - 输入多点时返回shape为(N, 3)
        
        示例：
            >>> converter = Lidar2Motor_1XXG()
            >>> # 单点转换
            >>> point = np.array([20.5, 6.7, 16.3])
            >>> old_offset = np.array([10.123, 20.456, 30.789])
            >>> new_offset = np.array([30.987, 10.123, 20.456])
            >>> motor_angle = 0.008
            >>> result = converter.cal_new_offset_matrix(point, old_offset, new_offset, motor_angle)
            >>> 
            >>> # 多点转换
            >>> points = np.array([[20.5, 6.7, 16.3], [21.0, 7.0, 16.5]])
            >>> motor_angles = np.array([0.008, 0.009])
            >>> results = converter.cal_new_offset_matrix(points, old_offset, new_offset, motor_angles)
        """
        # 确保输入为numpy数组
        points = np.asarray(points, dtype=np.float64)
        old_offset = np.asarray(old_offset, dtype=np.float64)
        new_offset = np.asarray(new_offset, dtype=np.float64)
        
        # 验证offset向量维度
        if old_offset.shape != (3,):
            raise ValueError(f"旧offset向量必须是3维向量，当前维度: {old_offset.shape}")
        if new_offset.shape != (3,):
            raise ValueError(f"新offset向量必须是3维向量，当前维度: {new_offset.shape}")
        
        # 判断是单点还是多点
        is_single_point = (points.ndim == 1)
        
        if is_single_point:
            # 单点处理
            if points.shape != (3,):
                raise ValueError(f"单点坐标必须是3维向量，当前维度: {points.shape}")
            return self._transform_single_point(points, old_offset, new_offset, motor_angles)
        else:
            # 多点处理
            if points.ndim != 2 or points.shape[1] != 3:
                raise ValueError(f"多点坐标必须是(N, 3)形状，当前形状: {points.shape}")
            
            n_points = points.shape[0]
            
            # 自动选择计算方法
            if n_points >= self.vectorize_threshold:
                # 使用向量化计算
                return self._transform_points_vectorized(points, old_offset, new_offset, motor_angles)
            else:
                # 使用循环计算
                return self._transform_points_loop(points, old_offset, new_offset, motor_angles)
    
    def _transform_single_point(
        self,
        point: np.ndarray,
        old_offset: np.ndarray,
        new_offset: np.ndarray,
        motor_angle: float
    ) -> np.ndarray:
        """
        转换单个点（内部方法）
        """
        # 将角度转换为弧度
        theta_rad = np.deg2rad(motor_angle)
        
        # 计算旋转矩阵（绕Z轴）
        cos_theta = np.cos(theta_rad)
        sin_theta = np.sin(theta_rad)
        
        # 旋转矩阵 R(θ)
        R_pos = np.array([
            [cos_theta, -sin_theta, 0],
            [sin_theta,  cos_theta, 0],
            [0,          0,         1]
        ], dtype=np.float64)
        
        # 旋转矩阵 R(-θ) = R(θ)^T
        R_neg = R_pos.T
        
        # 执行四步变换
        # 步骤1: 绕Z轴旋转 -motor_angle
        step1 = R_neg @ point
        
        # 步骤2: 减去旧offset向量
        step2 = step1 - old_offset
        
        # 步骤3: 加上新offset向量
        step3 = step2 + new_offset
        
        # 步骤4: 绕Z轴旋转 +motor_angle
        step4 = R_pos @ step3
        
        return step4
    
    def _transform_points_loop(
        self,
        points: np.ndarray,
        old_offset: np.ndarray,
        new_offset: np.ndarray,
        motor_angles: Union[np.ndarray, float]
    ) -> np.ndarray:
        """
        批量转换点云（循环版本，内部方法）
        """
        n_points = points.shape[0]
        
        # 处理motor_angles
        if isinstance(motor_angles, (int, float)):
            motor_angles = np.full(n_points, motor_angles, dtype=np.float64)
        else:
            motor_angles = np.asarray(motor_angles, dtype=np.float64)
            if motor_angles.shape != (n_points,):
                raise ValueError(
                    f"motor_angles数量必须与点云数量一致，"
                    f"期望: {n_points}，实际: {motor_angles.shape[0]}"
                )
        
        # 批量处理
        transformed_points = np.zeros_like(points)
        for i in range(n_points):
            transformed_points[i] = self._transform_single_point(
                points[i],
                old_offset,
                new_offset,
                motor_angles[i]
            )
        
        return transformed_points
    
    def _transform_points_vectorized(
        self,
        points: np.ndarray,
        old_offset: np.ndarray,
        new_offset: np.ndarray,
        motor_angles: Union[np.ndarray, float]
    ) -> np.ndarray:
        """
        批量转换点云（向量化版本，内部方法）
        """
        n_points = points.shape[0]
        
        # 处理motor_angles
        if isinstance(motor_angles, (int, float)):
            motor_angles = np.full(n_points, motor_angles, dtype=np.float64)
        else:
            motor_angles = np.asarray(motor_angles, dtype=np.float64)
            if motor_angles.shape != (n_points,):
                raise ValueError(
                    f"motor_angles数量必须与点云数量一致，"
                    f"期望: {n_points}，实际: {motor_angles.shape[0]}"
                )
        
        # 转换为弧度
        theta_rad = np.deg2rad(motor_angles)
        
        # 计算cos和sin
        cos_theta = np.cos(theta_rad)
        sin_theta = np.sin(theta_rad)
        
        # 步骤1: 旋转 -theta (使用负角度的旋转矩阵)
        x1 = points[:, 0] * cos_theta + points[:, 1] * sin_theta
        y1 = -points[:, 0] * sin_theta + points[:, 1] * cos_theta
        z1 = points[:, 2]
        
        # 步骤2: 减去旧offset
        x2 = x1 - old_offset[0]
        y2 = y1 - old_offset[1]
        z2 = z1 - old_offset[2]
        
        # 步骤3: 加上新offset
        x3 = x2 + new_offset[0]
        y3 = y2 + new_offset[1]
        z3 = z2 + new_offset[2]
        
        # 步骤4: 旋转 +theta
        x4 = x3 * cos_theta - y3 * sin_theta
        y4 = x3 * sin_theta + y3 * cos_theta
        z4 = z3
        
        # 组合结果
        return np.column_stack([x4, y4, z4])


if __name__ == "__main__":
    """
    测试和使用示例
    """
    print("=" * 60)
    print("LiDAR点云外参转换模块测试")
    print("=" * 60)
    
    # 创建转换器实例
    converter = Lidar2Motor_1XXG(vectorize_threshold=100)
    
    # 测试单点转换
    print("\n【测试1：单点转换】")
    point = np.array([20.5, 6.7, 16.3])
    old_offset = np.array([10.123, 20.456, 30.789])
    new_offset = np.array([30.987, 10.123, 20.456])
    motor_angle = 0.008
    
    new_point = converter.cal_new_offset_matrix(point, old_offset, new_offset, motor_angle)
    print(f"输入点: {point}")
    print(f"旧offset: {old_offset}")
    print(f"新offset: {new_offset}")
    print(f"电机角度: {motor_angle}°")
    print(f"转换后: [{new_point[0]:.6f}, {new_point[1]:.6f}, {new_point[2]:.6f}]")
    
    # 测试小批量转换（使用循环）
    print("\n【测试2：小批量转换（自动使用循环方法）】")
    points = np.array([
        [20.5, 6.7, 16.3],
        [21.0, 7.0, 16.5],
        [22.0, 8.0, 17.0]
    ])
    motor_angles = np.array([0.008, 0.009, 0.010])
    
    new_points = converter.cal_new_offset_matrix(points, old_offset, new_offset, motor_angles)
    print(f"输入点云数量: {len(points)} (小于阈值{converter.vectorize_threshold})")
    print(f"转换后点云:\n{new_points}")
    
    # 测试大批量转换（使用向量化）
    print("\n【测试3：大批量转换（自动使用向量化方法）】")
    large_points = np.random.randn(200, 3) * 10
    large_angles = np.random.rand(200) * 0.02
    
    new_large_points = converter.cal_new_offset_matrix(large_points, old_offset, new_offset, large_angles)
    print(f"输入点云数量: {len(large_points)} (大于阈值{converter.vectorize_threshold})")
    print(f"转换后点云前5个点:\n{new_large_points[:5]}")
    
    # 测试使用相同角度
    print("\n【测试4：使用相同角度转换多个点】")
    same_angle_points = converter.cal_new_offset_matrix(points, old_offset, new_offset, 0.008)
    print(f"所有点使用相同角度: 0.008°")
    print(f"转换后点云:\n{same_angle_points}")
    
    # 性能测试
    print("\n【测试5：性能测试】")
    import time
    
    # 生成大量测试数据
    n_test = 10000
    test_points = np.random.randn(n_test, 3) * 10
    test_angles = np.random.rand(n_test) * 0.02
    
    # 测试自动选择（向量化）
    start = time.time()
    result_auto = converter.cal_new_offset_matrix(test_points, old_offset, new_offset, test_angles)
    time_auto = time.time() - start
    
    # 强制使用循环方法（通过调整阈值）
    converter_loop = Lidar2Motor_1XXG(vectorize_threshold=100000)
    start = time.time()
    result_loop = converter_loop.cal_new_offset_matrix(test_points, old_offset, new_offset, test_angles)
    time_loop = time.time() - start
    
    # 强制使用向量化方法（通过调整阈值）
    converter_vec = Lidar2Motor_1XXG(vectorize_threshold=1)
    start = time.time()
    result_vec = converter_vec.cal_new_offset_matrix(test_points, old_offset, new_offset, test_angles)
    time_vec = time.time() - start
    
    print(f"点云数量: {n_test}")
    print(f"自动选择耗时: {time_auto:.4f} 秒 (使用向量化)")
    print(f"循环方法耗时: {time_loop:.4f} 秒")
    print(f"向量化方法耗时: {time_vec:.4f} 秒")
    print(f"加速比: {time_loop/time_vec:.2f}x")
    print(f"结果一致性检查: {np.allclose(result_loop, result_vec)}")
    print(f"最大差异: {np.abs(result_loop - result_vec).max():.15f} 米")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)