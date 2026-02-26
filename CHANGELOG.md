# Changelog

## [1.0.0] - 2026-02-26

### Server
- rAthena master branch, Renewal mode
- PACKETVER=20220406
- Packet Obfuscation disabled (`#undef PACKET_OBFUSCATION` in defines_post.hpp)
- Docker multi-stage build (linux/amd64)
- Deploy target: AWS Lightsail Tokyo
- Auto account registration enabled (new_account: yes)
- Rates: 50x EXP / 50x Drop / 50x Card

### Client
- Base: kRO Full Client 2022-07-21
- Exe: 2022-04-06_Ragexe_1648707856 patched with NEMO (12 patches)
- English msgstringtable.txt from ROenglishRE
- SystemEN/Navi_Data.lub for navigation fix

### NEMO Patches (12)
- Disable 1rag1 type parameters
- Disable Ragexe Filename Check
- Read Data Folder First
- Remove Gravity Ads
- Remove Gravity Logo
- Enable DNS Support
- Remove hardcoded address/port
- Restore old login packet
- Disable OTP Login Packet
- Disable password encryption for lang types 4, 7
- Disable Game Guard (NProtect)
- Disable packets id encryption
