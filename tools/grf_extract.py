#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRF (Gravity Resource File) extractor for Ragnarok Online.

GRF v2.0 format:
  Header (46 bytes):
    - Magic: "Master of Magic\0" (15+1 bytes)
    - Key (14 bytes, encryption-related, unused here)
    - FileTableOffset (4 bytes LE uint32)
    - Seed (4 bytes LE uint32, for DES decryption)
    - FileCount (4 bytes LE uint32) — real_count = filecount - seed - 7
    - Version (4 bytes LE uint32)

  File table (at offset FileTableOffset + 46):
    - CompressedSize (4 bytes LE uint32)
    - UncompressedSize (4 bytes LE uint32)
    - Then entries, each:
      - Filename: null-terminated string
      - CompressedSize (4 bytes LE uint32)
      - CompressedSizeAligned (4 bytes LE uint32)
      - UncompressedSize (4 bytes LE uint32)
      - Flags (1 byte): 0x01 = file, 0x02 = DES encrypted, 0x04 = mixed DES
      - Offset (4 bytes LE uint32) — from start of file + 46

Usage:
  python grf_extract.py <grf_file> --list [--filter .txt]
  python grf_extract.py <grf_file> --extract <internal_path> [--output <file>]
"""

import struct
import sys
import os
import zlib
import argparse

HEADER_SIZE = 46
MAGIC = b"Master of Magic\x00"


def read_grf_header(f):
    """Read and parse GRF header."""
    header = f.read(HEADER_SIZE)
    if len(header) < HEADER_SIZE:
        raise ValueError("File too small to be a GRF")

    magic = header[:16]
    if magic != MAGIC:
        raise ValueError(f"Invalid GRF magic: {magic!r}")

    # key = header[16:30]  # encryption key, unused
    file_table_offset = struct.unpack_from("<I", header, 30)[0]
    seed = struct.unpack_from("<I", header, 34)[0]
    file_count_raw = struct.unpack_from("<I", header, 38)[0]
    version = struct.unpack_from("<I", header, 42)[0]

    real_count = file_count_raw - seed - 7

    return {
        "file_table_offset": file_table_offset,
        "seed": seed,
        "file_count": real_count,
        "version": version,
    }


def read_file_table(f, header):
    """Read all file table entries."""
    table_offset = header["file_table_offset"] + HEADER_SIZE
    f.seek(table_offset)

    # File table header: compressed size, uncompressed size
    table_header = f.read(8)
    if len(table_header) < 8:
        raise ValueError("Cannot read file table header")

    table_compressed_size, table_uncompressed_size = struct.unpack("<II", table_header)

    # Read and decompress the file table
    table_data_compressed = f.read(table_compressed_size)
    table_data = zlib.decompress(table_data_compressed)

    if len(table_data) != table_uncompressed_size:
        print(f"Warning: table size mismatch: got {len(table_data)}, expected {table_uncompressed_size}")

    entries = []
    pos = 0
    count = header["file_count"]

    for _ in range(count):
        # Read null-terminated filename
        name_end = table_data.index(b"\x00", pos)
        filename = table_data[pos:name_end]
        pos = name_end + 1

        # Read entry fields (13 bytes)
        if pos + 13 > len(table_data):
            break

        compressed_size, compressed_size_aligned, uncompressed_size = struct.unpack_from("<III", table_data, pos)
        pos += 12
        flags = table_data[pos]
        pos += 1
        offset = struct.unpack_from("<I", table_data, pos)[0]
        pos += 4

        # Try to decode filename (GRF uses EUC-KR for Korean filenames)
        try:
            name_str = filename.decode("euc-kr")
        except UnicodeDecodeError:
            try:
                name_str = filename.decode("latin-1")
            except UnicodeDecodeError:
                name_str = filename.decode("ascii", errors="replace")

        entries.append({
            "filename": name_str,
            "filename_raw": filename,
            "compressed_size": compressed_size,
            "compressed_size_aligned": compressed_size_aligned,
            "uncompressed_size": uncompressed_size,
            "flags": flags,
            "offset": offset + HEADER_SIZE,
        })

    return entries


def extract_file(f, entry):
    """Extract a single file from GRF."""
    if entry["flags"] & 0x01 == 0:
        # Not a file (directory entry)
        return None

    f.seek(entry["offset"])
    data = f.read(entry["compressed_size_aligned"])

    if entry["compressed_size"] == entry["uncompressed_size"]:
        # Not compressed
        return data[:entry["uncompressed_size"]]

    # Decompress
    try:
        decompressed = zlib.decompress(data)
        return decompressed
    except zlib.error:
        # Try with the non-aligned size
        f.seek(entry["offset"])
        data = f.read(entry["compressed_size"])
        try:
            return zlib.decompress(data)
        except zlib.error as e:
            print(f"  Warning: failed to decompress {entry['filename']}: {e}")
            return None


def list_files(grf_path, filter_ext=None):
    """List all files in GRF."""
    with open(grf_path, "rb") as f:
        header = read_grf_header(f)
        print(f"GRF Version: 0x{header['version']:08X}")
        print(f"File count: {header['file_count']}")
        print()

        entries = read_file_table(f, header)

        count = 0
        for entry in entries:
            if entry["flags"] & 0x01 == 0:
                continue
            name = entry["filename"]
            if filter_ext and not name.lower().endswith(filter_ext.lower()):
                continue
            size = entry["uncompressed_size"]
            print(f"  {name}  ({size:,} bytes)")
            count += 1

        print(f"\nTotal files: {count}")
        return entries


def extract_to_file(grf_path, internal_path, output_path=None):
    """Extract a specific file from GRF."""
    # Normalize path separators
    search_path = internal_path.replace("/", "\\")

    with open(grf_path, "rb") as f:
        header = read_grf_header(f)
        entries = read_file_table(f, header)

        for entry in entries:
            entry_path = entry["filename"].replace("/", "\\")
            if entry_path.lower() == search_path.lower():
                data = extract_file(f, entry)
                if data is None:
                    print(f"Failed to extract: {internal_path}")
                    return False

                if output_path is None:
                    output_path = os.path.basename(internal_path.replace("\\", "/"))

                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                with open(output_path, "wb") as out:
                    out.write(data)

                print(f"Extracted: {internal_path} -> {output_path} ({len(data):,} bytes)")
                return True

        print(f"File not found in GRF: {internal_path}")
        print("Searching for similar names...")
        basename = os.path.basename(search_path).lower()
        for entry in entries:
            if basename in entry["filename"].lower():
                print(f"  Found: {entry['filename']}")
        return False


def main():
    parser = argparse.ArgumentParser(description="GRF file extractor for Ragnarok Online")
    parser.add_argument("grf_file", help="Path to .grf file")
    parser.add_argument("--list", action="store_true", help="List files in GRF")
    parser.add_argument("--filter", help="Filter by extension (e.g., .txt)")
    parser.add_argument("--extract", help="Internal path to extract (e.g., data\\\\skillnametable.txt)")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if not os.path.exists(args.grf_file):
        print(f"Error: GRF file not found: {args.grf_file}")
        sys.exit(1)

    if args.list:
        list_files(args.grf_file, args.filter)
    elif args.extract:
        success = extract_to_file(args.grf_file, args.extract, args.output)
        if not success:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
