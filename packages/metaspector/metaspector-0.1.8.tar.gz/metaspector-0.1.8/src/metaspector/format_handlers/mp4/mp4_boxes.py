# metaspector/format_handlers/mp4/mp4_boxes.py
# !/usr/bin/env python3

import logging
import plistlib
import struct
import io

from typing import Any, BinaryIO, Dict, Optional, Union, Tuple
from .mp4_bitstream_parser import BitReader
from .mp4_utils import (
    _decode_qt_language_code,
    _read_box_header,
    _read_uint8,
    _read_uint16,
    _read_uint32,
    _read_uint64,
    TRANSFER_CHARACTERISTICS_MAP,
    COLOR_PRIMARIES_MAP,
    MATRIX_COEFFICIENTS_MAP,
    _CHROMA_LOCATION_MAP,
    _AV1_CHROMA_LOCATION_MAP, _VP9_PROFILE_MAP, _AV1_PROFILE_MAP, _HEVC_PROFILE_MAP, _H264_PROFILE_MAP,
    _COVER_ART_FORMAT_MAP, _SUBTITLE_CODEC_MAP, _AUDIO_CODEC_MAP, _VIDEO_CODEC_MAP
)
from ...matrices.rating_matrix import get_age_classification

logger = logging.getLogger(__name__)


class MP4BoxParser:
    """
    A collection of static methods for parsing specific MP4 boxes.
    These methods are designed to be called by Mp4Parser.
    """

    class _TrackCharacteristics:
        """Holds boolean flags for track characteristics from 'udta'."""

        def __init__(self):
            self.main_program_content = False
            self.auxiliary_content = False
            self.original_content = False
            self.describes_video_for_accessibility = False
            self.enhances_speech_intelligibility = False
            self.dubbed_translation = False
            self.voice_over_translation = False
            self.language_translation = False
            self.forced_only = False
            self.describes_music_and_sound = False
            self.transcribes_spoken_dialog = False
            self.easy_to_read = False

        def update_from_tagc_value(self, text_value: str):
            t = text_value.lower().strip()
            if t == "public.main-program-content":
                self.main_program_content = True
            elif t == "public.auxiliary-content":
                self.auxiliary_content = True
            elif t == "public.original-content":
                self.original_content = True
            elif t == "public.accessibility.describes-video":
                self.describes_video_for_accessibility = True
            elif t == "public.accessibility.enhances-speech-intelligibility":
                self.enhances_speech_intelligibility = True
            elif t == "public.translation.dubbed":
                self.dubbed_translation = True
            elif t == "public.translation.voice-over":
                self.voice_over_translation = True
            elif t == "public.translation":
                self.language_translation = True
            elif t == "public.subtitles.forced-only":
                self.forced_only = True
            elif t == "public.accessibility.describes-music-and-sound":
                self.describes_music_and_sound = True
            elif t == "public.accessibility.transcribes-spoken-dialog":
                self.transcribes_spoken_dialog = True
            elif t == "public.easy-to-read":
                self.easy_to_read = True

    @staticmethod
    def _read_mp4_descriptor_length(f: BinaryIO) -> int:
        """Reads a variable-length size value from an MPEG-4 descriptor."""
        length = 0
        for _ in range(4):  # The size value is encoded in at most 4 bytes
            byte = _read_uint8(f)
            if byte is None:
                return 0
            length = (length << 7) | (byte & 0x7F)
            if not (byte & 0x80):  # The MSB of the last byte is 0
                break
        return length

    @staticmethod
    def _unescape_nal_payload(payload: bytes) -> bytes:
        """Removes emulation prevention bytes (0x03) from a NAL unit payload."""
        res = bytearray()
        i = 0
        while i < len(payload):
            if i + 2 < len(payload) and payload[i: i + 3] == b"\x00\x00\x03":
                res.extend(b"\x00\x00")
                i += 3
            else:
                res.append(payload[i])
                i += 1
        return bytes(res)

    @staticmethod
    def _parse_avcC(f: BinaryIO, box_end: int) -> Optional[Dict[str, Any]]:
        """
        Parses an 'avcC' box to determine profile, level, pixel format, and chroma location from the first SPS.
        """
        details: Dict[str, Any] = {
            "pixel_format": None,
            "profile": None,
            "profile_level": None,
            "chroma_location": None,
        }
        avcc_start = f.tell()
        try:
            f.seek(avcc_start + 5)
            num_sps = _read_uint8(f) & 0x1F
            if num_sps == 0:
                return None

            sps_len = _read_uint16(f)
            if sps_len is None or sps_len == 0:
                return None

            sps_payload = f.read(sps_len)
            unescaped_sps = MP4BoxParser._unescape_nal_payload(sps_payload)
            reader = BitReader(unescaped_sps)

            reader.read_bits(8)  # Skip the 1-byte NAL Unit Header

            profile_idc = reader.read_bits(8)
            details["profile"] = _H264_PROFILE_MAP.get(
                profile_idc, str(profile_idc)
            )

            reader.read_bits(8)  # Skip constraint_set flags / profile_compatibility

            level_idc = reader.read_bits(8)
            level = level_idc / 10.0 if level_idc > 0 else None

            if details["profile"] and level:
                details["profile_level"] = f"{level:.1f}"

            reader.read_ue()  # seq_parameter_set_id

            chroma_format_idc, bit_depth = 1, 8
            if profile_idc in [
                100,
                110,
                122,
                244,
                44,
                83,
                86,
                118,
                128,
                138,
                139,
                134,
                135,
            ]:
                chroma_format_idc = reader.read_ue()
                if chroma_format_idc == 3:
                    reader.read_bit()
                bit_depth = reader.read_ue() + 8
                reader.read_ue()
                reader.read_bit()
                if reader.read_bit():  # seq_scaling_matrix_present_flag
                    for i in range(8 if chroma_format_idc != 3 else 12):
                        if reader.read_bit():
                            scans = 16 if i < 6 else 64
                            last_scale, next_scale = 8, 8
                            for _ in range(scans):
                                if next_scale != 0:
                                    delta_scale = reader.read_se()
                                    next_scale = (last_scale + delta_scale + 256) % 256
                                last_scale = (
                                    next_scale if next_scale != 0 else last_scale
                                )

            reader.read_ue()
            pic_order_cnt_type = reader.read_ue()
            if pic_order_cnt_type == 0:
                reader.read_ue()
            elif pic_order_cnt_type == 1:
                reader.read_bit()
                reader.read_se()
                reader.read_se()
                for _ in range(reader.read_ue()):
                    reader.read_se()

            reader.read_ue()
            reader.read_bit()
            reader.read_ue()
            reader.read_ue()
            if not reader.read_bit():
                reader.read_bit()
            reader.read_bit()
            if reader.read_bit():
                reader.read_ue()
                reader.read_ue()
                reader.read_ue()
                reader.read_ue()

            if reader.read_bit():  # vui_parameters_present_flag
                if reader.read_bit():
                    if reader.read_bits(8) == 255:
                        reader.read_bits(32)
                if reader.read_bit():
                    reader.read_bit()
                if reader.read_bit():
                    reader.read_bits(3)
                    reader.read_bit()
                    if reader.read_bit():
                        reader.read_bits(24)
                if reader.read_bit():
                    top = reader.read_ue()
                    bottom = reader.read_ue()
                    details["chroma_location"] = (
                        _CHROMA_LOCATION_MAP.get(top)
                        if top == bottom
                        else f"{_CHROMA_LOCATION_MAP.get(top)}/{_CHROMA_LOCATION_MAP.get(bottom)}"
                    )

            if details["chroma_location"] is None and chroma_format_idc == 1:
                details["chroma_location"] = "left"

            pix_fmt_map = {0: "gray", 1: "yuv420p", 2: "yuv422p", 3: "yuv444p"}
            pix_fmt_base = pix_fmt_map.get(chroma_format_idc)
            if pix_fmt_base:
                details["pixel_format"] = (
                    f"{pix_fmt_base}{bit_depth}le" if bit_depth > 8 else pix_fmt_base
                )
            return details

        except (IndexError, struct.error) as e:
            logger.debug(f"Error parsing avcC box: {e}")
            return None
        finally:
            f.seek(box_end)

    @staticmethod
    def _parse_hvcC(f: BinaryIO, box_end: int) -> Optional[Dict[str, Any]]:
        """
        Parses an 'hvcC' box to determine profile, profile_level, pixel format, and chroma location from the first SPS.
        """
        details: Dict[str, Any] = {
            "pixel_format": None,
            "profile": None,
            "profile_level": None,
            "chroma_location": None,
        }
        hvcC_start = f.tell()
        try:
            f.seek(hvcC_start + 22)
            num_of_arrays = _read_uint8(f)
            if num_of_arrays is None:
                return None

            sps_payload = None
            for _ in range(num_of_arrays):
                array_info = _read_uint8(f)
                nal_unit_type = array_info & 0x3F
                num_nalus = _read_uint16(f)
                if num_nalus is None:
                    continue
                for _ in range(num_nalus):
                    nal_unit_len = _read_uint16(f)
                    if nal_unit_len is None:
                        continue
                    if nal_unit_type == 33 and sps_payload is None:  # NAL_UNIT_SPS
                        sps_payload = f.read(nal_unit_len)
                    else:
                        f.seek(nal_unit_len, 1)

            if sps_payload is None:
                return None

            unescaped_sps = MP4BoxParser._unescape_nal_payload(sps_payload)
            reader = BitReader(unescaped_sps)

            reader.read_bits(16)  # Skip NAL Unit Header
            reader.read_bits(4)
            sps_max_sub_layers_minus1 = reader.read_bits(3)
            reader.read_bit()

            reader.read_bits(2)
            reader.read_bit()
            profile_idc = reader.read_bits(5)
            details["profile"] = _HEVC_PROFILE_MAP.get(
                profile_idc, str(profile_idc)
            )
            reader.read_bits(32)
            reader.read_bits(48)

            level_idc = reader.read_bits(8)
            level = level_idc / 30.0 if level_idc > 0 else None

            if details["profile"] and level is not None:
                details["profile_level"] = f"{level:.1f}"

            if sps_max_sub_layers_minus1 > 0:
                sub_layer_profile_present_flag = []
                sub_layer_level_present_flag = []
                for _ in range(sps_max_sub_layers_minus1):
                    sub_layer_profile_present_flag.append(reader.read_bit())
                    sub_layer_level_present_flag.append(reader.read_bit())
                for _ in range(sps_max_sub_layers_minus1, 8):
                    reader.read_bits(2)
                for i in range(sps_max_sub_layers_minus1):
                    if sub_layer_profile_present_flag[i]:
                        reader.read_bits(88)
                    if sub_layer_level_present_flag[i]:
                        reader.read_bits(8)

            reader.read_ue()
            chroma_format_idc = reader.read_ue()
            if chroma_format_idc == 3:
                reader.read_bit()

            reader.read_ue()
            reader.read_ue()
            if reader.read_bit():
                reader.read_ue()
                reader.read_ue()
                reader.read_ue()
                reader.read_ue()

            bit_depth = reader.read_ue() + 8
            reader.read_ue()
            reader.read_ue()

            sps_sub_layer_ordering_info_present_flag = reader.read_bit()
            start_idx = (
                0
                if sps_sub_layer_ordering_info_present_flag
                else sps_max_sub_layers_minus1
            )
            for _ in range(start_idx, sps_max_sub_layers_minus1 + 1):
                reader.read_ue()
                reader.read_ue()
                reader.read_ue()

            reader.read_ue()
            reader.read_ue()
            reader.read_ue()
            reader.read_ue()
            reader.read_ue()
            reader.read_ue()

            if reader.read_bit():
                if reader.read_bit():
                    for size_id in range(4):
                        for matrix_id in range(6 if size_id < 3 else 2):
                            if not reader.read_bit():
                                reader.read_ue()
                            else:
                                num_coeffs = min(64, (1 << (4 + (size_id << 1))))
                                if size_id > 1:
                                    reader.read_se()
                                for _ in range(num_coeffs):
                                    reader.read_se()
            reader.read_bit()
            reader.read_bit()

            if reader.read_bit():
                reader.read_bits(8)
                reader.read_ue()
                reader.read_ue()
                reader.read_bit()

            num_short_term_ref_pic_sets = reader.read_ue()
            for i in range(num_short_term_ref_pic_sets):
                if i != 0 and reader.read_bit():
                    logger.debug(
                        "Unsupported SPS: inter_ref_pic_set_prediction is not supported."
                    )
                    return details
                num_negative_pics = reader.read_ue()
                num_positive_pics = reader.read_ue()
                for _ in range(num_negative_pics):
                    reader.read_ue()
                    reader.read_bit()
                for _ in range(num_positive_pics):
                    reader.read_ue()
                    reader.read_bit()

            if reader.read_bit():
                for _ in range(reader.read_ue()):
                    reader.read_ue()
                    reader.read_bit()

            reader.read_bit()
            reader.read_bit()

            if reader.read_bit():
                if reader.read_bit():
                    if reader.read_bits(8) == 255:
                        reader.read_bits(32)
                if reader.read_bit():
                    reader.read_bit()
                if reader.read_bit():
                    reader.read_bits(3)
                    reader.read_bit()
                    if reader.read_bit():
                        reader.read_bits(24)
                if reader.read_bit():
                    top_val = reader.read_ue()
                    bottom_val = reader.read_ue()
                    top_str = _CHROMA_LOCATION_MAP.get(top_val, str(top_val))
                    bottom_str = _CHROMA_LOCATION_MAP.get(bottom_val, str(bottom_val))
                    details["chroma_location"] = (
                        top_str if top_str == bottom_str else f"{top_str}/{bottom_str}"
                    )

            if details["chroma_location"] is None and chroma_format_idc == 1:
                details["chroma_location"] = "left"

            pix_fmt_map = {0: "gray", 1: "yuv420p", 2: "yuv422p", 3: "yuv444p"}
            pix_fmt_base = pix_fmt_map.get(chroma_format_idc)
            if pix_fmt_base:
                details["pixel_format"] = (
                    f"{pix_fmt_base}{bit_depth}le" if bit_depth > 8 else pix_fmt_base
                )
            return details

        except (IndexError, struct.error) as e:
            logger.debug(f"Error parsing hvcC box: {e}")
            return None
        finally:
            f.seek(box_end)

    @staticmethod
    def _parse_av1C(f: BinaryIO, box_end: int) -> Optional[Dict[str, Any]]:
        """Parses an 'av1C' box to determine the profile, profile_level, pixel format, and chroma location."""
        details: Dict[str, Any] = {
            "pixel_format": None,
            "profile": None,
            "profile_level": None,
            "chroma_location": None,
        }
        av1c_start = f.tell()
        try:
            av1c_data = f.read(box_end - av1c_start)
            if len(av1c_data) < 4:
                return None

            reader = BitReader(av1c_data)
            reader.read_bits(1)  # marker (1)
            reader.read_bits(7)  # version (7)

            seq_profile = reader.read_bits(3)
            seq_level_idx_0 = reader.read_bits(5)
            seq_tier_0 = reader.read_bits(1)

            high_bitdepth = reader.read_bits(1)
            twelve_bit = reader.read_bits(1)
            mono_chrome = reader.read_bits(1)
            chroma_subsampling_x = reader.read_bits(1)
            chroma_subsampling_y = reader.read_bits(1)
            chroma_sample_position = reader.read_bits(2)

            details["profile"] = _AV1_PROFILE_MAP.get(
                seq_profile, str(seq_profile)
            )

            major = (seq_level_idx_0 >> 2) + 2
            minor = seq_level_idx_0 & 3
            level = float(f"{major}.{minor}")

            if details["profile"]:
                tier_str = " (High)" if seq_tier_0 == 1 else ""
                details["profile_level"] = f"{level:.1f}{tier_str}"

            bit_depth = 8
            if high_bitdepth:
                bit_depth = 12 if twelve_bit else 10

            if mono_chrome:
                pix_fmt_base = "gray"
            else:
                if chroma_subsampling_x == 1 and chroma_subsampling_y == 1:
                    pix_fmt_base = "yuv420p"
                elif chroma_subsampling_x == 1 and chroma_subsampling_y == 0:
                    pix_fmt_base = "yuv422p"
                elif chroma_subsampling_x == 0 and chroma_subsampling_y == 0:
                    pix_fmt_base = "yuv444p"
                else:
                    pix_fmt_base = None

            if pix_fmt_base:
                details["pixel_format"] = (
                    f"{pix_fmt_base}{bit_depth}le" if bit_depth > 8 else pix_fmt_base
                )

            details["chroma_location"] = _AV1_CHROMA_LOCATION_MAP.get(
                chroma_sample_position, "unspecified"
            )

            return details
        except (IndexError, struct.error):
            return None
        finally:
            f.seek(box_end)

    @staticmethod
    def _parse_vpc_config(f: BinaryIO, box_end: int) -> Dict[str, Any]:
        """
        Parses a VP9 configuration box ('vpcC') to extract codec metadata.
        This parser handles the mandatory profile and optional extended fields for
        level, bit depth, chroma subsampling, and color information.
        """
        config: Dict[str, Any] = {}
        vpcc_start = f.tell()
        try:
            # A 'vpcC' box must contain at least the 1-byte profile.
            if box_end - vpcc_start < 1:
                logger.warning("Invalid 'vpcC' box size: too small.")
                return {}

            profile = _read_uint8(f)
            if profile is None:
                return {}
            config["profile"] = _VP9_PROFILE_MAP.get(profile, str(profile))

            # The presence of at least 5 more bytes indicates the extended configuration.
            if box_end - f.tell() >= 5:
                level = _read_uint8(f)
                if level is not None:
                    # Level is stored as an integer (e.g., 21 for level 2.1).
                    config["profile_level"] = f"{level / 10.0:.1f}"

                packed_byte = _read_uint8(f)
                if packed_byte is not None:
                    # Bits 4-7: bitDepth
                    config["bit_depth"] = (packed_byte >> 4) & 0x0F
                    # Bits 1-3: chromaSubsampling
                    config["chroma_subsampling"] = (packed_byte >> 1) & 0x07

                config["color_primaries"] = _read_uint8(f)
                config["transfer_characteristics"] = _read_uint8(f)
                config["matrix_coefficients"] = _read_uint8(f)
            else:
                # Infer details from profile if extended fields are absent.
                # Profile 2 is 10-bit; others are 8-bit.
                config["bit_depth"] = 10 if profile == 2 else 8
                config["chroma_subsampling"] = 0  # Assume 4:2:0

            # Chroma location is typically 'left' (co-sited) for 4:2:0 video.
            if config.get("chroma_subsampling") == 0:  # 0 indicates 4:2:0
                config["chroma_location"] = "left"
            else:
                config["chroma_location"] = "unspecified"

            return config
        except (IOError, struct.error) as e:
            # A warning is appropriate as malformed data can occur in practice.
            logger.warning(f"Could not parse 'vpcC' box due to an error: {e}")
            return {}
        finally:
            # Ensure the stream position is advanced to the end of the box.
            f.seek(box_end)

    @staticmethod
    def parse_tkhd(f: BinaryIO, box_end: int) -> Optional[int]:
        """Parses 'tkhd' box to get index."""
        version = _read_uint8(f)
        f.read(3)
        if version == 1:
            f.read(16)
            index = _read_uint32(f)
        elif version == 0:
            f.read(8)
            index = _read_uint32(f)
        else:
            index = None
        f.seek(box_end)
        return index

    @staticmethod
    def parse_mvhd(f: BinaryIO, box_end: int) -> Dict[str, Any]:
        """Parses 'mvhd' box to get the overall movie duration and timescale."""
        details = {"timescale": None, "duration": None}
        version = _read_uint8(f)
        f.read(3)
        if version == 1:
            f.read(16)
            details["timescale"] = _read_uint32(f)
            details["duration"] = _read_uint64(f)
        elif version == 0:
            f.read(8)
            details["timescale"] = _read_uint32(f)
            details["duration"] = _read_uint32(f)

        f.seek(box_end)
        return details

    @staticmethod
    def parse_mdhd(f: BinaryIO, box_end: int) -> Dict[str, Any]:
        """Parses 'mdhd' box to get timescale, duration, and language code."""
        details = {"timescale": None, "duration": None, "lang": "und"}
        version = _read_uint8(f)
        f.read(3)
        if version == 1:
            f.read(16)
            details["timescale"] = _read_uint32(f)
            details["duration"] = _read_uint64(f)
        elif version == 0:
            f.read(8)
            details["timescale"] = _read_uint32(f)
            details["duration"] = _read_uint32(f)
        else:
            f.seek(box_end)
            return details

        lang_and_quality = _read_uint16(f)
        if lang_and_quality is not None:
            details["lang"] = _decode_qt_language_code(lang_and_quality & 0x7FFF)
        f.seek(box_end)
        return details

    @staticmethod
    def parse_hdlr(f: BinaryIO, box_end: int) -> Dict[str, Any]:
        """Parses 'hdlr' box to get handler_type and handler_name."""
        f.read(8)
        handler_type = f.read(4)
        f.read(12)
        name_data = f.read(box_end - f.tell())
        handler_name = (
            name_data.decode("utf-8", errors="replace").rstrip("\x00").strip()
        )
        f.seek(box_end)
        return {"type": handler_type, "name": handler_name}

    @staticmethod
    def parse_elng(f: BinaryIO, box_end: int) -> Optional[str]:
        """Parses 'elng' box for extended language tag."""
        f.seek(4, 1)
        raw_data = f.read(box_end - f.tell())
        text = raw_data.decode("utf-8", errors="replace").split("\x00", 1)[0].strip()
        return text if text else None

    @staticmethod
    def parse_udta(
            f: BinaryIO, udta_end: int
    ) -> tuple[_TrackCharacteristics, Optional[str]]:
        """
        Parses 'udta' box for 'tagc' boxes (track characteristics) and
        a descriptive track name ('©nam', 'name', 'titl').
        Returns a tuple containing the characteristics flags and the track name if found.
        """
        flags = MP4BoxParser._TrackCharacteristics()
        name: Optional[str] = None
        current_pos = f.tell()

        while current_pos < udta_end:
            f.seek(current_pos)
            box_type, _, box_start, box_end = _read_box_header(f)
            if not box_type or box_end > udta_end:
                break

            if box_type == b"tagc":
                tagc_str = (
                    f.read(box_end - f.tell()).decode("utf-8", errors="replace").strip()
                )
                flags.update_from_tagc_value(tagc_str)
            elif box_type in (b"\xa9nam", b"name", b"titl") and name is None:
                f.seek(box_start + 8)
                potential_name = MP4BoxParser.parse_qtss(f, box_end)
                if potential_name:
                    name = potential_name

            current_pos = box_end

        f.seek(udta_end)
        return flags, name

    @staticmethod
    def parse_qtss(f: BinaryIO, box_end: int) -> Optional[str]:
        """Parses a QuickTime-style string metadata atom."""
        current_pos = f.tell()
        if box_end - current_pos >= 4:
            peek_byte = f.read(1)
            f.seek(current_pos)
            if peek_byte == b"\x00":
                f.read(4)
                current_pos = f.tell()

        string_data_length = box_end - current_pos
        if string_data_length <= 0:
            return None

        raw_string_data = f.read(string_data_length)
        decoded_string = (
            raw_string_data.decode("utf-8", errors="replace")
            .split("\x00", 1)[0]
            .strip()
        )
        return decoded_string if decoded_string else None

    @staticmethod
    def parse_itunes_data(
            f: BinaryIO, box_end: int, item_type: bytes
    ) -> Union[str, int, None]:
        """
        Parses the 'data' atom within an iTunes-style metadata item ('ilst').
        It uses the item_type to correctly distinguish between simple integers
        and composite "X of Y" numbers (track_number, disc_number).
        """
        data_start = f.tell()
        if box_end - data_start < 8:
            f.seek(box_end)
            return None

        value_format_indicator = _read_uint32(f)
        f.read(4)  # Skip 4 bytes of unknown purpose

        data_length = box_end - f.tell()
        if data_length < 0:
            f.seek(box_end)
            return None

        raw_data = f.read(data_length)
        f.seek(box_end)

        if not raw_data:
            return None

        try:
            if value_format_indicator == 1:  # UTF-8 String
                return raw_data.decode("utf-8", "replace").strip("\x00").strip()

            if item_type in (b"trkn", b"disk"):
                if len(raw_data) >= 4 and len(raw_data) <= 8:
                    current_num = (
                        int.from_bytes(raw_data[2:4], "big")
                        if len(raw_data) >= 4
                        else None
                    )
                    total_num = (
                        int.from_bytes(raw_data[4:6], "big")
                        if len(raw_data) >= 6
                        else None
                    )
                    if (
                            current_num is not None
                            and total_num is not None
                            and total_num > 0
                    ):
                        return f"{current_num}/{total_num}"
                    elif current_num is not None:
                        return str(current_num)
                return int.from_bytes(raw_data, "big", signed=True)

            if value_format_indicator in (0, 65, 74, 75, 76):
                return int.from_bytes(raw_data, "big", signed=False)
            elif value_format_indicator in (21, 22, 23, 24):
                return int.from_bytes(raw_data, "big", signed=True)
            else:
                logger.debug(
                    f"Unsupported iTunes data format indicator: {value_format_indicator}"
                )
                return None
        except Exception as e:
            logger.error(
                f"Error decoding iTunes data (type {value_format_indicator}, len {len(raw_data)}): {e}"
            )
            return None

    @staticmethod
    def _get_image_dimensions(
            image_data: bytes, mime_type: str
    ) -> Optional[Tuple[int, int]]:
        """
        Safely extracts image dimensions from raw image data without full decoding.
        Supports JPEG and PNG.
        """
        if not image_data:
            return None

        if mime_type == "image/jpeg":
            # JPEG: Find the Start of Frame marker (0xFFC0, 0xFFC1, 0xFFC2, or 0xFFC3)
            # and read the 16-bit height and width fields.
            try:
                data_stream = io.BytesIO(image_data)
                while True:
                    marker_byte = data_stream.read(1)
                    if not marker_byte:
                        break
                    if marker_byte == b"\xff":
                        marker = data_stream.read(1)
                        if marker in (b"\xc0", b"\xc1", b"\xc2", b"\xc3"):
                            data_stream.read(3)  # Skip length and precision
                            height = struct.unpack(">H", data_stream.read(2))[0]
                            width = struct.unpack(">H", data_stream.read(2))[0]
                            return width, height
                        elif marker == b"\xd9":  # End of Image
                            break
            except (IOError, struct.error) as e:
                logger.debug(f"Failed to parse JPEG dimensions: {e}")
            return None

        elif mime_type == "image/png":
            # PNG: The IHDR chunk contains the width and height at fixed offsets.
            # IHDR is always the first chunk after the 8-byte signature.
            if len(image_data) > 24 and image_data[12:16] == b"IHDR":
                try:
                    width = struct.unpack(">I", image_data[16:20])[0]
                    height = struct.unpack(">I", image_data[20:24])[0]
                    return width, height
                except struct.error as e:
                    logger.debug(f"Failed to parse PNG dimensions: {e}")
            return None

        return None

    @staticmethod
    def parse_ilst(
            f: BinaryIO, ilst_end: int
    ) -> Dict[str, Union[str, int, Dict[str, Any], None]]:
        """
        Parses the 'ilst' (item list) atom, which contains individual metadata items.
        It maps common iTunes metadata keys, processes them, and now parses embedded
        XML plists for rich movie metadata, skipping any truncated entries.
        """
        parsed_data: Dict[str, Union[str, int, Dict[str, Any], None]] = {}
        has_cover_art = False
        current_pos = f.tell()

        key_map = {
            b"\xa9nam": "title",
            b"\xa9ART": "artist",
            b"\xa9alb": "album",
            b"\xa9cmt": "comment",
            b"\xa9day": "release_date",
            b"\xa9gen": "genre",
            b"\xa9too": "encoder",
            b"\xa9wrt": "composer",
            b"trkn": "track_number",
            b"disk": "disc_number",
            b"gnre": "genre_id",
            b"covr": "cover_art",
            b"rtng": "itunesadvisory",
            b"cpil": "compilation",
            b"pgap": "gapless_playback",
            b"shwm": "show_name",
            b"eply": "episode_id",
            b"tvsn": "tv_season",
            b"tves": "tv_episode_number",
            b"tven": "tv_episode_id",
            b"desc": "description",
            b"ldes": "long_description",
            b"sdes": "series_description",
            b"pcst": "podcast",
            b"purl": "podcast_url",
            b"egid": "episode_guid",
            b"keyw": "keywords",
            b"catg": "category",
            b"hdvd": "hd_video",
            b"stik": "media_type",
            b"purd": "purchase_date",
            b"cprt": "copyright",
            b"akID": "apple_store_id",
            b"cnID": "content_id",
            b"geid": "genre_id_2",
            b"plID": "playlist_id",
            b"atID": "artist_id",
            b"alID": "album_id",
            b"cmID": "composer_id",
            b"xid ": "external_id",
            b"soal": "sort_album",
            b"soar": "sort_artist",
            b"soco": "sort_composer",
            b"sonm": "sort_name",
            b"sosn": "sort_show",
            b"sotp": "sort_title",
            b"aART": "album_artist",
            b"\xa9grp": "grouping",
            b"tmpo": "tempo",
            b"tvnn": "tv_network",
            b"stvd": "studio",
            b"cast": "cast",
            b"dirc": "directors",
            b"codr": "codirector",
            b"prod": "producers",
            b"exec": "executive_producer",
            b"swnm": "screenwriters",
            b"\xa9lyr": "lyrics",
            b"\xa9enc": "encoded_by",
            b"apID": "itunes_account",
            b"sfID": "itunes_country",
            b"ardr": "art_director",
            b"arrn": "arranger",
            b"\xa9aut": "lyricist",
            b"ackn": "acknowledgement",
            b"\xa9con": "conductor",
            b"\xa9lin": "linear_notes",
            b"\xa9mak": "record_company",
            b"\xa9ope": "original_artist",
            b"\xa9phg": "phonogram_rights",
            b"\xa9prd": "song_producer",
            b"perf": "performer",
            b"\xa9pub": "publisher",
            b"seng": "sound_engineer",
            b"solo": "soloist",
            b"crdt": "credits",
            b"\xa9wrk": "work_name",
            b"\xa9mvn": "movement_name",
            b"\xa9mvi": "movement_number",
            b"\xa9mvc": "movement_count",
            b"shwv": "show_work_and_movement",
            b"soaa": "sort_album_artist",
            b"tvsh": "tv_show_name",
            b"----": "content_rating",
            b"ownr": "owner",
        }

        while current_pos < ilst_end:
            f.seek(current_pos)
            item_type, _, item_start, item_end = _read_box_header(f)
            if not item_type or item_end > ilst_end:
                break

            key_name = key_map.get(
                item_type, item_type.decode("ascii", errors="replace").strip()
            )

            item_child_pos = item_start + 8
            while item_child_pos < item_end:
                f.seek(item_child_pos)
                data_type, _, data_start, data_end = _read_box_header(f)
                if not data_type or data_end > item_end:
                    break

                if data_type == b"data":
                    data_pos_before_read = f.tell()
                    value_format_indicator = _read_uint32(f)
                    f.read(4)

                    data_length = data_end - f.tell()
                    raw_data = f.read(data_length)

                    if item_type == b"covr":
                        if value_format_indicator in _COVER_ART_FORMAT_MAP:
                            has_cover_art = True
                            parsed_data["cover_art_mime"] = (
                                _COVER_ART_FORMAT_MAP.get(
                                    value_format_indicator
                                )
                            )
                            dimensions = MP4BoxParser._get_image_dimensions(
                                raw_data, parsed_data["cover_art_mime"]
                            )
                            if dimensions:
                                parsed_data["cover_art_dimensions"] = (
                                    f"{dimensions[0]}x{dimensions[1]}"
                                )
                        else:
                            has_cover_art = True
                            parsed_data["cover_art_mime"] = "application/octet-stream"
                        f.seek(data_end)
                        break

                    f.seek(data_pos_before_read)
                    parsed_value = MP4BoxParser.parse_itunes_data(
                        f, data_end, item_type
                    )

                    if parsed_value is not None:
                        if isinstance(
                                parsed_value, str
                        ) and parsed_value.strip().startswith("<?xml"):
                            try:
                                plist_data = plistlib.loads(
                                    parsed_value.encode("utf-8")
                                )
                                for plist_key, plist_value in plist_data.items():
                                    if plist_key in (
                                            "cast",
                                            "directors",
                                            "producers",
                                            "screenwriters",
                                    ) and isinstance(plist_value, list):
                                        simplified_list = [
                                            item.get("name")
                                            for item in plist_value
                                            if isinstance(item, dict)
                                               and item.get("name")
                                               and not item["name"].endswith("...")
                                        ]
                                        if simplified_list:
                                            parsed_data[plist_key] = simplified_list
                                    else:
                                        parsed_data[plist_key] = plist_value
                            except Exception as e:
                                logger.warning(
                                    f"Failed to parse XML plist data for '{key_name}': {e}"
                                )
                                parsed_data[key_name] = parsed_value
                        elif (
                                key_name in ("track_number", "disc_number")
                                and isinstance(parsed_value, str)
                                and "/" in parsed_value
                        ):
                            try:
                                num, total = map(int, parsed_value.split("/", 1))
                                parsed_data[key_name] = num
                                parsed_data[key_name.replace("_number", "_total")] = (
                                    str(total)
                                )
                            except (ValueError, TypeError):
                                parsed_data[key_name] = parsed_value
                        elif key_name == "hd_video" and isinstance(parsed_value, int):
                            parsed_data[key_name] = bool(parsed_value)
                            hd_map = {3: "2160p UHD", 2: "1080p HD", 1: "720p HD"}
                            parsed_data["hd_video_definition"] = hd_map.get(
                                parsed_value, "SD"
                            )
                            parsed_data["hd_video_definition_level"] = parsed_value
                        elif key_name == "content_rating" and isinstance(
                                parsed_value, str
                        ):
                            parts = parsed_value.split("|")
                            if len(parts) >= 3:
                                system = parts[0] if parts[0] else None
                                label = parts[1] if parts[1] else None
                                parsed_data["rating_system"] = system
                                parsed_data["rating_label"] = label
                                if system and label:
                                    parsed_data["rating_age_classification"] = (
                                        get_age_classification(system, label)
                                    )

                                try:
                                    rating_unit = int(parts[2])
                                    parsed_data["rating_unit"] = rating_unit
                                    flag_map = {
                                        400: "1080p HD",
                                        300: "720p HD",
                                        200: "SD",
                                    }
                                    if rating_unit in flag_map:
                                        parsed_data["hd_video_definition"] = flag_map[
                                            rating_unit
                                        ]
                                        # Map rating_unit to hdvd-style levels for consistency
                                        level_map = {400: 2, 300: 1, 200: 0}
                                        parsed_data["hd_video_definition_level"] = (
                                            level_map.get(rating_unit)
                                        )
                                except (ValueError, IndexError):
                                    parsed_data["rating_unit"] = None
                            else:
                                parsed_data[key_name] = parsed_value
                        elif key_name == "itunesadvisory" and isinstance(
                                parsed_value, int
                        ):
                            if parsed_value in (0, 2):
                                parsed_data[key_name] = "0"
                            elif parsed_value in (1, 4):
                                parsed_data[key_name] = "1"
                            else:
                                parsed_data[key_name] = str(parsed_value)
                        elif key_name in (
                                "compilation",
                                "gapless_playback",
                                "podcast",
                        ) and isinstance(parsed_value, int):
                            parsed_data[key_name] = bool(parsed_value)
                        else:
                            parsed_data[key_name] = parsed_value
                    break
                item_child_pos = data_end
            current_pos = item_end

        if has_cover_art:
            parsed_data["has_cover_art"] = True

        metadata = {}
        output_order = [
            "title",
            "artist",
            "album",
            "album_artist",
            "track_number",
            "track_total",
            "disc_number",
            "disc_total",
            "genre",
            "release_date",
            "duration_seconds",
            "tempo",
            "publisher",
            "record_company",
            "copyright",
            "isrc",
            "barcode",
            "upc",
            "media_type",
            "itunesadvisory",
            "rating_system",
            "rating_label",
            "rating_age_classification",
            "rating_unit",
            "lyrics",
            "comment",
            "grouping",
            "keywords",
            "description",
            "long_description",
            "series_description",
            "has_cover_art",
            "cover_art_mime",
            "cover_art_dimensions",
            "encoder",
            "encoded_by",
            "language",
            "compilation",
            "gapless_playback",
            "podcast",
            "category",
            "tv_show_name",
            "tv_episode_id",
            "tv_season",
            "tv_episode_number",
            "tv_network",
            "hd_video",
            "hd_video_definition",
            "hd_video_definition_level",
            "studio",
            "content_id",
            "composer",
            "performer",
            "directors",
            "producers",
            "screenwriters",
            "cast",
            "owner",
        ]

        for key in output_order:
            if key in parsed_data:
                metadata[key] = parsed_data.pop(key)

        metadata.update(parsed_data)

        if "media_type" in metadata and metadata["media_type"] == 1:
            metadata.pop("hd_video", None)
            metadata.pop("hd_video_definition", None)
            metadata.pop("hd_video_definition_level", None)
            if "itunesadvisory" not in metadata:
                metadata["itunesadvisory"] = 0
            metadata.pop("content_rating", None)

        f.seek(ilst_end)
        return metadata

    @staticmethod
    def parse_meta(
            f: BinaryIO, meta_end: int
    ) -> Dict[str, Union[str, int, Dict[str, Any], None]]:
        """
        Parses a 'meta' box for general file-level metadata.
        This box often contains an 'ilst' box for iTunes-style metadata.
        """
        metadata: Dict[str, Union[str, int, Dict[str, Any], None]] = {}
        meta_start = f.tell()
        if meta_end - meta_start < 4:
            f.seek(meta_end)
            return metadata

        f.read(4)
        current_pos = f.tell()

        hdlr_parsed = False
        if current_pos < meta_end:
            f.seek(current_pos)
            hdlr_type, hdlr_size, _, hdlr_end = _read_box_header(f)
            if hdlr_type == b"hdlr":
                MP4BoxParser.parse_hdlr(f, hdlr_end)
                hdlr_parsed = True
                current_pos = hdlr_end
            else:
                current_pos += hdlr_size if hdlr_size > 0 else 8

        if not hdlr_parsed:
            logger.warning("No 'hdlr' box found as first child of 'meta'.")

        while current_pos < meta_end:
            f.seek(current_pos)
            box_type, _, _, box_end = _read_box_header(f)
            if not box_type or box_end > meta_end:
                break
            if box_type == b"ilst":
                ilst_metadata = MP4BoxParser.parse_ilst(f, box_end)
                metadata.update(ilst_metadata)
            current_pos = box_end
        f.seek(meta_end)
        return metadata

    @staticmethod
    def parse_stsd_subtitle(
            f: BinaryIO, stsd_end: int
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        name: Optional[str] = None

        # Skip version (1), flags (3), and number of entries (4).
        f.read(8)
        if f.tell() >= stsd_end:
            f.seek(stsd_end)
            return None, None, None

        # Now we are at the beginning of the first sample entry.
        entry_type, _, entry_start, entry_end = _read_box_header(f)
        if not entry_type or entry_end > stsd_end:
            f.seek(stsd_end)
            return None, None, None

        codec_tag = entry_type.decode("ascii", errors="replace")
        codec = codec_tag
        codec_tag_string = _SUBTITLE_CODEC_MAP.get(codec_tag, codec_tag)

        # Look for a descriptive name inside this sample entry.
        if entry_type in (b"tx3g", b"mp4s", b"subp", b"clcp", b"text", b"c608"):
            current_child_pos = f.tell()
            while current_child_pos < entry_end:
                if entry_end - current_child_pos < 8:
                    break
                f.seek(current_child_pos)
                child_type, _, child_start, child_end = _read_box_header(f)
                if not child_type or child_end > entry_end:
                    break

                if child_type in (
                        b"\xa9nam",
                        b"name",
                        b"titl",
                        b"desc",
                        b"drmi",
                        b"text",
                        b"kind",
                        b"uri ",
                ):
                    f.seek(child_start + 8)
                    potential_name = MP4BoxParser.parse_qtss(f, child_end)
                    if potential_name:
                        name = potential_name
                        break
                current_child_pos = child_end

        f.seek(stsd_end)
        return codec, codec_tag_string, name

    @staticmethod
    def parse_stsd_audio(f: BinaryIO, stsd_end: int) -> Dict[str, Any]:
        """Parses 'stsd' for audio track details."""
        audio_details = {
            "codec": "unknown",
            "codec_tag_string": "unknown",
            "channels": 0,
            "sample_rate": 0,
        }
        channel_layout = None
        f.seek(8, 1)
        if f.tell() >= stsd_end:
            return audio_details

        entry_type, _, entry_start, entry_end = _read_box_header(f)
        if not entry_type:
            return audio_details

        codec_tag = entry_type.decode("ascii", errors="replace")
        audio_details["codec_tag_string"] = codec_tag
        audio_details["codec"] = _AUDIO_CODEC_MAP.get(codec_tag, codec_tag)

        f.seek(entry_start + 8)
        f.read(16)
        audio_details["channels"] = _read_uint16(f)
        audio_details["bits_per_sample"] = _read_uint16(f)
        f.read(4)
        sr = _read_uint32(f)
        if sr:
            audio_details["sample_rate"] = sr >> 16

        current_pos = f.tell()
        while current_pos < entry_end:
            f.seek(current_pos)
            child_type, _, child_start, child_end = _read_box_header(f)
            if not child_type or child_end > entry_end:
                break

            if child_type == b"esds":
                f.seek(child_start + 8 + 4)
                if _read_uint8(f) == 0x03:
                    MP4BoxParser._read_mp4_descriptor_length(f)
                    f.read(3)
                    if _read_uint8(f) == 0x04:
                        MP4BoxParser._read_mp4_descriptor_length(f)
                        f.read(13)
                        if _read_uint8(f) == 0x05:
                            if MP4BoxParser._read_mp4_descriptor_length(f) >= 2:
                                asc_data = f.read(2)
                                reader = BitReader(asc_data)
                                reader.read_bits(9)
                                channel_config = reader.read_bits(4)
                                channel_map = {
                                    1: (1, "1.0"), 2: (2, "2.0"), 3: (3, "3.0"),
                                    4: (4, "4.0"), 5: (5, "5.0"), 6: (6, "5.1"),
                                    7: (8, "7.1"),
                                }
                                if channel_config in channel_map:
                                    count, layout = channel_map[channel_config]
                                    audio_details["channels"] = count
                                    channel_layout = layout
                break

            elif child_type == b"dac3":
                f.read(1)
                bits = _read_uint8(f)
                if bits is not None:
                    acmod = (bits >> 3) & 0x07
                    lfeon = (bits >> 2) & 0x01
                    main_channels = {0: 2, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5}.get(acmod, 0)
                    audio_details["channels"] = main_channels + lfeon
                    channel_layout = "1+1" if acmod == 0 else f"{main_channels}.{lfeon}"
                break

            elif child_type == b"dec3":
                payload_start_pos = f.tell()
                payload = f.read(child_end - payload_start_pos)

                # Initialize dolby_atmos field for all E-AC-3 tracks.
                audio_details["dolby_atmos"] = False
                # If payload is > 5 bytes, it contains JOC data, so we set it to True.
                if len(payload) > 5:
                    audio_details["dolby_atmos"] = True

                f.seek(payload_start_pos)

                if audio_details.get("channels") == 8:
                    channel_layout = "7.1"

                f.read(2)
                if child_end - f.tell() >= 3:
                    f.seek(1, 1)
                    bits = _read_uint8(f)
                    if bits is not None:
                        acmod = (bits >> 1) & 0x07
                        lfeon = bits & 0x01
                        main_channels = {0: 2, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5}.get(acmod, 0)
                        audio_details["channels"] = main_channels + lfeon
                        channel_layout = "1+1" if acmod == 0 else f"{main_channels}.{lfeon}"
                break

            current_pos = child_end

        if channel_layout:
            audio_details["channel_layout"] = channel_layout

        f.seek(stsd_end)
        return audio_details

    @staticmethod
    def _parse_mdcv(f: BinaryIO, box_end: int) -> Optional[Dict[str, Any]]:
        """Parse Mastering Display Color Volume box for HDR metadata."""
        try:
            mdcv_data = {}
            # Read display primaries (G, B, R order) - each is 2 uint16 values (x, y)
            for color in ['red', 'green', 'blue']:
                x = _read_uint16(f)
                y = _read_uint16(f)
                if x is not None and y is not None:
                    mdcv_data[f"primary_{color[0]}"] = f"({x / 50000:.4f}, {y / 50000:.4f})"

            # White point
            wx = _read_uint16(f)
            wy = _read_uint16(f)
            if wx is not None and wy is not None:
                mdcv_data["white_point"] = f"({wx / 50000:.4f}, {wy / 50000:.4f})"

            # Luminance values
            max_lum = _read_uint32(f)
            min_lum = _read_uint32(f)
            if max_lum is not None:
                mdcv_data["max_luminance"] = f"{max_lum / 10000:.4f} cd/m²"
            if min_lum is not None:
                mdcv_data["min_luminance"] = f"{min_lum / 10000:.4f} cd/m²"

            return mdcv_data
        except:
            return None
        finally:
            f.seek(box_end)

    @staticmethod
    def _parse_clli(f: BinaryIO, box_end: int) -> Optional[Dict[str, Any]]:
        """Parse Content Light Level Information box for HDR metadata."""
        try:
            clli_data = {}
            max_cll = _read_uint16(f)
            max_fall = _read_uint16(f)
            if max_cll is not None:
                clli_data["max_cll"] = f"{max_cll} cd/m²"
            if max_fall is not None:
                clli_data["max_fall"] = f"{max_fall} cd/m²"
            return clli_data
        except:
            return None
        finally:
            f.seek(box_end)

    @staticmethod
    def _parse_hevc_sei_hdr(sei_payload: bytes, payload_type: int) -> Optional[Dict[str, Any]]:
        """Parse HEVC SEI HDR10 metadata (type 137 = mdcv, type 144 = clli)."""
        try:
            hdr_info = {}

            # Mastering Display Color Volume (SEI type 137)
            if payload_type == 137 and len(sei_payload) >= 24:
                offset = 0
                # Display primaries in GBR order
                for color in ['g', 'b', 'r']:
                    x = struct.unpack('>H', sei_payload[offset:offset + 2])[0]
                    y = struct.unpack('>H', sei_payload[offset + 2:offset + 4])[0]
                    hdr_info[f"primary_{color}"] = f"({x / 50000:.4f}, {y / 50000:.4f})"
                    offset += 4

                # White point
                wx = struct.unpack('>H', sei_payload[offset:offset + 2])[0]
                wy = struct.unpack('>H', sei_payload[offset + 2:offset + 4])[0]
                hdr_info["white_point"] = f"({wx / 50000:.4f}, {wy / 50000:.4f})"
                offset += 4

                # Luminance
                max_lum = struct.unpack('>I', sei_payload[offset:offset + 4])[0]
                min_lum = struct.unpack('>I', sei_payload[offset + 4:offset + 8])[0]
                hdr_info["max_luminance"] = f"{max_lum / 10000:.4f} cd/m²"
                hdr_info["min_luminance"] = f"{min_lum / 10000:.4f} cd/m²"

            # Content Light Level (SEI type 144)
            elif payload_type == 144 and len(sei_payload) >= 4:
                max_cll = struct.unpack('>H', sei_payload[0:2])[0]
                max_fall = struct.unpack('>H', sei_payload[2:4])[0]
                hdr_info["max_cll"] = f"{max_cll} cd/m²"
                hdr_info["max_fall"] = f"{max_fall} cd/m²"

            return hdr_info if hdr_info else None
        except Exception as e:
            logger.debug(f"Error parsing SEI HDR: {e}")
            return None

    @staticmethod
    def _extract_hdr_from_hevc_bitstream(sample_data: bytes) -> Optional[Dict[str, Any]]:
        """Extract HDR metadata AND profile/pixel_format/chroma_location from HEVC bitstream."""
        try:
            offset = 0
            hdr_metadata = {}

            # Parse NAL units (MP4 format uses 4-byte length prefix)
            while offset < len(sample_data) - 4:
                # Read NAL length
                nal_length = struct.unpack('>I', sample_data[offset:offset + 4])[0]
                offset += 4

                if nal_length == 0 or offset + nal_length > len(sample_data):
                    break

                nal_data = sample_data[offset:offset + nal_length]

                if len(nal_data) >= 2:
                    # Parse HEVC NAL header (2 bytes)
                    nal_header = struct.unpack('>H', nal_data[0:2])[0]
                    nal_type = (nal_header >> 9) & 0x3F

                    # SPS NAL unit (33) - Extract profile, pixel format, chroma location
                    if nal_type == 33:
                        logger.debug("Found SPS NAL unit, parsing for profile/pixel_format/chroma_location")
                        try:
                            unescaped_sps = MP4BoxParser._unescape_nal_payload(nal_data)
                            reader = BitReader(unescaped_sps)

                            # Skip NAL header (16 bits)
                            reader.read_bits(16)

                            # sps_video_parameter_set_id (4 bits)
                            reader.read_bits(4)
                            # sps_max_sub_layers_minus1 (3 bits)
                            sps_max_sub_layers_minus1 = reader.read_bits(3)
                            # sps_temporal_id_nesting_flag (1 bit)
                            reader.read_bit()

                            # profile_tier_level
                            reader.read_bits(2)  # general_profile_space
                            reader.read_bit()  # general_tier_flag
                            profile_idc = reader.read_bits(5)  # general_profile_idc
                            hdr_metadata["profile"] = _HEVC_PROFILE_MAP.get(profile_idc, str(profile_idc))

                            reader.read_bits(32)  # general_profile_compatibility_flags
                            reader.read_bits(48)  # general_constraint_indicator_flags
                            level_idc = reader.read_bits(8)  # general_level_idc

                            # Calculate level (level_idc / 30.0)
                            if level_idc > 0:
                                level = level_idc / 30.0
                                hdr_metadata["profile_level"] = f"{level:.1f}"
                                logger.debug(
                                    f"SPS profile_level: {hdr_metadata['profile_level']} (level_idc={level_idc})")

                            # Skip sub-layer info
                            if sps_max_sub_layers_minus1 > 0:
                                for _ in range(sps_max_sub_layers_minus1):
                                    reader.read_bit()  # sub_layer_profile_present_flag
                                    reader.read_bit()  # sub_layer_level_present_flag
                                for _ in range(sps_max_sub_layers_minus1, 8):
                                    reader.read_bits(2)  # reserved_zero_2bits

                            # sps_seq_parameter_set_id
                            reader.read_ue()

                            # chroma_format_idc
                            chroma_format_idc = reader.read_ue()
                            if chroma_format_idc == 3:
                                reader.read_bit()  # separate_colour_plane_flag

                            # pic_width_in_luma_samples
                            reader.read_ue()
                            # pic_height_in_luma_samples
                            reader.read_ue()

                            # conformance_window_flag
                            if reader.read_bit():
                                reader.read_ue()
                                reader.read_ue()
                                reader.read_ue()
                                reader.read_ue()

                            # bit_depth_luma_minus8
                            bit_depth = reader.read_ue() + 8
                            # bit_depth_chroma_minus8
                            reader.read_ue()

                            # Derive pixel format
                            pix_fmt_map = {0: "gray", 1: "yuv420p", 2: "yuv422p", 3: "yuv444p"}
                            pix_fmt_base = pix_fmt_map.get(chroma_format_idc)
                            if pix_fmt_base:
                                hdr_metadata["pixel_format"] = (
                                    f"{pix_fmt_base}{bit_depth}le" if bit_depth > 8 else pix_fmt_base
                                )

                            # Default chroma location for 4:2:0 (will be overridden if VUI specifies it)
                            if chroma_format_idc == 1:
                                hdr_metadata["chroma_location"] = "left"

                            # Parse through the rest of SPS to reach VUI
                            try:
                                # log2_max_pic_order_cnt_lsb_minus4
                                reader.read_ue()

                                # sps_sub_layer_ordering_info_present_flag
                                sps_sub_layer_ordering_info_present_flag = reader.read_bit()
                                start_idx = 0 if sps_sub_layer_ordering_info_present_flag else sps_max_sub_layers_minus1
                                for _ in range(start_idx, sps_max_sub_layers_minus1 + 1):
                                    reader.read_ue()  # sps_max_dec_pic_buffering_minus1
                                    reader.read_ue()  # sps_max_num_reorder_pics
                                    reader.read_ue()  # sps_max_latency_increase_plus1

                                # log2_min_luma_coding_block_size_minus3
                                reader.read_ue()
                                # log2_diff_max_min_luma_coding_block_size
                                reader.read_ue()
                                # log2_min_luma_transform_block_size_minus2
                                reader.read_ue()
                                # log2_diff_max_min_luma_transform_block_size
                                reader.read_ue()
                                # max_transform_hierarchy_depth_inter
                                reader.read_ue()
                                # max_transform_hierarchy_depth_intra
                                reader.read_ue()

                                # scaling_list_enabled_flag
                                if reader.read_bit():
                                    # sps_scaling_list_data_present_flag
                                    if reader.read_bit():
                                        # Skip scaling list data (complex, not needed for chroma location)
                                        pass

                                # amp_enabled_flag
                                reader.read_bit()
                                # sample_adaptive_offset_enabled_flag
                                reader.read_bit()
                                # pcm_enabled_flag
                                if reader.read_bit():
                                    reader.read_bits(4)  # pcm_sample_bit_depth_luma_minus1
                                    reader.read_bits(4)  # pcm_sample_bit_depth_chroma_minus1
                                    reader.read_ue()  # log2_min_pcm_luma_coding_block_size_minus3
                                    reader.read_ue()  # log2_diff_max_min_pcm_luma_coding_block_size
                                    reader.read_bit()  # pcm_loop_filter_disabled_flag

                                # num_short_term_ref_pic_sets
                                num_st_rps = reader.read_ue()
                                # Skip short term ref pic sets (too complex for now)
                                for i in range(num_st_rps):
                                    if i > 0 and reader.read_bit():
                                        # inter_ref_pic_set_prediction_flag - too complex, bail
                                        break
                                    num_negative_pics = reader.read_ue()
                                    num_positive_pics = reader.read_ue()
                                    for _ in range(num_negative_pics):
                                        reader.read_ue()
                                        reader.read_bit()
                                    for _ in range(num_positive_pics):
                                        reader.read_ue()
                                        reader.read_bit()

                                # long_term_ref_pics_present_flag
                                if reader.read_bit():
                                    num_long_term = reader.read_ue()
                                    for _ in range(num_long_term):
                                        reader.read_ue()
                                        reader.read_bit()

                                # sps_temporal_mvp_enabled_flag
                                reader.read_bit()
                                # strong_intra_smoothing_enabled_flag
                                reader.read_bit()

                                # vui_parameters_present_flag
                                if reader.read_bit():
                                    logger.debug("VUI parameters present, parsing for chroma location")
                                    # aspect_ratio_info_present_flag
                                    if reader.read_bit():
                                        aspect_ratio_idc = reader.read_bits(8)
                                        if aspect_ratio_idc == 255:  # EXTENDED_SAR
                                            reader.read_bits(16)  # sar_width
                                            reader.read_bits(16)  # sar_height

                                    # overscan_info_present_flag
                                    if reader.read_bit():
                                        reader.read_bit()  # overscan_appropriate_flag

                                    # video_signal_type_present_flag
                                    if reader.read_bit():
                                        reader.read_bits(3)  # video_format
                                        reader.read_bit()  # video_full_range_flag
                                        # colour_description_present_flag
                                        if reader.read_bit():
                                            reader.read_bits(8)  # colour_primaries
                                            reader.read_bits(8)  # transfer_characteristics
                                            reader.read_bits(8)  # matrix_coeffs

                                    # chroma_loc_info_present_flag
                                    if reader.read_bit():
                                        chroma_sample_loc_type_top_field = reader.read_ue()
                                        chroma_sample_loc_type_bottom_field = reader.read_ue()

                                        # Map to chroma location string
                                        chroma_loc = _CHROMA_LOCATION_MAP.get(chroma_sample_loc_type_top_field, "left")
                                        hdr_metadata["chroma_location"] = chroma_loc
                                        logger.debug(
                                            f"VUI chroma_location: {chroma_loc} (top={chroma_sample_loc_type_top_field}, bottom={chroma_sample_loc_type_bottom_field})")

                            except (IndexError, Exception) as e:
                                logger.debug(f"Could not parse to VUI for chroma location: {e}")

                            logger.debug(
                                f"SPS parsed: profile={hdr_metadata.get('profile')}, pixel_format={hdr_metadata.get('pixel_format')}, chroma_location={hdr_metadata.get('chroma_location')}")
                        except Exception as e:
                            logger.debug(f"Error parsing SPS: {e}")

                    # PREFIX_SEI (39) or SUFFIX_SEI (40)
                    elif nal_type in (39, 40):
                        sei_offset = 2  # Skip NAL header

                        # Parse SEI messages in this NAL unit
                        while sei_offset < len(nal_data) - 1:
                            # Read payload type (variable length encoding)
                            payload_type = 0
                            while sei_offset < len(nal_data):
                                byte = nal_data[sei_offset]
                                sei_offset += 1
                                payload_type += byte
                                if byte != 0xFF:
                                    break

                            # Read payload size (variable length encoding)
                            payload_size = 0
                            while sei_offset < len(nal_data):
                                byte = nal_data[sei_offset]
                                sei_offset += 1
                                payload_size += byte
                                if byte != 0xFF:
                                    break

                            if sei_offset + payload_size > len(nal_data):
                                break

                            # Extract SEI payload
                            sei_payload = nal_data[sei_offset:sei_offset + payload_size]
                            sei_offset += payload_size

                            # Parse HDR SEI
                            sei_hdr = MP4BoxParser._parse_hevc_sei_hdr(sei_payload, payload_type)
                            if sei_hdr:
                                hdr_metadata.update(sei_hdr)

                            # Stop at rbsp_trailing_bits
                            if sei_offset < len(nal_data) and nal_data[sei_offset] == 0x80:
                                break

                            # Early exit if we have both mdcv and clli
                            if 'max_luminance' in hdr_metadata and 'max_cll' in hdr_metadata:
                                break

                offset += nal_length

            return hdr_metadata if hdr_metadata else None
        except Exception as e:
            logger.debug(f"Error extracting HDR from bitstream: {e}")
            return None

    @staticmethod
    def _get_sample_info_from_stbl(f: BinaryIO, stbl_start: int, stbl_end: int) -> Optional[tuple]:
        """Get first sample offset and size from stbl."""
        try:
            chunk_offset = None
            sample_size = None
            current_pos = stbl_start

            while current_pos < stbl_end:
                f.seek(current_pos)
                box_type, _, box_start, box_end = _read_box_header(f)
                if not box_type or box_end > stbl_end:
                    break

                # Chunk offset (stco = 32-bit, co64 = 64-bit)
                if box_type == b"stco" and chunk_offset is None:
                    f.seek(box_start + 8)  # Skip size + type
                    f.read(4)  # Skip version + flags
                    entry_count = _read_uint32(f)
                    if entry_count and entry_count > 0:
                        chunk_offset = _read_uint32(f)
                elif box_type == b"co64" and chunk_offset is None:
                    f.seek(box_start + 8)
                    f.read(4)  # Skip version + flags
                    entry_count = _read_uint32(f)
                    if entry_count and entry_count > 0:
                        chunk_offset = _read_uint64(f)

                # Sample size (stsz)
                elif box_type == b"stsz" and sample_size is None:
                    f.seek(box_start + 8)
                    f.read(4)  # Skip version + flags
                    default_size = _read_uint32(f)
                    sample_count = _read_uint32(f)

                    if default_size and default_size > 0:
                        sample_size = default_size
                    elif sample_count and sample_count > 0:
                        sample_size = _read_uint32(f)

                if chunk_offset is not None and sample_size is not None:
                    logger.debug(f"Found sample: offset={chunk_offset}, size={sample_size}")
                    return (chunk_offset, min(sample_size, 65536))  # Limit to 64KB

                current_pos = box_end

            logger.debug(f"No sample found: chunk_offset={chunk_offset}, sample_size={sample_size}")
            return None
        except Exception as e:
            logger.debug(f"Error getting sample info: {e}")
            return None

    @staticmethod
    def parse_stsd_video_with_bitstream(
            f: BinaryIO,
            stsd_end: int,
            stbl_start: Optional[int] = None,
            stbl_end: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Parse video sample description with bitstream HDR extraction."""

        # First, parse normal stsd
        video_details = MP4BoxParser.parse_stsd_video(f, stsd_end)

        # For HEVC, always try bitstream parsing to get profile/pixel_format/chroma_location
        codec_tag = video_details.get("codec_tag_string", "")
        has_container_hdr = "max_luminance" in video_details or "max_cll" in video_details
        needs_bitstream_parse = (
                codec_tag in ("hvc1", "hev1", "dvh1", "dvhe") and
                (not has_container_hdr or
                 video_details.get("profile") is None or
                 video_details.get("pixel_format") is None)
        )

        logger.debug(
            f"Bitstream check: codec={codec_tag}, has_hdr={has_container_hdr}, "
            f"needs_parse={needs_bitstream_parse}, stbl_start={stbl_start}, stbl_end={stbl_end}")

        if needs_bitstream_parse and stbl_start and stbl_end:
            # Get first sample location
            sample_info = MP4BoxParser._get_sample_info_from_stbl(f, stbl_start, stbl_end)

            if sample_info:
                sample_offset, sample_size = sample_info
                logger.debug(f"Reading sample at offset={sample_offset}, size={sample_size}")
                try:
                    # Read sample data
                    current_pos = f.tell()
                    f.seek(sample_offset)
                    sample_data = f.read(sample_size)
                    f.seek(current_pos)

                    logger.debug(f"Read {len(sample_data)} bytes of sample data")

                    # Extract metadata from bitstream
                    if sample_data:
                        bitstream_data = MP4BoxParser._extract_hdr_from_hevc_bitstream(sample_data)
                        if bitstream_data:
                            logger.debug(f"Found bitstream data: {bitstream_data}")
                            video_details.update(bitstream_data)
                        else:
                            logger.debug("No metadata found in bitstream")
                except Exception as e:
                    logger.debug(f"Error reading sample: {e}")
            else:
                logger.debug("Could not find sample info")

        video_details.pop("_needs_bitstream_parse", None)

        return video_details

    @staticmethod
    def parse_stsd_video(
            f: BinaryIO,
            stsd_end: int,
    ) -> Dict[str, Any]:
        """
        Parses 'stsd' for video track details including resolution and HDR format.
        """
        video_details = {
            "codec": "unknown",
            "codec_tag_string": "unknown",
            "width": 0,
            "height": 0,
            "pixel_format": None,
            "profile": None,
            "chroma_location": None,
            "hdr_format": "SDR",
            "dolby_vision_profile": None,
            "dolby_vision_level": None,
            "dolby_vision": False,
            "dolby_vision_sdr_compatible": False,
        }

        f.seek(8, 1)
        if f.tell() >= stsd_end:
            return video_details

        entry_type, _, entry_start, entry_end = _read_box_header(f)
        if not entry_type:
            return video_details

        codec_tag = entry_type.decode("ascii", "replace")
        video_details.update(
            {
                "codec_tag_string": codec_tag,
                "codec": _VIDEO_CODEC_MAP.get(codec_tag, codec_tag),
            }
        )

        f.seek(entry_start + 8 + 24)
        width, height = _read_uint16(f), _read_uint16(f)
        if width:
            video_details["width"] = width
        if height:
            video_details["height"] = height

        current_pos = entry_start + 8 + 78
        mdcv_data, clli_data = None, None
        container_colr_found = False
        vpc_data: Dict[str, int] = {}

        codec_config_parsers = {
            b"avcC": MP4BoxParser._parse_avcC,
            b"hvcC": MP4BoxParser._parse_hvcC,
            b"av1C": MP4BoxParser._parse_av1C,
        }

        while current_pos < entry_end:
            f.seek(current_pos)
            child_type, _, child_start, child_end = _read_box_header(f)
            if not child_type or child_end > entry_end:
                break

            if child_type in (b"dvcC", b"dvvC"):
                video_details["dolby_vision"] = True
                f.seek(child_start + 8)  # Skip box header
                dv_version_major = _read_uint8(f)
                dv_version_minor = _read_uint8(f)
                if (val := _read_uint16(f)) is not None:
                    profile = (val >> 9) & 0x7F
                    level = (val >> 3) & 0x3F
                    rpu_present = (val >> 2) & 0x01
                    el_present = (val >> 1) & 0x01
                    bl_present = val & 0x01

                    # Read the next byte for bl_signal_compatibility_id (upper 4 bits)
                    next_byte = _read_uint8(f)
                    bl_compatibility_id = None
                    if next_byte is not None:
                        bl_compatibility_id = (next_byte >> 4) & 0x0F

                        # For profile 8, format as 8.x where x is the compatibility ID
                        if profile == 8 and bl_compatibility_id in (1, 2, 4, 6):
                            video_details["dolby_vision_profile"] = f"{profile}.{bl_compatibility_id}"
                        else:
                            video_details["dolby_vision_profile"] = profile
                    else:
                        video_details["dolby_vision_profile"] = profile

                    video_details["dolby_vision_level"] = level

                    # Add all the detailed Dolby Vision configuration fields
                    video_details["dolby_vision_version"] = f"{dv_version_major}.{dv_version_minor}"
                    video_details["dolby_vision_rpu_present"] = bool(rpu_present)
                    video_details["dolby_vision_el_present"] = bool(el_present)
                    video_details["dolby_vision_bl_present"] = bool(bl_present)
                    if bl_compatibility_id is not None:
                        video_details["dolby_vision_bl_compatibility_id"] = bl_compatibility_id

                    logger.debug(f"Dolby Vision box ({child_type.decode()}): "
                                 f"version={dv_version_major}.{dv_version_minor}, "
                                 f"raw_val=0x{val:04x}, profile={profile}, level={level}, "
                                 f"bl_compat_id={bl_compatibility_id if next_byte else 'N/A'}, "
                                 f"final_profile={video_details['dolby_vision_profile']}")
            elif child_type in codec_config_parsers:
                codec_details = codec_config_parsers[child_type](f, child_end)
                if codec_details:
                    video_details.update(
                        {k: v for k, v in codec_details.items() if v is not None}
                    )
            elif child_type == b"vpcC":
                vpc_data = MP4BoxParser._parse_vpc_config(f, child_end)
                if vpc_data:
                    video_details.update(vpc_data)
            elif child_type == b"colr":
                container_colr_found = True
                f.seek(child_start + 8)
                param_type = f.read(4)
                p, t, m = _read_uint16(f), _read_uint16(f), _read_uint16(f)

                if p is not None:
                    video_details["color_primaries"] = COLOR_PRIMARIES_MAP.get(p, str(p))
                if t is not None:
                    video_details["transfer_characteristics"] = TRANSFER_CHARACTERISTICS_MAP.get(t, str(t))
                if m is not None:
                    video_details["matrix_coefficients"] = MATRIX_COEFFICIENTS_MAP.get(m, str(m))

                if param_type == b"nclx" and (rb := _read_uint8(f)) is not None:
                    video_details["color_range"] = "full" if (rb >> 7) & 1 else "tv"
                else:
                    video_details["color_range"] = "tv"
            elif child_type == b"mdcv":
                mdcv_data = MP4BoxParser._parse_mdcv(f, child_end)
            elif child_type == b"clli":
                clli_data = MP4BoxParser._parse_clli(f, child_end)

            current_pos = child_end

        if codec_tag == "vp09" and vpc_data:
            bit_depth = vpc_data.get("bit_depth")
            chroma = vpc_data.get("chroma_subsampling")
            if (
                    video_details.get("transfer_characteristics")
                    in ("smpte2084", "arib-std-b67")
                    and bit_depth is not None
                    and bit_depth < 10
            ):
                bit_depth = 10
            if chroma is not None and bit_depth is not None:
                pix_fmt_base = {0: "yuv420p", 1: "yuv422p", 2: "yuv444p"}.get(chroma)
                if pix_fmt_base:
                    video_details["pixel_format"] = (
                        f"{pix_fmt_base}{bit_depth}le"
                        if bit_depth > 8
                        else pix_fmt_base
                    )

        if not container_colr_found and vpc_data:
            if (p := vpc_data.get("colour_primaries")) is not None:
                video_details["color_primaries"] = COLOR_PRIMARIES_MAP.get(p, str(p))
            if (t := vpc_data.get("transfer_characteristics")) is not None:
                video_details["transfer_characteristics"] = TRANSFER_CHARACTERISTICS_MAP.get(t, str(t))
            if (m := vpc_data.get("matrix_coefficients")) is not None:
                video_details["matrix_coefficients"] = MATRIX_COEFFICIENTS_MAP.get(m, str(m))

        if video_details.get("dolby_vision"):
            if "color_primaries" not in video_details:
                video_details["color_primaries"] = "bt2020"
            if "transfer_characteristics" not in video_details:
                video_details["transfer_characteristics"] = "smpte2084"
            if "matrix_coefficients" not in video_details:
                video_details["matrix_coefficients"] = "bt2020nc"
            is_hdr10_base = (
                    video_details.get("transfer_characteristics") == "smpte2084" and mdcv_data
            )
            video_details["hdr_format"] = (
                "HDR10, Dolby Vision" if is_hdr10_base else "Dolby Vision"
            )

            # Determine SDR compatibility based on bl_compatibility_id
            # Profile 8.1 (bl_compat=1) = HDR10 base, NOT SDR compatible
            # Profile 8.2 (bl_compat=2) = SDR base, YES SDR compatible
            # Profile 8.4 (bl_compat=4) = No backward compatibility
            bl_compat_id = video_details.get("dolby_vision_bl_compatibility_id")
            if bl_compat_id == 2:
                video_details["dolby_vision_sdr_compatible"] = True
            elif bl_compat_id in (1, 4, 6):
                video_details["dolby_vision_sdr_compatible"] = False
        elif video_details.get("transfer_characteristics") == "arib-std-b67":
            video_details["hdr_format"] = "HLG"
        elif video_details.get("transfer_characteristics") == "smpte2084":
            video_details["hdr_format"] = "HDR10" if mdcv_data else "HDR (PQ)"
        elif (mdcv_data or clli_data) and video_details.get("pixel_format") and "10le" in video_details.get(
                "pixel_format", ""):
            video_details["hdr_format"] = "HDR10"
        elif video_details.get("pixel_format") and "10le" in video_details.get("pixel_format", ""):
            video_details["hdr_format"] = "HDR10"

        if mdcv_data:
            video_details.update(mdcv_data)
        if clli_data:
            video_details.update(clli_data)

        if video_details.get("matrix_coefficients"):
            video_details["color_space"] = video_details["matrix_coefficients"]
        if video_details.get("transfer_characteristics"):
            video_details["color_transfer"] = video_details["transfer_characteristics"]

        if "color_range" not in video_details:
            video_details["color_range"] = "tv"

        if video_details.get("codec") == "vp9":
            video_details.pop("bit_depth", None)
            video_details.pop("chroma_subsampling", None)

        if not video_details.get("dolby_vision"):
            for key in [
                "dolby_vision",
                "dolby_vision_profile",
                "dolby_vision_level",
                "dolby_vision_sdr_compatible",
            ]:
                video_details.pop(key, None)

        f.seek(stsd_end)
        return video_details