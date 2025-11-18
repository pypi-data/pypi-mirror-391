/*
 * Copyright (c) 2022 - 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 *
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */


#ifndef NVTIFF_HEADER
#define NVTIFF_HEADER

#include <stdlib.h>
#include <stdint.h>
#include <cuda_runtime.h>
#include "library_types.h"
#include "nvtiff_version.h"

#define NVTIFFAPI

#if defined(__cplusplus)
  extern "C" {
#endif

/**********************************************************************/
/*             nvTIFF Encode declaration                              */
/**********************************************************************/

struct nvtiffEncoder;
typedef struct nvtiffEncoder* nvtiffEncoder_t;

struct nvtiffEncodeParams;
typedef struct nvtiffEncodeParams* nvtiffEncodeParams_t;

typedef enum nvtiffVariant {
    NVTIFF_REGULAR_TIFF = 42,
    NVTIFF_BIG_TIFF = 43
} nvtiffVariant_t;

/**********************************************************************/
/*             nvTIFF Geokey declaration                              */
/**********************************************************************/
typedef enum nvtiffGeoKeys {
    // GeoTIFF Configuration Keys
    NVTIFF_GEOKEY_GT_MODEL_TYPE                = 1024,
    NVTIFF_GEOKEY_GT_RASTER_TYPE               = 1025,
    NVTIFF_GEOKEY_GT_CITATION                  = 1026,

    // Geodetic CRS Parameter Keys
    NVTIFF_GEOKEY_GEODETIC_CRS                 = 2048,
    NVTIFF_GEOKEY_GEODETIC_CITATION            = 2049,
    NVTIFF_GEOKEY_GEODETIC_DATUM               = 2050,
    NVTIFF_GEOKEY_PRIME_MERIDIAN               = 2051,
    NVTIFF_GEOKEY_GEOG_LINEAR_UNITS            = 2052,
    NVTIFF_GEOKEY_GEOG_LINEAR_UNIT_SIZE        = 2053,
    NVTIFF_GEOKEY_GEOG_ANGULAR_UNITS           = 2054,
    NVTIFF_GEOKEY_GEOG_ANGULAR_UNIT_SIZE       = 2055,
    NVTIFF_GEOKEY_ELLIPSOID                    = 2056,
    NVTIFF_GEOKEY_ELLIPSOID_SEMI_MAJOR_AXIS    = 2057,
    NVTIFF_GEOKEY_ELLIPSOID_SEMI_MINOR_AXIS    = 2058,
    NVTIFF_GEOKEY_ELLIPSOID_INV_FLATTENING     = 2059,
    NVTIFF_GEOKEY_GEOG_AZIMUTH_UNITS           = 2060,
    NVTIFF_GEOKEY_PRIME_MERIDIAN_LONG          = 2061,
    
    // Projected CRS Parameter Keys
    NVTIFF_GEOKEY_PROJECTED_CRS                = 3072,
    NVTIFF_GEOKEY_PROJECTED_CITATION           = 3073,
    NVTIFF_GEOKEY_PROJECTION                   = 3074,
    NVTIFF_GEOKEY_PROJ_METHOD                  = 3075,
    NVTIFF_GEOKEY_PROJ_LINEAR_UNITS            = 3076,
    NVTIFF_GEOKEY_PROJ_LINEAR_UNIT_SIZE        = 3077,
    NVTIFF_GEOKEY_PROJ_STD_PARALLEL1           = 3078,
    NVTIFF_GEOKEY_PROJ_STD_PARALLEL            = 3078,
    NVTIFF_GEOKEY_PROJ_STD_PARALLEL2           = 3079,
    NVTIFF_GEOKEY_PROJ_NAT_ORIGIN_LONG         = 3080,
    NVTIFF_GEOKEY_PROJ_ORIGIN_LONG             = 3080,
    NVTIFF_GEOKEY_PROJ_NAT_ORIGIN_LAT          = 3081,
    NVTIFF_GEOKEY_PROJ_ORIGIN_LAT              = 3081,
    NVTIFF_GEOKEY_PROJ_FALSE_EASTING           = 3082,
    NVTIFF_GEOKEY_PROJ_FALSE_NORTHING          = 3083,
    NVTIFF_GEOKEY_PROJ_FALSE_ORIGIN_LONG       = 3084,
    NVTIFF_GEOKEY_PROJ_FALSE_ORIGIN_LAT        = 3085,
    NVTIFF_GEOKEY_PROJ_FALSE_ORIGIN_EASTING    = 3086,
    NVTIFF_GEOKEY_PROJ_FALSE_ORIGIN_NORTHING   = 3087,
    NVTIFF_GEOKEY_PROJ_CENTER_LONG             = 3088,
    NVTIFF_GEOKEY_PROJ_CENTER_LAT              = 3089,
    NVTIFF_GEOKEY_PROJ_CENTER_EASTING          = 3090,
    NVTIFF_GEOKEY_PROJ_CENTER_NORTHING         = 3091,
    NVTIFF_GEOKEY_PROJ_SCALE_AT_NAT_ORIGIN     = 3092,
    NVTIFF_GEOKEY_PROJ_SCALE_AT_ORIGIN         = 3092,
    NVTIFF_GEOKEY_PROJ_SCALE_AT_CENTER         = 3093,
    NVTIFF_GEOKEY_PROJ_AZIMUTH_ANGLE           = 3094,
    NVTIFF_GEOKEY_PROJ_STRAIGHT_VERT_POLE_LONG = 3095,

    // Vertical CRS Parameter Keys (4096-5119)
    NVTIFF_GEOKEY_VERTICAL                     = 4096,
    NVTIFF_GEOKEY_VERTICAL_CITATION            = 4097,
    NVTIFF_GEOKEY_VERTICAL_DATUM               = 4098,
    NVTIFF_GEOKEY_VERTICAL_UNITS               = 4099,

    NVTIFF_GEOKEY_BASE                         = 32768, // reserved for private use
    NVTIFF_GEOKEY_END                          = 65535 // maximum value
} nvtiffGeoKey_t;

typedef enum nvtiffGeoKeyDataType {
   NVTIFF_GEOKEY_TYPE_SHORT=1,
   NVTIFF_GEOKEY_TYPE_ASCII=2,
   NVTIFF_GEOKEY_TYPE_DOUBLE=3,
   NVTIFF_GEOKEY_TYPE_UNKNOWN=4
} nvtiffGeoKeyDataType_t;

// TIFF Tag types as defined in the TIFF specification
typedef enum nvtiffTagDataType {
    NVTIFF_TAG_TYPE_BYTE      =  1,
    NVTIFF_TAG_TYPE_ASCII     =  2,
    NVTIFF_TAG_TYPE_SHORT     =  3,
    NVTIFF_TAG_TYPE_LONG      =  4,
    NVTIFF_TAG_TYPE_RATIONAL  =  5,
    NVTIFF_TAG_TYPE_SBYTE     =  6,
    NVTIFF_TAG_TYPE_UNDEFINED =  7,
    NVTIFF_TAG_TYPE_SSHORT    =  8,
    NVTIFF_TAG_TYPE_SLONG     =  9,
    NVTIFF_TAG_TYPE_SRATIONAL = 10,
    NVTIFF_TAG_TYPE_FLOAT     = 11,
    NVTIFF_TAG_TYPE_DOUBLE    = 12,
    NVTIFF_TAG_TYPE_LONG8     = 16,
    NVTIFF_TAG_TYPE_SLONG8    = 17,
    NVTIFF_TAG_TYPE_IFD8      = 18,
} nvtiffTagDataType_t;

typedef enum nvtiffTag {
    NVTIFF_TAG_UNKNOWN = -1,
    NVTIFF_TAG_MODEL_PIXEL_SCALE = 33550,
    NVTIFF_TAG_MODEL_TIE_POINT =   33922,
    NVTIFF_TAG_MODEL_TRANSFORMATION = 34264
} nvtiffTag_t;

/**********************************************************************/
/*             nvTIFF Decode declaration                              */
/**********************************************************************/
// maximum number of values (ushorts) in the bit-per-sample (258) tag
#define MAX_NUM_SAMPLES (16)

/* nvTIFF status enums, returned by nvTIFF API */
typedef enum {
    NVTIFF_STATUS_SUCCESS = 0,
    NVTIFF_STATUS_NOT_INITIALIZED = 1,
    NVTIFF_STATUS_INVALID_PARAMETER = 2,
    NVTIFF_STATUS_BAD_TIFF = 3,
    NVTIFF_STATUS_TIFF_NOT_SUPPORTED = 4,
    NVTIFF_STATUS_ALLOCATOR_FAILURE = 5,
    NVTIFF_STATUS_EXECUTION_FAILED = 6,
    NVTIFF_STATUS_ARCH_MISMATCH = 7,
    NVTIFF_STATUS_INTERNAL_ERROR = 8,
    NVTIFF_STATUS_NVCOMP_NOT_FOUND = 9,
    NVTIFF_STATUS_NVJPEG_NOT_FOUND = 10,
    NVTIFF_STATUS_TAG_NOT_FOUND = 11,
    NVTIFF_STATUS_PARAMETER_OUT_OF_BOUNDS = 12,
    NVTIFF_STATUS_NVJPEG2K_NOT_FOUND = 13,
} nvtiffStatus_t;

// prototype for stream ordered device allocators with context
typedef int (*nvtiffDeviceMallocAsync)(void* ctx, void **ptr, size_t size, cudaStream_t stream);

typedef int (*nvtiffDeviceFreeAsync)(void* ctx, void *ptr, size_t size, cudaStream_t stream);

// prototype for stream ordered pinned  allocators with context
typedef int (*nvtiffPinnedMallocAsync)(void* ctx, void **ptr, size_t size, cudaStream_t stream);

typedef int (*nvtiffPinnedFreeAsync)(void* ctx, void *ptr, size_t size, cudaStream_t stream);

typedef struct {
    nvtiffDeviceMallocAsync device_malloc;
    nvtiffDeviceFreeAsync device_free;
    void *device_ctx;
} nvtiffDeviceAllocator_t;

typedef struct {
    nvtiffPinnedMallocAsync pinned_malloc;
    nvtiffPinnedFreeAsync pinned_free;
    void *pinned_ctx;
} nvtiffPinnedAllocator_t;

struct nvtiffDecoder;
typedef struct nvtiffDecoder* nvtiffDecoder_t;

struct nvtiffStream;
typedef struct nvtiffStream* nvtiffStream_t;

typedef enum nvtiffSampleFormat {
    NVTIFF_SAMPLEFORMAT_UNKNOWN       = 0,
    NVTIFF_SAMPLEFORMAT_UINT          = 1,
    NVTIFF_SAMPLEFORMAT_INT           = 2,
    NVTIFF_SAMPLEFORMAT_IEEEFP        = 3,
    NVTIFF_SAMPLEFORMAT_VOID          = 4,
    NVTIFF_SAMPLEFORMAT_COMPLEXINT    = 5,
    NVTIFF_SAMPLEFORMAT_COMPLEXIEEEFP = 6
} nvtiffSampleFormat_t;


typedef enum nvtiffPhotometricInt {
    NVTIFF_PHOTOMETRIC_UNKNOWN    = -1,
    NVTIFF_PHOTOMETRIC_MINISWHITE = 0,
    NVTIFF_PHOTOMETRIC_MINISBLACK = 1,
    NVTIFF_PHOTOMETRIC_RGB        = 2,
    NVTIFF_PHOTOMETRIC_PALETTE    = 3,	
    NVTIFF_PHOTOMETRIC_MASK  	  = 4,	
    NVTIFF_PHOTOMETRIC_SEPARATED  = 5,
    NVTIFF_PHOTOMETRIC_YCBCR      = 6,
} nvtiffPhotometricInt_t;

typedef enum nvtiffPlanarConfig {
    NVTIFF_PLANARCONFIG_UNKNOWN     = 0,
    NVTIFF_PLANARCONFIG_CONTIG      = 1,
    NVTIFF_PLANARCONFIG_SEPARATE    = 2
} nvtiffPlanarConfig_t;

typedef enum nvtiffCompression {
    NVTIFF_COMPRESSION_UNKNOWN = 0,
    NVTIFF_COMPRESSION_NONE = 1,
    NVTIFF_COMPRESSION_LZW = 5,
    NVTIFF_COMPRESSION_JPEG = 7,
    NVTIFF_COMPRESSION_ADOBE_DEFLATE = 8,
    NVTIFF_COMPRESSION_DEFLATE = 32946,
    NVTIFF_COMPRESSION_APERIO_JP2000_YCC = 33003,
    NVTIFF_COMPRESSION_APERIO_JP2000_RGB = 33005,
    NVTIFF_COMPRESSION_JP2000 = 34712
} nvtiffCompression_t;

typedef enum {
    NVTIFF_IMAGETYPE_REDUCED_IMAGE = 0b0001,
    NVTIFF_IMAGETYPE_PAGE          = 0b0010,
    NVTIFF_IMAGETYPE_MASK          = 0b0100,
    NVTIFF_IMAGETYPE_ENUM_FORCE_UINT32 =  0xFFFFFFFF,
} nvtiffImageType;
typedef uint32_t nvtiffImageType_t;

typedef struct nvtiffImageInfo {
    nvtiffImageType_t image_type;
    uint32_t image_width; 
    uint32_t image_height;
    nvtiffCompression_t compression;
    nvtiffPhotometricInt_t photometric_int;
    nvtiffPlanarConfig_t planar_config;
    uint16_t samples_per_pixel;
    uint16_t bits_per_pixel; // SUM(bits_per_sample)
    uint16_t bits_per_sample[MAX_NUM_SAMPLES];
    nvtiffSampleFormat_t sample_format[MAX_NUM_SAMPLES];
} nvtiffImageInfo_t;


typedef enum nvtiffImageGeometryType {
    NVTIFF_IMAGE_STRIPED = 0,
    NVTIFF_IMAGE_TILED = 1,
} nvtiffImageGeometryType_t;

typedef struct nvtiffImageGeometry {
    nvtiffImageGeometryType_t type;
    uint32_t image_depth;
    uint32_t strile_width;            // strile_width = image_width for strips
    uint32_t strile_height;
    uint32_t strile_depth;            // strile_depth = image_depth for strips
    uint32_t num_striles_per_plane;
    uint32_t num_striles;
} nvtiffImageGeometry_t;

typedef enum nvtiffOutputFormat {
    NVTIFF_OUTPUT_UNCHANGED_I    = 0,   // Interleaved channels
    NVTIFF_OUTPUT_RGB_I_UINT8    = 1,   // Interleaved RGB with 8 bits per channel
    NVTIFF_OUTPUT_RGB_I_UINT16   = 2,   // Interleaved RGB with 16 bits per channel
} nvtiffOutputFormat_t;

struct nvtiffDecodeParams;
typedef struct nvtiffDecodeParams* nvtiffDecodeParams_t;

typedef struct
{
    void **plane_data;
    size_t *plane_pitch_bytes;
    uint32_t num_planes; 
} nvtiffImage_t;

/**
* @brief returns library's property values.
* @param type [in]         : Version type, MAJOR_VERSION, MINOR_VERSION or PATCH_LEVEL
* @param value [in/out]        : Version number
*/
nvtiffStatus_t NVTIFFAPI nvtiffGetProperty(libraryPropertyType type, int *value);


nvtiffStatus_t NVTIFFAPI nvtiffDecodeParamsCreate(nvtiffDecodeParams_t* decode_params);

nvtiffStatus_t NVTIFFAPI nvtiffDecodeParamsDestroy(nvtiffDecodeParams_t decode_params);

nvtiffStatus_t NVTIFFAPI nvtiffStreamCreate(nvtiffStream_t *tiff_stream);

nvtiffStatus_t NVTIFFAPI nvtiffStreamDestroy(nvtiffStream_t tiff_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecoderCreate(nvtiffDecoder_t *decoder,
    nvtiffDeviceAllocator_t *device_allocator,
    nvtiffPinnedAllocator_t *pinned_allocator,
    cudaStream_t cuda_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecoderCreateSimple(nvtiffDecoder_t *decoder, 
    cudaStream_t cuda_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecoderDestroy(nvtiffDecoder_t decoder,
    cudaStream_t cuda_stream);


/**********************************************************************/
/*    nvTIFF Stream APIs for file Parsing and extracting Metadata     */
/**********************************************************************/

nvtiffStatus_t NVTIFFAPI nvtiffStreamParseFromFile(const char *fname, nvtiffStream_t tiff_stream);

nvtiffStatus_t NVTIFFAPI nvtiffStreamParse(const uint8_t *buffer, size_t buffer_size, nvtiffStream_t tiff_stream);

nvtiffStatus_t NVTIFFAPI nvtiffStreamPrint(nvtiffStream_t tiff_stream);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetNumImages(nvtiffStream_t tiff_stream, 
    uint32_t *num_images);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetImageInfo(nvtiffStream_t tiff_stream, 
    uint32_t image_id,
    nvtiffImageInfo_t *image_info);


nvtiffStatus_t NVTIFFAPI nvtiffStreamGetImageGeometry(nvtiffStream_t tiff_stream, 
    uint32_t image_id,
    nvtiffImageGeometry_t* geometry);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetGeoKeyInfo(nvtiffStream_t tiff_stream, 
    nvtiffGeoKey_t key, 
    uint32_t *size, 
    uint32_t *count, 
    nvtiffGeoKeyDataType_t* type);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetTagInfo(nvtiffStream_t tiff_stream,
    uint32_t image_id,
    nvtiffTag_t tiff_tag,
    nvtiffTagDataType_t *tag_type,
    uint32_t *size,
    uint32_t *count);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetTagValue(nvtiffStream_t tiff_stream,
    uint32_t image_id,
    nvtiffTag_t tiff_tag,
    void *tag_value,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetTagInfoGeneric(nvtiffStream_t tiff_stream,
    uint32_t image_id,
    uint16_t tiff_tag,
    nvtiffTagDataType_t *tag_type,
    uint32_t *size,
    uint32_t *count);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetTagValueGeneric(nvtiffStream_t tiff_stream,
    uint32_t image_id,
    uint16_t tiff_tag,
    void *tag_value,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetNumberOfGeoKeys(nvtiffStream_t tiff_stream, 
    nvtiffGeoKey_t* key, 
    uint32_t *num_keys);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetGeoKey(nvtiffStream_t tiff_stream, 
    nvtiffGeoKey_t key, 
    void *val,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetGeoKeyASCII(nvtiffStream_t tiff_stream, 
    nvtiffGeoKey_t key, 
    char* szStr,
    uint32_t szStrMaxLen);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetGeoKeySHORT(nvtiffStream_t tiff_stream, 
    nvtiffGeoKey_t key, 
    unsigned short* val,
    uint32_t index,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffStreamGetGeoKeyDOUBLE(nvtiffStream_t tiff_stream, 
    nvtiffGeoKey_t key, 
    double* val,
    uint32_t index,
    uint32_t count);

/**********************************************************************/
/*             nvTIFF Decode APIs                                     */
/**********************************************************************/

nvtiffStatus_t NVTIFFAPI nvtiffDecodeRange(nvtiffStream_t tiff_stream, 
    nvtiffDecoder_t decoder,
    unsigned int sub_file_start, 
    unsigned int sub_file_num,
    unsigned char **image_out,
    cudaStream_t cuda_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecode(nvtiffStream_t tiff_stream, 
    nvtiffDecoder_t nvtiff_decoder,
    unsigned char **image_out,
    cudaStream_t cuda_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecodeImage(nvtiffStream_t tiff_stream, 
    nvtiffDecoder_t decoder,
    nvtiffDecodeParams_t params, 
    uint32_t image_id,
    void* image_out_d,
    cudaStream_t cuda_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecodeImageEx(nvtiffStream_t tiff_stream, 
    nvtiffDecoder_t decoder,
    nvtiffDecodeParams_t params, 
    uint32_t image_id,
    nvtiffImage_t* image_out,
    cudaStream_t cuda_stream);

nvtiffStatus_t NVTIFFAPI nvtiffDecodeCheckSupported(nvtiffStream_t tiff_stream,
    nvtiffDecoder_t decoder,
    nvtiffDecodeParams_t params,
    uint32_t image_id);

/**********************************************************************/
/*             nvTIFF Decode Params                                   */
/**********************************************************************/

nvtiffStatus_t NVTIFFAPI nvtiffDecodeParamsSetOutputFormat(
    nvtiffDecodeParams_t decode_params,
    nvtiffOutputFormat_t format);

nvtiffStatus_t NVTIFFAPI nvtiffDecodeParamsSetROI(
    nvtiffDecodeParams_t decode_params,
    int32_t offset_x,
    int32_t offset_y,
    int32_t roi_width,
    int32_t roi_height);

/**********************************************************************/
/*                  V2 Encode APIs                                    */
/**********************************************************************/
                            
nvtiffStatus_t NVTIFFAPI nvtiffEncoderCreate(
    nvtiffEncoder_t* encoder,
    nvtiffDeviceAllocator_t* deviceAllocator,
    nvtiffPinnedAllocator_t* pinnedAllocator,
    cudaStream_t stream);

// Destroys encoder freeing all the allocated memory on both the
// host and the device.
nvtiffStatus_t NVTIFFAPI nvtiffEncoderDestroy(nvtiffEncoder_t encoder, cudaStream_t stream);

// Get either the metadata size or the bitstream size or both
// If metadataSize ptr is null, don't compute it
// If bitstreamSize ptr is null, don't compute it
// But if bitstreamSize ptr is not null and bitstream is not ready, return an error
nvtiffStatus_t NVTIFFAPI nvtiffGetBitstreamSize(
    nvtiffEncoder_t encoder,
    nvtiffEncodeParams_t* params,
    uint32_t nParams,
    size_t* metadataSize,
    size_t* bitstreamSize);

// Write a whole tiff stream (including metadata) to a buffer
nvtiffStatus_t NVTIFFAPI nvtiffWriteTiffBuffer(
    nvtiffEncoder_t encoder,
    nvtiffEncodeParams_t* params,
    uint32_t nParams,
    uint8_t* buffer,
    size_t size,
    cudaStream_t stream);

// Write a whole tiff stream (including metadata) to a file
nvtiffStatus_t NVTIFFAPI nvtiffWriteTiffFile(
    nvtiffEncoder_t encoder,
    nvtiffEncodeParams_t* params,
    uint32_t nParams,
    const char* fname,
    cudaStream_t stream);

nvtiffStatus_t NVTIFFAPI nvtiffEncode(
    nvtiffEncoder_t encoder, 
    nvtiffEncodeParams_t* params, 
    uint32_t nParams, 
    cudaStream_t stream);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeFinalize(
    nvtiffEncoder_t encoder,
    nvtiffEncodeParams_t* params,
    uint32_t nParams,
    cudaStream_t stream);

/**********************************************************************/
/*             nvTIFF Encode Params                                   */
/**********************************************************************/

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsCreate(
    nvtiffEncodeParams_t* params);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsDestroy(
    nvtiffEncodeParams_t params,
    cudaStream_t stream);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetTiffVariant(
    nvtiffEncodeParams_t params,
    nvtiffVariant_t variant);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetImageInfo(
    nvtiffEncodeParams_t params,
    const nvtiffImageInfo_t* finfo);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetImageGeometry(
    nvtiffEncodeParams_t params,
    const nvtiffImageGeometry_t* geometry);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetInputs(
    nvtiffEncodeParams_t params,
    uint8_t** images_d,
    uint32_t nImages);

/**********************************************************************/
/*             GEO Tiff                                               */
/**********************************************************************/

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetGeoKey(
    nvtiffEncodeParams_t params,
    nvtiffGeoKey_t key,
    nvtiffGeoKeyDataType_t type,
    void* value,
    uint32_t valueSize,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetTag(
    nvtiffEncodeParams_t params,
    uint16_t tag,
    nvtiffTagDataType type,
    void* value,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetGeoKeySHORT(
    nvtiffEncodeParams_t params,
    nvtiffGeoKey_t key,
    uint16_t value,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetGeoKeyDOUBLE(
    nvtiffEncodeParams_t params,
    nvtiffGeoKey_t key,
    double value,
    uint32_t count);

nvtiffStatus_t NVTIFFAPI nvtiffEncodeParamsSetGeoKeyASCII(
    nvtiffEncodeParams_t params,
    nvtiffGeoKey_t key,
    const char* value,
    uint32_t valueSize);

#if defined(__cplusplus)
  }
#endif

#endif
