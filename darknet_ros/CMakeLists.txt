cmake_minimum_required(VERSION 3.5)
project(darknet_ros)

set(CMAKE_CXX_STANDARD 17)


# Define path of darknet folder here.
find_path(DARKNET_PATH
  NAMES "README.md"
  HINTS "${CMAKE_CURRENT_SOURCE_DIR}/../darknet/")
message(STATUS "Darknet path dir = ${DARKNET_PATH}")
add_definitions(-DDARKNET_FILE_PATH="${DARKNET_PATH}")

# Find CUDA
find_package(CUDA QUIET)
if (CUDA_FOUND)
  find_package(CUDA REQUIRED)
  message(STATUS "CUDA Version: ${CUDA_VERSION_STRINGS}")
  message(STATUS "CUDA Libararies: ${CUDA_LIBRARIES}")
  set(
    CUDA_NVCC_FLAGS
    ${CUDA_NVCC_FLAGS};
    -O3
    -gencode arch=compute_35,code=sm_35
    -gencode arch=compute_50,code=[sm_50,compute_50]
    -gencode arch=compute_52,code=[sm_52,compute_52]
    -gencode arch=compute_61,code=sm_61
    -gencode arch=compute_62,code=sm_62
    -gencode arch=compute_70,code=sm_70
    -gencode arch=compute_75,code=[sm_75,compute_75]
  )
  add_definitions(-DGPU)
else()
  list(APPEND LIBRARIES "m")
endif()

# Find X11
message ( STATUS "Searching for X11..." )
find_package ( X11 REQUIRED )
if ( X11_FOUND )
  include_directories ( ${X11_INCLUDE_DIR} )
  link_libraries ( ${X11_LIBRARIES} )
  message ( STATUS " X11_INCLUDE_DIR: " ${X11_INCLUDE_DIR} )
  message ( STATUS " X11_LIBRARIES: " ${X11_LIBRARIES} )
endif ( X11_FOUND )

# Find rquired packeges
find_package(OpenCV 3 REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_msgs REQUIRED)
find_package(image_transport REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(darknet_ros_msgs REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(nav2_util REQUIRED)

set(dependencies
    rclcpp
    rclpy
    rclcpp_lifecycle
    rclcpp_action
    std_msgs
    image_transport
    cv_bridge
    sensor_msgs
    darknet_ros_msgs
    ament_index_cpp
    nav2_util
)

# Enable OPENCV in darknet
add_definitions(-DOPENCV)
add_definitions(-O4 -g)

include_directories(
  ${DARKNET_PATH}/src
  ${DARKNET_PATH}/include
  include
  ${catkin_INCLUDE_DIRS}
)

set(PROJECT_LIB_FILES
    src/YoloObjectDetector.cpp                    src/image_interface.c
)

set(DARKNET_CORE_FILES
    ${DARKNET_PATH}/src/activation_layer.c        ${DARKNET_PATH}/src/im2col.c
    ${DARKNET_PATH}/src/activations.c             ${DARKNET_PATH}/src/image.c
    ${DARKNET_PATH}/src/avgpool_layer.c           ${DARKNET_PATH}/src/layer.c
    ${DARKNET_PATH}/src/batchnorm_layer.c         ${DARKNET_PATH}/src/list.c
    ${DARKNET_PATH}/src/blas.c                    ${DARKNET_PATH}/src/local_layer.c
    ${DARKNET_PATH}/src/box.c                     ${DARKNET_PATH}/src/lstm_layer.c
    ${DARKNET_PATH}/src/col2im.c                  ${DARKNET_PATH}/src/matrix.c
    ${DARKNET_PATH}/src/connected_layer.c         ${DARKNET_PATH}/src/maxpool_layer.c
    ${DARKNET_PATH}/src/convolutional_layer.c     ${DARKNET_PATH}/src/network.c
    ${DARKNET_PATH}/src/cost_layer.c              ${DARKNET_PATH}/src/normalization_layer.c
    ${DARKNET_PATH}/src/crnn_layer.c              ${DARKNET_PATH}/src/option_list.c
    ${DARKNET_PATH}/src/crop_layer.c              ${DARKNET_PATH}/src/parser.c
    ${DARKNET_PATH}/src/cuda.c                    ${DARKNET_PATH}/src/region_layer.c
    ${DARKNET_PATH}/src/data.c                    ${DARKNET_PATH}/src/reorg_layer.c
    ${DARKNET_PATH}/src/deconvolutional_layer.c   ${DARKNET_PATH}/src/rnn_layer.c
    ${DARKNET_PATH}/src/demo.c                    ${DARKNET_PATH}/src/route_layer.c
    ${DARKNET_PATH}/src/detection_layer.c         ${DARKNET_PATH}/src/shortcut_layer.c
    ${DARKNET_PATH}/src/dropout_layer.c           ${DARKNET_PATH}/src/softmax_layer.c
    ${DARKNET_PATH}/src/gemm.c                    ${DARKNET_PATH}/src/tree.c
    ${DARKNET_PATH}/src/gru_layer.c               ${DARKNET_PATH}/src/utils.c
    ${DARKNET_PATH}/src/upsample_layer.c          ${DARKNET_PATH}/src/logistic_layer.c
    ${DARKNET_PATH}/src/l2norm_layer.c            ${DARKNET_PATH}/src/yolo_layer.c

    ${DARKNET_PATH}/examples/art.c                ${DARKNET_PATH}/examples/lsd.c
    ${DARKNET_PATH}/examples/attention.c          ${DARKNET_PATH}/examples/nightmare.c
    ${DARKNET_PATH}/examples/captcha.c            ${DARKNET_PATH}/examples/regressor.c
    ${DARKNET_PATH}/examples/cifar.c              ${DARKNET_PATH}/examples/rnn.c
    ${DARKNET_PATH}/examples/classifier.c         ${DARKNET_PATH}/examples/segmenter.c
    ${DARKNET_PATH}/examples/coco.c               ${DARKNET_PATH}/examples/super.c
    ${DARKNET_PATH}/examples/darknet.c            ${DARKNET_PATH}/examples/tag.c
    ${DARKNET_PATH}/examples/detector.c           ${DARKNET_PATH}/examples/yolo.c
    ${DARKNET_PATH}/examples/go.c
)

set(DARKNET_CUDA_FILES
    ${DARKNET_PATH}/src/activation_kernels.cu     ${DARKNET_PATH}/src/crop_layer_kernels.cu
    ${DARKNET_PATH}/src/avgpool_layer_kernels.cu  ${DARKNET_PATH}/src/deconvolutional_kernels.cu
    ${DARKNET_PATH}/src/blas_kernels.cu           ${DARKNET_PATH}/src/dropout_layer_kernels.cu
    ${DARKNET_PATH}/src/col2im_kernels.cu         ${DARKNET_PATH}/src/im2col_kernels.cu
    ${DARKNET_PATH}/src/convolutional_kernels.cu  ${DARKNET_PATH}/src/maxpool_layer_kernels.cu
)

if (CUDA_FOUND)

  link_directories(
    ${CUDA_TOOLKIT_ROOT_DIR}/lib64
  )

  cuda_add_library(${PROJECT_NAME}_lib
    ${PROJECT_LIB_FILES} ${DARKNET_CORE_FILES}
    ${DARKNET_CUDA_FILES}
  )
  
  ament_target_dependencies(${PROJECT_NAME}_lib ${dependencies})

  target_link_libraries(${PROJECT_NAME}_lib
    cuda
    cudart
    cublas
    curand
  )

  cuda_add_executable(${PROJECT_NAME}
    src/yolo_object_detector_node.cpp
  )
  
  ament_target_dependencies(${PROJECT_NAME} ${dependencies})

else()

  add_library(${PROJECT_NAME}_lib
    ${PROJECT_LIB_FILES} ${DARKNET_CORE_FILES}
  )
  ament_target_dependencies(${PROJECT_NAME}_lib ${dependencies})

  add_executable(${PROJECT_NAME}
    src/yolo_object_detector_node.cpp
  )
  ament_target_dependencies(${PROJECT_NAME} ${dependencies})

endif()

target_link_libraries(${PROJECT_NAME}_lib
  m
  pthread
  stdc++
  ${OpenCV_LIBRARIES}
  ${catkin_LIBRARIES}
  ${OpenCV_LIBS}
)

target_link_libraries(${PROJECT_NAME}
  ${PROJECT_NAME}_lib
)


install(TARGETS ${PROJECT_NAME}_lib ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)


install(
  DIRECTORY include/
  DESTINATION include/
  FILES_MATCHING PATTERN "*.h"
)

install(DIRECTORY yolo_network_config/cfg yolo_network_config/weights DESTINATION share/${PROJECT_NAME}/yolo_network_config/)
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME}/)

#############
## Testing ##
#############

if(BUILD_TESTING)
  # Download yolov2.weights
  #set(PATH "${CMAKE_CURRENT_SOURCE_DIR}/yolo_network_config/weights")
  #set(FILE "${PATH}/yolov2.weights")
  #message(STATUS "Checking and downloading yolov2.weights if needed ...")
  #if (NOT EXISTS "${FILE}")
  #  message(STATUS "... file does not exist. Downloading now ...")
  #  execute_process(COMMAND wget http://pjreddie.com/media/files/yolov2.weights -P ${PATH})
  #endif()

  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)
  
  #ament_add_gtest(${PROJECT_NAME}_object_detection-test
  #  test/object_detection.test
  #  test/test_main.cpp
  #  test/ObjectDetection.cpp
  #)
  #target_link_libraries(${PROJECT_NAME}_object_detection-test
  #  ${PROJECT_NAME}_lib
  #)
endif()


ament_export_include_directories(include)
ament_export_libraries(${PROJECT_NAME}_lib)
ament_export_dependencies(${dependencies})

ament_package()
