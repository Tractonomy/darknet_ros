import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
  use_sim_time = LaunchConfiguration('use_sim_time', default = 'false')
  autoconfigure = LaunchConfiguration('autoconfigure', default = 'true')
  autostart = LaunchConfiguration('autostart', default = 'true')
  darknet_ros_share_dir = get_package_share_directory('darknet_ros')

  yolo_weights_path = LaunchConfiguration('yolo_weights_path', default = darknet_ros_share_dir + '/yolo_network_config/weights')
  yolo_config_path = LaunchConfiguration('yolo_config_path', default = darknet_ros_share_dir + '/yolo_network_config/cfg')
  ros_param_file = LaunchConfiguration('ros_param_file', default = darknet_ros_share_dir + 'config/ros.yaml')
  network_param_file = LaunchConfiguration('network_param_file', default = darknet_ros_share_dir + 'config/carts-tiny.yaml')

  declare_yolo_weights_path_cmd = DeclareLaunchArgument(
    'yolo_weights_path',
    default_value = darknet_ros_share_dir + '/yolo_network_config/weights',
    description = 'Path to yolo weights') 
  declare_yolo_config_path_cmd = DeclareLaunchArgument(
    'yolo_config_path',
    default_value = darknet_ros_share_dir + '/yolo_network_config/cfg',
    description = 'Path to yolo config') 
  declare_ros_param_file_cmd = DeclareLaunchArgument(
    'ros_param_file',
    default_value = darknet_ros_share_dir + '/config/ros.yaml',
    description = 'Path to file with ROS related config')  
  declare_network_param_file_cmd = DeclareLaunchArgument(
    'network_param_file',
    default_value = darknet_ros_share_dir + '/config/carts-tiny.yaml',
    description = 'Path to file with network param file')  

  darknet_ros_cmd = Node(
    package='darknet_ros',
    node_executable='darknet_ros',
    node_name='darknet_ros',
    output='screen',
    emulate_tty='True',
    parameters=[ros_param_file, network_param_file,
      {
        "autostart": autostart,
        "autoconfigure": autoconfigure,
        "config_path": yolo_config_path, 
        "weights_path": yolo_weights_path,
        "use_sim_time": use_sim_time,
      },
    ])
  
  # TODO most remappings can be removed when remappings support wildcards (out/**:=camera/color/image_raw/\1)
  compression_node = Node(
    package='image_transport',
    node_executable='republish',
    output='screen',
    remappings=[
            ('in', 'darknet/detection_image'),
            ('out', 'darknet/detection_image'),
            ('out/compressed', 'darknet/detection_image/compressed'),
            ('out/compressedDepth', 'darknet/detection_image/compressedDepth'),
            ('out/theora', 'darknet/detection_image/theora'),
        ],
    arguments=['raw', 'compressed'],
    )

  ld = LaunchDescription()

  ld.add_action(declare_yolo_weights_path_cmd)
  ld.add_action(declare_yolo_config_path_cmd)
  ld.add_action(declare_ros_param_file_cmd)
  ld.add_action(declare_network_param_file_cmd)
  
  ld.add_action(darknet_ros_cmd)
  ld.add_action(compression_node)

  return ld
