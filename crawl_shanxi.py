import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 配置
SAVE_DIR = "project_data/raw_docs"
os.makedirs(SAVE_DIR, exist_ok=True)
URL_LIST_PATH = os.path.join(SAVE_DIR, "url_list.txt")
ALL_TEXT_PATH = os.path.join(SAVE_DIR, "all_raw_text.txt")

# 手动在这里填入山西政务办事指南网页链接，至少30条
TARGET_URLS = [
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?type=2&url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/0db3bf5ae1004e319ae4633803ab2093",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/f0344c35f18d49579f295a538cf474ab",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/62d29c28c6bd489a82389e07014fe975",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c82a915055b74d40bbbe79d772ae039e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/e20af3645997415cb229d0ce57ae9e93",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c58c3ca9464447d1b57d1baf8d70a004",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/1fc06ba4e9894101832bbb750b0cea4f",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/783604acedd14d8dac508c38644fdfb1",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/79d0ce5b470a4bdf89943eb71e8697cf",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/47d29647f853491e86dc381789ca8f9f",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/e04f3632abfd4e20ba50c971016e21cb",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/49a1cdd2ca0240b386fa6255101840a0",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/969c8e8dc7a0431cb1d19cd77d915342",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b46ae4e0ae25426787ef5737ab2af638",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/f66810b6c6044de49a492c6642baf9b3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/0375819df2a64b8283a76acb19c7679d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/40ba702ac22448c89a26fe78bd17b163",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/d2264437cfde4bd58127cce1346f56d8",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/cdddd0a73ea34f6ba0ff0c886a7e7b9b",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/6d8fdb350ab04ddd828f2a0ca82e6f78",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c8cddffcf48143648138928b36393359",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/db8c5393aa4348d2817fa4b4531bd79e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/4ac10665ee2943bbb68a6a87bab1ee0f",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/1eaeea5345dd4e0fb718ba53607f6061",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/dee64be448d8464a9e961a6cb89a9a97",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/48df922ffaba4b2eb2dce98b23f0d25d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/16498c3237cc44f2a1671e9a9124a4a8",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/16498c3237cc44f2a1671e9a9124a4a8",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/f2a90a4331a24b869f2acbeb6d568339",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a4f01a56b65d4244a4ca487b648f57ae",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/79a4bbbe8531475ebad4cdf856a27167",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/0c4f06009d654a3784ef3039e94ba3df",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/618f169433b8474186168b548d019678",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/dbb31016845a463292878511856e997a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/36131460932b412884f21f008d464824",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/3947425654704db19589756268d3b866",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/40641844784f48288124f82336408291",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/42827983287b40409232343000248015",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/45347194412441188d08008243d44252",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/4814723444744114814dd22114484772",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/4b2274317808404180f0204422d04221",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/4c724833302041419322228411040077",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/51334134344441429241042443204443",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/52427343744441129202240242104434",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/53127343744441129202240242104434",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/55447233442441419321224421140077",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/572274317808404180f0204422d04221",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/5814723444744114814dd22114484772",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/60347194412441188d08008243d44252",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/62827983287b40409232343000248015",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/64641844784f48288124f82336408291",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/6747425654704db19589756268d3b866",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/69131460932b412884f21f008d464824",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/B125434ABFA2409B93F82E3E1EA6112E",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/A23F451CCE34418A88422F134C472DB7",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/C34E562DDF45429B99533G245D583EC8",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/D45F673EEG56430C00644H356E694FD9",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/E56G784FFH67441D11755I467F705GE0",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/F67H895GGI78452E22866J578G816HF1",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/G78I906HHJ89463F33977K689H927IG2",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/H89J017IIK90474G44088L790I038JH3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/I90K128JJL01485H55199M801J149KI4",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/J01L239KKM12496I66200N912K250LJ5",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/K12M340LLN23407J77311O023L361MK6",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/L23N451MMO34418K88422P134M472NL7",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/M34O562NNP45429L99533Q245N583OM8",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/N45P673OOQ56430M00644R356O694PN9",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/O56Q784PPR67441N11755S467P705QO0",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/P67R895QQS78452O22866T578Q816RP1",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/Q78S906RRT89463P33977U689R927SQ2",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/R89T017SSU90474Q44088V790S038TR3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/S90U128TTV01485R55199W801T149US4",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/T01V239UUV12496S66200X912U250VT5",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/01f9d2a7c3b84e2a91d7f6c5b3a8d9e2",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/02e8c1b6a2d74f3b80c6e5d4a2b7f1d3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/03d7a0c5b1e64a4c79d5f4c3b1a6e0f4",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/04c6b9d4a0f54b5d68c4e3d2a0b5f9e5",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/05b5a8c39e44c6e57b3d2c1b9a4e8d06",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/06a497b28d34d7f46a2c1b0a89d7c6e7",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/07f386a17c24e8d359b1a9f78b6c5d48",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/08e275906b14f9c248a0f8e6d5c3b299",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/09d164895a04a0b137f9e7d4c2b1a30a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/10c0537849f4b1a026e8d6c3b1a9f41b",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/11b9426738e4c2f915d7c4a2b0e8f52c",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/12a8315627d4d3e804c6b3a9f1d7e63d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/13f7204516c4e4d793b5a2f8e0c6d74e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/14e6193405b4f5c682a4b1e7d9f5c85f",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/15d5082394a4a6b571f3c0d6e8b4a960",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/16c4971283f4b7a460e2b9c5a7f3d071",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/17b3860172e4c8d359d1f8e4c2b1a82b",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/18a2759061d4d9e248c0a7d3f1e9b93c",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/19f1648950c4ea1b37b9e6c2b0a8d44d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/20e0537849b4f2c16a8d5c3b9f1a55e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/21d9a8c7b6e54f3a92d0f1c3b5a7e901",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/22c8b7a6c5d44e2b81e9f0b2a4c6d812",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/23b7a5d4e3c44f1a70f8e9d1b3a5c723",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/24a6c4e3f2b44d0b69d7c8e0a2b4d634",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/25f5b3d2e1a44c9a58c6d7f9b1a3c545",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/26e4a2c1d0f44b8e47b5c6d8a9f2b456",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/27d3b1e0c9a44a7d36a4b5c7d8e1a367",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/28c2a0d9b8f44f6c2593a4b6c7d0e278",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/29b1d8c7a6e44e5b148293a5b7c9d189",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/30a0f7b5c4d44d4a037182a4b6c8e09a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/31f9e6a4b3c44c3f92607183a5b7d0ab",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/32e8d5b3a2f44b2e815926074b6c9fbc",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/33c7c4a2b1e44a1d704831598a7b6cde",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/34b6b3d1f0a44f0c69392487b8a5c1ef",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/35a5a2c0e9b44e9b58241396a7b4d201",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/36f491b9d8a44c8a47150247b6c3e312",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/37e380a8c7d44b7d36049135a4b2c423",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/38d27f97b6c44a6c259380249a5b1d34",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/39c16e86a5b44f5b148279138a4b0e45",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/40b05d7594a44e4a0371680279b5f56a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/41a94c6483f44d39f26179036b4a0e71",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/42f83b5372e44c28e15068925a39f182",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/43e72a4261d44b17d04957814928e093",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/44d6193150c44a06c93846703817d904",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/45c5082049b44f95b82735692706c815",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/46b4971938a44e84a71624581695b726",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/47a3860827f44d73960513470584a637",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/48f2759716e44c628594023694739548",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/49e1648605d44b517483912583628459",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/50d0537594c44a40637280147251736a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/51c9426483b44f39526179036140627b",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/52b8315372a44e28415068925039518c",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/53a7204261f44d17304957814928409d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/54f6193150e44c06293846703817390e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/55e5082049d44b95182735692706281f",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/56d4971938c44a840716245816951720",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/57c3860827b44f739605134705840631",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/58b2759716a44e628594023694739542",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/59a1648605f44d517483912583628453",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/60f0537594e44c406372801472517364",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/61f94c7482a44d38f15068925b4a1e72",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/62e83b6371f44c27e04957814a39f283",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/63d72a5260e44b16d93846703928e194",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/64c6194159d44a05c827356924817d05",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/65b5083048c44f94b716245813926c16",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/66a4972937b44e83a605134702815b27",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/67f3861826a44d729594023691704a38",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/68e2750715944c618483912580693549",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/69d1649604e44b50737280147958245a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/70c0538593f44a496261790368471b6b",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/71b9427482e44f38515068925739a77c",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/72a8316371d44e27404957814628f68d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/73f7205260c44d16393846703517e79e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/74e6194159b44c052827356924068f8f",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/75d5083048a44b94171624581319a90",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/76c4972937944a830605134702084ba1",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/77b3861826844f729594023691973ab2",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/78a2750715744e6184839125808693c3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/79f1649604544d50737280147954284d4",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/80e0538593d44c496261790368471b5e",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/81d94c6482b44d38f15079036a4b0e73",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/82c83b5371a44c27e0496892593af284",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/83b72a4260f44b16d93857814829e195",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/84a6193159e44a05c82746703718d056",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/85f5082048d44f94b71635692607c167",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/86e4971937c44e83a60524581596b278",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/87d3860826b44d72959413470485a389",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/88c2759715a44c61848302369374949a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/89b1648604f44b5073729125826385ab",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/90a0537593e44a4962618014715276bc",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/91f9426482d44f38515079036041a7cd",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/92e8315371c44e27404968925930f6de",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/93d7204260b44d16393857814829e7ef",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/94c6193159a44c05282746703718d0f0",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/95b5082048f44b94171635692607c101",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/96a4971937e44a83060524581596b212",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/97f3860826d44f72959413470485a323",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/98e2759715c44e618483023693749434",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/99d1648604b44d507372912582638545",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a0c0537593a44c496261801471527656",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a1b94c7482c44d38f15089036a4b0e74",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a2a83b6371e44c27e0497892593af285",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a3f72a5260d44b16d93867814829e196",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a4e6194159f44a05c82756703718d057",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a5d5083048e44f94b71645692607c168",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a6c4972937a44e83a60534581596b279",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a7b3861826f44d72959423470485a380",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a8a2750715b44c618483123693749491",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/a9f1649604d44b5073720125826385a2",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b0e0538593c44a4962619014715276b3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b1d9426482f44f38515089036041a7c4",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b2c8315371d44e27404978925930f6d5",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b3b7204260a44d16393867814829e7e6",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b4a6193159c44c05282756703718d0f7",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b5f5082048144b94171645692607c108",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b6e4971937344a83060534581596b219",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b7d3860826444f72959423470485a32a",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b8c2759715544e61848312369374943b",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/b9b1648604644d50737201258263854c",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c0a0537593744c49626190147152765d",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c1b94c7482844d38f15099036a4b0e75",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c2a83b6371944c27e0498892593af286",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c3f72a5260744b16d93877814829e197",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c4e6194159844a05c82766703718d058",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c5d5083048944f94b71655692607c169",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c6c4972937744e83a60544581596b280",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c7b3861826844d72959433470485a381",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c8a2750715944c618483223693749492",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/c9f1649604744b5073721125826385a3",
    "https://www.sxzwfw.gov.cn/icity/icity/proinfo_new?url=https://zwfwpt.sxzwfw.gov.cn:10002/aaa/person/d0e0538593844a4962610014715276b4"

]

def extract_main_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        # 删除导航、页脚、侧边栏等无关标签
        for tag in soup.select("nav, header, footer, .sidebar, .menu, script, style"):
            tag.decompose()

        # 获取标题
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "untitled"
        # 清洗文件名（去掉不能作为文件名的符号）
        safe_title = "".join(c for c in title if c not in r'\/:*?"<>|')

        # 提取正文
        text = soup.get_text(strip=True, separator="\n")
        return title, safe_title, text
    except Exception as e:
        print(f"【失败】{url}, err: {e}")
        return None, None, None

def main():
    all_text_buffer = []
    with open(URL_LIST_PATH, "w", encoding="utf-8") as f_url:
        f_url.write("标题\tURL\t抓取日期\n")
        for url in TARGET_URLS:
            title, safe_title, text = extract_main_text(url)
            if not title:
                continue
            # 单网页保存txt
            txt_path = os.path.join(SAVE_DIR, f"{safe_title}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            # 写入url清单
            now = datetime.now().strftime("%Y-%m-%d")
            f_url.write(f"{title}\t{url}\t{now}\n")
            all_text_buffer.append(text)
            print(f"✅已保存：{title}")
    # 合并全部原文到all_raw_text.txt
    with open(ALL_TEXT_PATH, "w", encoding="utf-8") as f_all:
        f_all.write("\n=====DOC SPLIT=====\n".join(all_text_buffer))
    print(f"\n🎉全部完成，一共抓取 {len(all_text_buffer)} 篇文档")

if __name__ == "__main__":
    main()
