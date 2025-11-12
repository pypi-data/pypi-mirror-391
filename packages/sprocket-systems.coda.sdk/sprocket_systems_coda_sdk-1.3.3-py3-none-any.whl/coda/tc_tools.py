###########################################################
# Application Name  : tc_tools.py
# Author            : Skywalker Dev Labs
# Date              : September 4th, 2025
# Description       : tools for calculations with timecode
# Location          : Original is kept in 1031-tc_tools
#
# Frame rate tools:
#   string      float_to_v_fr_string(double v_fr) <- does not yet exist (29.97df can not be distinguished from 29.97)
#   double      v_fr_string_to_float(v_fr_string)
#   double      v_fr_string_to_non_pulldown_float(v_fr_string)
#   Conversion to/from:
#     double      vid_frames_to_audio_frames(v_fs, v_fr_string, a_fr)
#     double      audio_frames_to_vid_frames(a_fs, v_fr_string, a_fr)
#     double      vid_frames_to_time_seconds(v_fs, v_fr_string)
#     double      time_seconds_to_vid_frames(time_s, v_fr_string)
#     double      vid_frames_to_timecode_seconds(v_fs, v_fr_string)
#     double      timecode_seconds_to_vid_frames(timecode_s, v_fr_string)
#   Specialty:
#     double      vid_frames_align_to_audio_frames(v_fs, v_fr_string, a_fr, pad_or_trim)
# Timecode/frame rate tools:
#   General:
#     bool        tc_is_whole_video_frames(tc, v_fr_string)
#     string      tc_round(tc, partial_v_fr_digits, v_fr_string)
#   Conversion to/from:
#     double      tc_to_vid_frames(tc, v_fr_string)
#     string      vid_frames_to_tc(v_fs, v_fr_string)
#     double      tc_to_time_seconds(tc, v_fr_string)
#     string      time_seconds_to_tc(time_s, v_fr_string)
#     double      tc_to_audio_frames(tc, v_fr_string, a_fr)
#     string      audio_frames_to_tc(a_fs, v_fr_string, a_fr)
#   double      tc_add(tc_addend_a, tc_addend_b, v_fr_string)
#   double      tc_sub(tc_minuend, tc_subtrahend, v_fr_string)
#
# Utilites
#   string      tc_tools_version()
#   tc_hr, tc_min, tc_sec, tc_frames, tc_partial_frames   parse_tc_string(tc, v_fr_string)
#
# Abbreviations used in this file:
#   v_fr          video frame rate as a double      "(v)ideo (f)rame (r)ate"
#   v_fs          video frame count as a double     "(v)ideo (f)rame(s)"
#   a_fr          audio frame rate as a double      "(a)udio (f)rame (r)ate"
#   a_fs          audio frame count as a double     "(a)udio (f)rame(s)"
#   tc            timecode as a string in the form "HR:MN:SC:FR.partial_frames"
#   time_s        time in real seconds (not timecode seconds)
#   timecode_s    time in timecode seconds
#   v_fr_string   video frame rate as a string, one of:
#       VID_FRAME_RATE_STRING_2397
#       VID_FRAME_RATE_STRING_2400
#       VID_FRAME_RATE_STRING_2500
#       VID_FRAME_RATE_STRING_2997
#       VID_FRAME_RATE_STRING_2997df
#       VID_FRAME_RATE_STRING_3000
#   pad_or_trim   add or trim to align video frames to audio frames.  one of:
#       'pad'
#       'trim'
# 
# Notes:
#   partial_frames:       is a fraction of the given frame rate.
#       For example: "00:00:00:03.141" @ 24.00 fps is equal to 3.141 video frames.
#
#   timecode_seconds:     the number of seconds at the timecode rate... not the clock on the wall.
#       timecode_seconds will differ from time_s for pull-down rates (23, 29, and 29DF)
#       29.97df is a special case where timecode_seconds is equal to the number of video frames at the timecode rate.
#       And so:
#           00:01:00;02 @29.97df  is equal to 60.0000000 timecode_seconds.
#           00:01:00:00 @29.97    is equal to 60.0000000 timecode_seconds.
#           00:01:00:02 @29.97    is equal to 60.0666667 timecode_seconds.
#           00:01:00:00 @30.00    is equal to 60.0000000 timecode_seconds.
#   partial_v_fr_digits:  an int, the number of decimal places to round to
#
#   As of 2023-05-09:
#       vid_frames_to_tc    will round to the nearest thousandth of a partial frame (using const PARTIAL_FRAME_NUMBER_OF_DIGITS for precision)
#       time_seconds_to_tc  will round to the nearest thousandth of a partial frame (using const PARTIAL_FRAME_NUMBER_OF_DIGITS for precision)
###########################################################

from decimal import Decimal

def tc_tools_version():
    return '1.3.2'

# @abstract     Video frame rates as strings use by tool
# @discussion   VID_FRAME_RATE_STRING_2997df is not fully supported
VID_FRAME_RATE_STRING_2397 = '23'
VID_FRAME_RATE_STRING_2400 = '24'
VID_FRAME_RATE_STRING_2500 = '25'
VID_FRAME_RATE_STRING_2997 = '29'
VID_FRAME_RATE_STRING_2997df = '29DF'
VID_FRAME_RATE_STRING_3000 = '30'
VID_FRAME_RATE_STRING_4800 = '48'
VID_FRAME_RATE_STRING_5000 = '50'
VID_FRAME_RATE_STRING_6000 = '60'

# delimeter to use when creating a 2997df tc string
# this has no effect on reading a tc string (when reading, it can be either : or ;);
TC_TOOLS_29DF_SEC_FRAME_DELIM = ':' # traditionally, this is a ;

PARTIAL_FRAME_NUMBER_OF_DIGITS = 7
ALIGN_VFS_ROUND_DIGITS = 9


valid_v_fr_strings = [
    VID_FRAME_RATE_STRING_2397,
    VID_FRAME_RATE_STRING_2400,
    VID_FRAME_RATE_STRING_2500,
    VID_FRAME_RATE_STRING_2997,
    VID_FRAME_RATE_STRING_2997df,
    VID_FRAME_RATE_STRING_3000,
    VID_FRAME_RATE_STRING_4800,
    VID_FRAME_RATE_STRING_5000,
    VID_FRAME_RATE_STRING_6000,
]


def v_fr_string_validate(v_fr_string):
    """Validate v_fr_string and return an upper() version"""
    v_fr_str_upper = v_fr_string.upper()
    v_fr_str_okay = False
    for v in valid_v_fr_strings:
        if v == v_fr_str_upper:
            v_fr_str_okay = True
            break
    if not v_fr_str_okay:
        err_msg = ''.join(['tc_tools: frame rate not recognized = ', v_fr_string])
        print(err_msg)
        raise Exception(err_msg)
    return v_fr_str_upper


def v_fr_string_to_non_pulldown_float(v_fr_string):
    """Convert from one of the enum frame rate strings to the non-pulldown float value."""
    v_fr_str_upper = v_fr_string_validate(v_fr_string)
    if v_fr_str_upper == VID_FRAME_RATE_STRING_2397:
        v_fr = 24.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2400:
        v_fr = 24.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2500:
        v_fr = 25.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2997:
        v_fr = 30.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2997df:
        v_fr = 30.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_3000:
        v_fr = 30.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_4800:
        v_fr = 48.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_5000:
        v_fr = 50.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_6000:
        v_fr = 60.0
    else:
        err_msg = ''.join(['tc_tools: frame rate not recognized = ', v_fr_string, ' This should never happen.'])
        print(err_msg)
        raise Exception(err_msg)
    return v_fr


def v_fr_string_to_float(v_fr_string):
    """Convert from one of the enum frame rate strings to the actual float value."""
    v_fr_str_upper = v_fr_string_validate(v_fr_string)
    if v_fr_str_upper == VID_FRAME_RATE_STRING_2397:
        v_fr = 24.0/1.001
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2400:
        v_fr = 24.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2500:
        v_fr = 25.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2997:
        v_fr = 30/1.001
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_2997df:
        v_fr = 30/1.001
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_3000:
        v_fr = 30.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_4800:
        v_fr = 48.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_5000:
        v_fr = 50.0
    elif v_fr_str_upper == VID_FRAME_RATE_STRING_6000:
        v_fr = 60.0
    else:
        err_msg = ''.join(['tc_tools: frame rate not recognized = ', v_fr_string, ' This should never happen.'])
        print(err_msg)
        raise Exception(err_msg)
    return v_fr


def vid_frames_to_audio_frames(v_fs, v_fr_string, a_fr):
    """Convert from number of video frames to audio frames."""
    v_fr = v_fr_string_to_float(v_fr_string)
    a_fs = v_fs * ( a_fr / v_fr )
    return a_fs

def audio_frames_to_vid_frames(a_fs, v_fr_string, a_fr):
    """Convert from number of audio frames to video frames."""
    v_fr = v_fr_string_to_float(v_fr_string)
    v_fs = a_fs * (v_fr / a_fr)
    return v_fs


def vid_frames_to_time_seconds(v_fs, v_fr_string):
    """Convert from number of video frames to time in seconds."""
    v_fr = v_fr_string_to_float(v_fr_string)
    return v_fs / v_fr

def time_seconds_to_vid_frames(time_s, v_fr_string):
    """Convert from time in seconds to number of video frames."""
    v_fr = v_fr_string_to_float(v_fr_string)
    return v_fr * time_s


def vid_frames_to_timecode_seconds(v_fs, v_fr_string):
    """Convert from number of video frames to time in timcode seconds."""
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    return v_fs / v_fr

def timecode_seconds_to_vid_frames(time_s, v_fr_string):
    """Convert from time in timecode seconds to number of video frames."""
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    return v_fr * time_s


############################################################################################
#   Local utility functions
############################################################################################

def is_float_whole_number(f):
    if f == round(f): return True
    return False

def tc_components_to_tc(tc_hr, tc_min, tc_sec, tc_fr, tc_partial_frames, v_fr_string):
    """Assemble timecode components into a timecode string."""
    # 2023-11-30 DRJ: need to accomodate 2997df
    # if tc_partial_frames + tc_fr + tc_sec ends up adding to minutes, we need to make adjustments.
    #       v_fr_string = VID_FRAME_RATE_STRING_2997df
    #            tc_hr  = 0
    #            tc_min = 0
    #            tc_sec = 59
    #             tc_fr = 30
    # tc_partial_frames = 0
    # the resulting tc would be 00:01:00:02
    # 2024-05-10 DRJ: when tc_partial_frames was less than 0.0001, it was being written in exp notation.
    #   And so, I added the Decimal bits.
    # 2025-01-07 DRJ: Decimal does some mangled rounding!  0.6 is printed ad 0.599999999999999999999
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    sec_fr_delimiter = ':'
    if v_fr_string == VID_FRAME_RATE_STRING_2997df:
        sec_fr_delimiter = TC_TOOLS_29DF_SEC_FRAME_DELIM

    while tc_partial_frames >= 1.0:
        tc_fr += 1
        tc_partial_frames -= 1.0
    while tc_fr >= v_fr:
        tc_sec += 1
        tc_fr -= int(v_fr)
    while tc_sec >= 60:
        tc_min += 1
        tc_sec -= 60
    while tc_min >= 60:
        tc_hr += 1
        tc_min -= 60

    tc = ''.join([ str(tc_hr).zfill(2), ':', str(tc_min).zfill(2), ':',str(tc_sec).zfill(2), sec_fr_delimiter, str(tc_fr).zfill(2)])
    if tc_partial_frames > 0.0:
        tc_partial_frames_string = str(tc_partial_frames).lstrip('0')
        if tc_partial_frames < 0.0001:
            tc_partial_frames_string = str(Decimal(tc_partial_frames)).lstrip('0')
        if (len(tc_partial_frames_string) + 1) > PARTIAL_FRAME_NUMBER_OF_DIGITS:
            tc_partial_frames_string = tc_partial_frames_string[0:PARTIAL_FRAME_NUMBER_OF_DIGITS + 1].rstrip('0')
        tc = ''.join([tc,tc_partial_frames_string ])
    return tc


############################################################################################
#   specialty and general conversion
############################################################################################
    
#
# returns the number of video frames you must add or trim so that video and audio frames are aligned
#     v_fs          the current number of video frames
#     v_fr_string   the video frame rate
#     a_fr          the audio frame rate
#     pad_or_trim   either 'pad' or 'trim'
def vid_frames_align_to_audio_frames(v_fs, v_fr_string, a_fr, pad_or_trim):
    #booger
    v_fr_str_upper = v_fr_string_validate(v_fr_string)

    rounded_v_fs = round(v_fs, ALIGN_VFS_ROUND_DIGITS)
    if pad_or_trim == 'pad':
        v_fs_to_add = 0.0
        if not is_float_whole_number(rounded_v_fs):
            v_fs_to_add += int(v_fs + 1) - v_fs
            v_fs_to_add = round(v_fs_to_add, ALIGN_VFS_ROUND_DIGITS)
        if (v_fr_str_upper == VID_FRAME_RATE_STRING_2997) or (v_fr_str_upper == VID_FRAME_RATE_STRING_2997df):
            if a_fr != 48000.0:
                err_msg = ''.join(['tc_tools: align_to_audio_frames: 29.97 and 29DF currently only audio frame rate of 48000.0 is supported. a_fr = ', str(a_fr)])
                print(err_msg)
                raise Exception(err_msg)
            v_fs_whole_vid_frames = round(v_fs + v_fs_to_add, ALIGN_VFS_ROUND_DIGITS)
            v_fs_whole_vid_frames_mod_5 = v_fs_whole_vid_frames % 5.0
            if v_fs_whole_vid_frames_mod_5:
                v_fs_to_add += 5 - v_fs_whole_vid_frames_mod_5
        return v_fs_to_add
    if pad_or_trim == 'trim':
        v_fs_to_trim = 0.0
        if not is_float_whole_number(rounded_v_fs):
            v_fs_to_trim += v_fs - int(v_fs)
        if (v_fr_str_upper == VID_FRAME_RATE_STRING_2997) or (v_fr_str_upper == VID_FRAME_RATE_STRING_2997df):
            if a_fr != 48000.0:
                err_msg = ''.join(['tc_tools: align_to_audio_frames: 29.97 and 29DF currently only audio frame rate of 48000.0 is supported. a_fr = ', str(a_fr)])
                print(err_msg)
                raise Exception(err_msg)
            v_fs_whole_vid_frames = round(v_fs - v_fs_to_trim, ALIGN_VFS_ROUND_DIGITS)
            v_fs_whole_vid_frames_mod_5 = v_fs_whole_vid_frames % 5.0
            if v_fs_whole_vid_frames_mod_5:
                v_fs_to_trim += v_fs_whole_vid_frames_mod_5
        return v_fs_to_trim
    err_msg = ''.join(['tc_tools: align_to_audio_frames: mode must be one of trim or pad'])
    print(err_msg)
    raise Exception(err_msg)


def parse_tc_string(tc, v_fr_string):
    """
    parse tc into tc_hr, tc_min, tc_sec, tc_frames, tc_partial_frames
    TODO: 2025-09-26: use frame rate to only allow ';' in the case of VID_FRAME_RATE_STRING_2997df
    """
    parse_ok = True
    tc_splits = tc.rstrip().split(":")
    try:
        if 3 == len(tc_splits):
            tc_splits_df = tc_splits[2].split(";")
            if 2 == len(tc_splits_df):
                tc_sec = int(tc_splits_df[0])
                tc_fr_and_partial = tc_splits_df[1]
            else:
                parse_ok = False
        elif 4 == len(tc_splits):
            tc_sec = int(tc_splits[2])
            tc_fr_and_partial = tc_splits[3]
        else:
            parse_ok = False
        if parse_ok:
            tc_hr = int(tc_splits[0])
            tc_min = int(tc_splits[1])
            tc_frames = int(tc_fr_and_partial.split(".")[0])
            if len(tc_fr_and_partial) > 2:
                tc_partial_frames = float(''.join(['0.', tc_fr_and_partial.split(".")[1]]))
            else:
                tc_partial_frames = 0.0
    except:
        parse_ok = False
    if not parse_ok:
        err_msg = ''.join(['tc is not valid form HR:MN:SC:FR.partial tc = ', tc])
        print(err_msg)
        raise Exception(err_msg)
    return tc_hr, tc_min, tc_sec, tc_frames, tc_partial_frames


def tc_is_whole_video_frames(tc, v_fr_string):
    """Return true if timecode string is a whole number of video frames."""
    try:
        tc_hr, tc_min, tc_sec, tc_frames, tc_partial_frames = parse_tc_string(tc, v_fr_string)
    except Exception as e:
        err_msg = ''.join(['tc_tools: tc_is_whole_video_frames: ', str(e)])
        print(err_msg)
        raise Exception(err_msg)
    if tc_partial_frames != 0.0:
        return False
    return True


def tc_round(tc, partial_v_fr_digits, v_fr_string):
    v_fs = tc_to_vid_frames(tc, v_fr_string)
    v_fs = round(v_fs, partial_v_fr_digits)
    return vid_frames_to_tc(v_fs, v_fr_string)


############################################################################################
#   Conversion to/from timecode
############################################################################################

def tc_to_vid_frames(tc, v_fr_string):
    """Get the number of video frames from timecode."""
    v_fr_str_upper = v_fr_string_validate(v_fr_string)

    v_fr = v_fr_string_to_non_pulldown_float(v_fr_str_upper)
    tc_hr, tc_min, tc_sec, tc_frames, tc_partial_frames = parse_tc_string(tc, v_fr_str_upper)
    frame_count = tc_frames
    # 29.97 Drop-Frame Time Code eliminates 2 frames every minute except for minutes 00, 10, 20, 30, 40, and 50
    if v_fr_str_upper == VID_FRAME_RATE_STRING_2997df:
        total_minutes = tc_min + (tc_hr * 60)
        frames_due_to_minutes = v_fr * total_minutes * 60
        frames_due_to_minutes -= (int(total_minutes) * 2)
        frames_due_to_minutes += (int(total_minutes / 10) * 2)
        frames_due_to_seconds = v_fr * tc_sec
        frame_count += frames_due_to_seconds
        frame_count += frames_due_to_minutes
    else:
        frame_count += v_fr * tc_sec
        frame_count += v_fr * tc_min * 60 
        frame_count += v_fr * tc_hr * 60 * 60
    return frame_count + tc_partial_frames

def vid_frames_to_tc(v_fs, v_fr_string):
    """Get timecode from the number of video frames ."""
    v_fr_str_upper = v_fr_string_validate(v_fr_string)
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_str_upper)
    # if we are negative, wrap around
    v_fs_24hr = tc_to_vid_frames('24:00:00:00', v_fr_str_upper)
    v_fs = round(v_fs, PARTIAL_FRAME_NUMBER_OF_DIGITS)
    if v_fs < 0:
        v_fs = v_fs + v_fs_24hr
    if v_fs > v_fs_24hr:
        v_fs = v_fs - v_fs_24hr

    _tc = str("00:00:00:00")
    _vid_frames = v_fs
    if v_fr_str_upper == VID_FRAME_RATE_STRING_2997df:
        if True:
            # for every 1800 video frames, add two video frames
            minutes_fr_to_add = int(v_fs/1800) * 2
            # for every 18000 video frames, take away two video frames
            minutes_fr_to_remove = int(v_fs/18000) * 2
            v_fs += minutes_fr_to_add
            v_fs -= minutes_fr_to_remove
        total_seconds = v_fs / v_fr
        total_minutes = total_seconds / 60.0
        total_minutes_int = int(total_minutes)
        _vid_frames += (total_minutes_int * 2)
        _vid_frames -= (int(total_minutes_int / 10) * 2)
    if True:
        _tc_hr = int(_vid_frames / (v_fr * 60 * 60))
        _vid_frames = _vid_frames - v_fr * _tc_hr * 60 * 60
        _tc_min = int(_vid_frames / (v_fr * 60))
        _vid_frames = _vid_frames - v_fr * _tc_min * 60
        _tc_sec = int(_vid_frames / (v_fr))
        _vid_frames = _vid_frames - v_fr * _tc_sec
        _tc_fr = int(_vid_frames)
        _vid_frames = _vid_frames - _tc_fr
        _tc_subfr = _vid_frames
        _subframes = round(_tc_subfr, PARTIAL_FRAME_NUMBER_OF_DIGITS)
        _tc  = tc_components_to_tc(_tc_hr, _tc_min, _tc_sec, _tc_fr, _subframes, v_fr_str_upper)
    _tc_v_vs = tc_to_vid_frames(_tc, v_fr_string)
    if _tc_v_vs > v_fs_24hr:
        # should never happen
        err_msg = ''.join(['tc_tools: vid_frames_to_tc() result exceeds 24hr.  This should never happen.'])
        print(err_msg)
        raise Exception(err_msg)
    return _tc


def time_seconds_to_tc(time_s, v_fr_string):
    v_fs = time_s * v_fr_string_to_float(v_fr_string)
    return vid_frames_to_tc(v_fs,v_fr_string)


def tc_to_time_seconds(tc, v_fr_string):
    v_fs = tc_to_vid_frames(tc, v_fr_string)
    time_s = v_fs / v_fr_string_to_float(v_fr_string)
    return time_s


def tc_to_audio_frames(tc, v_fr_string, a_fr):
    v_fs = tc_to_vid_frames(tc, v_fr_string)
    return vid_frames_to_audio_frames(v_fs, v_fr_string, a_fr)


def audio_frames_to_tc(a_fs, v_fr_string, a_fr):
    v_fs = audio_frames_to_vid_frames(a_fs, v_fr_string, a_fr)
    return vid_frames_to_tc(v_fs, v_fr_string)


def tc_sub(tc_minuend, tc_subtrahend, v_fr_string):
    """Get the timecode difference in video frames."""
    dif_vid_frames = tc_to_vid_frames(tc_minuend, v_fr_string) - tc_to_vid_frames(tc_subtrahend, v_fr_string)
    return dif_vid_frames


def tc_add(tc_addend_a, tc_addend_b, v_fr_string):
    """Get the timecode sum in video frames."""
    sum_vid_frames = tc_to_vid_frames(tc_addend_a, v_fr_string) + tc_to_vid_frames(tc_addend_b, v_fr_string)
    return sum_vid_frames


############################################################################################
#
#   for direct testing
#
############################################################################################

if __name__ == "__main__":
    print('tc_tools: top of __main__')

    vid_frame_rate = VID_FRAME_RATE_STRING_2397
    tc = '00:00:01:15'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))

    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    tc_v_fs = 2589411
    tc = vid_frames_to_tc(tc_v_fs,vid_frame_rate)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: tc               = ',tc)
    tc_v_fs = 757473

    tc = vid_frames_to_tc(tc_v_fs,vid_frame_rate)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: tc               = ',tc)

    vid_frame_rate = VID_FRAME_RATE_STRING_2400
    tc = '00:00:01:15'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))

    tc = '00:00:01:20'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))
    
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    tc = '00:00:01:14'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))

    exit(0)
