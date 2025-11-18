 /* Copyright 2005-2021 NVIDIA Corporation.  All rights reserved.
  *
  * NOTICE TO LICENSEE:
  *
  * The source code and/or documentation ("Licensed Deliverables") are
  * subject to NVIDIA intellectual property rights under U.S. and
  * international Copyright laws.
  *
  * The Licensed Deliverables contained herein are PROPRIETARY and
  * CONFIDENTIAL to NVIDIA and are being provided under the terms and
  * conditions of a form of NVIDIA software license agreement by and
  * between NVIDIA and Licensee ("License Agreement") or electronically
  * accepted by Licensee.  Notwithstanding any terms or conditions to
  * the contrary in the License Agreement, reproduction or disclosure
  * of the Licensed Deliverables to any third party without the express
  * written consent of NVIDIA is prohibited.
  *
  * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
  * LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
  * SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  THEY ARE
  * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
  * NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
  * DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
  * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
  * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
  * LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
  * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
  * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
  * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
  * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
  * OF THESE LICENSED DELIVERABLES.
  *
  * U.S. Government End Users.  These Licensed Deliverables are a
  * "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
  * 1995), consisting of "commercial computer software" and "commercial
  * computer software documentation" as such terms are used in 48
  * C.F.R. 12.212 (SEPT 1995) and are provided to the U.S. Government
  * only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
  * 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
  * U.S. Government End Users acquire the Licensed Deliverables with
  * only those rights set forth herein.
  *
  * Any use of the Licensed Deliverables in individual and commercial
  * software must include, in the user documentation and internal
  * comments to the code, the above Disclaimer and U.S. Government End
  * Users Notice.
  */

/*!
* \file cufftMp.h
* \brief Public header file for the NVIDIA CUDA FFT library (CUFFT)
*/

#ifndef _CUFFTMP_H_
#define _CUFFTMP_H_
#include "cufftXt.h"
#include "cudalibxt.h"
#include "cufft.h"


#ifndef CUFFTAPI
#ifdef _WIN32
#define CUFFTAPI __stdcall
#else
#define CUFFTAPI
#endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

#if CUFFT_VERSION != 12103
  #error cuFFT and cuFFTMp version mismatch. .../math_libs/X.Y/include/cufftmp/ should be included before .../math_libs/X.Y/include/
#endif

//
// cufftMpCommType specifies how to initialize cuFFTMp
//
typedef enum cufftMpCommType_t {
    CUFFT_COMM_MPI = 0x00, // comm_handle is a pointer to an MPI communicator.
    CUFFT_COMM_NONE = 0x01 // comm_handle should be null and NVSHMEM bootstrapping is implicit.
} cufftMpCommType;

cufftResult CUFFTAPI cufftMpAttachComm(cufftHandle plan,
                                       cufftMpCommType comm_type,
                                       void *comm_handle);

cufftResult CUFFTAPI cufftXtSetDistribution(cufftHandle plan,
                                            int rank,
                                            const long long int* lower_input,
                                            const long long int* upper_input,
                                            const long long int* lower_output,
                                            const long long int* upper_output,
                                            const long long int* strides_input,
                                            const long long int* strides_output);

cufftResult CUFFTAPI cufftXtSetSubformatDefault(cufftHandle plan,
                                                cufftXtSubFormat subformat_forward,
                                                cufftXtSubFormat subformat_inverse);

//
// The following cufftMpMakePlan* APIs are introduced to ensure the communicator does not go out of scope at the planning phase.
//
inline cufftResult CUFFTAPI cufftMpMakePlan2d(cufftHandle plan, int nx, int ny, cufftType type, void *comm_handle, cufftMpCommType comm_type, size_t *workSize) {

    cufftResult res = cufftMpAttachComm(plan, comm_type, comm_handle);
    if (res != CUFFT_SUCCESS){
        return res;
    };

	return cufftMakePlan2d(plan, nx, ny, type, workSize);
}

inline cufftResult CUFFTAPI cufftMpMakePlan3d(cufftHandle plan, int nx, int ny, int nz, cufftType type, void *comm_handle, cufftMpCommType comm_type, size_t *workSize) {

    cufftResult res = cufftMpAttachComm(plan, comm_type, comm_handle);
    if (res != CUFFT_SUCCESS){
        return res;
    };

	return cufftMakePlan3d(plan, nx, ny, nz, type, workSize);
}

inline cufftResult CUFFTAPI cufftMpMakePlanDecomposition(cufftHandle plan,
                                                        int rank,
                                                        int *n,
                                                        const long long int* lower_input,
                                                        const long long int* upper_input,
                                                        const long long int* strides_input,
                                                        const long long int* lower_output,
                                                        const long long int* upper_output,
                                                        const long long int* strides_output,
                                                        cufftType type,
                                                        void *comm_handle,
                                                        cufftMpCommType comm_type,
                                                        size_t *workSize)
{
    // Basic sanity check.
    if (workSize == nullptr || n == nullptr) {
        return CUFFT_INVALID_VALUE;
    }

    cufftResult res = cufftXtSetDistribution(plan, rank, lower_input, upper_input, lower_output, upper_output, strides_input, strides_output);
    if (res != CUFFT_SUCCESS){
        return res;
    };

    if (rank == 2) {
        return cufftMpMakePlan2d(plan, n[0], n[1], type, comm_handle, comm_type, workSize);
    }
    else if (rank == 3) {
        return cufftMpMakePlan3d(plan, n[0], n[1], n[2], type, comm_handle, comm_type, workSize);
    }
    else {
        return CUFFT_NOT_IMPLEMENTED; // 1D FFTs in cuFFTMp is not yet supported.
    }

}

typedef struct cufftReshapeHandle_st* cufftReshapeHandle;

cufftResult CUFFTAPI cufftMpCreateReshape(cufftReshapeHandle *handle);

cufftResult CUFFTAPI cufftMpGetReshapeSize(cufftReshapeHandle handle,
                                           size_t *workspace_size);

cufftResult CUFFTAPI __cufftMpMakeReshape_11_4(cufftReshapeHandle handle,
                                              size_t element_size,
                                              int rank,
                                              const long long int* lower_input,
                                              const long long int* upper_input,
                                              const long long int* strides_input,
                                              const long long int* lower_output,
                                              const long long int* upper_output,
                                              const long long int* strides_output,
                                              void *comm_handle,
                                              cufftMpCommType comm_type);

#ifndef CUFFT_NO_INLINE
static inline cufftResult cufftMpMakeReshape(cufftReshapeHandle handle,
                                            size_t element_size,
                                            int rank,
                                            const long long int* lower_input,
                                            const long long int* upper_input,
                                            const long long int* strides_input,
                                            const long long int* lower_output,
                                            const long long int* upper_output,
                                            const long long int* strides_output,
                                            void *comm_handle,
                                            cufftMpCommType comm_type) {
   return __cufftMpMakeReshape_11_4(handle, element_size, rank, lower_input, upper_input, strides_input, lower_output, upper_output, strides_output, comm_handle, comm_type);
};
#endif

cufftResult CUFFTAPI cufftMpExecReshapeAsync(cufftReshapeHandle handle,
                                             void *data_out,
                                             const void *data_in,
                                             void *workspace,
                                             cudaStream_t stream);

cufftResult CUFFTAPI cufftMpDestroyReshape(cufftReshapeHandle handle);

#ifdef __cplusplus
}
#endif

#endif
