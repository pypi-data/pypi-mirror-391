CMAKE_MINIMUM_REQUIRED(VERSION 3.5)
PROJECT(units VERSION "1.1.0" LANGUAGES C CXX)

find_package(YggdrasilRapidJSON REQUIRED)
add_executable(units units.cpp)
target_link_libraries(units PRIVATE YggdrasilRapidJSON)
