option(DISPATCH_FFN_COMBINE_PROFILE "Enable dispatch_ffn_combine stage profiling" OFF)
# 支持 build.sh / 环境变量开启，无需改 cmake 命令行
if(DEFINED ENV{DISPATCH_FFN_COMBINE_PROFILE})
    string(TOLOWER "$ENV{DISPATCH_FFN_COMBINE_PROFILE}" _dffc_profile_env)
    if(_dffc_profile_env MATCHES "^(1|on|true|yes)$")
        set(DISPATCH_FFN_COMBINE_PROFILE ON CACHE BOOL "" FORCE)
    endif()
endif()

set(_DISPATCH_FFN_INC_OPTS)
set(_DISPATCH_FFN_PROFILE_OPTS)
if (DISPATCH_FFN_COMBINE_PROFILE)
    list(APPEND _DISPATCH_FFN_PROFILE_OPTS -DDISPATCH_FFN_COMBINE_PROFILE=1)
endif()
if (EXISTS ${ASCEND_CANN_PACKAGE_PATH}/aarch64-linux/ascendc/include)
    list(APPEND _DISPATCH_FFN_INC_OPTS -I${ASCEND_CANN_PACKAGE_PATH}/aarch64-linux/ascendc/include)
elseif (EXISTS ${ASCEND_CANN_PACKAGE_PATH}/arm64-linux/ascendc/include)
    list(APPEND _DISPATCH_FFN_INC_OPTS -I${ASCEND_CANN_PACKAGE_PATH}/arm64-linux/ascendc/include)
elseif (EXISTS ${ASCEND_CANN_PACKAGE_PATH}/${CMAKE_SYSTEM_PROCESSOR}-linux/ascendc/include)
    list(APPEND _DISPATCH_FFN_INC_OPTS -I${ASCEND_CANN_PACKAGE_PATH}/${CMAKE_SYSTEM_PROCESSOR}-linux/ascendc/include)
endif()
if (EXISTS ${CMAKE_SOURCE_DIR}/third_party/catlass/include)
    list(APPEND _DISPATCH_FFN_INC_OPTS -I${CMAKE_SOURCE_DIR}/third_party/catlass/include)
endif()

add_op_to_compiled_list()

if (BUILD_OPEN_PROJECT)
    target_sources(op_host_aclnnInner PRIVATE
        dispatch_ffn_combine_def.cpp
    )
endif()

add_ops_compile_options(
    OP_NAME DispatchFFNCombine
    OPTIONS
        --cce-auto-sync=on
        -Wno-deprecated-declarations
        -Werror
        -DHCCL_COMM
        -DCATLASS_ARCH=2201
        ${_DISPATCH_FFN_INC_OPTS}
        ${_DISPATCH_FFN_PROFILE_OPTS}
)

if (NOT BUILD_OPS_RTY_KERNEL)
    add_modules_sources(OPTYPE dispatch_ffn_combine ACLNNTYPE aclnn_inner)
    target_include_directories(${OPHOST_NAME}_tiling_obj PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/../op_kernel
    )
    if (DISPATCH_FFN_COMBINE_PROFILE)
        target_compile_definitions(${OPHOST_NAME}_tiling_obj PRIVATE DISPATCH_FFN_COMBINE_PROFILE=1)
    endif()
endif()
