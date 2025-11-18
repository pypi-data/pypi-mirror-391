CMAKE_MINIMUM_REQUIRED(VERSION 3.5)
PROJECT(yggdrasil VERSION "1.1.0" LANGUAGES C CXX)

find_package(YggdrasilRapidJSON REQUIRED)
add_executable(yggdrasil yggdrasil.cpp)
target_link_libraries(yggdrasil PRIVATE YggdrasilRapidJSON)
