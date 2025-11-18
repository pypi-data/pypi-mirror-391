from ._classes import *




"""
RLAPI void InitAudioDevice(void);                                     // Initialize audio device and context
RLAPI void CloseAudioDevice(void);                                    // Close the audio device and context
RLAPI bool IsAudioDeviceReady(void);                                  // Check if audio device has been initialized successfully
RLAPI void SetMasterVolume(float volume);                             // Set master volume (listener)
RLAPI float GetMasterVolume(void);                                    // Get master volume (listener)
"""
init_audio_device = lib.InitAudioDevice
close_audio_device = lib.CloseAudioDevice

makeconnect("IsAudioDeviceReady", [], c_bool)
def is_audio_device_ready():
    return lib.IsAudioDeviceReady()

makeconnect("SetMasterVolume", [c_float])
def set_master_volume(volume: float):
    lib.SetMasterVolume(volume)

makeconnect("GetMasterVolume", [], c_float)
def get_master_volume():
    return lib.GetMasterVolume()

"""
RLAPI void PlaySound(Sound sound);                                    // Play a sound
RLAPI void StopSound(Sound sound);                                    // Stop playing a sound
RLAPI void PauseSound(Sound sound);                                   // Pause a sound
RLAPI void ResumeSound(Sound sound);                                  // Resume a paused sound

RLAPI bool IsSoundPlaying(Sound sound);                               // Check if a sound is currently playing
RLAPI void SetSoundVolume(Sound sound, float volume);                 // Set volume for a sound (1.0 is max level)
RLAPI void SetSoundPitch(Sound sound, float pitch);                   // Set pitch for a sound (1.0 is base level)
RLAPI void SetSoundPan(Sound sound, float pan);                       // Set pan for a sound (0.5 is center)

RLAPI Wave WaveCopy(Wave wave);                                       // Copy a wave to a new wave
RLAPI void WaveCrop(Wave *wave, int initFrame, int finalFrame);       // Crop a wave to defined frames range
RLAPI void WaveFormat(Wave *wave, int sampleRate, int sampleSize, int channels); // Convert wave data to desired format
RLAPI float *LoadWaveSamples(Wave wave);                              // Load samples data from wave as a 32bit float data array
RLAPI void UnloadWaveSamples(float *samples);   
"""

makeconnect("PlaySound", [Sound])
def play_sound(sound: Sound):
    lib.PlaySound(sound)

makeconnect("StopSound", [Sound])
def stop_sound(sound: Sound):
    lib.StopSound(sound)

makeconnect("PauseSound", [Sound])
def pause_sound(sound: Sound):
    lib.PauseSound(sound)

makeconnect("ResumeSound", [Sound])
def resume_sound(sound: Sound):
    lib.ResumeSound(sound)

makeconnect("IsSoundPlaying", [Sound], c_bool)
def is_sound_playing(sound: Sound):
    return lib.IsSoundPlaying(sound)

makeconnect("SetSoundVolume", [Sound])
def set_sound_volume(sound: Sound, volume: float):
    lib.SetSoundVolume(sound, volume)

makeconnect("SetSoundPitch", [Sound])
def set_sound_pitch(sound: Sound, pitch: float):
    lib.SetSoundPitch(sound, pitch)

makeconnect("SetSoundPan", [Sound])
def set_sound_pan(sound: Sound, pan: float):
    lib.SetSoundPan(sound, pan)

# WaveCopy
makeconnect("WaveCopy", [Wave], Wave)
def wave_copy(wave: Wave):
    """Copy a wave to a new wave."""
    return lib.WaveCopy(wave)


# WaveCrop
makeconnect("WaveCrop", [POINTER(Wave), c_int, c_int])
def wave_crop(wave: Wave, init_frame: int, final_frame: int):
    """Crop a wave to a defined frame range."""
    lib.WaveCrop(byref(wave), init_frame, final_frame)
    return wave


# WaveFormat
makeconnect("WaveFormat", [POINTER(Wave), c_int, c_int, c_int])
def wave_format(wave: Wave, sample_rate: int, sample_size: int, channels: int):
    """Convert wave data to desired format (sample rate, bit depth, channels)."""
    lib.WaveFormat(byref(wave), sample_rate, sample_size, channels)
    return wave


# LoadWaveSamples
makeconnect("LoadWaveSamples", [Wave], POINTER(c_float))
def load_wave_samples(wave: Wave):
    """Load 32-bit float samples from a wave and return a pointer."""
    return lib.LoadWaveSamples(wave)


# UnloadWaveSamples
makeconnect("UnloadWaveSamples", [POINTER(c_float)])
def unload_wave_samples(samples):
    """Unload 32-bit float samples previously loaded from a wave."""
    lib.UnloadWaveSamples(samples)
