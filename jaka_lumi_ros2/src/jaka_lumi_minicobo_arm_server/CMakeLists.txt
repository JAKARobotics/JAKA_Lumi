cmake_minimum_required(VERSION 3.8)
project(jaka_lumi_minicobo_arm_server)

set(CMAKE_BUILD_TYPE Debug)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(control_msgs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_visual_tools REQUIRED)
find_package(moveit_core REQUIRED)


# Optionally find additional dependencies
# find_package(Boost REQUIRED)

# Declare executable targets
add_executable(lumi_minicobo_arm_server src/lumi_minicobo_arm_server.cpp)

# Link libraries
ament_target_dependencies(lumi_minicobo_arm_server
  rclcpp
  std_msgs
  geometry_msgs
  sensor_msgs
  moveit_msgs
  action_msgs
  control_msgs
  moveit_ros_planning_interface
)

# For including directories in ROS 2
target_include_directories(lumi_minicobo_arm_server
  PUBLIC
    include
  PRIVATE
    ${ament_INCLUDE_DIRS}
)


# Specify where to find external libraries
set(LIBRARY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/lib)

# Add the directory to the search path
link_directories(${LIBRARY_DIR})

# Find the library and link it properly
target_link_libraries(lumi_minicobo_arm_server ${LIBRARY_DIR}/libjakaAPI.so)

# Install executables
install(TARGETS
  lumi_minicobo_arm_server
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

ament_package()



