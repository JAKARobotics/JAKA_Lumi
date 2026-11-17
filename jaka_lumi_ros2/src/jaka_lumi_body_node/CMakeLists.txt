cmake_minimum_required(VERSION 3.8)
# silence “Policy CMP0148 is not set” warnings
if(POLICY CMP0148)
  cmake_policy(SET CMP0148 OLD)
endif()

project(jaka_lumi_body_node)


# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
# find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Find libcurl
find_package(CURL REQUIRED)


# Declare the interface
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/MoveService.srv"
  "srv/ReadStatusService.srv"
  DEPENDENCIES builtin_interfaces
)

# Create executable
add_executable(lumi_body_node 
  src/lumi_body_node.cpp
)

# Add include paths for external header-only libraries like nlohmann_json
target_include_directories(lumi_body_node  PUBLIC
  /usr/include
)

target_link_libraries(lumi_body_node 
  CURL::libcurl
)

# Link dependencies
ament_target_dependencies(lumi_body_node 
  rclcpp
  sensor_msgs
  # std_msgs
  std_srvs
  rosidl_default_generators
)

rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(lumi_body_node ${cpp_typesupport_target})

# Install target
install(TARGETS lumi_body_node 
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files, if any (optional)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# ament_export_dependencies(rosidl_default_runtime)
ament_package()
