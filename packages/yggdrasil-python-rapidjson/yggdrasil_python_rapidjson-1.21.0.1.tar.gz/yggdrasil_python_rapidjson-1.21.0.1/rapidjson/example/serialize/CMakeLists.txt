CMAKE_MINIMUM_REQUIRED(VERSION 3.5)
PROJECT(serialize VERSION "1.1.0" LANGUAGES C CXX)

find_package(YggdrasilRapidJSON REQUIRED)
add_executable(serialize serialize.cpp)
target_link_libraries(serialize PRIVATE YggdrasilRapidJSON)
