from ._classes import *








'''
RLAPI Texture2D LoadTexture(const char *fileName);                                                       // Load texture from file into GPU memory (VRAM)
RLAPI Texture2D LoadTextureFromImage(Image image);                                                       // Load texture from image data
RLAPI TextureCubemap LoadTextureCubemap(Image image, int layout);                                        // Load cubemap from image, multiple image cubemap layouts supported
RLAPI RenderTexture2D LoadRenderTexture(int width, int height);                                          // Load texture for rendering (framebuffer)

RLAPI bool IsTextureValid(Texture2D texture);                                                            // Check if a texture is valid (loaded in GPU)
RLAPI void UnloadTexture(Texture2D texture);                                                             // Unload texture from GPU memory (VRAM)
RLAPI bool IsRenderTextureValid(RenderTexture2D target);                                                 // Check if a render texture is valid (loaded in GPU)
RLAPI void UnloadRenderTexture(RenderTexture2D target);                                                  // Unload render texture from GPU memory (VRAM)
RLAPI void UpdateTexture(Texture2D texture, const void *pixels);                                         // Update GPU texture with new data (pixels should be able to fill texture)
RLAPI void UpdateTextureRec(Texture2D texture, Rectangle rec, const void *pixels);                       // Update GPU texture rectangle with new data (pixels and rec should fit in texture)
'''

makeconnect("LoadTexture", [c_char_p], Texture2D)
def load_texture(file_name: str):
    return lib.LoadTexture(file_name.encode())

makeconnect("LoadTextureFromImage", [Image], Texture2D)
def load_texture_from_image(image: Image):
    return lib.LoadTextureFromImage(image)

makeconnect("LoadTextureCubemap", [Image, c_int], TextureCubemap)
def load_texture_cubemap(image: Image, layout: int):
    return lib.LoadTextureCubemap(image, layout)

makeconnect("LoadRenderTexture", [c_int, c_int], RenderTexture2D)
def load_render_texture(width: int, height: int):
    return lib.LoadRenderTexture(width, height)

"""
RLAPI Model LoadModel(const char *fileName);                                                // Load model from files (meshes and materials)
RLAPI Model LoadModelFromMesh(Mesh mesh);                                                   // Load model from generated mesh (default material)
RLAPI bool IsModelValid(Model model);                                                       // Check if a model is valid (loaded in GPU, VAO/VBOs)
RLAPI void UnloadModel(Model model);                                                        // Unload model (including meshes) from memory (RAM and/or VRAM)
RLAPI BoundingBox GetModelBoundingBox(Model model);                                         // Compute model bounding box limits (considers all meshes)
"""

makeconnect("LoadModel", [c_char_p], Model)
def load_model(file_name: str):
    return lib.LoadModel(file_name.encode())

makeconnect("LoadModelFromMesh", [Mesh], Model)
def load_model_from_mesh(mesh: Mesh):
    return lib.LoadModelFromMesh(mesh)

makeconnect("IsModelValid", [Model], c_bool)
def is_model_valid(model: Model):
    return lib.IsModelValid(model)

makeconnect("UnloadModel", [Model])
def unload_model(model: Model):
    lib.UnloadModel(model)

makeconnect("GetModelBoundingBox", [Model], BoundingBox)
def get_model_bounding_box(model: Model):
    return lib.GetModelBoundingBox(model)

"""
// NOTE: These functions do not require GPU access
RLAPI Image LoadImage(const char *fileName);                                                             // Load image from file into CPU memory (RAM)
RLAPI Image LoadImageRaw(const char *fileName, int width, int height, int format, int headerSize);       // Load image from RAW file data
RLAPI Image LoadImageAnim(const char *fileName, int *frames);                                            // Load image sequence from file (frames appended to image.data)

RLAPI Image LoadImageAnimFromMemory(const char *fileType, const unsigned char *fileData, int dataSize, int *frames); // Load image sequence from memory buffer

RLAPI Image LoadImageFromMemory(const char *fileType, const unsigned char *fileData, int dataSize);      // Load image from memory buffer, fileType refers to extension: i.e. '.png'
RLAPI Image LoadImageFromTexture(Texture2D texture);                                                     // Load image from GPU texture data
RLAPI Image LoadImageFromScreen(void);                                                                   // Load image from screen buffer and (screenshot)
RLAPI bool IsImageValid(Image image);                                                                    // Check if an image is valid (data and parameters)
RLAPI void UnloadImage(Image image);                                                                     // Unload image from CPU memory (RAM)
RLAPI bool ExportImage(Image image, const char *fileName);                                               // Export image data to file, returns true on success
RLAPI unsigned char *ExportImageToMemory(Image image, const char *fileType, int *fileSize);              // Export image to memory buffer
RLAPI bool ExportImageAsCode(Image image, const char *fileName);                                         // Export image as code file defining an array of bytes, returns true on success
"""

makeconnect("LoadImage", [c_char_p], Image)
def load_image(file_name: str):
    return lib.LoadImage(file_name.encode())

# ---- LoadImageRaw ----
makeconnect("LoadImageRaw", [c_char_p, c_int, c_int, c_int, c_int], Image)
def load_image_raw(file_name: str, width: int, height: int, format: int, header_size: int):
    return lib.LoadImageRaw(file_name.encode(), width, height, format, header_size)

# ---- LoadImageAnim ----
makeconnect("LoadImageAnim", [c_char_p, POINTER(c_int)], Image)
def load_image_anim(file_name: str):
    frames = c_int(0)
    img = lib.LoadImageAnim(file_name.encode(), byref(frames))
    return img, frames.value

# ---- LoadImageAnimFromMemory ----
makeconnect("LoadImageAnimFromMemory", [c_char_p, POINTER(c_ubyte), c_int, POINTER(c_int)], Image)
def load_image_anim_from_memory(file_type: str, file_data: bytes):
    data = (c_ubyte * len(file_data))(*file_data)
    frames = c_int(0)
    img = lib.LoadImageAnimFromMemory(file_type.encode(), data, len(file_data), byref(frames))
    return img, frames.value

makeconnect("LoadImageFromMemory", [c_char_p, POINTER(c_ubyte), c_int], Image)
def load_image_from_memory(file_type: str, file_data: bytes):
    data = (c_ubyte * len(file_data))(*file_data)
    return lib.LoadImageFromMemory(file_type, data, len(file_data))

makeconnect("LoadImageFromTexture", [Texture2D], Image)
def load_image_from_texture(texture: Texture2D):
    return lib.LoadImageFromTexture(texture)

makeconnect("LoadImageFromScreen", [], Image)
def load_image_from_screen():
    return lib.LoadImageFromScreen()




"""
// NOTE: Shader functionality is not available on OpenGL 1.1
RLAPI Shader LoadShader(const char *vsFileName, const char *fsFileName);   // Load shader from files and bind default locations
RLAPI Shader LoadShaderFromMemory(const char *vsCode, const char *fsCode); // Load shader from code strings and bind default locations
RLAPI bool IsShaderValid(Shader shader);                                   // Check if a shader is valid (loaded on GPU)
RLAPI int GetShaderLocation(Shader shader, const char *uniformName);       // Get shader uniform location
RLAPI int GetShaderLocationAttrib(Shader shader, const char *attribName);  // Get shader attribute location
RLAPI void SetShaderValue(Shader shader, int locIndex, const void *value, int uniformType);               // Set shader uniform value
RLAPI void SetShaderValueV(Shader shader, int locIndex, const void *value, int uniformType, int count);   // Set shader uniform value vector
RLAPI void SetShaderValueMatrix(Shader shader, int locIndex, Matrix mat);         // Set shader uniform value (matrix 4x4)
RLAPI void SetShaderValueTexture(Shader shader, int locIndex, Texture2D texture); // Set shader uniform value and bind the texture (sampler2d)
RLAPI void UnloadShader(Shader shader);      
"""

"""
RLAPI void UploadMesh(Mesh *mesh, bool dynamic);                                            // Upload mesh vertex data in GPU and provide VAO/VBO ids
RLAPI void UpdateMeshBuffer(Mesh mesh, int index, const void *data, int dataSize, int offset); // Update mesh vertex data in GPU for a specific buffer index
RLAPI void UnloadMesh(Mesh mesh);                                                           // Unload mesh data from CPU and GPU
RLAPI void DrawMesh(Mesh mesh, Material material, Matrix transform);                        // Draw a 3d mesh with material and transform
RLAPI void DrawMeshInstanced(Mesh mesh, Material material, const Matrix *transforms, int instances); // Draw multiple mesh instances with material and different transforms
RLAPI BoundingBox GetMeshBoundingBox(Mesh mesh);                                            // Compute mesh bounding box limits
RLAPI void GenMeshTangents(Mesh *mesh);                                                     // Compute mesh tangents
RLAPI bool ExportMesh(Mesh mesh, const char *fileName);                                     // Export mesh data to file, returns true on success
RLAPI bool ExportMeshAsCode(Mesh mesh, const char *fileName);                               // Export mesh as code file (.h) defining multiple arrays of vertex attributes
"""

"""
RLAPI Wave LoadWave(const char *fileName);                            // Load wave data from file
RLAPI Wave LoadWaveFromMemory(const char *fileType, const unsigned char *fileData, int dataSize); // Load wave from memory buffer, fileType refers to extension: i.e. '.wav'
RLAPI bool IsWaveValid(Wave wave);                                    // Checks if wave data is valid (data loaded and parameters)
RLAPI Sound LoadSound(const char *fileName);                          // Load sound from file
RLAPI Sound LoadSoundFromWave(Wave wave);                             // Load sound from wave data
RLAPI Sound LoadSoundAlias(Sound source);                             // Create a new sound that shares the same sample data as the source sound, does not own the sound data
RLAPI bool IsSoundValid(Sound sound);                                 // Checks if a sound is valid (data loaded and buffers initialized)
RLAPI void UpdateSound(Sound sound, const void *data, int sampleCount); // Update sound buffer with new data (data and frame count should fit in sound)
RLAPI void UnloadWave(Wave wave);                                     // Unload wave data
RLAPI void UnloadSound(Sound sound);                                  // Unload sound
RLAPI void UnloadSoundAlias(Sound alias);                             // Unload a sound alias (does not deallocate sample data)
RLAPI bool ExportWave(Wave wave, const char *fileName);               // Export wave data to file, returns true on success
RLAPI bool ExportWaveAsCode(Wave wave, const char *fileName);         // Export wave sample data to code (.h), returns true on success
"""

makeconnect("LoadWave", [c_char_p], Wave)
def load_wave(file_name: str): 
    return lib.LoadWave(file_name.encode())

makeconnect("LoadWaveFromMemory", [c_char_p, ubyte_p, c_int], Wave)

makeconnect("IsWaveValid", [Wave], c_bool)
def is_wave_valid(wave: Wave):
    return lib.IsWaveValid(wave)

makeconnect("LoadSound", [c_char_p], Sound)
def load_sound(file_name: str): 
    return lib.LoadSound(file_name.encode())

makeconnect("LoadSoundFromWave", [Wave], Sound)
def load_sound_from_wave(wave: Wave):
    return lib.LoadSoundFromWave(wave)

makeconnect("LoadSoundAlias", [Sound], Sound)
def load_sound_alias(source: Sound):
    return lib.LoadSoundAlias(source)

makeconnect("IsSoundValid", [Sound], c_bool)
def is_sound_valid(sound: Sound):
    return lib.IsSoundValid(sound)

makeconnect("UpdateSound", [Sound, c_void_p, c_int])
def update_sound(sound: Sound, data, sample_count: int):
    lib.UpdateSound(sound, data, sample_count)

makeconnect("UnloadWave", [Wave])
def unload_wave(wave: Wave):
    lib.UnloadSound(wave)

makeconnect("UnloadSound", [Sound])
def unload_sound(sound: Sound):
    lib.UnloadSound(sound)

makeconnect("UnloadSoundAlias", [Sound])
def unload_sound_alias(alias: Sound):
    lib.UnloadSoundAlias(alias)

makeconnect("ExportWave", [Wave, c_char_p], c_bool)
def export_wave(wave: Wave, file_name: str):
    lib.ExportWave(wave, file_name.encode())

makeconnect("ExportWaveAsCode", [Wave, c_char_p], c_bool)
def export_wave_as_code(wave: Wave, file_name: str):
    lib.ExportWaveAsCode(wave, file_name.encode())
