# https://www.youtube.com/@DiaoChan
from colorama import init, Fore
from os import listdir
from colorama import Fore, Style
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os,zipfile,colorama,shutil,xml.dom.minidom,xml.sax,os,re,shutil,random,getopt,sys,pyzstd,mmap,math
from pathlib import Path

def get_input(prompt):
    while True:
        value = input(prompt).strip().lower()
        if value in {'y', 'n'}:
            return value
        print("\033[1;91m[!] INVALID INPUT! PLEASE ENTER Y OR N.")
resources_path = "Resources"

def _version_key(name):
    parts = re.findall(r"\d+|[A-Za-z]+", name)
    key = []
    for part in parts:
        key.append((0, int(part)) if part.isdigit() else (1, part.lower()))
    return key

def find_latest_resources_version(root=resources_path):
    if not os.path.isdir(root):
        return None
    candidates = []
    for entry in os.listdir(root):
        path = os.path.join(root, entry)
        if not os.path.isdir(path) or not re.search(r"\d", entry):
            continue
        hero = os.path.join(path, "Databin", "Client", "Actor", "heroSkin.bytes")
        lang_dir = os.path.join(path, "Languages", "VN_Garena_VN")
        if os.path.isfile(hero) and os.path.isdir(lang_dir):
            candidates.append(entry)
    return sorted(candidates, key=_version_key)[-1] if candidates else None

version = find_latest_resources_version() or "UNKNOWN"
if version == "UNKNOWN":
    if not os.path.isdir(resources_path):
        print("\033[1;91m[!] 'Resources/' DIRECTORY NOT FOUND!\033[0m")
    else:
        print("\033[1;91m[!] NO VALID GAME VERSION FOUND IN 'Resources/'!\033[0m")
themtinhnang = get_input("\033[1;97m[\033[1;92m?\033[1;97m] OTHER FUNCTION Y/n: ")
if themtinhnang == 'y':
    while True:
        android_ios = get_input("\n\033[1;97m[\033[1;92m?\033[1;97m] MOD IOS FILE Y/n: ")
        antidec = get_input("\n\033[1;97m[\033[1;92m?\033[1;97m] ANTIDEC FILE AGES Y/n: ")
        CAMXA = get_input("\n\033[1;97m[\033[1;92m?\033[1;97m] MOD CAM XA JUNGLEMARK.XML Y/n: ")

        repeat = get_input("\n\033[1;97m[\033[1;92m?\033[1;97m] DO YOU WANT TO CHOOSE AGAIN? Y/n: ")
        if repeat == 'n':
            break
else:
    android_ios = antidec = CAMXA = 'n'
os.system("clear")    
print("\n\033[1;97m[\033[1;92m✓ \033[1;97m] YOUR SELECTION:")
print(f"\033[1;92m•\033[1;97m VERSION: {version}")
print(f"\033[1;92m•\033[1;97m MOD IOS FILE: {android_ios.upper()}")
print(f"\033[1;92m•\033[1;97m ANTIDEC FILE: {antidec.upper()}")
print(f"\033[1;92m•\033[1;97m MOD CAM XA: {CAMXA.upper()}")
file_path = Path("FILES_CODE/ZSTD_DICT.xml")
with file_path.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
    ZSTD_DICT = mm.read()
ZSTD_LEVEL = 17

#=========================================================================================================================                        
class StringBytes:
    def __init__(self,String):
        self.String=String
        self.OldString=String
    def tell(self):
        return len(self.OldString)-len(self.String)
    def seek(self,I,O=0):
        if O==0:
            self.String=self.OldString[I:]
        elif O==1:
            self.String=self.String[I:]
    def read(self,Int=None):
        if Int==None:
            if type(self.String)==str:
                return ""
            else:
                return b""
        R=self.String[:Int]
        self.String=self.String[Int:]
        return R
class Bytes_XML:
    def decode(String):
        def get_int(A):
            return int.from_bytes(A.read(4), 'little')        
        def get_str(A, pos=None):
            if pos is not None:
                A.seek(pos, 0)
            ofs = get_int(A)
            stri = A.read(ofs-4)
            return stri.decode()        
        def get_node(A, fid=None, sta=None):
            global i
            ofs = get_int(A)
            stri = get_str(A)
            stri1 = stri
            myid = i
            i += 1
            A.seek(4, 1)
            aidx = get_int(A)
            ite = False
            attr = {}
            for j in range(0, aidx):
                attr1 = get_attr(A)
                if type(attr1) == str:
                    text1 = attr1
                    ite = True
                else:
                    attr.update(attr1)
            if fid is None:
                nod[myid] = ET.SubElement(root, stri1, attrib=attr)
            else:
                nod[myid] = ET.SubElement(nod[fid], stri1, attrib=attr)
            if ite:
                if text1 == '':
                    nod[myid].set("value",' ')
                else:
                    nod[myid].set("value",text1)
            check_four(A)
            chk = sta + ofs - A.tell()
            if chk > 12:
                A.seek(4, 1)
                sidx = get_int(A)
                for h in range(0, sidx):
                    get_node(A, myid, A.tell())
            A.seek(sta + ofs, 0)        
        def get_attr(A, pos=None):
            if pos is None:
                pos = A.tell()
            ofs = get_int(A)
            type = get_int(A)
            if type == 5:
                stri = A.read(ofs - 8).decode()[1:]
                check_four(A)
                A.seek(pos + ofs, 0)
                return stri
            else:
                if type == 6:
                    stri = A.read(ofs - 8).decode()
                    if stri[0:2] == 'JT':
                        if stri == 'JTArr':
                            stri = 'Array'
                        elif stri == 'JTPri':
                            stri = 'String'
                        else:
                            stri = stri[2:]
                        name = 'var'
                    else:
                        name = 'var_Raw'
                elif type == 8:
                    stri2 = A.read(ofs - 8).decode()
                    if stri2[0:4] == 'Type':
                        stri = stri2[4:]
                        name = 'type'
                    else:
                        stri = stri2
                        name = 'type_Raw'
                else:
                    stri = A.read(ofs - 8).decode()
                    name = str(type)
                    A.seek(pos + ofs, 0)
                return {name:stri}
        def check_four(A):
            if get_int(A) != 4:
                A.seek(-4, 1)
        A=StringBytes(String)
        global i, nod, root
        i = 0
        nod = {}
        ofs = get_int(A)
        stri = get_str(A)
        stri1 = stri
        A.seek(4, 1)
        aidx = get_int(A)
        ite = False
        attr = {}
        for j in range(0, aidx):
            attr1 = get_attr(A)
            if type(attr1) == str:
                text1 = attr1
                ite = True
            else:
                attr.update(attr1)
        root = ET.Element(stri1, attrib=attr)
        if ite:
            nod[myid].set("value",text1)
        check_four(A)
        chk = ofs - A.tell()
        if chk > 12:
            A.seek(4, 1)
            sidx = get_int(A)
            for h in range(0, sidx):
                get_node(A, None, A.tell())
        try:return minidom.parseString(ET.tostring(root,"utf-8").decode()).toprettyxml(indent="  ",newl="\r\n").encode()
        except: return ET.tostring(root,"utf-8").decode()
    def encode(xmlfile):
        def byteint(num):
            return num.to_bytes(4, byteorder='little')
        def bytestr(stri):
            outbyte = byteint(len(stri) + 4)
            outbyte = outbyte + stri.encode()
            return outbyte
        def byteattr(key, attr):
            if key == 'var':
                if attr[key] == 'Array':
                    stri = 'JTArr'
                elif attr[key] == 'String':
                    stri = 'JTPri'
                else:
                    stri = 'JT' + attr[key]
                aid = 6
            elif key == 'var_Raw':
                stri = attr[key]
                aid = 6
            elif key == 'type':
                stri = 'Type' + attr[key]
                aid = 8
            elif key == 'type_Raw':
                stri = attr[key]
                aid = 8
            elif key == "value": return b""
            else:
                import unicodedata
                if unicodedata.numeric(key):
                    stri = attr[key]
                    aid = int(key)
            stripro = stri.encode()
            outbyte = byteint(len(stripro) + 8) + byteint(aid) + stripro
            return outbyte
        def bytenode(node):
            iftex = False
            name1 = node.tag
            name = bytestr(name1)
            attr1 = b''
            aindex = len(node.attrib)
            plus = 8
            for key in node.attrib:
                if key=="value":aindex-=1
                attr1 = attr1 + byteattr(key, node.attrib)
            if (node.get("value") != None) and (node.get("value")[0:1] != '\n'):
                if node.get("value") == ' ':
                    stri1 = ''
                else:
                    stri1 = node.get("value")
                iftex = True
                stripro = ('V' + stri1).encode()
                attr1 = attr1 + byteint(len(stripro) + 8) + byteint(5) + stripro + byteint(4)
                aindex += 1
                plus = 4
            attr1 = byteint(len(attr1) + plus) + byteint(aindex) + attr1 + byteint(4)
            alchild = b''
            if len(node):
                cindex = 0
                for child in node:
                    alchild = alchild + bytenode(child)
                    cindex += 1
                alchild = byteint(len(alchild) + 8) + byteint(cindex) + alchild
            else:
                if iftex == False:
                    alchild = byteint(4)
            bnode = name + attr1 + alchild
            bnode = byteint(len(bnode) + 4) + bnode
            return bnode
        tree = ET.fromstring(xmlfile)
        byt = bytenode(tree)
        return byt
        
#=========================================================================================================================                        
def process_file(file_path_FL, LC):
    with open(file_path_FL, "rb") as f:
        G = f.read()
        with open(file_path_FL, "wb") as f1:
            try:
                if LC == "1":
                    f1.write(Bytes_XML.decode(G))
                elif LC == "2":
                    f1.write(Bytes_XML.encode(G.decode()))
            except Exception as e:
                pass

#=========================================================================================================================                        
def process_directory(directory_path, LC):
    file_path_FL = directory_path
    process_file(file_path_FL, LC) 
 
 #=========================================================================================================================                        
icon154 = b'q\x03\x00\x00(<\x00\x00\x9a\x00\x00\x00\x14\x00\x00\x00E2B78973E5DA0F49_##\x00\x00\x00\x00\x00\x14\x00\x00\x0020ACB10A3F5C4B9A_##\x00\x07\x00\x00\x00301540\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00{\x02\x00\x00\x10\x00\x00\x00Share_15412.jpg\x00\x10\x00\x00\x00Share_15412.jpg\x00\x10\x00\x00\x00Share_15412.jpg\x00\n\x00\x00\x0015412.jpg\x00\x08\x00\x00\x00\x10\x00\x00\x00Skin_Icon_Model\x00\x14\x00\x00\x005AFB0F28AFD223F5_##\x00\x10\x00\x00\x00Skin_Icon_Skill\x00\x14\x00\x00\x0053AF2640805E7163_##\x00\x13\x00\x00\x00Skin_Icon_Dialogue\x00\x14\x00\x00\x00BF08C3E00D2DC1EC_##\x00\x16\x00\x00\x00Skin_Icon_SoundEffect\x00\x14\x00\x00\x00727C8C77DC33BCAB_##\x00\x15\x00\x00\x00Skin_Icon_Atmosphere\x00\x14\x00\x00\x0082D4F38570FF05F5_##\x00\x14\x00\x00\x00Skin_Icon_Animation\x00\x14\x00\x00\x002048DFA5BAFC6E13_##\x00\x15\x00\x00\x00Skin_Icon_BackToTown\x00\x14\x00\x00\x00BFB1C5549350A312_##\x00\x14\x00\x00\x00Skin_Icon_HeadFrame\x00\x14\x00\x00\x005CF3DDF4FFF3F0A7_##\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00%\x00\x00\x00BG_Yena_15413/BG_Commons_01_Platform\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01\xa6\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x003015412_B43_1.jpg\x00\x10\x00\x00\x003015412head.jpg\x00\x0e\x00\x00\x00Hero_1540.png\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00'
icon154fix = b'^\x03\x00\x00(<\x00\x00\x9a\x00\x00\x00\x14\x00\x00\x00E2B78973E5DA0F49_##\x00\x00\x00\x00\x00\x14\x00\x00\x0020ACB10A3F5C4B9A_##\x00\x07\x00\x00\x00301540\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00{\x02\x00\x00\x10\x00\x00\x00Share_15412.jpg\x00\x10\x00\x00\x00Share_15412.jpg\x00\x10\x00\x00\x00Share_15412.jpg\x00\n\x00\x00\x0015412.jpg\x00\x08\x00\x00\x00\x10\x00\x00\x00Skin_Icon_Model\x00\x14\x00\x00\x005AFB0F28AFD223F5_##\x00\x10\x00\x00\x00Skin_Icon_Skill\x00\x14\x00\x00\x0053AF2640805E7163_##\x00\x13\x00\x00\x00Skin_Icon_Dialogue\x00\x14\x00\x00\x00BF08C3E00D2DC1EC_##\x00\x16\x00\x00\x00Skin_Icon_SoundEffect\x00\x14\x00\x00\x00727C8C77DC33BCAB_##\x00\x15\x00\x00\x00Skin_Icon_Atmosphere\x00\x14\x00\x00\x0082D4F38570FF05F5_##\x00\x14\x00\x00\x00Skin_Icon_Animation\x00\x14\x00\x00\x002048DFA5BAFC6E13_##\x00\x15\x00\x00\x00Skin_Icon_BackToTown\x00\x14\x00\x00\x00BFB1C5549350A312_##\x00\x14\x00\x00\x00Skin_Icon_HeadFrame\x00\x14\x00\x00\x005CF3DDF4FFF3F0A7_##\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00%\x00\x00\x00BG_Yena_15413/BG_Commons_01_Platform\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01\xa6\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x003015412.jpg\x00\x10\x00\x00\x003015412head.jpg\x00\x01\x00\x00\x00\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00'
iconvalheinevo1 = b'\x13\x03\x00\x00\xff3\x00\x00\x85\x00\x00\x00\x14\x00\x00\x00F9B9135D9DECEB62_##\x00\x0b\x00\x00\x00\x14\x00\x00\x0075939F64822D8D0D_##\x00\x08\x00\x00\x003013311\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00Share_13311.jpg\x00\x10\x00\x00\x00Share_13311.jpg\x00\x10\x00\x00\x00Share_13311.jpg\x00\n\x00\x00\x0013311.jpg\x00\x05\x00\x00\x00\x10\x00\x00\x00Skin_Icon_Model\x00\x14\x00\x00\x00D1188909BCF1A796_##\x00\x10\x00\x00\x00Skin_Icon_Skill\x00\x14\x00\x00\x008771C9DA02F4FEA6_##\x00\x16\x00\x00\x00Skin_Icon_SoundEffect\x00\x14\x00\x00\x008D69A8C30826E8D2_##\x00\x13\x00\x00\x00Skin_Icon_Dialogue\x00\x14\x00\x00\x006740D42BD5B8DAF3_##\x00\x15\x00\x00\x00Skin_Icon_Atmosphere\x00\x14\x00\x00\x002231A8E028E42D2D_##\x00\x15\x00\x00\x00Skin_Icon_BackToTown\x00\x14\x00\x00\x00D74BB3893108A06A_##\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00%\x00\x00\x00BG_Commons_01/BG_Commons_01_Platform\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01x\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x003013311.jpg\x00\x10\x00\x00\x003013311head.jpg\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00'
iconvalheinevo5 = b'/\x03\x00\x00\xff3\x00\x00\x85\x00\x00\x00\x14\x00\x00\x00F9B9135D9DECEB62_##\x00\x0b\x00\x00\x00\x14\x00\x00\x0075939F64822D8D0D_##\x00\n\x00\x00\x003013311_2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00Share_13311_2.jpg\x00\x12\x00\x00\x00Share_13311_2.jpg\x00\x12\x00\x00\x00Share_13311_2.jpg\x00\x0c\x00\x00\x0013311_2.jpg\x00\x05\x00\x00\x00\x10\x00\x00\x00Skin_Icon_Model\x00\x14\x00\x00\x00D1188909BCF1A796_##\x00\x10\x00\x00\x00Skin_Icon_Skill\x00\x14\x00\x00\x008771C9DA02F4FEA6_##\x00\x16\x00\x00\x00Skin_Icon_SoundEffect\x00\x14\x00\x00\x008D69A8C30826E8D2_##\x00\x13\x00\x00\x00Skin_Icon_Dialogue\x00\x14\x00\x00\x006740D42BD5B8DAF3_##\x00\x15\x00\x00\x00Skin_Icon_Atmosphere\x00\x14\x00\x00\x002231A8E028E42D2D_##\x00\x15\x00\x00\x00Skin_Icon_BackToTown\x00\x14\x00\x00\x00D74BB3893108A06A_##\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x003\x00\x00\x00BG_DiRenJie_13312_T3/BG_yinyingzhishou_01_platform\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01x\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x00\x003013311_2.jpg\x00\x12\x00\x00\x003013311_1head.jpg\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00'
bacvalheinevo1 = b'\r\x01\x00\x00\xff3\x00\x00\x85\x00\x00\x00\x14\x00\x00\x00D898FD6DC80FD88F_##\x00\x0b\x00\x00\x00\x14\x00\x00\x0062C20D284D202339_##\x00\x14\x00\x00\x00105E41477A829A72_##\x00\x01\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x0013311.png\x00\x00\x00\x01\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc4\x0b=\x00\x00\xf7\x07\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x0020220902000000\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xdd\x83\x01\x00\x01\x01\x00\x00\x06,\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00'
bacvalheinevo5 = b'\x15\x01\x00\x00\xff3\x00\x00\x85\x00\x00\x00\x14\x00\x00\x000B0B75B334002849_##\x00\x0b\x00\x00\x00\x14\x00\x00\x006B7679BBD5264133_##\x00\x14\x00\x00\x00942E74C2AD28AE4C_##\x00\x01\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x12\x00\x00\x00Awake_Label_5.png\x00\x01\x00\x01\x00\x00\x00\x00\x01\xc7\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x8a\t=\x00\x00\x9f\x8c\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x0020210318060000\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x86\x01\x00\x01\x01\x00\x00\x06:\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00'
iconngokhongevo1 = b'\\\x03\x00\x00CA\x00\x00\xa7\x00\x00\x00\x14\x00\x00\x00EBC0C74462FF4B6A_##\x00\x07\x00\x00\x00\x14\x00\x00\x00DDB8BB646733B67E_##\x00\x07\x00\x00\x00301677\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00Share_16707.jpg\x00\x10\x00\x00\x00Share_16707.jpg\x00\x10\x00\x00\x00Share_16707.jpg\x00\n\x00\x00\x0016707.jpg\x00\x08\x00\x00\x00\x10\x00\x00\x00Skin_Icon_Model\x00\x14\x00\x00\x008407CA15068FFAAA_##\x00\x14\x00\x00\x00Skin_Icon_Animation\x00\x14\x00\x00\x00C35E60871AB1288B_##\x00\x15\x00\x00\x00Skin_Icon_Atmosphere\x00\x14\x00\x00\x007CD9214682BAB4D9_##\x00\x15\x00\x00\x00Skin_Icon_BackToTown\x00\x14\x00\x00\x0030F7AD035D47227A_##\x00\x10\x00\x00\x00Skin_Icon_Skill\x00\x14\x00\x00\x00B64FCE08AE9DDFE5_##\x00\x16\x00\x00\x00Skin_Icon_SoundEffect\x00\x14\x00\x00\x0051BF047372097407_##\x00\x13\x00\x00\x00Skin_Icon_Dialogue\x00\x14\x00\x00\x00E51142379BF893FC_##\x00\x14\x00\x00\x00Skin_Icon_HeadFrame\x00\x14\x00\x00\x00B68080AD661210A0_##\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00%\x00\x00\x00BG_Commons_01/BG_Commons_01_Platform\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01N\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00301677.jpg\x00\x0f\x00\x00\x00301677head.jpg\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00'
iconngokhongevo5 = b'r\x03\x00\x00CA\x00\x00\xa7\x00\x00\x00\x14\x00\x00\x00EBC0C74462FF4B6A_##\x00\x07\x00\x00\x00\x14\x00\x00\x00DDB8BB646733B67E_##\x00\t\x00\x00\x00301677_2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00Share_16707_2.jpg\x00\x12\x00\x00\x00Share_16707_2.jpg\x00\x12\x00\x00\x00Share_16707_2.jpg\x00\x0c\x00\x00\x0016707_2.jpg\x00\x08\x00\x00\x00\x10\x00\x00\x00Skin_Icon_Model\x00\x14\x00\x00\x008407CA15068FFAAA_##\x00\x14\x00\x00\x00Skin_Icon_Animation\x00\x14\x00\x00\x00C35E60871AB1288B_##\x00\x15\x00\x00\x00Skin_Icon_Atmosphere\x00\x14\x00\x00\x007CD9214682BAB4D9_##\x00\x15\x00\x00\x00Skin_Icon_BackToTown\x00\x14\x00\x00\x0030F7AD035D47227A_##\x00\x10\x00\x00\x00Skin_Icon_Skill\x00\x14\x00\x00\x00B64FCE08AE9DDFE5_##\x00\x16\x00\x00\x00Skin_Icon_SoundEffect\x00\x14\x00\x00\x0051BF047372097407_##\x00\x13\x00\x00\x00Skin_Icon_Dialogue\x00\x14\x00\x00\x00E51142379BF893FC_##\x00\x14\x00\x00\x00Skin_Icon_HeadFrame\x00\x14\x00\x00\x00B68080AD661210A0_##\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00-\x00\x00\x00BG_wukongjuexing2/BG_wukongjuexing2_Platform\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x01N\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00301677_2.jpg\x00\x11\x00\x00\x00301677_2head.jpg\x00\x01\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00'
bacngokhongevo1 = b'CA\x00\x00\xa7\x00\x00\x00\x14\x00\x00\x000B0B75B334002849_##\x00\x07\x00\x00\x00\x14\x00\x00\x006B7679BBD5264133_##\x00\x14\x00\x00\x00942E74C2AD28AE4C_##\x00\x01\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x12\x00\x00\x00Awake_Label_1.png'    
bacngokhongevo5 = b'CA\x00\x00\xa7\x00\x00\x00\x14\x00\x00\x000B0B75B334002849_##\x00\x07\x00\x00\x00\x14\x00\x00\x006B7679BBD5264133_##\x00\x14\x00\x00\x00942E74C2AD28AE4C_##\x00\x01\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x12\x00\x00\x00Awake_Label_5.png'    
ngoaihinhvaneov=b'/\x0c\x00\x00\x0b\x00\x00\x00ElementE\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom0\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.SkinElement\x04\x00\x00\x00\xd7\x0b\x00\x00\n\x00\x00\x00\x16\x02\x00\x00\x14\x00\x00\x00ArtSkinPrefabLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xca\x01\x00\x00\x03\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD1\x04\x00\x00\x00\x04\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD3\x04\x00\x00\x00\x04\x00\x00\x00\xa4\x00\x00\x00\x16\x00\x00\x00ArtSkinPrefabLODEx0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00V\x00\x00\x00\x01\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\x1c\x02\x00\x00\x17\x00\x00\x00ArtSkinLobbyShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xcd\x01\x00\x00\x03\x00\x00\x00\x97\x00\x00\x00\x0b\x00\x00\x00Element\x80\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringR\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_Show1\x04\x00\x00\x00\x04\x00\x00\x00\x97\x00\x00\x00\x0b\x00\x00\x00Element\x80\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringR\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_Show2\x04\x00\x00\x00\x04\x00\x00\x00\x97\x00\x00\x00\x0b\x00\x00\x00Element\x80\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringR\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_Show3\x04\x00\x00\x00\x04\x00\x00\x00E\x01\x00\x00\x1b\x00\x00\x00ArtSkinLobbyIdleShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xf2\x00\x00\x00\x03\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\xa5\x00\x00\x00\x1a\x00\x00\x00ArtSkinLobbyShowCamera\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_AW5_Cam\x04\x00\x00\x00\x04\x00\x00\x00^\x00\x00\x00\x18\x00\x00\x00Cam02InterpolateTime:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V1.5\x04\x00\x00\x00\x04\x00\x00\x00b\x00\x00\x00\x1c\x00\x00\x00Cam02InterpolateDuration:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V0.9\x04\x00\x00\x00\x04\x00\x00\x00V\x00\x00\x00\x1a\x00\x00\x00PreloadAnimatorEffects0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\x04\x00\x00\x00\x8c\x03\x00\x00\n\x00\x00\x00LookAtF\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom1\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.CameraLookAt\x04\x00\x00\x004\x03\x00\x00\x04\x00\x00\x00B\x01\x00\x00\n\x00\x00\x00Offset4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xfc\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V-0.07000029\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x05\x00\x00\x00y?\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x11\x00\x00\x00\x05\x00\x00\x00V1.539993\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V-3.739998\x04\x00\x00\x00\x04\x00\x00\x00H\x01\x00\x00\r\x00\x00\x00Direction4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xff\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V0.002750125\x04\x00\x00\x00\x04\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00yB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V0.009888734\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V0.9999473\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x0c\x00\x00\x00Duration8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V1\x04\x00\x00\x00\x04\x00\x00\x00R\x00\x00\x00\r\x00\x00\x00CameraFOV9\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0b\x00\x00\x00\x05\x00\x00\x00V17\x04\x00\x00\x00\x04\x00\x00\x00m\x00\x00\x00\x0f\x00\x00\x00LightConfigR\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom=\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.PrepareBattleLightConfig\x04\x00\x00\x00\x04\x00\x00\x00'
ngoaihinhvaneovvang=b'J\x0c\x00\x00\x0b\x00\x00\x00ElementE\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom0\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.SkinElement\x04\x00\x00\x00\r\x0c\x00\x00\n\x00\x00\x00\x16\x02\x00\x00\x14\x00\x00\x00ArtSkinPrefabLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xca\x01\x00\x00\x03\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\xa4\x00\x00\x00\x16\x00\x00\x00ArtSkinPrefabLODEx0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00V\x00\x00\x00\x01\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x007\x02\x00\x00\x17\x00\x00\x00ArtSkinLobbyShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xe8\x01\x00\x00\x03\x00\x00\x00\xa0\x00\x00\x00\x0b\x00\x00\x00Element\x89\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Component/13312_DiRenJie_AW5_RT_2_Show2\x04\x00\x00\x00\x04\x00\x00\x00\xa0\x00\x00\x00\x0b\x00\x00\x00Element\x89\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Component/13312_DiRenJie_AW5_RT_2_Show2\x04\x00\x00\x00\x04\x00\x00\x00\xa0\x00\x00\x00\x0b\x00\x00\x00Element\x89\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Component/13312_DiRenJie_AW5_RT_2_Show2\x04\x00\x00\x00\x04\x00\x00\x00E\x01\x00\x00\x1b\x00\x00\x00ArtSkinLobbyIdleShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xf2\x00\x00\x00\x03\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\xa5\x00\x00\x00\x1a\x00\x00\x00ArtSkinLobbyShowCamera\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_AW5_Cam\x04\x00\x00\x00\x04\x00\x00\x00^\x00\x00\x00\x18\x00\x00\x00Cam02InterpolateTime:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V1.5\x04\x00\x00\x00\x04\x00\x00\x00b\x00\x00\x00\x1c\x00\x00\x00Cam02InterpolateDuration:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V0.9\x04\x00\x00\x00\x04\x00\x00\x00V\x00\x00\x00\x1a\x00\x00\x00PreloadAnimatorEffects0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\x04\x00\x00\x00\x8c\x03\x00\x00\n\x00\x00\x00LookAtF\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom1\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.CameraLookAt\x04\x00\x00\x004\x03\x00\x00\x04\x00\x00\x00B\x01\x00\x00\n\x00\x00\x00Offset4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xfc\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V-0.07000029\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x05\x00\x00\x00y?\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x11\x00\x00\x00\x05\x00\x00\x00V1.539993\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V-3.739998\x04\x00\x00\x00\x04\x00\x00\x00H\x01\x00\x00\r\x00\x00\x00Direction4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xff\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V0.002750125\x04\x00\x00\x00\x04\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00yB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V0.009888734\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V0.9999473\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x0c\x00\x00\x00Duration8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V1\x04\x00\x00\x00\x04\x00\x00\x00R\x00\x00\x00\r\x00\x00\x00CameraFOV9\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0b\x00\x00\x00\x05\x00\x00\x00V17\x04\x00\x00\x00\x04\x00\x00\x00m\x00\x00\x00\x0f\x00\x00\x00LightConfigR\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom=\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.PrepareBattleLightConfig\x04\x00\x00\x00\x04\x00\x00\x00'
ngoaihinhvaneovdo= b'J\x0c\x00\x00\x0b\x00\x00\x00ElementE\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom0\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.SkinElement\x04\x00\x00\x00\r\x0c\x00\x00\n\x00\x00\x00\x16\x02\x00\x00\x14\x00\x00\x00ArtSkinPrefabLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xca\x01\x00\x00\x03\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x96\x00\x00\x00\x0b\x00\x00\x00Element\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_04_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\xa4\x00\x00\x00\x16\x00\x00\x00ArtSkinPrefabLODEx0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00V\x00\x00\x00\x01\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x007\x02\x00\x00\x17\x00\x00\x00ArtSkinLobbyShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xe8\x01\x00\x00\x03\x00\x00\x00\xa0\x00\x00\x00\x0b\x00\x00\x00Element\x89\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Component/13312_DiRenJie_AW5_RT_3_Show2\x04\x00\x00\x00\x04\x00\x00\x00\xa0\x00\x00\x00\x0b\x00\x00\x00Element\x89\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Component/13312_DiRenJie_AW5_RT_3_Show2\x04\x00\x00\x00\x04\x00\x00\x00\xa0\x00\x00\x00\x0b\x00\x00\x00Element\x89\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Component/13312_DiRenJie_AW5_RT_3_Show2\x04\x00\x00\x00\x04\x00\x00\x00E\x01\x00\x00\x1b\x00\x00\x00ArtSkinLobbyIdleShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xf2\x00\x00\x00\x03\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\xa5\x00\x00\x00\x1a\x00\x00\x00ArtSkinLobbyShowCamera\x7f\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringQ\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/133_DiRenJie/Awaken/13312_DiRenJie_AW5_Cam\x04\x00\x00\x00\x04\x00\x00\x00^\x00\x00\x00\x18\x00\x00\x00Cam02InterpolateTime:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V1.5\x04\x00\x00\x00\x04\x00\x00\x00b\x00\x00\x00\x1c\x00\x00\x00Cam02InterpolateDuration:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V0.9\x04\x00\x00\x00\x04\x00\x00\x00V\x00\x00\x00\x1a\x00\x00\x00PreloadAnimatorEffects0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\x04\x00\x00\x00\x8c\x03\x00\x00\n\x00\x00\x00LookAtF\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom1\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.CameraLookAt\x04\x00\x00\x004\x03\x00\x00\x04\x00\x00\x00B\x01\x00\x00\n\x00\x00\x00Offset4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xfc\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V-0.07000029\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x05\x00\x00\x00y?\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x11\x00\x00\x00\x05\x00\x00\x00V1.539993\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V-3.739998\x04\x00\x00\x00\x04\x00\x00\x00H\x01\x00\x00\r\x00\x00\x00Direction4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xff\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V0.002750125\x04\x00\x00\x00\x04\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00yB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V0.009888734\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V0.9999473\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x0c\x00\x00\x00Duration8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V1\x04\x00\x00\x00\x04\x00\x00\x00R\x00\x00\x00\r\x00\x00\x00CameraFOV9\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0b\x00\x00\x00\x05\x00\x00\x00V17\x04\x00\x00\x00\x04\x00\x00\x00m\x00\x00\x00\x0f\x00\x00\x00LightConfigR\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom=\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.PrepareBattleLightConfig\x04\x00\x00\x00\x04\x00\x00\x00'
ngoaihinhkhieov=b'B\x10\x00\x00\x0b\x00\x00\x00ElementE\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom0\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.SkinElement\x04\x00\x00\x00\xea\x0f\x00\x00\x0e\x00\x00\x00\x10\x02\x00\x00\x14\x00\x00\x00ArtSkinPrefabLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xc4\x01\x00\x00\x03\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_WuKong/Awaken/1678_sunwukong_03_LOD1\x04\x00\x00\x00\x04\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_WuKong/Awaken/1678_sunwukong_03_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_WuKong/Awaken/1678_sunwukong_03_LOD3\x04\x00\x00\x00\x04\x00\x00\x00\xa4\x00\x00\x00\x16\x00\x00\x00ArtSkinPrefabLODEx0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00V\x00\x00\x00\x01\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\x16\x02\x00\x00\x17\x00\x00\x00ArtSkinLobbyShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xc7\x01\x00\x00\x03\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_WuKong/Awaken/1678_sunwukong_03_Show1\x04\x00\x00\x00\x04\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_WuKong/Awaken/1678_sunwukong_03_Show2\x04\x00\x00\x00\x04\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_WuKong/Awaken/1678_sunwukong_03_Show3\x04\x00\x00\x00\x04\x00\x00\x00E\x01\x00\x00\x1b\x00\x00\x00ArtSkinLobbyIdleShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xf2\x00\x00\x00\x03\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\xa2\x00\x00\x00\x1a\x00\x00\x00ArtSkinLobbyShowCamera|\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringN\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_wukong/Awaken/1678_sunwukong_03_Cam\x04\x00\x00\x00\x04\x00\x00\x00\xa3\x00\x00\x00\x19\x00\x00\x00ArtSkinLobbyShowMovie~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/167_wukong/Awaken/1678_sunwukong_03_Movie\x04\x00\x00\x00\x04\x00\x00\x00Y\x00\x00\x00\x11\x00\x00\x00useNewMecanim<\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x1a\x00\x00\x00\x08\x00\x00\x00TypeSystem.Boolean\r\x00\x00\x00\x05\x00\x00\x00VTrue\x04\x00\x00\x00\x04\x00\x00\x00W\x00\x00\x00\x0f\x00\x00\x00bUnityLight<\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x1a\x00\x00\x00\x08\x00\x00\x00TypeSystem.Boolean\r\x00\x00\x00\x05\x00\x00\x00VTrue\x04\x00\x00\x00\x04\x00\x00\x00a\x00\x00\x00\x19\x00\x00\x00bUseCodeAnimComponent<\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x1a\x00\x00\x00\x08\x00\x00\x00TypeSystem.Boolean\r\x00\x00\x00\x05\x00\x00\x00VTrue\x04\x00\x00\x00\x04\x00\x00\x00f\x00\x00\x00\x08\x00\x00\x00MSAAR\x00\x00\x00\x03\x00\x00\x00\x0e\x00\x00\x00\x06\x00\x00\x00JTEnum2\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.EAntiAliasing\n\x00\x00\x00\x05\x00\x00\x00V2\x04\x00\x00\x00\x04\x00\x00\x00$\x03\x00\x00\x1a\x00\x00\x00PreloadAnimatorEffects0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xd2\x02\x00\x00\x05\x00\x00\x00\x8e\x00\x00\x00\x0b\x00\x00\x00Elementw\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringI\x00\x00\x00\x05\x00\x00\x00Vprefab_skill_effects/hero_skill_effects/167_WuKong/wukong_Sprint\x04\x00\x00\x00\x04\x00\x00\x00\x93\x00\x00\x00\x0b\x00\x00\x00Element|\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringN\x00\x00\x00\x05\x00\x00\x00Vprefab_skill_effects/hero_skill_effects/167_WuKong/wukong_Sprint_Idle\x04\x00\x00\x00\x04\x00\x00\x00\x93\x00\x00\x00\x0b\x00\x00\x00Element|\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringN\x00\x00\x00\x05\x00\x00\x00Vprefab_skill_effects/hero_skill_effects/167_WuKong/wukong_Sprint_Loop\x04\x00\x00\x00\x04\x00\x00\x00\x92\x00\x00\x00\x0b\x00\x00\x00Element{\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringM\x00\x00\x00\x05\x00\x00\x00Vprefab_skill_effects/hero_skill_effects/167_WuKong/wukong_Sprint_Run\x04\x00\x00\x00\x04\x00\x00\x00\x84\x00\x00\x00\x0b\x00\x00\x00Elementm\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String?\x00\x00\x00\x05\x00\x00\x00Vprefab_skill_effects/Dance_Effects/167/dance_03_texiao\x04\x00\x00\x00\x04\x00\x00\x00\x86\x03\x00\x00\n\x00\x00\x00LookAtF\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom1\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.CameraLookAt\x04\x00\x00\x00.\x03\x00\x00\x04\x00\x00\x00B\x01\x00\x00\n\x00\x00\x00Offset4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xfc\x00\x00\x00\x03\x00\x00\x00S\x00\x00\x00\x05\x00\x00\x00xB\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x14\x00\x00\x00\x05\x00\x00\x00V-0.05998039\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x05\x00\x00\x00y?\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x11\x00\x00\x00\x05\x00\x00\x00V1.389713\x04\x00\x00\x00\x04\x00\x00\x00Q\x00\x00\x00\x05\x00\x00\x00z@\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x12\x00\x00\x00\x05\x00\x00\x00V-2.490662\x04\x00\x00\x00\x04\x00\x00\x00B\x01\x00\x00\r\x00\x00\x00Direction4\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom\x1f\x00\x00\x00\x08\x00\x00\x00TypeUnityEngine.Vector3\x04\x00\x00\x00\xf9\x00\x00\x00\x03\x00\x00\x00T\x00\x00\x00\x05\x00\x00\x00xC\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x15\x00\x00\x00\x05\x00\x00\x00V1.831149E-07\x04\x00\x00\x00\x04\x00\x00\x00T\x00\x00\x00\x05\x00\x00\x00yC\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x15\x00\x00\x00\x05\x00\x00\x00V-8.35189E-09\x04\x00\x00\x00\x04\x00\x00\x00I\x00\x00\x00\x05\x00\x00\x00z8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V1\x04\x00\x00\x00\x04\x00\x00\x00P\x00\x00\x00\x0c\x00\x00\x00Duration8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V1\x04\x00\x00\x00\x04\x00\x00\x00R\x00\x00\x00\r\x00\x00\x00CameraFOV9\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0b\x00\x00\x00\x05\x00\x00\x00V17\x04\x00\x00\x00\x04\x00\x00\x00m\x00\x00\x00\x0f\x00\x00\x00LightConfigR\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom=\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.PrepareBattleLightConfig\x04\x00\x00\x00\x04\x00\x00\x00'
bienvengokonhoctyhentaiz=open("FILES_CODE/BIENVENGOKONHOCTY.xml",'rb')
bienvengokonhocty=bienvengokonhoctyhentaiz.read()
bienvevanxathanhentaiz=open("FILES_CODE/BIENVEVANXATHAN.xml",'rb')
bienvevanxathan=bienvevanxathanhentaiz.read()
codebienvehentaiz=open("FILES_CODE/CODEBIENVE.xml",'rb')
CODEBIENVE=codebienvehentaiz.read()
projackhentaiz=open("FILES_CODE/PROJACK.xml",'rb')
projack=projackhentaiz.read()
haste11113hentaiz=open("FILES_CODE/Haste11113.xml",'rb')
haste11113=haste11113hentaiz.read()
haste51015hentaiz=open("FILES_CODE/Haste51015.xml",'rb')
haste51015=haste51015hentaiz.read()
haste15015hentaiz=open("FILES_CODE/Haste15015.xml",'rb')
haste15015=haste15015hentaiz.read()
CODECHECKGThentaiz=open("FILES_CODE/CODECHECKGT.xml",'rb')
CODECHECKGT=CODECHECKGThentaiz.read()
CODEXMLGThentaiz = open("FILES_CODE/CODEXMLGT.xml", 'rb')
CODEXMLGT = CODEXMLGThentaiz.read()
codecheckbvhentaiz=open("FILES_CODE/CODECHECKBVXML.xml",'rb')
CODECHECKBVXML=codecheckbvhentaiz.read()
codefixdancehentaiz=open("FILES_CODE/Dance.xml",'rb')
FIXDANCE=codefixdancehentaiz.read()
codebvlilihentaiz=open("FILES_CODE/CODEBVLILI.xml",'rb')
CODEBVLILI=codebvlilihentaiz.read()
codebvyenahentaiz=open("FILES_CODE/CODEBVYENA.xml",'rb')
CODEBVYENA=codebvyenahentaiz.read()
codechecks2=open("FIX_SKIN/Airi/CHECKS2AIRI.xml",'rb')
CHECKS2AIRI=codechecks2.read()
codechecks2mod=open("FIX_SKIN/Airi/CHECKS2AIRIMOD.xml",'rb')
CHECKS2AIRIMOD=codechecks2mod.read()
codes2b1=open("FIX_SKIN/Airi/CODES2B1.xml",'rb')
CODES2B1=codes2b1.read()
codes2b1mod=open("FIX_SKIN/Airi/CODES2B1MOD.xml",'rb')
CODES2B1MOD=codes2b1mod.read()
codechecks21=open("FIX_SKIN/Airi/CHECKS21AIRI.xml",'rb')
CHECKS21AIRI=codechecks21.read()
codechecks21mod=open("FIX_SKIN/Airi/CHECKS21AIRIMOD.xml",'rb')
CHECKS21AIRIMOD=codechecks21mod.read()
codechecks22=open("FIX_SKIN/Airi/CHECKS22AIRI.xml",'rb')
CHECKS22AIRI=codechecks22.read()
codechecks22mod=open("FIX_SKIN/Airi/CHECKS22AIRIMOD.xml",'rb')
CHECKS22AIRIMOD=codechecks22mod.read()
codes1=open("FIX_SKIN/Lau/CODES1LAU.xml",'rb')
CODES1LAU=codes1.read()
codes1mod=open("FIX_SKIN/Lau/CODES1LAUMOD.xml",'rb')
CODES1LAUMOD=codes1mod.read()
codes1b1=open("FIX_SKIN/Lau/CODES1B1LAU.xml",'rb')
CODES1B1LAU=codes1b1.read()
codes1b1mod=open("FIX_SKIN/Lau/CODES1B1LAUMOD.xml",'rb')
CODES1B1LAUMOD=codes1b1mod.read()
codes1b2=open("FIX_SKIN/Lau/CODES1B2LAU.xml",'rb')
CODES1B2LAU=codes1b2.read()
codes1b2mod=open("FIX_SKIN/Lau/CODES1B2LAUMOD.xml",'rb')
CODES1B2LAUMOD=codes1b2mod.read()
actionu1=open("FIX_SKIN/Nakroth/ACTIONU1.xml",'rb')
ACTIONU1=actionu1.read()
u1mod=open("FIX_SKIN/Nakroth/U1MOD.xml",'rb')
U1MOD=u1mod.read()
actiongoc=open("FIX_SKIN/Hayate/ACTION.xml",'rb')
ACTION=actiongoc.read()
a1mod=open("FIX_SKIN/Hayate/A1MOD.xml",'rb')
A1MOD=a1mod.read()
a2mod=open("FIX_SKIN/Hayate/A2MOD.xml",'rb')
A2MOD=a2mod.read()
a3mod=open("FIX_SKIN/Hayate/A3MOD.xml",'rb')
A3MOD=a3mod.read()
s1mod=open("FIX_SKIN/Hayate/S1MOD.xml",'rb')
S1MOD=s1mod.read()
s12mod=open("FIX_SKIN/Hayate/S12MOD.xml",'rb')
S12MOD=s12mod.read()
s1b1mod=open("FIX_SKIN/Hayate/S1B1MOD.xml",'rb')
S1B1MOD=s1b1mod.read()
s215013=open("FIX_SKIN/Nakroth13/S2.xml",'rb')
S215013=s215013.read()
s215013mod=open("FIX_SKIN/Nakroth13/S2Mod.xml",'rb')
S2MOD15013=s215013mod.read()
wukongbackmod1=open("FIX_SKIN/Wukong/16707_BackMod.xml",'rb')
WUKONGBACKMOD=wukongbackmod1.read()
wukongu1b0=open("FIX_SKIN/Wukong/U1B0.xml",'rb')
WUKONGU1B0=wukongu1b0.read()
wukongu1b0mod=open("FIX_SKIN/Wukong/U1B0Mod.xml",'rb')
WUKONGU1B0MOD=wukongu1b0mod.read()
suffix_list = range(1, 41)
for suffix in suffix_list:
    mod_filename = f"FIX_SKIN/Billow/TTDA_Mod{suffix}.xml"
    with open(mod_filename, 'rb') as mod_file:
        globals()[f'TTDA_Mod{suffix}'] = mod_file.read()
    fix_filename = f"FIX_SKIN/Billow/TTDA_Fix{suffix}.xml"
    with open(fix_filename, 'rb') as fix_file:
        globals()[f'TTDA_Fix{suffix}'] = fix_file.read()
suffix_list = range(1, 7)
for suffix in suffix_list:
    mod_filename = f"FIX_SKIN/Capheny/CNDC_Mod{suffix}.xml"
    with open(mod_filename, 'rb') as mod_file:
        globals()[f'CNDC_Mod{suffix}'] = mod_file.read()
    fix_filename = f"FIX_SKIN/Capheny/CNDC_Fix{suffix}.xml"
    with open(fix_filename, 'rb') as fix_file:
        globals()[f'CNDC_Fix{suffix}'] = fix_file.read()
suffix_list = range(1, 42)
for suffix in suffix_list:
    mod_filename = f"FIX_SKIN/Bolt_Baron/TPTM_Mod{suffix}.xml"
    with open(mod_filename, 'rb') as mod_file:
        globals()[f'TPTM_Mod{suffix}'] = mod_file.read()
    fix_filename = f"FIX_SKIN/Bolt_Baron/TPTM_Fix{suffix}.xml"
    with open(fix_filename, 'rb') as fix_file:
        globals()[f'TPTM_Fix{suffix}'] = fix_file.read()
suffix_list = range(1, 20)
for suffix in suffix_list:
    mod_filename = f"FIX_SKIN/Veera/TSTS_Mod{suffix}.xml"
    with open(mod_filename, 'rb') as mod_file:
        globals()[f'TSTS_Mod{suffix}'] = mod_file.read()
    fix_filename = f"FIX_SKIN/Veera/TSTS_Fix{suffix}.xml"
    with open(fix_filename, 'rb') as fix_file:
        globals()[f'TSTS_Fix{suffix}'] = fix_file.read()
gtHasteE1 = CODEXMLGT
gtHasteE1_leave = CODEXMLGT
AABBCC = 'DiaoChan'
ngoaihinhxanhveres = b'9\t\x00\x00\x0b\x00\x00\x00ElementE\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom0\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.SkinElement\x04\x00\x00\x00\xe1\x08\x00\x00\x0b\x00\x00\x00\x10\x02\x00\x00\x14\x00\x00\x00ArtSkinPrefabLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xc4\x01\x00\x00\x03\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_2_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_2_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_2_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\xa4\x00\x00\x00\x16\x00\x00\x00ArtSkinPrefabLODEx0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00V\x00\x00\x00\x01\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\x16\x02\x00\x00\x17\x00\x00\x00ArtSkinLobbyShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xc7\x01\x00\x00\x03\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_2_Show2\x04\x00\x00\x00\x04\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_2_Show2\x04\x00\x00\x00\x04\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_2_Show2\x04\x00\x00\x00\x04\x00\x00\x00E\x01\x00\x00\x1b\x00\x00\x00ArtSkinLobbyIdleShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xf2\x00\x00\x00\x03\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\x93\x00\x00\x00\x1a\x00\x00\x00ArtSkinLobbyShowCameram\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String?\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/5208_Veres_Cam\x04\x00\x00\x00\x04\x00\x00\x00Z\x00\x00\x00\x16\x00\x00\x00CamInterpolateTime8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V7\x04\x00\x00\x00\x04\x00\x00\x00^\x00\x00\x00\x18\x00\x00\x00Cam02InterpolateTime:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V1.1\x04\x00\x00\x00\x04\x00\x00\x00`\x00\x00\x00\x1c\x00\x00\x00Cam02InterpolateDuration8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V2\x04\x00\x00\x00\x04\x00\x00\x00V\x00\x00\x00\x1a\x00\x00\x00PreloadAnimatorEffects0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\x04\x00\x00\x00\\\x00\x00\x00\n\x00\x00\x00LookAtF\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom1\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.CameraLookAt\x04\x00\x00\x00\x04\x00\x00\x00m\x00\x00\x00\x0f\x00\x00\x00LightConfigR\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom=\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.PrepareBattleLightConfig\x04\x00\x00\x00\x04\x00\x00\x00'
ngoaihinhdoveres = b'9\t\x00\x00\x0b\x00\x00\x00ElementE\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom0\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.SkinElement\x04\x00\x00\x00\xe1\x08\x00\x00\x0b\x00\x00\x00\x10\x02\x00\x00\x14\x00\x00\x00ArtSkinPrefabLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xc4\x01\x00\x00\x03\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_3_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_3_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\x94\x00\x00\x00\x0b\x00\x00\x00Element}\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringO\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_3_LOD2\x04\x00\x00\x00\x04\x00\x00\x00\xa4\x00\x00\x00\x16\x00\x00\x00ArtSkinPrefabLODEx0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00V\x00\x00\x00\x01\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\x16\x02\x00\x00\x17\x00\x00\x00ArtSkinLobbyShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xc7\x01\x00\x00\x03\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_3_Show2\x04\x00\x00\x00\x04\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_3_Show2\x04\x00\x00\x00\x04\x00\x00\x00\x95\x00\x00\x00\x0b\x00\x00\x00Element~\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.StringP\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/Component/5208_Veres_RT_3_Show2\x04\x00\x00\x00\x04\x00\x00\x00E\x01\x00\x00\x1b\x00\x00\x00ArtSkinLobbyIdleShowLOD0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\xf2\x00\x00\x00\x03\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00N\x00\x00\x00\x0b\x00\x00\x00Element7\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String\t\x00\x00\x00\x05\x00\x00\x00V\x04\x00\x00\x00\x04\x00\x00\x00\x93\x00\x00\x00\x1a\x00\x00\x00ArtSkinLobbyShowCameram\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.String?\x00\x00\x00\x05\x00\x00\x00VPrefab_Characters/Prefab_Hero/520_Veres/5208_Veres_Cam\x04\x00\x00\x00\x04\x00\x00\x00Z\x00\x00\x00\x16\x00\x00\x00CamInterpolateTime8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V7\x04\x00\x00\x00\x04\x00\x00\x00^\x00\x00\x00\x18\x00\x00\x00Cam02InterpolateTime:\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\x0c\x00\x00\x00\x05\x00\x00\x00V1.1\x04\x00\x00\x00\x04\x00\x00\x00`\x00\x00\x00\x1c\x00\x00\x00Cam02InterpolateDuration8\x00\x00\x00\x03\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTPri\x19\x00\x00\x00\x08\x00\x00\x00TypeSystem.Single\n\x00\x00\x00\x05\x00\x00\x00V2\x04\x00\x00\x00\x04\x00\x00\x00V\x00\x00\x00\x1a\x00\x00\x00PreloadAnimatorEffects0\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTArr\x1b\x00\x00\x00\x08\x00\x00\x00TypeSystem.String[]\x04\x00\x00\x00\x04\x00\x00\x00\\\x00\x00\x00\n\x00\x00\x00LookAtF\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom1\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.CameraLookAt\x04\x00\x00\x00\x04\x00\x00\x00m\x00\x00\x00\x0f\x00\x00\x00LightConfigR\x00\x00\x00\x02\x00\x00\x00\r\x00\x00\x00\x06\x00\x00\x00JTCom=\x00\x00\x00\x08\x00\x00\x00TypeAssets.Scripts.GameLogic.PrepareBattleLightConfig\x04\x00\x00\x00\x04\x00\x00\x00'

#=========================================================================================================================                        
def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)

#=========================================================================================================================                        
def giai(a):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcd", ["help", "compress", "decompress"])
    except getopt.GetoptError:
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            sys.exit()
    if not args:
        args = a
        anti = b''
        input_blob = None
        with open(args, "rb") as f:
            if b'"Jg' in f.read():
                return
        with open(args, "rb") as f:
            input_blob = f.read()
        if opts:
            opt, arg = opts[0]
        else:
            pos = input_blob.find(b"\x28\xb5\x2f\xfd")
            if pos != -1:
                opt = "-d"
                input_blob = input_blob[pos:]
            else:
                opt = "-c"
        zstd_mode = None
        try:
            if opt in ("-c", "--compress"):
                zstd_mode = "compress"
                output_blob = bytearray(pyzstd.compress(input_blob, ZSTD_LEVEL, pyzstd.ZstdDict(ZSTD_DICT, True)))
                output_blob[0:0] = len(input_blob).to_bytes(4, byteorder="little", signed=False)
                output_blob[0:0] = b"\x22\x4a\x00\xef"
                new = random.randbytes(0)
                anti += new
            elif opt in ("-d", "--decompress"):
                input_blob = input_blob[input_blob.find(b"\x28\xb5\x2f\xfd"):]
                zstd_mode = "decompress"
                output_blob = pyzstd.decompress(input_blob, pyzstd.ZstdDict(ZSTD_DICT, True))
            output_path = args
            with open(output_path, "wb") as output_file:
                output_file.write(output_blob)
            with open(output_path, "ab") as output_file:
                output_file.write(anti)
        except pyzstd.ZstdError:
            pass
    return
    
#=========================================================================================================================                        
def Track_Guid_Skill(file_path):
    with open(file_path, "rb") as r0:
        context = r0.read()
        Tracks = re.findall(rb'<Track trackName="(.*?)</Track>', context, re.DOTALL)
        if Tracks:
            for i in range(len(Tracks)):
                trackName = Tracks[i]
                guid_track = (re.findall(rb'guid="(.+?)" enabled', trackName)[0]).decode()
                guid_true = str.encode(f'id="{i}" guid="{guid_track}"')
                IdGuidFalse = re.findall(str.encode(rf'id="(.+?)" guid="{guid_track}"'), context)
                if IdGuidFalse:
                    for j in range(len(IdGuidFalse)):
                        j = IdGuidFalse[j].decode()
                        guid_false = str.encode(f'id="{j}" guid="{guid_track}"')
                        context = context.replace(guid_false, guid_true)
    with open(file_path, "wb") as w0:
        w0.write(context)

#=========================================================================================================================                            
def ArtSkinLobbyIdleShowLOD(data4):
    a=camSkin.find(b'\x00ArtSkinLobbyIdleShowLOD')-7
    a10=camSkin.find(b'\x00ArtSkinLobbyIdleShowLOD')-3
    a3=camSkin[a:a+8]
    a4=a3[4:]
    a2=camSkin[a:a+4]
    vitri=int.from_bytes(a2,byteorder='little')
    ne=camSkin[vitri:]
    vitri2=int.from_bytes(a4,byteorder='little')
    a5=camSkin[a:a+vitri]
    a25=camSkin[a10:a10+vitri2]
    a22=camSkin[a10:a10+vitri2].replace(b'\x00ArtSkinLobbyIdleShowLOD',b'\x00ArtLobbyIdleShowLOD')
    a13=len(a22).to_bytes(4,byteorder='little')+a22[4:]
    code=a5.replace(a25,a13)
    data4=len(code).to_bytes(4,byteorder='little')+code[4:]+ne
    return data4

#=========================================================================================================================                        
def ArtPrefabLODnew(data):
    a=ab.find(b'\x00ArtPrefabLOD')-7
    a2=ab[a:a+4]
    a3=ab[a:a+5]
    a4=a3[4:5]#so 10
    vitri=int.from_bytes(a2,byteorder='little')
    data=ab[a:a+vitri]
    return data

#=========================================================================================================================                        
def ArtPrefabLODExnew(data4):
    a=ab.find(b'\x00ArtPrefabLODEx')-7
    a2=ab[a:a+4]
    a3=ab[a:a+5]
    a4=a3[4:5]#so 10
    vitri=int.from_bytes(a2,byteorder='little')
    data4=ab[a:a+vitri]
    return data4

#=========================================================================================================================                        
def ArtSkinPrefabLODnew(data3):
    a=ab.find(b'\x00ArtSkinPrefabLOD')-7
    a10=ab.find(b'\x00ArtSkinPrefabLOD')-3
    a3=ab[a:a+8]
    a4=a3[4:]
    a2=ab[a:a+4]
    vitri=int.from_bytes(a2,byteorder='little')
    vitri2=int.from_bytes(a4,byteorder='little')
    a5=ab[a:a+vitri]
    a25=ab[a10:a10+vitri2]
    a22=ab[a10:a10+vitri2].replace(b'\x00ArtSkinPrefabLOD',b'\x00ArtPrefabLOD')
    a13=len(a22).to_bytes(4,byteorder='little')+a22[4:]
    code=a5.replace(a25,a13)
    data3=len(code).to_bytes(2,byteorder='little')+code[2:]
    return data3 

#=========================================================================================================================                        
def ArtSkinPrefabLODExnew(data2):
    a=ab.find(b'\x00ArtSkinPrefabLODEx')-7
    a10=ab.find(b'\x00ArtSkinPrefabLODEx')-3
    a3=ab[a:a+8]
    a4=a3[4:]
    a2=ab[a:a+4]
    vitri=int.from_bytes(a2,byteorder='little')
    vitri2=int.from_bytes(a4,byteorder='little')
    a5=ab[a:a+vitri]
    a25=ab[a10:a10+vitri2]
    a22=ab[a10:a10+vitri2].replace(b'\x00ArtSkinPrefabLODEx',b'\x00ArtPrefabLODEx')
    a13=len(a22).to_bytes(4,byteorder='little')+a22[4:]
    code=a5.replace(a25,a13)
    data2=len(code).to_bytes(4,byteorder='little')+code[4:]
    return data2

#=========================================================================================================================                        
def bienve(data):#Prefab_Skill_Effects/Hero_Skill_Effects/Name_Hero/ID_Skin/
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    IDBV1=IDCHECK.encode()
    codenew1=codenew.replace(b'guid="tentuong',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    codenew3=codenew1.replace(b'Name_Hero',teninfo23)
    data=codenew3.replace(b'ID_Skin',IDBV1)
    return data

#=========================================================================================================================                        
def bienve1(data):#Prefab_Skill_Effects/Hero_Skill_Effects/Name_Hero/ID_Skin/
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    IDBV1=IDCHECK.encode()
    codenew1=codenew.replace(b'guid="tentuong',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    data=codenew1.replace(b'Prefab_Skill_Effects/Hero_Skill_Effects/Name_Hero/ID_Skin/',b'prefab_skill_effects/component_effects/16707/16707_5/')
    return data

#=========================================================================================================================                        
def bienvecheck(data):
    teninfobv1=NAME_HERO[4:].encode()
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    CODECHECKBIENVE= CODECHECKBVXML
    codenew=CODECHECKBIENVE.replace(b'value="ID_Hero',b'value="'+IDBV)
    data=codenew.replace(b'guid="Cre',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    return data

#=========================================================================================================================                        
def hasteE1(data):
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    IDBV1=IDCHECK.encode()
    codenew1=codenew.replace(b'guid="tentuong',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    codenew3=codenew1.replace(b'Name_Hero',teninfo23)
    data=codenew3.replace(b'ID_Skin',IDBV1)
    return data 
#=========================================================================================================================                        
def hasteE1check(data):
    teninfobv1=NAME_HERO[4:].encode()
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    codenew=data.replace(b'value="ID_Hero',b'value="'+IDBV)
    data=codenew.replace(b'guid="Cre',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    return data
    
#=========================================================================================================================                        
def hasteE1_leave(data):
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    IDBV1=IDCHECK.encode()
    codenew1=codenew.replace(b'guid="tentuong',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    codenew3=codenew1.replace(b'Name_Hero',teninfo23)
    data=codenew3.replace(b'ID_Skin',IDBV1)
    return data 

#=========================================================================================================================                        
def hasteE1check_leave(data):
    teninfobv1=NAME_HERO[4:].encode()
    teninfo23=NAME_HERO.encode()
    IDBV=IDCHECK[:3].encode()
    codenew=data.replace(b'value="ID_Hero',b'value="'+IDBV)
    data=codenew.replace(b'guid="Cre',b'guid="'+AABBCC.encode('utf-8') + b'_'+teninfo23)
    return data
    
#=========================================================================================================================                        
def Function_Track_Guid_AddGetHoliday(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        with open(file_path, "rb") as r0:
            context = r0.read()
            Tracks = re.findall(rb'<Track trackName="(.*?)</Track>', context, re.DOTALL)
            if Tracks:
                for i in range(len(Tracks)):
                    trackName = Tracks[i]
                    guid_track = (re.findall(rb'guid="(.+?)" enabled', trackName)[0]).decode()
                    guid_true = str.encode(f'id="{i}" guid="{guid_track}"')
                    IdGuidFalse = re.findall(str.encode(rf'id="(.+?)" guid="{guid_track}"'), context)
                    if IdGuidFalse:
                        for j in range(len(IdGuidFalse)):
                            j = IdGuidFalse[j].decode()
                            guid_false = str.encode(f'id="{j}" guid="{guid_track}"')
                            context = context.replace(guid_false, guid_true)
        with open(file_path, "wb") as w0:
            w0.write(context)

#=========================================================================================================================                                    
def AddGetHolidayResourcePath(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        with open(file_path, "rb") as r0:
            context = r0.read()
            tracks = re.findall(rb'(<Track .*?</Track>)', context, re.DOTALL)
            if tracks:
                for track in tracks:
                    if isinstance(track, bytes):
                        if re.search(rb'enabled="false"', track):
                            continue
                        resource_match = re.search(rb'<String name="(.*?)" value="prefab_skill_effects(.*?)"', track)
                        resource_name = resource_match.group(2).decode() if resource_match else ""
                        short_name = resource_name.split("/")[-1] if resource_name else ""
                        getholiday = f'''<Track trackName="DiaoChan[FixEffectsSkin]" eventType="GetHolidayResourcePathTick" guid="MOD-BY-DiaoChan-ANCAPLAMCHO" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">\n      <Event eventName="GetHolidayResourcePathTick" time="0.000" isDuration="false" guid="DiaoChan">\n        <String name="holidayResourcePathPrefix" value="prefab_skill_effects{resource_name}" refParamName="" useRefParam="false" />\n        <String name="outPathParamName" value="{short_name}" refParamName="" useRefParam="false" />\n        <String name="outSoundEventParamName" value="" refParamName="" useRefParam="false" />\n      </Event>\n    </Track>\n    '''
                        if resource_name:
                            updated_track = re.sub(rb'<String name="(.*?)" value="prefab_skill_effects.*?" refParamName="" useRefParam="false" />', f'<String name="\\1" value="" refParamName="{short_name}" useRefParam="true" />'.encode(), track)
                            combined_tracks = getholiday.encode() + updated_track
                            context = context.replace(track, combined_tracks)
        with open(file_path, "wb") as w0:
            w0.write(context)
            
#=========================================================================================================================                        
while True:
    def main(numbers):
        results = []
        for number in numbers:
            number_str = str(number)
            if len(number_str) == 5:
                results.append(number)
            else:
                print(f"\033[1;91mThe Number {number} Is Invalid. Please Enter A Number With 4 Or 5 Digits.\033[0m")
                return None
        return results
    try:
        chonchedo = input("\n\033[1;97m[\033[1;92m?\033[1;97m] Cách Thức Nhập Id Để Mod\n[\033[1;92m1\033[1;97m] Qua Nhập Id\n[\033[1;92m2\033[1;97m] Qua Input_Id.txt\n\033[1;92m==>\033[1;97m ")
        if chonchedo == "1":
            while True:        	
                input_numbers = input("\n\033[1;97m[\033[1;92m?\033[1;97m]\033[1;92m ID Skin: ")
                if not input_numbers:
                    print("[\033[1;91m!\033[1;97m] \033[1;91mChưa Có Id Trong File, Hãy Thêm Vào Trước Khi Tiếp Tục!\033[1;97m")
                else:
                    break                    
        if chonchedo == "2":   
            if not os.path.exists("Input_Id.txt"):
                with open("Input_Id.txt", "w") as file:
                    file.write("")        	
            while True:
                input("\033[1;97m[\033[1;92m!\033[1;97m]\033[1;92m Hãy Thêm Id Cần Mod Vào Input_Id.txt, Thêm Rồi Thì Nhấn Enter\033[1;97m")                
                print("\n")
                with open("Input_Id.txt") as f:
                    input_numbers = f.read().strip()
                if not input_numbers:
                    print("[\033[1;91m!\033[1;97m] \033[1;91mChưa Có Id Ở File Input.txt, Hãy Thêm Vào Trước Khi Tiếp Tục!\033[1;97m")
                else:
                    break
        if chonchedo == "1":                    
            numbers = [int(num) for num in input_numbers.split()]
        if chonchedo == "2":        
            numbers = [int(num) for num in input_numbers.split('\n')]    
    except ValueError:
        print("\033[1;91mInvalid input. Please enter numbers only.\033[0m")
        continue
    results = main(numbers)
    if results is None:
        continue
    result_str = ' '.join(map(str, results))
    IDD = result_str
    IDMODSKIN = IDD.split()
    IDMODSKIN1 = IDD.split()
    DANHSACH = IDD.split()
    try:
        with open(f'Resources/{version}/Databin/Client/Actor/heroSkin.bytes', 'rb') as f:
            a = f.read()
        if b'"J\x00' in a:
            giai(f'Resources/{version}/Databin/Client/Actor/heroSkin.bytes')
    except FileNotFoundError:
        print("\033[1;91mFile heroSkin.bytes not found.\033[0m")
        break
    map1 = f'Resources/{version}/Languages/VN_Garena_VN/languageMap.txt'
    map2 = f'Resources/{version}/Languages/VN_Garena_VN/languageMap_Newbie.txt'
    map3 = f'Resources/{version}/Languages/VN_Garena_VN/languageMap_WorldConcept.txt'
    map4 = f'Resources/{version}/Languages/VN_Garena_VN/languageMap_Xls.txt'
    map5 = f'Resources/{version}/Languages/VN_Garena_VN/lanMapIncremental.txt'
    FILES_MAP = [map1, map2, map3, map4, map5]
    for mapp in FILES_MAP:
        try:
            with open(mapp, 'rb') as f:
                a = f.read()
            if b'"J\x00' in a:
                giai(mapp)
        except FileNotFoundError:
            print(f"\033[1;91mFile {mapp} not found.\033[0m")
            continue
    TENSKIN = []
    for mapp in FILES_MAP:
        for i in DANHSACH:
            with open(mapp, 'rb') as f:
                rpl = f.read()
            with open(f'Resources/{version}/Databin/Client/Actor/heroSkin.bytes', 'rb') as f:
                RPL = f.read()
            i = int(i)
            IDFIND = RPL.find(i.to_bytes(4, 'little') + int(str(i)[:3]).to_bytes(4, 'little'))
            if IDFIND != -1:
                VT = RPL[IDFIND+12:IDFIND+31]
                VT1 = rpl.find(VT)
                VT2 = rpl.find(b'\r', VT1)
                VTR = rpl[VT1:VT2]
                VT = RPL[IDFIND+40:IDFIND+59]
                VT1 = rpl.find(VT)
                VT2 = rpl.find(b'\r', VT1)
                VTR_SKIN = rpl[VT1:VT2]
                A = VTR[22:]
                B = VTR_SKIN[22:]
                sanitized_input = ((A + b' ' + B).decode())
                sanitized_input = ''.join(char for char in sanitized_input if char not in ['/', '\\', ':', '*', '?', '"', '<', '>', '|'])
                TENSKIN.append(sanitized_input)
    aaabbbcccnnn = ''
    for sanitized_input in TENSKIN:
        if sanitized_input == ' ':
            continue
        if '[ex]' in sanitized_input:
            print("\033[1;91mTHIS SKIN DOES NOT EXIST\033[0m")
            continue
        else:
            print("\033[1;97m" + sanitized_input + "\033[0m")
            aaabbbcccnnn = sanitized_input
            sanitized_input = sanitized_input + " [DiaoChan]"
    sanitized_input = aaabbbcccnnn + " [DiaoChan]"
    if len(DANHSACH) > 1:
        sanitized_input = input("\033[1;97m[\033[1;91m?\033[1;97m] Enter Skin Pack Name: ") + " [DiaoChan]"
        
    #===================================================================================================================
    base_path = f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/"
    directories = ["Actor", "Shop", "Sound", "Skill", "Character", "Motion", "Global", "Huanhua"]
    for directory in directories:
        os.makedirs(os.path.join(base_path, directory), exist_ok=True)
    os.makedirs(f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/", exist_ok=True)
    
    #===================================================================================================================
    files_to_copy = [("file_actor_mod", f"Resources/{version}/Databin/Client/Actor/heroSkin.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Actor/heroSkin.bytes"),("file_shop_mod", f"Resources/{version}/Databin/Client/Shop/HeroSkinShop.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Shop/HeroSkinShop.bytes"),("file_sound_mod1", f"Resources/{version}/Databin/Client/Sound/BattleBank.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Sound/BattleBank.bytes"),("file_sound_mod2", f"Resources/{version}/Databin/Client/Sound/ChatSound.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Sound/ChatSound.bytes"),("file_sound_mod3", f"Resources/{version}/Databin/Client/Sound/HeroSound.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Sound/HeroSound.bytes"),("file_sound_mod4", f"Resources/{version}/Databin/Client/Sound/LobbyBank.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Sound/LobbyBank.bytes"),("file_sound_mod5", f"Resources/{version}/Databin/Client/Sound/LobbySound.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Sound/LobbySound.bytes"),("file_mod_skill1", f"Resources/{version}/Databin/Client/Skill/liteBulletCfg.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Skill/liteBulletCfg.bytes"),("file_mod_skill2", f"Resources/{version}/Databin/Client/Skill/skillmark.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Skill/skillmark.bytes"),("file_mod_Character", f"Resources/{version}/Databin/Client/Character/ResCharacterComponent.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Character/ResCharacterComponent.bytes"),("file_mod_version", f"Resources/{version}/version.txt", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/version.txt"),("file_mod_Modtion", f"Resources/{version}/Databin/Client/Motion/ResSkinMotionBaseCfg.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Motion/ResSkinMotionBaseCfg.bytes"),("file_mod_vien", f"Resources/{version}/Databin/Client/Global/HeadImage.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Global/HeadImage.bytes"),("huanhua_mod", f"Resources/{version}/Databin/Client/Huanhua/ResKillBillboardCfg.bytes", f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Huanhua/ResKillBillboardCfg.bytes")]
    for var_name, src, dst in files_to_copy:
        globals()[var_name] = dst
        shutil.copy2(src, dst)
    for var_name, _, dst in files_to_copy:
        if var_name not in ["file_mod_version", "file_actor_mod"]:
            giai(dst)
    Sound_Files = f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Sound"
    with zipfile.ZipFile(f'Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/CommonActions.pkg.bytes') as f:
        f.extractall(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/')
        files = ["Born.xml","Dance.xml","DanceBullet.xml","Back.xml","HasteE1.xml","HasteE1_leave.xml"]
        for file in files:
            giai(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/{file}')
        f.close()
    #===================================================ICON_BAC================================================================
    for IDMODSKIN in IDMODSKIN:
        SKINEOV = ''
        if IDMODSKIN == '13311':
            SKINEOV = "r"
        if IDMODSKIN == '16707':
            SKINEOV = "b"
        if IDMODSKIN == '15412':
            SKINEOV = "y"
        if IDMODSKIN == '51015':
            SKINEOV = "l"            
             
        nhap_id = IDMODSKIN
        IDCHECK = IDMODSKIN
        IDSOUND_S = IDMODSKIN
        phukien = ''
        phukienv = ''
        if IDCHECK == '52007':
            phukien1 = input('\033[1;97m[\033[1;91m?\033[1;97m] Mod Component:\n\033[1;97m [1] \033[1;92mGreen\n\033[1;97m [2] \033[1;92mRed\n\033[1;97m [3] \033[1;92mNo Mod Component\n\033[1;97m[•] INPUT: ')
            if phukien1 == "1":
               phukien = 'xanh'
            if phukien1 == "2":
               phukien = 'do'
        if IDCHECK == '13311':
            phukien1v = '3'#input('\033[1;97m[\033[1;91m?\033[1;97m] Mod Component:\n\033[1;97m [1] \033[1;92mYellow\n\033[1;97m [2] \033[1;92mRed\n\033[1;97m [3] \033[1;92mNo Mod Component\n\033[1;97m[•] INPUT: ')
            if phukien1v == "1":
               phukienv = 'vangv'
            if phukien1v == "2":
               phukienv = 'dov'
        if IDSOUND_S[3:4] == '0':
            IDSOUND_S=IDSOUND_S[:3]+IDSOUND_S[4:]
        IDSOUND1=IDSOUND_S[3:]
        IDSOUND12=IDSOUND1.encode()
        IDSOUND = b"_Skin" + IDSOUND12
        IDINFO=int(IDMODSKIN)+1
        IDINFO=str(IDINFO)
        if str(IDINFO)[3:4] == '0':
            IDINFO=IDINFO[:3]+IDINFO[4:]
        IDINFO=str(IDINFO)
        print("\033[1;97m[\033[1;92m•\033[1;97m] Modifying ID " + IDCHECK)                               
        #=========================================================================================================================            
        if IDCHECK in ["16707"]:            
            duongdan = file_actor_mod
            try:
                with open(duongdan, 'rb') as f:
                    codenew = f.read()        
                codenew = codenew.replace(iconngokhongevo1, iconngokhongevo5)        
                with open(duongdan, 'wb') as f:
                    f.write(codenew)       
            except:
                pass 
            duongdan2 = file_shop_mod
            try:
                with open(duongdan2, 'rb') as f:
                    codenew = f.read()        
                codenew = codenew.replace(bacngokhongevo1, bacngokhongevo5)        
                with open(duongdan2, 'wb') as f:
                    f.write(codenew)        
            except:
                pass  
        #=========================================================================================================================            
        if IDCHECK in ["13311"]:      
            duongdan = file_actor_mod
            try:
                with open(duongdan, 'rb') as f:
                    codenew = f.read()        
                codenew = codenew.replace(iconvalheinevo1, iconvalheinevo5)        
                with open(duongdan, 'wb') as f:
                    f.write(codenew)        
            except:
                pass 
            duongdan2 = file_shop_mod
            try:
                with open(duongdan2, 'rb') as f:
                    codenew = f.read()        
                codenew = codenew.replace(bacvalheinevo1, bacvalheinevo5)        
                with open(duongdan2, 'wb') as f:
                    f.write(codenew)        
            except:
                pass 

        #=========================================================================================================================                            
        ID = IDCHECK
        IDB = int(ID).to_bytes(4, byteorder="little")
        IDH = int(ID[0:3]).to_bytes(4, byteorder="little")
        Files = [file_actor_mod, file_shop_mod]
        a = 1
        for File in Files:
            All = []
            Skin = ""
            file = open(File, "rb")
            Code = file.read()
            Find= -10
            while True:
                Find = Code.find(b"\x00\x00"+IDH, Find+10)
                if Find == -1: break
                elif str(int.from_bytes(Code[Find-2:Find], byteorder="little"))[0:3] == ID[0:3]:
                    VT2 = int.from_bytes(Code[Find-6:Find-4], byteorder="little")
                    Code2 = Code[Find-6:Find-6+VT2]
                    All.append(Code2)
                    if Code2.find(IDB) != -1: Skin=Code2
            if Skin == "":
                IDNew = IDCHECK[:3] + "00"
                IDK = int(IDNew).to_bytes(4, byteorder="little")
                IDH2 = int(IDNew[0:3]).to_bytes(4, byteorder="little")
                Find = Code.find(IDK+IDH2)
                Sum = int.from_bytes(Code[Find-4:Find-2], byteorder="little")
                Skin = Code[Find-4:Find-4+Sum]                    
            for Id in All:
                Cache = Skin.replace(Skin[4:6], Id[4:6], 1)
                Cache = Cache.replace(Cache[35:44], Id[35:40]+Cache[40:44],1)
                Hero = hex(int(ID[0:3]))[2:] 
                if len(Hero) == 3: Hero = Hero[1:3] + "0" + Hero[0]
                else: Hero+="00"
                Hero += "0000"
                Hero = bytes.fromhex(Hero)
                Cache = Cache.replace(Cache[8:12],Hero,1)
                if File == Files[0]:
                    if Id == All[0]:
                        ID30 = b"\x07\x00\x00\x0030" + bytes(ID[0:3] + "0", "utf8") + b"\x00"
                        XYZ = Cache[64]
                        ID0 = Cache[64: 68 + XYZ]
                        Cache = Cache.replace(ID0, ID30, 1)
                        VT = Id.find(b"Hero_")
                        NumHero = Id[VT - 4]
                        Hero = Id[VT - 4: VT + NumHero]
                        Cache = Cache.replace(b"jpg\x00\x01\x00\x00\x00\x00", b"jpg\x00" + Hero)
                        Full = Cache.count(Hero)
                        if Full > 1:
                            Cache = Cache.replace(b"jpg\x00" + Hero, b"jpg\x00\x01\x00\x00\x00\x00", Full - 1)
                        EndTheCode = hex(len(Cache))
                        if len(EndTheCode) == 5:
                            EndTheCode = EndTheCode[3:5] + "0" + EndTheCode[2:3]
                        else:
                            EndTheCode = EndTheCode[4:6] + EndTheCode[2:4]
                        EndTheCode = bytes.fromhex(EndTheCode)
                        Cache = Cache.replace(Cache[0:2], EndTheCode, 1)
                Code = Code.replace(Id, Cache, 1)
                dieukienmod1=[]
                dieukienmod1.append(Cache)
                for dieukienmod2 in dieukienmod1:
                    if b"Hero" in dieukienmod2:
                         dieukienmod = dieukienmod2
            file = open(File, "wb")
            W = file.write(Code)                
            file.close()
            
        #=========================================================================================================================            
        if IDCHECK in ["15412"]:      
            duongdan = file_actor_mod
            try:
                with open(duongdan, 'rb') as f:
                    codenew = f.read()        
                codenew = codenew.replace(icon154, icon154fix)        
                with open(duongdan, 'wb') as f:
                    f.write(codenew)        
            except:
                pass                 
                  
        #======================================================AM_THANH_DATABIN=============================================================
        if IDCHECK == "53002" or b"Skin_Icon_SoundEffect" in dieukienmod or b"Skin_Icon_Dialogue" in dieukienmod:
            skin_id_input = IDMODSKIN
            sound_directory = Sound_Files
            sound_files = os.listdir(sound_directory)

            all_skin_ids = []
            for i in range(99):
                if i < 10:
                    i = "0" + str(i)
                all_skin_ids.append(b"\x00" + int(skin_id_input[0:3] + str(i)).to_bytes(4, byteorder="little"))

            initial_skin_id = all_skin_ids[0]
            selected_skin_id = all_skin_ids[int(skin_id_input[3:])]

            all_skin_ids.remove(selected_skin_id)
            all_skin_ids.remove(initial_skin_id)

            for sound_file_name in sound_files:
                with open(os.path.join(sound_directory, sound_file_name), "rb") as sound_file:
                    sound_data = sound_file.read()

                if skin_id_input == "13311":
                    if sound_file_name == 'BattleBank.bytes':
                        sound_data = sound_data.replace(b'\x9dO\x14', b'\xff3\x00').replace(b'\x9eO\x14', b'\xff3\x00').replace(b'\x9fO\x14', b'\xff3\x00').replace(b'\xa0O\x14', b'\xff3\x00')
                    if sound_file_name == 'ChatSound.bytes':
                        sound_data = sound_data.replace(b'\x9fO\x14', b'\xff3\x00')
                    if sound_file_name == 'HeroSound.bytes':
                        sound_data = sound_data.replace(b'\x9fO\x14', b'\xff3\x00').replace(b'\xa0O\x14', b'\xff3\x00')
                    if sound_file_name == 'LobbyBank.bytes':
                        sound_data = sound_data.replace(b'\xa0O\x14', b'\xff3\x00')
                    if sound_file_name == 'LobbySound.bytes':
                        sound_data = sound_data.replace(b'\xa0O\x14', b'\xff3\x00')

                if skin_id_input == "16707":
                    if sound_file_name == 'BattleBank.bytes':
                        sound_data = sound_data.replace(b'/~\x19', b'CA\x00').replace(b'0~\x19', b'CA\x00').replace(b'1~\x19', b'CA\x00')
                    if sound_file_name == 'ChatSound.bytes':
                        sound_data = sound_data.replace(b'0~\x19', b'CA\x00')
                    if sound_file_name == 'HeroSound.bytes':
                        sound_data = sound_data.replace(b'0~\x19', b'CA\x00').replace(b'1~\x19', b'CA\x00')
                    if sound_file_name == 'LobbyBank.bytes':
                        sound_data = sound_data.replace(b'0~\x19', b'CA\x00')
                    if sound_file_name == 'LobbySound.bytes':
                        sound_data = sound_data.replace(b'0~\x19', b'CA\x00')

                if sound_file_name != "CoupleSound.bytes":
                    for skin_id in all_skin_ids:
                        skin_id += b"\x00" * 8
                        sound_data = sound_data.replace(skin_id, b"\x0000" + b"\x00" * 10)
                else:
                    for skin_id in all_skin_ids:
                        skin_id += b"\x02\x00\x00\x00\x01"
                        sound_data = sound_data.replace(skin_id, b"\x0000\x00\x00\x02\x00\x00\x00\x01")

                if sound_data.find(selected_skin_id) != -1:
                    if sound_file_name != "CoupleSound.bytes":
                        sound_data = sound_data.replace(initial_skin_id + b"\x00" * 8, b"\x0000" + b"\x00" * 10)
                        sound_data = sound_data.replace(selected_skin_id + b"\x00" * 8, initial_skin_id + b"\x00" * 8)
                    else:
                        sound_data = sound_data.replace(initial_skin_id + b"\x02\x00\x00\x00\x01", b"\x0000\x00\x00\x02\x00\x00\x00\x01")
                        sound_data = sound_data.replace(selected_skin_id + b"\x02\x00\x00\x00\x01", initial_skin_id + b"\x02\x00\x00\x00\x01")

                with open(os.path.join(sound_directory, sound_file_name), "wb") as sound_file:
                    sound_file.write(sound_data)
                    
        #=======================================================Skill_Databin_Litebullet============================================================
        if IDCHECK == "53002" or b"Skin_Icon_Skill" in dieukienmod or b"Skin_Icon_BackToTown" in dieukienmod:
            file_paths = [file_mod_skill1]
            matching_files = []
            user_id = IDMODSKIN
            user_id_bytes = bytes(f"fects/{user_id[0:3]}_", "utf8")
            for file in file_paths:
                if user_id_bytes in open(file, "rb").read():
                    matching_files.append(file)
            for file in matching_files:
                if user_id == '13311':
                    with open(file, "rb") as f:
                        code_content = f.read()
                        code_content = code_content.replace(b"prefab_skill_effects/hero_skill_effects/133_direnjie/",
                                                              b"prefab_skill_effects/component_effects/13311/13311_5/")
                    with open(file, "wb") as f:
                        f.write(code_content)
                    break
                modified_codes = []
                buffer_codes = []
                with open(file, "rb") as f:
                    begin_content = f.read(140)
                    while True:
                        data_length = f.read(2)
                        if data_length == b"":
                             break
                        section_length = data_length[0] + data_length[1] * 256 + 2
                        code_section = data_length + f.read(section_length)
                        if user_id_bytes in code_section:
                             modified_codes.append(code_section)
                for code_section in modified_codes:
                    start_index = code_section.find(user_id_bytes) + 6
                    end_index = code_section.find(b"/", start_index) + 1
                    hero_name = code_section[start_index:end_index]
                    code_section = code_section.replace(b"Prefab_Skill_Effects/Hero_Skill_Effects",b"prefab_skill_effects/hero_skill_effects")
                    code_section = code_section.replace(b"hero_skill_effects/" + hero_name,b"hero_skill_effects/" + hero_name + bytes(user_id + "/", "utf"))
                    offset = code_section.find(b"prefab_skill_effects") - 4
                    length_change = bytes.fromhex(hex(code_section[offset] + len(user_id) + 1)[2:]) + b"\x00" * 3
                    code_section = code_section.replace(code_section[offset:offset + 4], length_change)
                    target_length = hex(len(code_section) - 4)[2:]
                    if len(target_length) == 3:
                        target_length = target_length[1:3] + "0" + target_length[0]
                    elif len(target_length) == 2:
                        target_length += "00"
                    target_length = bytes.fromhex(target_length)
                    code_section = code_section.replace(code_section[0:2], target_length, 1)
                    buffer_codes.append(code_section)
                modified_content = open(file, "rb").read()
                for index in range(len(modified_codes)):
                    modified_content = modified_content.replace(modified_codes[index], buffer_codes[index], 1)
                with open(file, "wb") as f:
                    f.write(modified_content)
                       
        #=======================================================Skill_Databin_SkillMark============================================================
        if IDCHECK[:3] in ["119", "127", "141", "124", "162", "166", "173", "177", "132", "199", "154", "528", "531", "538", "540"]:
            if b"Skin_Icon_Skill" in dieukienmod or b"Skin_Icon_BackToTown" in dieukienmod:
                file_paths = [file_mod_skill2]
                matching_files = []
                user_id = IDMODSKIN
                user_id_bytes = bytes(f"fects/{user_id[0:3]}_", "utf8")
                for file in file_paths:
                    if user_id_bytes in open(file, "rb").read():
                        matching_files.append(file)
                for file in matching_files:
                    modified_codes = []
                    buffer_codes = []
                    with open(file, "rb") as f:
                        begin_content = f.read(140)
                        while True:
                            data_length = f.read(2)
                            if data_length == b"":
                                break
                            section_length = data_length[0] + data_length[1] * 256 + 2
                            code_section = data_length + f.read(section_length)
                            if user_id_bytes in code_section:
                                modified_codes.append(code_section)
                    for code_section in modified_codes:
                        start_index = code_section.find(user_id_bytes) + 6
                        end_index = code_section.find(b"/", start_index) + 1
                        hero_name = code_section[start_index:end_index]
                        code_section = code_section.replace(b"Prefab_Skill_Effects/Hero_Skill_Effects",b"prefab_skill_effects/hero_skill_effects")
                        code_section = code_section.replace(b"hero_skill_effects/" + hero_name,b"hero_skill_effects/" + hero_name + bytes(user_id + "/", "utf"))
                        offset = code_section.find(b"prefab_skill_effects") - 4
                        length_change = bytes.fromhex(hex(code_section[offset] + len(user_id) + 1)[2:]) + b"\x00" * 3
                        code_section = code_section.replace(code_section[offset:offset + 4], length_change)
                        target_length = hex(len(code_section) - 4)[2:]
                        if len(target_length) == 3:
                            target_length = target_length[1:3] + "0" + target_length[0]
                        elif len(target_length) == 2:
                            target_length += "00"
                        target_length = bytes.fromhex(target_length)
                        code_section = code_section.replace(code_section[0:2], target_length, 1)
                        buffer_codes.append(code_section)
                    modified_content = open(file, "rb").read()
                    for index in range(len(modified_codes)):
                        modified_content = modified_content.replace(modified_codes[index], buffer_codes[index], 1)
                    with open(file, "wb") as f:
                        f.write(modified_content)

        #=====================================================Character==============================================================
        if IDCHECK not in ["PHIMSEX"]:
            file_name = file_mod_Character
        with open(file_name, 'rb') as file:
            file_content = file.read()
        replacement_text = b"YTB:DiaoChan"
        full_code = replacement_text
        with open(file_name, 'wb') as file:
            file.write(full_code)

        #========================================================DIEU_NHAY===========================================================
        file_path = file_mod_Modtion
        skin_id = IDMODSKIN
        all_ids = []

        for i in range(99):
            if i < 10:
                all_ids.append(skin_id[0:3] + "0" + str(i))
            else:
                all_ids.append(skin_id[0:3] + str(i))

        all_patterns = []

        for id in all_ids:
            hex_id = hex(int(id))[2:]
            all_patterns.append(bytes.fromhex(f"{hex_id[2:4]}{hex_id[0:2]}0000"))

        with open(file_path, "rb") as file:
            file_start = file.read(140)
            all_codes = []
            
            while True:
                segment_length = file.read(2)
                if segment_length == b"":
                    file.close()
                    break
                segment_length_value = segment_length[0] + segment_length[1] * 256 + 2
                code = segment_length + file.read(segment_length_value)
                if all_patterns[all_ids.index(skin_id)] in code:
                    all_codes.append(code)
                elif all_patterns[0] in code:
                    all_codes.append(code)

        dance_codes = []
        dance_codes_database = []
        dance_codes_mod = []

        for code in all_codes:
            if code[0:2] in b"6\x00S\x00":
                dance_codes_database.append(code)
            else:
                dance_codes.append(code)
                dance_codes_mod.append(code)

        dance_selection = 0

        if len(dance_codes_database) > 1:
            dance_selection = int(1)-1

        if len(dance_codes_database) > 0:
            selected_dance_code = dance_codes_database[dance_selection]
            dance_mod_id = selected_dance_code[21:25]
            for code in dance_codes:
                index = dance_codes.index(code)
                for pattern in all_patterns:
                    position = code.find(pattern)
                    if position != -1:
                        code_to_replace = code[position + 4:position + 8]
                        code = code.replace(code_to_replace, dance_mod_id, 1)
                    else:
                        break
                dance_codes[index] = code
        else:
            for code in dance_codes:
                index = dance_codes.index(code)
                position_ref = code.find(all_patterns[all_ids.index(skin_id)])
                dance_mod_id = code[position_ref + 4:position_ref + 8]
                for pattern in all_patterns:
                    position = code.find(pattern)
                    if position != -1:
                        code_to_replace = code[position + 4:position + 8]
                        code = code.replace(code_to_replace, dance_mod_id, 1)
                    else:
                        break
                dance_codes[index] = code

        with open(file_path, "rb") as file:
            content = file.read()
            file.close()

        for i in range(len(dance_codes_mod)):
            content = content.replace(dance_codes_mod[i], dance_codes[i], 1)

        if len(dance_codes) + len(dance_codes_database) == 0:
            for pattern in all_patterns:
                content = content.replace(pattern, b"00\x00\x00", 1)

        with open(file_path, "wb") as file:
            file.write(content)

        #===================================================VIEN================================================================
        if len(IDMODSKIN1) == 1:
            if b'Skin_Icon_HeadFrame' in dieukienmod:                
                data = dieukienmod
                target = b'\x00\x00\x10\x00\x00\x00Share_'+IDCHECK.encode()+b'.jpg'
                index = data.find(target) - 2
                two_bytes_before = data[index:index+2]
                
                if two_bytes_before != b'\x00\x00':
                    inp=file_mod_vien
                    with open(inp,'rb') as f:
                        ab=f.read()
                    a=two_bytes_before
                    i=ab.find(a)-4
                    vt=ab[i:i+4]
                    vtr=int.from_bytes(vt,byteorder='little')
                    vt1=ab[i:i+vtr]
                    id2='6500'
                    a1=bytes.fromhex(str(id2))
                    f.close()
                    i1=ab.find(a1)-4
                    vt11=ab[i1:i1+4]
                    vtr1=int.from_bytes(vt11,byteorder='little')
                    vt2=ab[i1:i1+vtr1]
                    vt1=vt1.replace(a,a1)
                    vt11=ab.replace(vt2,vt1)
                    with open(inp,'wb') as go:
                        go.write(vt11)
            else:
                pass
                    
        #===================================================Skill_Ages================================================================
        CODE_BV_HERO = b''
        def modify_skill_data(data, new_id, effect_name_lowercase, effect_name):
            modified_data = data.read().replace(string1, string1 + new_id).replace(string3, string3 + new_id).replace(string2, string2 + new_id).replace(string4, string4 + new_id).replace(b"""tyEffect" value="true""", b"""tyEffect" value="false""").replace(string5, string5 + new_id).replace(string7, string7 + new_id)
            modified_data = modified_data.replace(SKIN_EFFECT_ID, IDMODSKIN)
            data = modified_data.replace(SKIN_EFFECT_ID, IDMODSKIN)
            return data
        
        Files_Directory_Path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/'
        with zipfile.ZipFile(f'Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/Actor_'+f'{IDMODSKIN[:3]}'+'_Actions.pkg.bytes') as File_Zip:
            File_Zip.extractall(Files_Directory_Path)
            File_Zip.close()
        
        HERO_NAME_LIST = os.listdir(Files_Directory_Path)
        for HERO_NAME_ITEM in HERO_NAME_LIST:
            NAME_HERO = HERO_NAME_ITEM

        #=========================================================================================================================                    
        if IDCHECK == "53002" or b"Skin_Icon_Skill" in dieukienmod or b"Skin_Icon_BackToTown" in dieukienmod or IDCHECK == "53702":
        
            new_folder_path = Files_Directory_Path
            new_files_list = os.listdir(new_folder_path)
            NAME_HERO = new_files_list
            effect_name = NAME_HERO
        
            for new_file_item in new_files_list:
                effect_name = new_file_item
        
            for name1 in NAME_HERO:
                NAME_HERO = name1
        
            directory_path = Files_Directory_Path + f'{NAME_HERO}' + '/skill/'
            file_name = effect_name
            effect_name_db = file_name[4:]
            effect_info = effect_name_db.capitalize()
            file_name = file_name.replace(effect_name_db, effect_info)
            new_effect_name = file_name.encode()
            effect_name = effect_name.encode()
            effect_name_lowercase = effect_name.lower()
            effect_name_lowercase = bytes(effect_name_lowercase)
            new_id = IDMODSKIN
            IDMODSKIN = IDMODSKIN.encode()
            new_id_with_slash = IDMODSKIN + b"/"
            files_in_directory = os.listdir(directory_path)
        
            string1 = b"hero_skill_effects/" + effect_name_lowercase + b"/"
            string2 = b"hero_skill_effects/" + effect_name + b"/"
            string3 = b"Hero_Skill_Effects/" + effect_name_lowercase + b"/"
            string4 = b"Hero_Skill_Effects/" + effect_name + b"/"
            string5 = b"hero_skill_effects/" + new_effect_name + b"/"
            string7 = b"Hero_Skill_Effects/" + new_effect_name + b"/"
            string_new = b"hero_skill_effects/" + effect_name_lowercase + b"/"
            SKIN_EFFECT_ID = IDMODSKIN + b"/" + IDMODSKIN
            New_Files = files_in_directory
            MKBV = b''
            for file_item in New_Files:
                file_path = Files_Directory_Path + f'{NAME_HERO}' + '/' + 'skill/' + file_item
                giai(file_path)
                if IDCHECK not in ["16707"]:              
                    if file_item.find('Back') != -1:
                        if IDCHECK+'_Back.xml' == file_item:
                            with open(Files_Directory_Path + f'{NAME_HERO}' + '/' + 'skill/' + file_item, 'rb') as f:
                                CODE_BV_HERO = f.readlines()
                                MKBV = b'\x36'
                        continue
        
                if file_item.endswith('.xml'):
                    with open(file_path, 'rb') as file:
                        modified_data = modify_skill_data(file, new_id_with_slash, effect_name_lowercase, effect_name)
                    with open(file_path, 'wb') as file:
                        file.write(modified_data)

        #=========================================================================================================================            
                if IDCHECK not in ["59901", "59802", "10915", "52714"]:
                    with open(file_path, 'rb') as f:
                        sec = f.read().replace(b'<SkinOrAvatarList id="' + IDCHECK.encode() + b'" />',b'<SkinOrAvatarList id="237' + IDCHECK[-2:].encode() + b'" />')
                        f.close()
                    with open(file_path, 'wb') as f:
                        f.write(sec)                       

        #=========================================================================================================================                                
                if IDCHECK not in ["59901", "59802", "10915", "52714"]:
                    with open(file_path, 'rb') as f:
                        sec = f.read().replace(b'SkinAvatarFilterType="9">',b'SkinAvatarFilterType="9DiaoChan">').replace(b'SkinAvatarFilterType="11">',b'SkinAvatarFilterType="9">').replace(b'SkinAvatarFilterType="9DiaoChan">',b'SkinAvatarFilterType="11">')
                    with open(file_path, 'wb') as f:
                        f.write(sec)                                  

        #=========================================================================================================================                                
                if file_item == 'Death.xml':
                    with open(file_path, 'rb') as f:
                        sec = f.read().replace(b'</Action>', b'<Track trackName="CommonSkillProcessBarDuration0" eventType="CommonSkillProcessBarDuration" guid="8f26cacc-ee15-4857-94aa-ffccd0b1a87a" enabled="true" refParamName="" useRefParam="false" r="0.933" g="0.000" b="1.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">\n	<Event eventName="CommonSkillProcessBarDuration" time="0.000" length="4.500" isDuration="true">\n		<TemplateObject name="targetId" objectName="self" id="0" isTemp="false" refParamName="" useRefParam="false"/>\n		<int name="width" value="0" refParamName="" useRefParam="false"/>\n		<bool name="useCurrentSkillName" value="false" refParamName="" useRefParam="false"/>\n		<String name="skillNameTextKey" value="Mod By DiaoChan" refParamName="" useRefParam="false"/>\n       </Event>\n   </Track>\n </Action>')
                        f.close()
                    with open(file_path, 'wb') as f:
                        f.write(sec)        

        #=========================================================================================================================            
                if IDCHECK =='13015':
                    if file_item == 'A4.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'\n        <bool name="useNegateValue" value="true" refParamName="" useRefParam="false" />',b'')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)            

        #=========================================================================================================================                                        
                if IDCHECK == '10611':
                    if file_item == 'U1B1.xml':
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'<Condition id="10" guid="2e5f463f-105d-4143-b786-e59ea8b34fa2" status="true" />', b'\r\n    <!-- '+AABBCC.encode('utf-8') +b' -->')
                            f.close()
                        with open(file_path, 'wb') as f:
                            f.write(sec)
                    if file_item == 'A3.xml':
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'<String name="clipName" value="Atk3"', b'<String name="clipName" value="Atk1"')
                            f.close()
                        with open(file_path, 'wb') as f:
                            f.write(sec)

        #=========================================================================================================================                                        
                if IDCHECK == '15412':
                    if file_item == 'P12E2.xml':
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'Prefab_Skill_Effects/Hero_Skill_Effects/154_HuaMuLan/15412/15413_HuaMuLan_Red', b'Prefab_Skill_Effects/Hero_Skill_Effects/154_HuaMuLan/15413_HuaMuLan_Red')
                            f.close()
                        with open(file_path, 'wb') as f:
                            f.write(sec)

        #=========================================================================================================================                                        
                if IDCHECK == '17106':
                    if file_item == 'P1E5.xml':
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/171_zhangfei/17106/1719_zhangfei', b'prefab_skill_effects/hero_skill_effects/171_zhangfei/1719_zhangfei')
                            f.close()
                        with open(file_path, 'wb') as f:
                            f.write(sec)

        #=========================================================================================================================                                        
                if IDCHECK =='11107':
                    if file_item != 'Death.xml':                 	
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'<String name="clipName" value="Atk', b'<String name="clipName" value="11107/Atk').replace(b'<String name="clipName" value="Spell', b'<String name="clipName" value="11107/Spell')
                        with open(file_path, 'wb') as f:
                            f.write(sec)
                        
        #=========================================================================================================================                                        
                if IDCHECK =='51504':
                    if file_item != 'Death.xml':                 	
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'<String name="clipName" value="Atk', b'<String name="clipName" value="51504/Atk').replace(b'<String name="clipName" value="Spell', b'<String name="clipName" value="51504/Spell')
                        with open(file_path, 'wb') as f:
                            f.write(sec)                        

        #=========================================================================================================================                                    
                if IDCHECK =='15704':
                    if file_item != 'Death.xml':                 	
                        with open(file_path, 'rb') as f:
                                sec = f.read().replace(b'<String name="clipName" value="Atk', b'<String name="clipName" value="15704/Atk').replace(b'<String name="clipName" value="Spell', b'<String name="clipName" value="15704/Spell')                        
                        with open(file_path, 'wb') as f:
                            f.write(sec)

        #=========================================================================================================================                                    
                if IDCHECK =='10603':
                    if file_item != 'Death.xml':                 	
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'<String name="clipName" value="Atk', b'<String name="clipName" value="10603/Atk').replace(b'<String name="clipName" value="Spell', b'<String name="clipName" value="10603/Spell')                        
                        with open(file_path, 'wb') as f:
                            f.write(sec)

        #=========================================================================================================================                                    
                if IDCHECK =='52007':
                    if phukien == "do":
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/520_Veres/52007/',b'prefab_skill_effects/component_effects/52007/5200402/')
                        with open(file_path, 'wb') as f:
                            f.write(sec)
                            
                    if phukien == "xanh":
                        with open(file_path, 'rb') as f:
                            sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/520_Veres/52007/',b'prefab_skill_effects/component_effects/52007/5200401/')
                        with open(file_path, 'wb') as f:
                            f.write(sec)  

        #=========================================================================================================================                                                                                                                  
                if IDCHECK[:3] =='524':
                    if file_item == 'A1E9.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/524_Capheny/'+IDCHECK.encode()+b'/Atk1_FireRange',b'prefab_skill_effects/hero_skill_effects/524_Capheny/Atk1_FireRange')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)

        #=========================================================================================================================                                         
                if IDCHECK[:3] =='537':
                    if file_item == 'S12.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/537_Trip/Trip_attack_spell01_1prefab_skill_effects/hero_skill_effects/537_Trip/Trip_attack_spell01_1prefab_skill_effects/hero_skill_effects/537_Trip/Trip_attack_spell01_1_S',b'prefab_skill_effects/hero_skill_effects/537_Trip/Trip_attack_spell01_1_S')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)

        #=========================================================================================================================                                         
                if IDCHECK =='53702':
                    if file_item == ["S13B1.xml", "S14B1.xml"]:
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/537_Trip/53702/Trip_attack_spell01_Indicator',b'prefab_skill_effects/hero_skill_effects/537_Trip/Trip_attack_spell01_Indicator')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)                             

        #=========================================================================================================================            
                if IDCHECK =='11119':
                    if file_item =='A1B1.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'<String name="prefabName" value="prefab_characters/commonempty" refParamName="" useRefParam="false" />', b'<String name="prefabName" value="prefab_skill_effects/hero_skill_effects/111_sunshangxiang/11119/sunshangxiang_fly_01b" refParamName="" useRefParam="false" />\r\n        <Vector3i name="translation" x="0" y="750" z="0" refParamName="" useRefParam="false" />')
                        with open(file_path,'wb') as f: f.write(sec)                        
                    if file_item == 'A2B1.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'<String name="prefabName" value="prefab_characters/commonempty" refParamName="" useRefParam="false" />',b'<String name="prefabName" value="prefab_skill_effects/hero_skill_effects/111_sunshangxiang/11119/sunshangxiang_fly_01b" refParamName="" useRefParam="false" />\r\n        <Vector3i name="translation" x="0" y="700" z="0" refParamName="" useRefParam="false" />')
                        with open(file_path,'wb') as f: f.write(sec)                            

        #=========================================================================================================================                                         
                if IDCHECK[:3] =='544':
                    if file_item =='U1E0.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'Bone_Whisk03',b'Bone_Weapon01')
                        with open(file_path,'wb') as f: f.write(sec)                      
                    if file_item == 'A4B1.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/544_Painter/'+IDCHECK.encode()+b'/Painter_Atk4_blue',b'prefab_skill_effects/hero_skill_effects/544_Painter/Painter_Atk4_blue').replace(b'prefab_skill_effects/hero_skill_effects/544_Painter/'+IDCHECK.encode()+b'/Painter_Atk4_red',b'prefab_skill_effects/hero_skill_effects/544_Painter/Painter_Atk4_red')
                        with open(file_path,'wb') as f: f.write(sec)

        #=========================================================================================================================                                    
                if IDCHECK == '13112':
                    if file_item =='P1E5.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'Bone_Blade',b'Bip001 Prop1').replace(b'Bone_Weapon01',b'Bip001 Prop1')
                        with open(file_path,'wb') as f: f.write(sec)
 
        #=========================================================================================================================                                   
                if IDCHECK == '13111':
                    if file_item =='P1E5.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'Bone_Blade',b'Bone_Weapon01').replace(b'Bip001 Prop1',b'Bone_Weapon01')
                        with open(file_path,'wb') as f: f.write(sec)
                        
        #=========================================================================================================================            
                if IDCHECK == '13116':
                    if file_item =='P1E5.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'Bone_Blade',b'Bip001 Prop1').replace(b'Bone_Weapon01',b'Bip001 Prop1')
                        with open(file_path,'wb') as f: f.write(sec)

        #=========================================================================================================================                                    
                if IDCHECK == '13311':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/133_direnjie/13311/',b'prefab_skill_effects/component_effects/13311/13311_5/').replace(b'"Play_DiRenJie_Attack_1"', b'"Play_DiRenJie_Attack_1_Skin11_AW2"').replace(b'"Play_DiRenJie_Voice_Short"', b'"Play_DiRenJie_Voice_Short_Skin11_AW3"').replace(b'"Play_DiRenJie_Attack_Hit_1"', b'"Play_DiRenJie_Attack_Hit_1_Skin11_AW2"').replace(b'"Play_DiRenJie_Skill_A"', b'"Play_DiRenJie_Skill_A_Skin11_AW2"').replace(b'"Play_DiRenJie_Voice_Anger"', b'"Play_DiRenJie_Voice_Anger_Skin11_AW3"').replace(b'"Play_DiRenJie_Skill_A_Hit"', b'"Play_DiRenJie_Skill_A_Hit_Skin11_AW2"').replace(b'"Play_DiRenJie_Attack_Hit_2"', b'"Play_DiRenJie_Attack_Hit_2_Skin11_AW2"').replace(b'"Play_DiRenJie_Skill_B"', b'"Play_DiRenJie_Skill_B_Skin11_AW2"').replace(b'"Play_DiRenJie_Skill_B_Hit"', b'"Play_DiRenJie_Skill_B_Hit_Skin11_AW2"').replace(b'"Play_DiRenJie_Card_Red"', b'"Play_DiRenJie_Card_Red_Skin11_AW2"').replace(b'"Play_DiRenJie_Card_Blue"', b'"Play_DiRenJie_Card_Blue_Skin11_AW2"').replace(b'"Play_DiRenJie_Card_Yellow"', b'"Play_DiRenJie_Card_Yellow_Skin11_AW2"').replace(b'"Play_DiRenJie_Voice_Dead"', b'"Play_DiRenJie_Voice_Dead_Skin11_AW3"').replace(b'"Play_DiRenJie_Voice_Skill_B"', b'"Play_DiRenJie_Voice_Skill_B_Skin11_AW3"').replace(b'"Play_DiRenJie_Skill_C"', b'"Play_DiRenJie_Skill_C_Skin11_AW2"').replace(b'"Play_DiRenJie_Voice_Skill_C"', b'"Play_DiRenJie_Voice_Skill_C_Skin11_AW3"').replace(b'"Play_DiRenJie_Skill_C_Hit"', b'"Play_DiRenJie_Skill_C_Hit_Skin11_AW2"')
                        with open(file_path,'wb') as f: f.write(sec)

        #=========================================================================================================================                                    
                if IDCHECK =='13311':
                    if "U1" in file_item:
                        if phukienv == "vangv":
                            with open(file_path, 'rb') as f:
                                sec = f.read().replace(b'prefab_skill_effects/component_effects/13311/13311_5/',b'prefab_skill_effects/component_effects/13311/1331101/')
                            with open(file_path, 'wb') as f:
                                f.write(sec)
                                
                        if phukienv == "dov":
                            with open(file_path, 'rb') as f:
                                sec = f.read().replace(b'prefab_skill_effects/component_effects/13311/13311_5/',b'prefab_skill_effects/component_effects/13311/1331102/')
                            with open(file_path, 'wb') as f:
                                f.write(sec)

        #=========================================================================================================================            
                if IDCHECK == '15004':
                    with open(file_path, 'rb') as f: sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/150_hanxin/15004/',b'prefab_skill_effects/component_effects/15033/15037/')
                    with open(file_path,'wb') as f: f.write(sec)

        #=========================================================================================================================            
                if IDCHECK == '16707':
                    with open(file_path, 'rb') as f: sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/167_wukong/16707/',b'prefab_skill_effects/component_effects/16707/16707_5/').replace(b'"Play_Back_WuKong"', b'"Play_Back_WuKong_Skin7_AW3"').replace(b'"Play_WuKong_Attack_1"', b'"Play_WuKong_Attack_1_Skin7_AW3"').replace(b'"Play_WuKong_VO_Short"', b'"Play_WuKong_VO_Short_Skin7_AW4"').replace(b'"Play_WuKong_Attack_Hit_1"', b'"Play_WuKong_Attack_Hit_1_Skin7_AW3"').replace(b'"Play_WuKong_Attack_2"', b'"Play_WuKong_Attack_2_Skin7_AW3"').replace(b'"Play_WuKong_VO_Anger"', b'"Play_WuKong_VO_Anger_Skin7_AW4"').replace(b'"Play_WuKong_Skill_Passive_Hit1"', b'"Play_WuKong_Skill_Passive_Hit1_Skin7_AW3"').replace(b'"Play_WuKong_Skill_Passive_Hit2"', b'"Play_WuKong_Skill_Passive_Hit2_Skin7_AW3"').replace(b'"Play_WuKong_Skill_Passive_Hit3"', b'"Play_WuKong_Skill_Passive_Hit3_Skin7_AW3"').replace(b'"Play_WuKong_Skill_B_2"', b'"Play_WuKong_Skill_B_2_Skin7_AW3"').replace(b'"Play_WuKong_Skill_B_Hit"', b'"Play_WuKong_Skill_B_Hit_Skin7_AW3"').replace(b'"Play_WuKong_VO_Dead"', b'"Play_WuKong_VO_Dead_Skin7_AW4"').replace(b'"Play_WuKong_Skill_A_2"', b'"Play_WuKong_Skill_A_2_Skin7_AW3"').replace(b'"Play_WuKong_Skill_A_Hit"', b'"Play_WuKong_Skill_A_Hit_Skin7_AW3"').replace(b'"Play_WuKong_Skill_A_1"', b'"Play_WuKong_Skill_A_1_Skin7_AW3"').replace(b'"Play_WuKong_VO_Skill_A"', b'"Play_WuKong_VO_Skill_A_Skin7_AW4"').replace(b'"Play_WuKong_Skill_A_Run"', b'"Play_WuKong_Skill_A_Run_Skin7_AW3"').replace(b'"Stop_WuKong_Skill_A_Run"', b'"Stop_WuKong_Skill_A_Run_Skin7_AW3"').replace(b'"Play_WuKong_Skill_B_1"', b'"Play_WuKong_Skill_B_1_Skin7_AW3"').replace(b'"Play_WuKong_VO_Skill_B"', b'"Play_WuKong_VO_Skill_B_Skin7_AW4"').replace(b'"Play_WuKong_Skill_C"', b'"Play_WuKong_Skill_C_Skin7_AW3"').replace(b'"Play_WuKong_VO_Skill_C"', b'"Play_WuKong_VO_Skill_C_Skin7_AW4"').replace(b'"Play_WuKong_Skill_C_01"', b'"Play_WuKong_Skill_C_01_Skin7_AW3"').replace(b'"Play_WuKong_Skill_C_02"', b'"Play_WuKong_Skill_C_02_Skin7_AW3"').replace(b'"Play_WuKong_Skill_C_Hit"', b'"Play_WuKong_Skill_C_Hit_Skin7_AW3"')
                    with open(file_path,'wb') as f: f.write(sec)
                    if file_item =='U1B0.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(WUKONGU1B0, WUKONGU1B0MOD)
                        with open(file_path,'wb') as f: f.write(sec)          
                        
                if IDCHECK == '16707':           
                    if file_item == '16707_Back.xml':
                        with open(file_path, 'wb') as f:
                            f.write(WUKONGBACKMOD)

        #=========================================================================================================================                                    
                if IDCHECK == '13609':
                    if file_item =='U1B1.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'        <String name="resourceName" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03" refParamName="" useRefParam="false" />', b'        <String name="resourceName" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03" refParamName="" useRefParam="false" />\r\n        <String name="resourceName2" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03_1" refParamName="" useRefParam="false" />\r\n        <String name="resourceName3" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03_2" refParamName="" useRefParam="false" />').replace(b'        <String name="resourceName" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03_e" refParamName="" useRefParam="false" />', b'        <String name="resourceName" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03_e" refParamName="" useRefParam="false" />\r\n        <String name="resourceName2" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03_1_e" refParamName="" useRefParam="false" />\r\n        <String name="resourceName3" value="prefab_skill_effects/hero_skill_effects/136_wuzetian/13609/wuzetian_attack_spell03_2_e" refParamName="" useRefParam="false" />')
                        with open(file_path,'wb') as f: f.write(sec)
                    if file_item =='S1B1.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'<Vector3 name="scaling" x="1.300" y="1.000" z="1.000" refParamName="" useRefParam="false" />', b'<Vector3 name="scaling" x="1.000" y="1.000" z="1.000" refParamName="" useRefParam="false" />')
                        with open(file_path,'wb') as f: f.write(sec)

        #=========================================================================================================================                                    
                if IDCHECK == '13613':
                    if file_item =='S1B1.xml':
                        with open(file_path, 'rb') as f: sec = f.read().replace(b'<Vector3 name="scaling" x="1.300" y="1.000" z="1.000" refParamName="" useRefParam="false" />', b'<Vector3 name="scaling" x="1.000" y="1.000" z="1.000" refParamName="" useRefParam="false" />')
                        with open(file_path,'wb') as f: f.write(sec)                        

        #=========================================================================================================================                                    
                if IDCHECK =='15012':
                    if file_item == 'U1.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/150_Hanxin_spellC_01',b'prefab_skill_effects/hero_skill_effects/150_HanXin/15012/150_hanxin_spellc_01')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)                  

        #=========================================================================================================================            
                if IDCHECK =='59702':           	
                    if file_item == 'P1E01.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'e40d96061260" enabled="true"',b'e40d96061260" enabled="false"')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)
                    if file_item == 'P2.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/KuangTie_attack02_spell02A_1',b'prefab_skill_effects/hero_skill_effects/597_kuangtie/59702/KuangTie_attack02_spell02A_1')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)
                    if file_item == 'U1.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/KuangTie_attack_spell03_1',b'prefab_skill_effects/hero_skill_effects/597_kuangtie/59702/KuangTie_attack_spell03_1')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)
                    if file_item == 'U11.xml':
                        with open(file_path, 'rb') as f:
                             sec = f.read().replace(b'prefab_skill_effects/hero_skill_effects/KuangTie_attack02_spell03_1',b'prefab_skill_effects/hero_skill_effects/597_kuangtie/59702/KuangTie_attack02_spell03_1')
                             f.close()
                        with open(file_path, 'wb') as f:
                             f.write(sec)         

        #=========================================================================================================================                                     
                if IDCHECK == '13011':              
                    if file_item == 'S2B1.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CODES2B1,CODES2B1MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 
                    if file_item == 'S2.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CHECKS2AIRI,CHECKS2AIRIMOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 
                    if file_item == 'S21.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CHECKS21AIRI,CHECKS21AIRIMOD).replace(b"""<Track trackName="TriggerParticleTick1" eventType="TriggerParticleTick" guid="a07302eb-cb3b-4146-9996-d018f92247aa" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">""",b"""<Track trackName="TriggerParticleTick1" eventType="TriggerParticleTick" guid="a07302eb-cb3b-4146-9996-d018f92247aa" enabled="false" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">""").replace(b"GongBenWuZang_attack01_spell01_2",b"GongBenWuZang_attack01_spell01_1")
                        with open(file_path, 'wb') as f:
                            f.write(new_content)        
                    if file_item == 'S22.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CHECKS22AIRI,CHECKS22AIRIMOD).replace(b"""<Track trackName="TriggerParticleTick1" eventType="TriggerParticleTick" guid="a07302eb-cb3b-4146-9996-d018f92247aa" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">""",b"""<Track trackName="TriggerParticleTick1" eventType="TriggerParticleTick" guid="a07302eb-cb3b-4146-9996-d018f92247aa" enabled="false" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">""").replace(b"GongBenWuZang_attack01_spell01_3",b"GongBenWuZang_attack01_spell01_2")
                        with open(file_path, 'wb') as f:
                            f.write(new_content)                                  

        #=========================================================================================================================                                    
                if IDCHECK == '14111':              
                    if file_item == 'S1.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CODES1LAU,CODES1LAUMOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 
                    if file_item == 'S1B1.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CODES1B1LAU, CODES1B1LAUMOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content)        
                    if file_item == 'S1B2.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(CODES1B2LAU,CODES1B2LAUMOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content)      

        #=========================================================================================================================                                    
                if IDCHECK == '13210':              
                    if file_item == 'A1.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(ACTION,A1MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 
                    if file_item == 'A2.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(ACTION,A2MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content)  
                    if file_item == 'A3.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(ACTION,A3MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 
                    if file_item in['S1B0.xml','S11B0.xml','S12B0.xml']:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            content = re.sub(b'"resourceName" value="(.*?)"', b'"resourceName" value="DiaoChan"', content)
                            new_content = content.replace(ACTION,S1MOD).replace(ACTION,S12MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 
                    if file_item == 'S1B1.xml':
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(b'\n        <bool name="useNegateValue" value="true" refParamName="" useRefParam="false" />',b'').replace(ACTION,S1B1MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content) 

        #=========================================================================================================================            
                if IDCHECK =='15015':
                    if file_item == "U1.xml":
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            content = re.sub(b'"resourceName" value="(.*?)"', b'"resourceName" value="DiaoChan"', content)
                            new_content = content.replace(ACTIONU1,U1MOD)
                        with open(file_path, 'wb') as f:
                            f.write(new_content)                                      

        #=========================================================================================================================            
                if IDCHECK =='54307':
                    with open(file_path, 'rb') as f:
                         sec = f.read().replace(b'\n        <bool name="useNegateValue" value="true" refParamName="" useRefParam="false" />',b'')
                         f.close()
                    with open(file_path, 'wb') as f:
                         f.write(sec)          

        #=========================================================================================================================                                     
                if IDCHECK == '15013':          
                    if file_item in ["A1.xml", "A2.xml", "A3.xml"]:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(b'guid="9d243092-f160-4189-a9da-f132595032c9" enabled="true"',b'guid="9d243092-f160-4189-a9da-f132595032c9" enabled="false"')
                        with open(file_path, 'wb') as f:
                            f.write(new_content)            
                    if file_item in ["S2.xml"]:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            new_content = content.replace(b'<int name="skinId" value="' + IDCHECK.encode() + b'" refParamName="" useRefParam="false" />\r\n        <bool name="bEqual" value="false" refParamName="" useRefParam="false" />\r\n        <bool name="bSkipLogicCheck" value="true" refParamName="" useRefParam="false" />',b'<int name="skinId" value="' + b'9999' + b'" refParamName="" useRefParam="false" />\r\n        <<bool name="bEqual" value="false" refParamName="" useRefParam="false" />>\r\n        <bool name="bSkipLogicCheck" value="true" refParamName="" useRefParam="false" />').replace(b'<int name="skinId" value="' + IDCHECK.encode() + b'" refParamName="" useRefParam="false" />\r\n        <bool name="bSkipLogicCheck" value="true" refParamName="" useRefParam="false" />',b'<int name="skinId" value="' + b'9999' + b'" refParamName="" useRefParam="false" />\r\n        <bool name="bEqual" value="false" refParamName="" useRefParam="false" />\r\n        <bool name="bSkipLogicCheck" value="true" refParamName="" useRefParam="false" />').replace(b'<int name="skinId" value="' + b'9999' + b'" refParamName="" useRefParam="false" />\r\n        <<bool name="bEqual" value="false" refParamName="" useRefParam="false" />>\r\n        <bool name="bSkipLogicCheck" value="true" refParamName="" useRefParam="false" />',b'<int name="skinId" value="' + b'9999' + b'" refParamName="" useRefParam="false" />\r\n        <bool name="bSkipLogicCheck" value="true" refParamName="" useRefParam="false" />').replace(b'<Condition id="14" guid="b73050c0-0afc-4e3b-98e2-6ffe12d3d489" status="true" />\r\n      <Condition id="15" guid="84b2cbba-51cc-4673-adab-a3624a854953" status="false" />', b'<Condition id="15" guid="84b2cbba-51cc-4673-adab-a3624a854953" status="false" />').replace(b'<Condition id="14" guid="b73050c0-0afc-4e3b-98e2-6ffe12d3d489" status="true" />\r\n      <Event eventName="CheckActorPositionDuration"', b'<Event eventName="CheckActorPositionDuration"').replace(b'<Condition id="14" guid="b73050c0-0afc-4e3b-98e2-6ffe12d3d489" status="true" />\r\n      <Event eventName="HitTriggerTick"', b'<Event eventName="HitTriggerTick"').replace(b'<Condition id="37" guid="173653f1-8aaf-47ee-84a3-92cf343f6711" status="false" />\r\n      <Condition id="14" guid="b73050c0-0afc-4e3b-98e2-6ffe12d3d489" status="true" />\r\n      <Event eventName="SetAnimationParamsTick"', b'<Condition id="37" guid="173653f1-8aaf-47ee-84a3-92cf343f6711" status="false" />\r\n      <Event eventName="SetAnimationParamsTick"').replace(S215013, S2MOD15013)
                        with open(file_path, 'wb') as f:
                            f.write(new_content)        

        #=========================================================================================================================                                     
                if IDCHECK == '59901' and file_item == 'S1.xml':
                         with open(file_path, 'rb') as f:
                          rpl = f.read().replace(TTDA_Mod18,TTDA_Fix18).replace(TTDA_Mod19,TTDA_Fix19).replace(TTDA_Mod20,TTDA_Fix20).replace(TTDA_Mod21,TTDA_Fix21)
                          f.close()
                         with open(file_path, 'wb') as f:f.write(rpl) 
                if file_item == 'S1B00.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'59901/59904',b'59901')                                                                                               
                        with open(file_path, 'wb') as f:f.write(rpl)     
                if file_item == 'S1B0.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TTDA_Mod22,TTDA_Fix22).replace(TTDA_Mod23,TTDA_Fix23)
                        with open(file_path, 'wb') as f:f.write(rpl)                                                  
                if file_item == 'S1B1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TTDA_Mod24,TTDA_Fix24).replace(TTDA_Mod25,TTDA_Fix25).replace(TTDA_Mod26,TTDA_Fix26).replace(TTDA_Mod27,TTDA_Fix27).replace(TTDA_Mod28,TTDA_Fix28).replace(TTDA_Mod29,TTDA_Fix29).replace(TTDA_Mod30,TTDA_Fix30).replace(TTDA_Mod31,TTDA_Fix31).replace(TTDA_Mod32,TTDA_Fix32)
                        with open(file_path, 'wb') as f:f.write(rpl)
                if file_item == 'S1E92.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TTDA_Mod33,TTDA_Fix33).replace(TTDA_Mod34,TTDA_Fix34).replace(TTDA_Mod35,TTDA_Fix35)
                        with open(file_path, 'wb') as f:f.write(rpl)
                if file_item == 'S2B00.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TTDA_Mod36,TTDA_Fix36)
                        with open(file_path, 'wb') as f:f.write(rpl)
                if file_item == 'S2E10.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'599_LvMeng/59901/',b'599_LvMeng/')
                        with open(file_path, 'wb') as f:f.write(rpl)                                                        
                if file_item == 'S2E80.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'599_LvMeng/59901/',b'599_LvMeng/')
                        with open(file_path, 'wb') as f:f.write(rpl)  
                if file_item == 'U1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TTDA_Mod37,TTDA_Fix37)
                        with open(file_path, 'wb') as f:f.write(rpl)   
                if file_item == 'u11b1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TTDA_Mod38,TTDA_Fix38).replace(TTDA_Mod39,TTDA_Fix39)
                        with open(file_path, 'wb') as f:f.write(rpl)                                                 
                if file_item == 'U11.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'59901/LvMeng_attack_spell03F',b'LvMeng_attack_spell03F')
                        with open(file_path, 'wb') as f:f.write(rpl)
                if file_item == 'U1E8.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'Play_Billow_Skill_C_1_Hit_Skin1',b'Play_Billow_Skill_C_1_Hit')
                        with open(file_path, 'wb') as f:f.write(rpl)     
                if file_item == 'U1E9.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'59901/LvMeng_hurt02',b'LvMeng_hurt02').replace(b' SkinAvatarFilterType="9">',b' SkinAvatarFilterType="11">')
                        with open(file_path, 'wb') as f:f.write(rpl)                                                                          

        #=========================================================================================================================                   
                if IDCHECK == '59802' and file_item != 'S2E6.xml':
                         with open(file_path, 'rb') as f:
                          rpl = f.read().replace(TPTM_Mod1,TPTM_Fix1).replace(TPTM_Mod2,TPTM_Fix2).replace(TPTM_Mod3,TPTM_Fix3).replace(TPTM_Mod4,TPTM_Fix4).replace(TPTM_Mod5,TPTM_Fix5).replace(TPTM_Mod6,TPTM_Fix6).replace(TPTM_Mod7,TPTM_Fix7).replace(TPTM_Mod8,TPTM_Fix8).replace(TPTM_Mod9,TPTM_Fix9).replace(TPTM_Mod10,TPTM_Fix10).replace(TPTM_Mod11,TPTM_Fix11).replace(TPTM_Mod12,TPTM_Fix12).replace(TPTM_Mod13,TPTM_Fix13).replace(TPTM_Mod14,TPTM_Fix14).replace(TPTM_Mod15,TPTM_Fix15).replace(TPTM_Mod16,TPTM_Fix16)
                         with open(file_path, 'wb') as f:f.write(rpl)
                if file_item == 'A1B12.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod17,TPTM_Fix17).replace(TPTM_Mod18,TPTM_Fix18).replace(TPTM_Mod19,TPTM_Fix19)
                        with open(file_path,'wb') as f: f.write(rpl)      
                if file_item == 'A1B2.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod20,TPTM_Fix20)
                        with open(file_path,'wb') as f: f.write(rpl)  
                if file_item == 'A1E17.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod21,TPTM_Fix21).replace(TPTM_Mod22,TPTM_Fix22)
                        with open(file_path,'wb') as f: f.write(rpl)
                if file_item == 'P0B1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod23,TPTM_Fix23)
                        with open(file_path,'wb') as f: f.write(rpl)           
                if file_item == 'P1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod24,TPTM_Fix24)
                        with open(file_path,'wb') as f: f.write(rpl) 
                if file_item == 'S1E1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod25,TPTM_Fix25)
                        with open(file_path,'wb') as f: f.write(rpl)
                if file_item == 'S2E1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod26,TPTM_Fix26)
                        with open(file_path,'wb') as f: f.write(rpl)                                 
                if file_item == 'S2E6.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod27,TPTM_Fix27).replace(TPTM_Mod28,TPTM_Fix28).replace(TPTM_Mod29,TPTM_Fix29)
                        with open(file_path,'wb') as f: f.write(rpl) 
                if file_item == 'U1E1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod30,TPTM_Fix30).replace(TPTM_Mod31,TPTM_Fix31)
                        with open(file_path,'wb') as f: f.write(rpl)     
                if file_item == 'U2B1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod32,TPTM_Fix32).replace(TPTM_Mod33,TPTM_Fix33).replace(TPTM_Mod34,TPTM_Fix34).replace(TPTM_Mod35,TPTM_Fix35)
                        with open(file_path,'wb') as f: f.write(rpl)
                if file_item == 'U2B2.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod36,TPTM_Fix36).replace(TPTM_Mod37,TPTM_Fix37).replace(TPTM_Mod38,TPTM_Fix38)
                        with open(file_path,'wb') as f: f.write(rpl)       
                if file_item == 'U2B5.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TPTM_Mod39,TPTM_Fix39).replace(TPTM_Mod40,TPTM_Fix40).replace(TPTM_Mod41,TPTM_Fix41)
                        with open(file_path,'wb') as f: f.write(rpl)
                if file_item == 'U2E6.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'59802/11120',b'59802')
                        with open(file_path,'wb') as f: f.write(rpl)         
                  
        #=========================================================================================================================                                             
                if IDCHECK == '10915' :
                         with open(file_path, 'rb') as f:
                          rpl = f.read().replace(TSTS_Mod1,TSTS_Fix1).replace(TSTS_Mod2,TSTS_Fix2).replace(TSTS_Mod3,TSTS_Fix3)
                         with open(file_path, 'wb') as f:f.write(rpl)   
                if file_item == 'A1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod4,TSTS_Fix4)
                        with open(file_path,'wb') as f: f.write(rpl)     
                if file_item == 'A3.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod5,TSTS_Fix5)
                        with open(file_path,'wb') as f: f.write(rpl)        
                if file_item == 'S1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod6,TSTS_Fix6)
                        with open(file_path,'wb') as f: f.write(rpl)                                                
                if file_item == 'A2.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod7,TSTS_Fix7).replace(TSTS_Mod8,TSTS_Fix8).replace(TSTS_Mod9,TSTS_Fix9)
                        with open(file_path,'wb') as f: f.write(rpl)                                      
                if file_item == 'PSE.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'10915_Wusuxie',b'10915/10915_Wusuxie')
                        with open(file_path,'wb') as f: f.write(rpl) 
                if file_item == 'S1B2.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod10,TSTS_Fix10)
                        with open(file_path,'wb') as f: f.write(rpl)   
                if file_item == 'S2.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod11,TSTS_Fix11).replace(TSTS_Mod12,TSTS_Fix12)
                        with open(file_path,'wb') as f: f.write(rpl)                             
                if file_item == 'S2E9.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod13,TSTS_Fix13)
                        with open(file_path,'wb') as f: f.write(rpl)                                  
                if file_item == 'U1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod14,TSTS_Fix14)
                        with open(file_path,'wb') as f: f.write(rpl) 
                if file_item == 'U1B0.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod15,TSTS_Fix15).replace(TSTS_Mod16,TSTS_Fix16)
                        with open(file_path,'wb') as f: f.write(rpl)     
                if file_item == 'U1E1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod17,TSTS_Fix17)
                        with open(file_path,'wb') as f: f.write(rpl)        
                if file_item == 'U2B0.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(TSTS_Mod18,TSTS_Fix18).replace(TSTS_Mod19,TSTS_Fix19)
                        with open(file_path,'wb') as f: f.write(rpl)                                                                  

        #=========================================================================================================================                                     
                if IDCHECK == '52414' :
                         with open(file_path, 'rb') as f:
                          rpl = f.read().replace(CNDC_Mod1,CNDC_Fix1).replace(CNDC_Mod2,CNDC_Fix2).replace(CNDC_Mod3,CNDC_Fix3)
                         with open(file_path, 'wb') as f:f.write(rpl)                  
                if file_item == 'S3.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(CNDC_Mod4,CNDC_Fix4)
                        with open(file_path,'wb') as f: f.write(rpl)     
                if file_item == 'S3_1.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(CNDC_Mod5,CNDC_Fix5)
                        with open(file_path,'wb') as f: f.write(rpl)                             
                if file_item == 'Death.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(b'52414_Capheny_death_01',b'52414/52414_Capheny_death_01')
                        with open(file_path,'wb') as f: f.write(rpl)                                             
                if file_item == 'S1E2.xml':
                        with open(file_path, 'rb') as f: rpl = f.read().replace(CNDC_Mod6,CNDC_Fix6)
                        with open(file_path,'wb') as f: f.write(rpl)            

        #=========================================================================================================================                                                             
        if IDCHECK == "59901":
            duongdan12=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/Back.xml'
            duongdan13=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/P10E2.xml'      
            duongdan14=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/U1E8.xml'   
            duongdan15=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/u1b1.xml'       
            duongdan16=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/S11.xml'
            duongdan17=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/S1B00.xml'
            duongdan18=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/S1E60.xml'  
            duongdan19=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/S1E92.xml'      
            duongdan20=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/S2.xml' 
            duongdan21=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/S2E80.xml'
            duongdan22=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/U1.xml'
            duongdan23=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/U1E9.xml'
            duongdan24=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/599_LvMeng/skill/U11.xml'
            with open (duongdan12, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'<String name="parentResourceName" value="prefab_skill_effects/tongyong_effects/tongyong_hurt/born_back_reborn/huicheng_tongyong_01"', b'<String name="parentResourceName" value="prefab_skill_effects/hero_skill_effects/599_LvMeng/59901/huicheng_tongyong_01"').replace(b'<SkinOrAvatarList id="59901" />',b'<SkinOrAvatarList id="59998" />').replace(b'f51150fb-c68a-4fa4-9845-7f67ba2d2e7f" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="11">',b'@').replace(b'"false" SkinAvatarFilterType="9">',b'"false" SkinAvatarFilterType="11">').replace(b'@',b'f51150fb-c68a-4fa4-9845-7f67ba2d2e7f" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="9">')
            with open (duongdan12,'wb') as f : f.write(noidung)
            with open (duongdan13, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'ac256a1a-676f-48ee-b5ed-370ccc8486d0" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="11">',b'ac256a1a-676f-48ee-b5ed-370ccc8486d0" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="9">')
            with open (duongdan13,'wb') as f : f.write(noidung)       
            with open (duongdan14, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'Play_Billow_Skill_C_1_Hit_Skin1',b'Play_Billow_Skill_C_1_Hit')
            with open (duongdan14,'wb') as f : f.write(noidung)      
            with open (duongdan15, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'5e4bb41d-712c-4130-9ba1-55d2c45bf992" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="11" nameSpace="">',b'5e4bb41d-712c-4130-9ba1-55d2c45bf992" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="9" nameSpace="">').replace(b'b751ff51-f5d6-4e50-8fa0-6ecefa15f3cb" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="11">',b'b751ff51-f5d6-4e50-8fa0-6ecefa15f3cb" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="9">').replace(b'f61eb017-9d5c-4c48-9dd9-7f02f863f32f" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="11">',b'f61eb017-9d5c-4c48-9dd9-7f02f863f32f" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="9">').replace(b'f2fa08f9-761c-42f9-adca-4c231a8032c9" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="11">',b'f2fa08f9-761c-42f9-adca-4c231a8032c9" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="9">').replace(b'e1df1d27-473e-40e2-aa3a-a9ab2dffe139" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="11">',b'e1df1d27-473e-40e2-aa3a-a9ab2dffe139" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" SkinAvatarFilterType="9">').replace(b'<Vector3i name="direction" x="0" y="0" z="0" refParamName="targetdir" useRefParam="true" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59998" />',b'<Vector3i name="direction" x="0" y="0" z="0" refParamName="targetdir" useRefParam="true" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59901" />').replace(b'<int name="Radius" value="2500" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59998" />',b'<int name="Radius" value="2500" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59901" />').replace(b'<int name="SelfSkillCombineID_1" value="599899" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59998" />',b'<int name="SelfSkillCombineID_1" value="599899" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59901" />')
            with open (duongdan15,'wb') as f : f.write(noidung)       
            with open (duongdan16, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'/599_LvMeng/skill/s11b1',b'/599_lvmeng/skill/s11b1')
            with open (duongdan16,'wb') as f : f.write(noidung)            
            with open (duongdan17, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'Prefab_Skill_Effects/Hero_Skill_Effects/599_LvMeng/59901/LvMeng_attack_spell01B_01',b'prefab_skill_effects/hero_skill_effects/599_LvMeng/59901/LvMeng_attack_spell01B_01')
            with open (duongdan17,'wb') as f : f.write(noidung)        
            with open (duongdan18, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'<String name="prefabName" value="Prefab_Skill_Effects/Hero_Skill_Effects/599_LvMeng/59901/5991_LvMeng_Shak" refParamName="" useRefParam="false" />',b'<String name="prefabName" value="prefab_skill_effects/hero_skill_effects/599_LvMeng/59901/5991_LvMeng_Shak" refParamName="" useRefParam="false" />')
            with open (duongdan18,'wb') as f : f.write(noidung)      
            with open (duongdan19, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'<String name="resourceName" value="prefab_skill_effects/hero_skill_effects/599_LvMeng/59901/LvMeng_buff_01" refParamName="" useRefParam="false" />',b'<String name="resourceName" value="prefab_skill_effects/hero_skill_effects/599_lvmeng/59901/LvMeng_buff_01" refParamName="" useRefParam="false" />')
            with open (duongdan19,'wb') as f : f.write(noidung)    
            with open (duongdan20, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'prefab_characters/prefab_hero/599_LvMeng',b'prefab_characters/prefab_hero/599_lvmeng')
            with open (duongdan20,'wb') as f : f.write(noidung)      
            with open (duongdan21, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'/599_LvMeng',b'/599_lvmeng')
            with open (duongdan21,'wb') as f : f.write(noidung)            
            with open (duongdan22, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'<String name="ActionName" value="prefab_characters/prefab_hero/599_LvMeng/skill/u1b0" refParamName="" useRefParam="false" />',b'<String name="ActionName" value="prefab_characters/prefab_hero/599_lvmeng/skill/u1b0" refParamName="" useRefParam="false" />').replace(b'<String name="ActionName" value="prefab_characters/prefab_hero/599_LvMeng/skill/u1b100" refParamName="" useRefParam="false" />',b'<String name="ActionName" value="prefab_characters/prefab_hero/599_lvmeng/skill/u1b100" refParamName="" useRefParam="false" />').replace(b'<String name="ActionName" value="prefab_characters/prefab_hero/599_LvMeng/skill/u1b1" refParamName="" useRefParam="false" />',b'<String name="ActionName" value="prefab_characters/prefab_hero/599_lvmeng/skill/u1b1" refParamName="" useRefParam="false" />')
            with open (duongdan22,'wb') as f : f.write(noidung)      
            with open (duongdan23, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'<String name="resourceName" value="prefab_skill_effects/hero_skill_effects/599_LvMeng/LvMeng_hurt02" refParamName="" useRefParam="false" />',b'<String name="resourceName" value="prefab_skill_effects/hero_skill_effects/599_lvmeng/LvMeng_hurt02" refParamName="" useRefParam="false" />')
            with open (duongdan23,'wb') as f : f.write(noidung)     
            with open (duongdan24, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'78615394-1765-40c5-b480-846eddecf8b1" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="11">',b'78615394-1765-40c5-b480-846eddecf8b1" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="9">').replace(b'<Vector3i name="direction" x="0" y="0" z="0" refParamName="targetdir" useRefParam="true" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59998" />',b'<Vector3i name="direction" x="0" y="0" z="0" refParamName="targetdir" useRefParam="true" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59901" />').replace(b'eb3dd322-d92f-453b-98bb-e3d26f3765e1" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="11">',b'eb3dd322-d92f-453b-98bb-e3d26f3765e1" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="9">').replace(b'<int name="Radius" value="2500" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59998" />',b'<int name="Radius" value="2500" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59901" />').replace(b'542de572-8bc1-400b-bb43-09f9320feb77" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="11">',b'542de572-8bc1-400b-bb43-09f9320feb77" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="false" SkinAvatarFilterType="9">').replace(b'<int name="SelfSkillCombineID_1" value="599899" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59998" />',b'<int name="SelfSkillCombineID_1" value="599899" refParamName="" useRefParam="false" />\r\n      </Event>\r\n      <SkinOrAvatarList id="59901" />').replace(b'<String name="ActionName" value="prefab_characters/prefab_hero/599_LvMeng/skill/u1b100"',b'<String name="ActionName" value="prefab_characters/prefab_hero/599_lvmeng/skill/u1b100"').replace(b'<String name="ActionName" value="prefab_characters/prefab_hero/599_LvMeng/skill/u11b1"',b'<String name="ActionName" value="prefab_characters/prefab_hero/599_lvmeng/skill/u11b1"').replace(b'<String name="resourceName" value="prefab_skill_effects/hero_skill_effects/599_LvMeng/LvMeng_attack_spell03F"',b'<String name="resourceName" value="prefab_skill_effects/hero_skill_effects/599_lvmeng/LvMeng_attack_spell03F"')
            with open (duongdan24,'wb') as f : f.write(noidung)                                  
                                          
        if IDCHECK == "59802":
            duongdan25=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/598_DaSiKong/skill/Skin3E1.xml'
            duongdan26=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/598_DaSiKong/skill/A1B5.xml'     
            duongdan27=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/598_DaSiKong/skill/A1B6.xml'         
            duongdan28=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/598_DaSiKong/skill/A1B51.xml'
            duongdan29=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/598_DaSiKong/skill/A1B61.xml'    
            with open (duongdan25,'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'\\',b"/").replace(b'Prefab_Skill_Effects/Hero_Skill_Effects/',b'prefab_skill_effects/hero_skill_effects/')
            with open (duongdan25,'wb') as f : f.write(noidung)                    
            with open (duongdan26,'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'SkinAvatarFilterType="9"',b"@").replace(b'SkinAvatarFilterType="11"',b'SkinAvatarFilterType="9"').replace(b"@",b'SkinAvatarFilterType="11"')
            with open (duongdan26,'wb') as f : f.write(noidung)   
            with open (duongdan27,'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'SkinAvatarFilterType="9"',b"@").replace(b'SkinAvatarFilterType="11"',b'SkinAvatarFilterType="9"').replace(b"@",b'SkinAvatarFilterType="11"')
            with open (duongdan27,'wb') as f : f.write(noidung)                
            with open (duongdan28,'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'SkinAvatarFilterType="9"',b"@").replace(b'SkinAvatarFilterType="11"',b'SkinAvatarFilterType="9"').replace(b"@",b'SkinAvatarFilterType="11"')
            with open (duongdan28,'wb') as f : f.write(noidung)                 
            with open (duongdan29,'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b'SkinAvatarFilterType="9"',b"@").replace(b'="11',b'="9').replace(b"@",b'SkinAvatarFilterType="11"')
            with open (duongdan29,'wb') as f : f.write(noidung)                          
        #==================================================Auto_Check_Ages=================================================================
        if b"Skin_Icon_Skill" in dieukienmod or b"Skin_Icon_BackToTown" in dieukienmod or IDCHECK == "53702":
            IDNODMODCHECK = ['14111', '16707', '13011', '15009', '54307', '10620', '14104', '14107', '12106', '59901', '10915', '52414', '19610']
            
            if IDCHECK not in IDNODMODCHECK:
                files_list = os.listdir(directory_path)
        
                for filename in files_list:
                    if (filename in ['S1.xml', 'S1B1.xml', 'S1B2.xml'] and IDCHECK == "14111") or \
                       (filename in ['S2.xml', 'S21.xml', 'S22.xml'] and IDCHECK == "13011") or \
                       (filename not in ['13210_Back.xml', 'S2B2.xml', 't2p1.xml', 't2p2.xml'] and IDCHECK == "13210") or \
                       (filename == 'P1E5.xml' and IDCHECK[:3] == '131') or \
                       (filename != 'S1B1.xml' and IDCHECK == '13609') or \
                       (filename != 'U1E1.xml' and IDCHECK == '10611') or \
                       (filename == 'U1.xml' and IDCHECK == '10611') or \
                       (filename == 'u1b1.xml' and IDCHECK == '59901') or \
                       (filename == 'S2.xml' and IDCHECK == '15013') or \
                       (filename == 'U1.xml' and IDCHECK == '15015'):
                        continue
                    
                    file_path = os.path.join(directory_path, filename)
                    with open(file_path, 'rb') as f:
                        All = f.read()
        
                    if b'"Jg\x00' in All:
                        continue
        
                    ListAll = All.split(b'\r\n')
                    List_DOANAll = All.split(b'    <Track trackName="')
        
                    SKM = b'\r\n        <int name="skinId" value="99999" refParamName="" useRefParam="false" />'
                    IDS = b'\r\n        <int name="skinId" value="' + IDCHECK.encode() + b'" refParamName="" useRefParam="false" />'
                    EQF = b'\r\n        <bool name="bEqual" value="false" refParamName="" useRefParam="false" />'
                    EQT = b'\r\n        <bool name="bEqual" value="true" refParamName="" useRefParam="false" />'
                    UNV = b'\r\n        <bool name="useNegateValue" value="true" refParamName="" useRefParam="false" />'
                    UNF = b'\r\n        <bool name="useNegateValue" value="false" refParamName="" useRefParam="false" />'
                    bol = b'\r\n        <bool name="'
                    check_vt = b'CheckSkinIdVirtualTick'
                    check_sk = b'CheckSkinIdTick'
        
                    CODE_CHECK = [x for x in List_DOANAll if IDS.lower() in x.lower()]
                    if len(CODE_CHECK) != 0:
                        for text in CODE_CHECK:
                            if check_sk.lower() in text.lower():
                                if bol not in text:
                                    text1 = text.replace(IDS, IDS + EQF).replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
                                if EQF not in text and EQT in text:
                                    text1 = text.replace(EQT, EQF).replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
                                if EQF in text:
                                    text1 = text.replace(EQF, b'').replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
                                if EQF not in text:
                                    text1 = text.replace(IDS, IDS + EQF).replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
                            if check_vt.lower() in text.lower():
                                if UNV in text:
                                    text1 = text.replace(UNV, b'').replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
                                if UNF in text:
                                    text1 = text.replace(UNF, UNV).replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
                                if UNV not in text:
                                    text1 = text.replace(IDS, IDS + UNV).replace(IDS, SKM)
                                    All = All.replace(text, text1)
                                    continue
        
                    with open(file_path, 'wb') as f:
                        f.write(All)

        #===============================================Sound_Ages====================================================================
        if IDCHECK == "53002" or b"Skin_Icon_SoundEffect" in dieukienmod or b"Skin_Icon_Dialogue" in dieukienmod:
            if IDCHECK not in ["13311", "16707"]:
                directory_path = Files_Directory_Path + f'{NAME_HERO}' + '/skill/'        
                o = directory_path
                ID = (IDSOUND)
                File = os.listdir(o)
                for file in File:
                    with open(o + file, 'rb') as f:
                        rpl = f.readlines()
                    with open(o + file, 'rb') as f:
                        Rpl = f.read()
                    Code = []
                    for i in rpl:
                        if i.find(b'<String name="eventName" value="') != -1:
                            Code.append(i[40:i.find(b'" refParamName="" useRefParam="false" />')])
                    for i in Code:
                        a = b'<String name="eventName" value="' + i + b'" refParamName="" useRefParam="false" />'
                        if Code:
                            Rpl = Rpl.replace(a, b'<String name="eventName" value="' + i + IDSOUND + b'" refParamName="" useRefParam="false" />')
                    if Rpl != open(o + file, 'rb').read():
                        with open(o + file, 'wb') as f:
                            f.write(Rpl)     
                    if antidec.lower() == 'y':       
                        giai(o + file)   
        path = Files_Directory_Path + f'{NAME_HERO}' + '/skill/'
        AddGetHolidayResourcePath(path)            
        Function_Track_Guid_AddGetHoliday(path)                        
        #===============================================ANTI-DEC====================================================================       
        if antidec.lower() == 'y':
            directory = Files_Directory_Path + f'{NAME_HERO}' + '/skill/'
            num_bytes = '1'
            try:
                num_bytes = int(num_bytes)
            except ValueError:
                pass
            else:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if filename.endswith(".xml"):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if '"Jg' in f.read():
                                continue
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    bytes_to_add = bytes([random.randint(0, 255) for _ in range(num_bytes)])
                    while file_data[-num_bytes:] == bytes_to_add:
                        bytes_to_add = bytes([random.randint(0, 255) for _ in range(num_bytes)])
                    file_data += bytes_to_add
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                        
        #=========================================================NGOAI_HINH==========================================================
        INFO_MOD = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/'
        with zipfile.ZipFile(f'Resources/{version}/Prefab_Characters/Actor_'+f'{IDINFO[:3]}'+'_Infos.pkg.bytes') as f:
            f.extractall(INFO_MOD)
            f.close()
        duongdan=INFO_MOD+'Prefab_Hero/'+f'{NAME_HERO}'+'/'
        newpath=duongdan+'/'+NAME_HERO+'_actorinfo.bytes'
        giai(newpath)
        def skincanmod(data):
            trc1=r.find(timtrc,r.find(b'SkinPrefabG'))
            vt1=r.find(b'JTCom0',trc1-300)
            a1=r[vt1-31:]
            a3=vt1 - 31
            skin1=a1[:4]
            skin2=int.from_bytes(skin1,byteorder='little')
            data=r[a3:a3+skin2]
            return data
        op = newpath
        trc=IDINFO
        with open(op,'rb') as f:
            r=f.read()
            r1=r
            timtrc = trc.encode()
            f.close()
        #skin
        mkcam=b''
        teninfobv1=NAME_HERO
        if IDCHECK == '14111':
            teninfobv1='141_DiaoChan'
        tenefec2=teninfobv1.encode()
        tenefec=teninfobv1.lower().encode()
        newteneffec=tenefec[4:].capitalize()
        newteneffec=tenefec[:4]+newteneffec
        str1 = b"hero_skill_effects/" + tenefec2 + b"/"
        str2 = b"hero_skill_effects/" + tenefec + b"/"
        str3 = b"Hero_Skill_Effects/" + tenefec2 + b"/"
        str4 = b"Hero_Skill_Effects/" + tenefec + b"/"
        str5 = b"hero_skill_effects/" + newteneffec + b"/"
        str7 = b"Hero_Skill_Effects/" + newteneffec + b"/"
        IDskineffecđbt=IDCHECK.encode()+b"/"+IDCHECK.encode()
        idnew=IDCHECK.encode()+b"/"
        mkcam =b''
        new1=b''
        new1+=skincanmod(r)
        if IDCHECK == '13311':
            if phukienv == "vangv":
                new1=ngoaihinhvaneovvang
            if phukienv == "dov":
                new1=ngoaihinhvaneovdo
            if phukienv == '':
                new1=ngoaihinhvaneov
        if IDCHECK == '16707':
            new1=ngoaihinhkhieov
        if IDCHECK == '52007':
            if phukien == "do":
                new1=ngoaihinhdoveres
            if phukien == "xanh":
                new1=ngoaihinhxanhveres
        IDskineffecđbt=IDCHECK.encode()+b"/"+IDCHECK.encode()
        idnew=IDCHECK.encode()+b'/'
        ID1=IDCHECK.encode()
        if new1.find(b'prefab_skill_effects/hero_skill_effects/')!= -1:#rpl = f.read().replace(str1,str1+ idnew).replace(str3,str3 + idnew).replace(str2,str2 + idnew).replace(str4,str4 + idnew).replace(b"""tyEffect" value="true""",b"""tyEffect" value="false""").replace(str5,str5+ idnew).replace(str6,str6 + idnew).replace(str7,str7 + idnew).replace(str8,str8 + idnew)
            FIND=new1.find(b'PreloadAnimatorEffects')-8
            VT1=new1[FIND:FIND+4]
            VTR=int.from_bytes(VT1,byteorder='little')
            VTM=new1[FIND:FIND+VTR]
            VTM9=VTM
            VTM=(VTR+12).to_bytes(4,byteorder='little')+VTM[4:]
            ELe=VTM.find(b'Element')-8
            ELe1=VTM.find(b'Element')-16
            VTRCM=VTM[:ELe-8] #vt đầu PreloadAnimatorEffects
            DAU=VTM[ELe:ELe+4]
            VTR=int.from_bytes(DAU,byteorder='little')
            VTM1=VTM[ELe:ELe+VTR]#chuẩn
            VTM1=(VTR+6).to_bytes(4,byteorder='little')+VTM1[4:]
            VTCUOI=VTM[ELe:]#owr cuoois
            VTCUOI1=VTM[ELe1:ELe1+8] #đếm full eleme
            tinh=VTM.count(b'Element')
            VTM=VTCUOI
            KB=0
            CODEFULL=b''
            for i in range(tinh):
                    ELe=VTM.find(b'Element')-8
                    DAU=VTM[ELe:ELe+4]
                    VTR=int.from_bytes(DAU,byteorder='little')
                    VTM1=VTM[ELe:ELe+VTR]#chuẩn
                    if VTM1.find(b'Vprefab_skill_effects/hero_skill_effects/') == -1:
                        CODEFULL+=VTM1
                        break
                    VTM1=(VTR+6).to_bytes(4,byteorder='little')+VTM1[4:]
                    VTCUOI=VTM[VTR:]
                    ELe1=VTM.find(b'Element')+7
                    DAU1=VTM[ELe1:ELe1+4]
                    VTR=int.from_bytes(DAU1,byteorder='little')
                    VTM2=VTM[ELe1:ELe1+VTR]#đếm r
                    VTM2=(VTR+6).to_bytes(4,byteorder='little')+VTM2[4:]
                    newvt=VTM1.find(b'Vprefab_skill_effects/')-8
                    MOI=VTM1[newvt:newvt+4]
                    VTR=int.from_bytes(MOI,byteorder='little')
                    VTR3=VTM1[newvt:newvt+VTR]
                    VTM3=(VTR+6).to_bytes(4,byteorder='little')+VTR3[4:]
                    CODE=VTM1[:15]+VTM2[:46]+VTM3+b'\x04\x00\x00\x00\x04\x00\x00\x00'
                    VTM=VTCUOI
                    CODEFULL+=CODE
            CODEFULL=CODEFULL.replace(str1,str1+ idnew).replace(str2,str2 + idnew)#.to_bytes(4,byteorder='little')
            CODEFULL=len(VTRCM+VTCUOI1+CODEFULL).to_bytes(4,byteorder='little')+VTRCM[4:]+(len(VTCUOI1+CODEFULL)).to_bytes(4,byteorder='little')+VTCUOI1[4:]+CODEFULL
            new1=new1.replace(VTM9,CODEFULL)
            new1=len(new1).to_bytes(4,byteorder='little')+new1[4:]
            mkcam = b'\x05'#\x05
        skinmoi=new1
        skinprefag=r.find(b'SkinPrefabG')-8
        tinhskinpre=r[skinprefag:skinprefag+4]
        tinhskinpre1=int.from_bytes(tinhskinpre,byteorder='little')
        tinhskinpre2=r[skinprefag:skinprefag+tinhskinpre1] #
        JTCom0 = tinhskinpre2.count(b"JTCom0")
        beginskin=tinhskinpre2[:101]
        CodeSkinNew=beginskin+new1*JTCom0 #
        tinhCodeSkinNew1=CodeSkinNew[:93]
        tinhCodeSkinNew=CodeSkinNew[93:]
        Elenmen=len(tinhCodeSkinNew).to_bytes(4,byteorder='little')+tinhCodeSkinNew[4:]
        SkinPrefag1=tinhCodeSkinNew1+Elenmen
        SkinPrefag=len(SkinPrefag1).to_bytes(4,byteorder='little')+SkinPrefag1[4:]
        codeskinnew=r1.replace(tinhskinpre2,SkinPrefag)

        def ArtSkinPrefabLOD(data3):
            a=skinmoi.find(b'\x00ArtSkinPrefabLOD')-7
            a10=skinmoi.find(b'\x00ArtSkinPrefabLOD')-3
            a3=skinmoi[a:a+8]
            a4=a3[4:]
            a2=skinmoi[a:a+4]
            vitri=int.from_bytes(a2,byteorder='little')
            vitri2=int.from_bytes(a4,byteorder='little')
            a5=skinmoi[a:a+vitri]
            a25=skinmoi[a10:a10+vitri2]
            a22=skinmoi[a10:a10+vitri2].replace(b'\x00ArtSkinPrefabLOD',b'\x00ArtPrefabLOD')
            a13=len(a22).to_bytes(4,byteorder='little')+a22[4:]
            code=a5.replace(a25,a13)
            data3=len(code).to_bytes(4,byteorder='little')+code[4:]
            return data3 
        def ArtSkinLobbyShowLOD(data4):
            a=skinmoi.find(b'\x00ArtSkinLobbyShowLOD')-7
            a10=skinmoi.find(b'\x00ArtSkinLobbyShowLOD')-3
            a3=skinmoi[a:a+8]
            a4=a3[4:]
            a2=skinmoi[a:a+4]
            vitri=int.from_bytes(a2,byteorder='little')
            vitri2=int.from_bytes(a4,byteorder='little')
            a5=skinmoi[a:a+vitri]
            a25=skinmoi[a10:a10+vitri2]
            a22=skinmoi[a10:a10+vitri2].replace(b'\x00ArtSkinLobbyShowLOD',b'\x00ArtLobbyShowLOD')
            a13=len(a22).to_bytes(4,byteorder='little')+a22[4:]
            code=a5.replace(a25,a13)
            data4=len(code).to_bytes(4,byteorder='little')+code[4:]
            return data4
        #codeskinmd
        SkinMD=r[:skinprefag]
        #skinmd Art
        Art=SkinMD.find(b'ArtPrefabLOD')-8
        tinhskinpre=SkinMD[Art:Art+4]
        tinhskinpre1=int.from_bytes(tinhskinpre,byteorder='little')
        tinhskinpre2=SkinMD[Art:Art+tinhskinpre1] #
        #skinmd ArtLobbyShowLOD
        ArtLobby=SkinMD.find(b'ArtLobbyShowLOD')-8
        tinhArtLobby=SkinMD[ArtLobby:ArtLobby+4]
        tinhArtLobby1=int.from_bytes(tinhArtLobby,byteorder='little')
        tinhArtLobby2=SkinMD[ArtLobby:ArtLobby+tinhArtLobby1] #
        ArtSkinPrefab=b''
        ArtSkinPrefab+=ArtSkinPrefabLOD(skinmoi)
        CodeNewMD=SkinMD.replace(tinhskinpre2,ArtSkinPrefab)
        ArtSkinLobby=b''
        ArtSkinLobby+=ArtSkinLobbyShowLOD(skinmoi)
        CodeNewMD=CodeNewMD.replace(tinhArtLobby2,ArtSkinLobby)
        ArtLobbyIdle=CodeNewMD.find(b'ArtLobbyIdleShowLOD0')-8
        cammd=CodeNewMD[ArtLobbyIdle:999999]
        ArtLobbyIdleSkin=skinmoi.find(b'ArtSkinLobbyIdleShowLOD')-8
        camSkin=skinmoi[ArtLobbyIdleSkin:999999]
        camSkin=ArtSkinLobbyIdleShowLOD(camSkin)
        if mkcam == b'\x05':
            camSkin=camSkin.replace(CODEFULL,b'')
        CodeNewMD=CodeNewMD.replace(cammd,camSkin)
        CodeFull=codeskinnew.replace(SkinMD,CodeNewMD)
        RootDtrc=CodeFull[:84]
        RootDsau=CodeFull[84:]
        RootD1=RootDsau[8:12]
        VTR=int.from_bytes(RootD1,byteorder='little')#ArtPrefabLOD
        m=RootDsau.find(b'ArtPrefabLOD')-8
        tinhRootDsau=len(RootDsau).to_bytes(4,byteorder='little')+RootDsau[4:]
        tinhRootDtrc=RootDtrc+tinhRootDsau
        CodeDayDu=len(tinhRootDtrc).to_bytes(4,byteorder='little')+tinhRootDtrc[4:]
        CodeDayDu=CodeDayDu.replace(b"Light<",b"00000<")
        CodeDayDu=CodeDayDu.replace(b'_LOD2',b'_LOD1').replace(b'_LOD3',b'_LOD1').replace(b'_Show2\x04',b'_Show1\x04').replace(b'_Show3\x04',b'_Show1\x04')
        tinhcam=CodeDayDu[:89]
        with open(op,'wb')as f: f.write(CodeDayDu)
        o=open(op,'rb')
        h=o.read(92)
        k=0
        while True:
            r1=o.read(4)
            if r1==b'':
                break
            KB=r1.hex()
            KB=KB[6:8]+KB[4:6]+KB[2:4]+KB[0:2]
            KB=int(KB,16)
            O=r1+o.read(KB-4)
            k+=1
        o.close()
        k=k.to_bytes(1,byteorder='little')
        tinhcam1=CodeDayDu[:88]+k
        CodeDayDu=CodeDayDu.replace(tinhcam,tinhcam1)
        with open(op,'wb')as f: f.write(CodeDayDu)

        #=========================================================================================================================            
        LC = '1'
        Directory = newpath
        process_directory(Directory, LC)
        with open(Directory, 'rb') as code_cre:
            cre = code_cre.read()
            cre = re.sub(rb'<ActorName var="String" type="System.String" value=".*?"/>',b'<ActorName var="String" type="System.String" value="NGC_6503"/>',cre)
        with open(Directory, 'wb') as f:
            f.write(cre)
        LC = '2'
        Directory = newpath
        process_directory(Directory, LC)  

        #=========================================================================================================================                  
        if IDCHECK == "19015":
            LC = '1'
            Directory = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/Prefab_Hero/190_ZhuGeLiang/190_ZhuGeLiang_actorinfo.bytes'
            process_directory(Directory, LC)
            with open(Directory, 'rb') as code_tulen:
                tulen = code_tulen.read()
                tulen = tulen.replace(b'\n  <useMecanim var="String" type="System.Boolean" value="True"/>', b'')
            with open(Directory, 'wb') as f:
                f.write(tulen)
            LC = '2'
            Directory = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/Prefab_Hero/190_ZhuGeLiang/190_ZhuGeLiang_actorinfo.bytes'
            process_directory(Directory, LC)
            
        #=========================================================TRAP_ELSU==========================================================
        if IDCHECK[:3] == '196':
            if b"Skin_Icon_Skill" in dieukienmod:
                giai(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/Prefab_Hero/196_Elsu/196_Elsu_trap_actorinfo.bytes')
                LC = '1'
                Directory = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/Prefab_Hero/196_Elsu/196_Elsu_trap_actorinfo.bytes'
                process_directory(Directory, LC)
                with open(Directory, 'rb') as code_elsu:
                    elsu = code_elsu.read()
                    elsu = elsu.replace(b'Prefab_Skill_Effects/Hero_Skill_Effects/196_Elsu/BaiLiShouYue_attack02_spell01_LOD', b'Prefab_Skill_Effects/Hero_Skill_Effects/196_Elsu/' + IDCHECK.encode() + b'/BaiLiShouYue_attack02_spell01_LOD')
                with open(Directory, 'wb') as f:
                    f.write(elsu)
                LC = '2'
                Directory = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/Prefab_Hero/196_Elsu/196_Elsu_trap_actorinfo.bytes'
                process_directory(Directory, LC) 
                
        #=========================================================BIEN_VE==========================================================
        if b"Skin_Icon_BackToTown" in dieukienmod or b"Skin_Icon_Animation" in dieukienmod:
            cod = CODEBIENVE
            duongdan = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/Back.xml'

            for ibv in range(1, 2):
                if SKINEOV in ('r', 'b', 'y', 'l'):
                    break
                with open(duongdan, 'rb') as f:
                    bv = f.read()
                    f.close()                   
                ab = b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'
                ab = ab.replace(b'guid="tentuong', b'guid="' + AABBCC.encode('utf-8') + b'_' + NAME_HERO.encode())
                codenew = cod.replace(b'stopAfterLastEvent="true">', b'stopAfterLastEvent="true">' + ab)
                aa = b''
                aa += bienve(codenew)
                aabv = b''
                aabv += bienvecheck(codenew)
                CodeFullBV = aa
                codenew = bv.replace(projack, aabv)
                codenew = codenew.replace(b'\r\n  </Action>\r\n</Project>', CodeFullBV)
                with open(duongdan, 'wb') as f:
                    f.write(codenew)

        #=========================================================================================================================                    
            if SKINEOV == 'b':
                with open(duongdan, 'rb') as f:
                    bv = f.read()
                    f.close()
                ab = b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'
                ab = ab.replace(b'guid="tentuong', b'guid="' + AABBCC.encode('utf-8') + b'_' + NAME_HERO.encode())
                cod = bienvengokonhocty
                codenew = cod.replace(b'stopAfterLastEvent="true">', b'stopAfterLastEvent="true">' + ab)
                aabv = b''
                aabv += bienvecheck(codenew)
                codenew = bv.replace(projack, aabv).replace(b'\r\n  </Action>\r\n</Project>', codenew)
                with open(duongdan, 'wb') as f:
                    f.write(codenew)

        #=========================================================================================================================                    
            if SKINEOV == 'r':
                with open(duongdan, 'rb') as f:
                    bv = f.read()
                    f.close()
                ab = b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'
                ab = ab.replace(b'guid="tentuong', b'guid="' + AABBCC.encode('utf-8') + b'_' + NAME_HERO.encode())
                cod = bienvevanxathan
                codenew = cod.replace(b'stopAfterLastEvent="true">', b'stopAfterLastEvent="true">' + ab)
                aabv = b''
                aabv += bienvecheck(codenew)
                codenew = bv.replace(projack, aabv).replace(b'\r\n  </Action>\r\n</Project>', codenew)
                with open(duongdan, 'wb') as f:
                    f.write(codenew)              

        #=========================================================================================================================                    
            if SKINEOV == 'y':
                with open(duongdan, 'rb') as f:
                    bv = f.read()
                    f.close()
                ab = b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'
                ab = ab.replace(b'guid="tentuong', b'guid="' + AABBCC.encode('utf-8') + b'_' + NAME_HERO.encode())
                cod = CODEBVYENA
                codenew = cod.replace(b'stopAfterLastEvent="true">', b'stopAfterLastEvent="true">' + ab)
                aabv = b''
                aabv += bienvecheck(codenew)
                codenew = bv.replace(projack, aabv).replace(b'\r\n  </Action>\r\n</Project>', codenew)
                with open(duongdan, 'wb') as f:
                    f.write(codenew)

        #=========================================================================================================================                                
            if SKINEOV == 'l':
                with open(duongdan, 'rb') as f:
                    bv = f.read()
                    f.close()
                ab = b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'
                ab = ab.replace(b'guid="tentuong', b'guid="' + AABBCC.encode('utf-8') + b'_' + NAME_HERO.encode())
                cod = CODEBVLILI
                codenew = cod.replace(b'stopAfterLastEvent="true">', b'stopAfterLastEvent="true">' + ab)
                aabv = b''
                aabv += bienvecheck(codenew)
                codenew = bv.replace(projack, aabv).replace(b'\r\n  </Action>\r\n</Project>', codenew)
                with open(duongdan, 'wb') as f:
                    f.write(codenew)                                                                

        #=========================================================GIA_TOC==========================================================
        if b"Skin_Icon_BackToTown" in dieukienmod or b"Skin_Icon_Animation" in dieukienmod:
            RPL = CODE_BV_HERO    
            cod = CODEBIENVE    
            duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/HasteE1.xml'    
            for ibv in range(1,2):    
                with open(duongdan,'rb') as f: a234123=f.read()    
                f.close()    
                ab=b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'    
                codenew=gtHasteE1.replace(b'stopAfterLastEvent="true">',b'stopAfterLastEvent="true">'+ab)    
                aa=b''    
                aa+=hasteE1(codenew)    
                aabv=b''    
                aabv+=hasteE1check(CODECHECKGT)
                CodeFullBV=aa    
                codenew=a234123.replace(b'\r\n  </Action>\r\n</Project>',aabv)    
                codenew=codenew.replace(b'\r\n  </Action>\r\n</Project>',CodeFullBV)    
                if IDCHECK == '11113':    
                    codenew = codenew.replace(b'''11113/JiaSu_tongyong_01" refParamName="" useRefParam="false" />''',haste11113)
                if IDCHECK == '51015':    
                    codenew = codenew.replace(b'''51015/JiaSu_tongyong_01" refParamName="" useRefParam="false" />''',haste51015)    
                if IDCHECK == '16307':    
                    codenew = codenew.replace(b'16307/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''16307/juyoujing_jiasu_01" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="0.000" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '50112':    
                    codenew = codenew.replace(b'50112/JiaSu_tongyong_01',b'50112/suanni_sprint')    
                if IDCHECK == '13116':    
                    codenew = codenew.replace(b'13116/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''13116/huijidi_01_lobby" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.300" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '15412':    
                    codenew = codenew.replace(b'15412/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''15412/huijidi_01_lobby" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.300" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '11607':    
                    codenew = codenew.replace(b'11607/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''11607/jingke_sprint_01" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.300" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '14111':    
                    codenew = codenew.replace(b'14111/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''14111/14111_luoer_Sprint" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.200" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '15009':    
                    codenew = codenew.replace(b'15009/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''15009/T2_Spint" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.150" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '15015':    
                    codenew = codenew.replace(b'''15015/JiaSu_tongyong_01" refParamName="" useRefParam="false" />''',haste15015)    
                if IDCHECK == '52011':    
                    codenew = codenew.replace(b'52011/JiaSu_tongyong_01',b'52011/520_Veres_long_sprint_loop')    
                if IDCHECK == '54307':    
                    codenew = codenew.replace(b'54307/JiaSu_tongyong_01',b'54307/yao_sprint')                    
                codenew = codenew.replace(b'JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'JiaSu_tongyong_01" refParamName="" useRefParam="false" />\n        <Vector3 name="bindPosOffset" x="0.000" y="0.700" z="-0.600" refParamName="" useRefParam="false" />')
                with open (duongdan,'wb') as f : f.write(codenew)    

        #=========================================================================================================================            
                duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/HasteE1_leave.xml'    
                with open(duongdan,'rb') as f: a234123=f.read()    
                f.close()    
                ab=b'\r\n      <Condition id="0" guid="tentuong" status="true"/>'    
                codenew=gtHasteE1_leave.replace(b'stopAfterLastEvent="true">',b'stopAfterLastEvent="true">'+ab)    
                aa=b''    
                aa+=hasteE1_leave(codenew)    
                aabv=b''    
                aabv+=hasteE1check(CODECHECKGT)
                CodeFullBV=aa    
                codenew=a234123.replace(b'\r\n  </Action>\r\n</Project>',aabv)    
                codenew=codenew.replace(b'\r\n  </Action>\r\n</Project>',CodeFullBV)    
                if IDCHECK == '16307':    
                    codenew = codenew.replace(b'16307/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''16307/juyoujing_jiasu_01" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="0.000" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '50112':    
                    codenew = codenew.replace(b'50112/JiaSu_tongyong_01',b'50112/suanni_sprint')    
                if IDCHECK == '13116':    
                    codenew = codenew.replace(b'13116/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''13116/huijidi_01_lobby" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.300" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '15412':    
                    codenew = codenew.replace(b'15412/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''15412/huijidi_01_lobby" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.300" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '11607':    
                    codenew = codenew.replace(b'11607/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''11607/jingke_sprint_01" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.300" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '14111':    
                    codenew = codenew.replace(b'14111/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''14111/14111_luoer_Sprint" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.200" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '15009':    
                    codenew = codenew.replace(b'15009/JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'''15009/T2_Spint" refParamName="" useRefParam="false" />
        <Vector3 name="bindPosOffset" x="0.000" y="-0.150" z="0.000" refParamName="" useRefParam="false" />    ''')
                if IDCHECK == '15015':    
                    codenew = codenew.replace(b'''15015/JiaSu_tongyong_01" refParamName="" useRefParam="false" />''',haste15015)    
                if IDCHECK == '52011':    
                    codenew = codenew.replace(b'52011/JiaSu_tongyong_01',b'52011/520_Veres_long_sprint_loop')    
                if IDCHECK == '54307':    
                    codenew = codenew.replace(b'54307/JiaSu_tongyong_01',b'54307/yao_sprint')    
                codenew = codenew.replace(b'JiaSu_tongyong_01" refParamName="" useRefParam="false" />',b'JiaSu_tongyong_01" refParamName="" useRefParam="false" />\n        <Vector3 name="bindPosOffset" x="0.000" y="0.700" z="-0.600" refParamName="" useRefParam="false" />')
                with open (duongdan,'wb') as f : f.write(codenew)    
        #=========================================================Animation-Dance.xml==========================================================
        duongdandance=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/Dance.xml'
        with open (duongdandance, 'rb') as f:
            noidungxx = f.read()                
            noidungxx = noidungxx.replace(b'</Action>', FIXDANCE)
        with open (duongdandance,'wb') as f : f.write(noidungxx)

        #=========================================================CheckSkin-Dance.xml==========================================================
        if IDCHECK == "10620":
            duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/Dance.xml'
            with open (duongdan, 'rb') as f:
                noidungxx = f.read()                
                noidungxx = noidungxx.replace(b'"skinId" value="10620"', b'"heroId" value="106"')
            with open (duongdan,'wb') as f : f.write(noidungxx)

        #=========================================================================================================================                        
        if IDCHECK == "52011":
            duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/Dance.xml'
            with open (duongdan, 'rb') as f:
                noidungxx = f.read()                
                noidungxx = noidungxx.replace(b'"skinId" value="52011"', b'"heroId" value="520"')
            with open (duongdan,'wb') as f : f.write(noidungxx)                        
            
        #=========================================================CheckSkin-DanceBullet.xml==========================================================
        if IDCHECK == "10620":
            duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/DanceBullet.xml'
            with open (duongdan, 'rb') as f:
                noidungxx = f.read()                
                noidungxx = noidungxx.replace(b'"skinId" value="10620"', b'"heroId" value="106"')
            with open (duongdan,'wb') as f : f.write(noidungxx)

        #=========================================================================================================================                        
        if IDCHECK == "52011":
            duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/DanceBullet.xml'
            with open (duongdan, 'rb') as f:
                noidungxx = f.read()                
                noidungxx = noidungxx.replace(b'"skinId" value="52011"', b'"heroId" value="520"')
            with open (duongdan,'wb') as f : f.write(noidungxx)            

        #=========================================================================================================================                        
        if IDCHECK == "54402":
            duongdan=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/DanceBullet.xml'
            with open (duongdan, 'rb') as f:
                noidungxx = f.read()                
                noidungxx = noidungxx.replace(b'"skinId" value="54402"', b'"heroId" value="544"')
            with open (duongdan,'wb') as f : f.write(noidungxx)                        
            
        #=========================================================Cam Xa==========================================================            
        if CAMXA.lower() == 'y':
            duongdancamxa=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/PassiveResource/junglemark.xml'
            giai(duongdancamxa)
            with open (duongdancamxa, 'rb') as f:
                noidungsexx = f.read()            
                noidungsexx = noidungsexx.replace(b'</Action>', b"""  <Track trackName="SetCameraHeightDuration0" eventType="SetCameraHeightDuration" guid="9489c796-894b-4c2e-9a95-acf27873964a" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">\n    <Event eventName="SetCameraHeightDuration" time="0.000" length="1.000" isDuration="true" guid="422a1ed9-a12c-44b3-a9c5-3fe899d689dd">\n      <int name="slerpTick" value="0" refParamName="" useRefParam="false"/>\n        <float name="heightRate" value="1.400" refParamName="" useRefParam="false"/>\n        <bool name="bOverride" value="true" refParamName="" useRefParam="false"/>\n        <bool name="leftTimeSlerpBack" value="true" refParamName="" useRefParam="false"/>\n        <String name="refParamName" value="" refParamName="" useRefParam="false"/>\n      </Event>\n	</Track>\n <Track trackName="InBattleMsgSendTick0" eventType="InBattleMsgSendTick" guid="5169fb6a-26eb-4bf0-ae25-0da74fe7d84a" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">\n	<Event eventName="InBattleMsgSendTick" time="0.000" isDuration="false" guid="9473c11a-e73b-4a84-b950-3b39d37dee13">\n	  <TemplateObject name="targetId" id="0" objectName="self" isTemp="false" refParamName="" useRefParam="false" />\n  	<String name="msgKey" value="Create:DiaoChan" refParamName="" useRefParam="false" />\n	</Event>\n  </Track>\n    </Action>""")    
            with open (duongdancamxa,'wb') as f : f.write(noidungsexx)
            giai(duongdancamxa)
            
        #=========================================================HIEU_UNG_VE_THAN==========================================================
        if IDCHECK in ("50108","14111","11107","15009","13015"):
            organSkin = f"Resources/{version}/Databin/Client/Actor/organSkin.bytes"
            organSkin_mod = f"FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Databin/Client/Actor/organSkin.bytes"
            shutil.copy(organSkin, organSkin_mod)
            giai(organSkin_mod)
            ID = IDCHECK
            file = open(organSkin_mod, "rb")
            IDN = str(hex(int(ID)))
            IDN = IDN[4:6] + IDN[2:4]
            IDN = bytes.fromhex(IDN)
            ALL_ID = []
            MD = int(ID[0:3] + "00")
            for IDNew in range(21):
                ALL_ID.append(str(MD))
                MD += 1
            ALL_ID.remove(ID)
            for x in range(20):
                IDK = str(hex(int(ALL_ID[x])))
                IDK = IDK[4:6] + IDK[2:4]
                IDK = bytes.fromhex(IDK)
                ALL_ID[x] = IDK
            Begin = file.read(140)
            Read = b"\x00"
            All = []
            while Read != b"":
                Read = file.read(36)
                if Read.find(IDN) != -1:
                    All.append(Read)
                try:
                    Max = Read[4] + (Read[5]*256)
                    Max0 = str(hex(Max))
                    if len(Max0) == 4:
                        Max0 = Max0[2:4] + "00"
                    if len(Max0) == 5:
                        Max0 = Max0[3:5] + "0" + Max0[2]
                    if len(Max0) == 6:
                        Max0 = Max0[4:6] + Max0[2:4]
                    Max0 = bytes.fromhex(Max0)
                except:
                    None
            file.close()
            file = open(organSkin_mod, "ab+")
            Read0 = file.read()
            for i in range(len(ALL_ID)):
                for j in range(len(All)):
                    CT = All[j]
                    if CT.find(IDN) != -1:
                        CT = CT.replace(IDN,ALL_ID[i])
                    else:
                        CT = CT.replace(ALL_ID[i-1],ALL_ID[i])
                    CTN = str(hex(Max0[0]+(Max0[1]*256)+1))
                    if len(CTN) == 4:
                        CTN = CTN[2:4]
                    if len(CTN) == 5:
                        CTN = CTN[3:5] + "0" + CTN[2]
                    if len(CTN) == 6:
                        CTN = CTN[4:6] + CTN[2:4]
                    CTN = bytes.fromhex(CTN)
                    OZ = b" \x00\x00\x00"
                    if len(CTN) == 1:
                        CT = CT.replace(OZ+CT[4:6],OZ+CTN+b"\x00",1)
                    if len(CTN) == 2:
                        CT = CT.replace(OZ+CT[4:6],OZ+CTN,1)
                    All[j] = CT
                    XXX = file.write(CT)
                    Max0 = CT[4:6]
            file.close()
            file = open(organSkin_mod, "rb")
            Read = file.read()
            Read = Read.replace(Begin[12:14],Max0,1)
            file.close()
            file = open(organSkin_mod, "wb")
            Z = file.write(Read)
            file.close()
        #=========================================================HABUANAK==========================================================
        if IDCHECK == "15009":
            duongdan1=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/PassiveResource/BlueBuff.xml'
            duongdan2=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/PassiveResource/RedBuff_Slow.xml'
            giai(duongdan1)
            giai(duongdan2)
            with open (duongdan1, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b"CheckSkinIdVirtualTick", b"CheckHeroIdTick").replace(b'"skinId" value="15009"', b'"heroId" value="150"')
            with open (duongdan1,'wb') as f : f.write(noidung)
            with open (duongdan2, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b"CheckSkinIdVirtualTick", b"CheckHeroIdTick").replace(b'"skinId" value="15009"', b'"heroId" value="150"')
            with open (duongdan2,'wb') as f : f.write(noidung)

        #=========================================================Biến Hình INFO 15013==========================================================
        if IDCHECK == "15013":
            duongdan1=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/PassiveResource/BlueBuff_CD.xml'
            giai(duongdan1)
            with open (duongdan1, 'rb') as f:
                noidung = f.read()
                noidung = noidung.replace(b"CheckSkinIdTick", b"CheckHeroIdTick").replace(b'"skinId" value="15013"', b'"heroId" value="150"')
            with open (duongdan1,'wb') as f : f.write(noidung)
            
        #=========================================================Giáp Cuồng Nộ 54402==========================================================
        if IDCHECK == "54402":
            giapcuongnoyan = input("\033[1;97m[\033[1;92m?\033[1;97m] SPECIAL: 54402 - MOD EFX GIÁP CUỒNG NỘ YAN Y/n \n[\033[1;92m•\033[1;97m] INPUT: ")
            if giapcuongnoyan.lower() == 'y':	
                with zipfile.ZipFile(f'Resources/{version}/Ages/Prefab_Gear.pkg.bytes') as f:
    	            f.extractall(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/mod2/')        
                file_path=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/mod2/Prefab_Gear/Defense/1338E1.xml'
                giai(file_path)
                with open (file_path, 'rb') as f:
                    noidung = f.read()
                    noidung = noidung.replace(b"</Action>", b"""  <Track trackName="DiaoChan" eventType="CheckHeroIdTick" guid="DiaoChan-54402" enabled="true" refParamName="" useRefParam="false" r="0.667" g="1.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true">\r\n      <Event eventName="CheckHeroIdTick" time="0.000" isDuration="false">\r\n        <TemplateObject name="targetId" objectName="target" id="1" isTemp="false" refParamName="" useRefParam="false"/>\r\n        <int name="heroId" value="544" refParamName="" useRefParam="false"/>\r\n      </Event>\r\n    </Track>\r\n    <Track trackName="TriggerParticle0" eventType="TriggerParticle" guid="NGC_6503" enabled="true" useRefParam="false" refParamName="" r="0.000" g="0.000" b="0.000" execOnForceStopped="false" execOnActionCompleted="false" stopAfterLastEvent="true" lod="0">\r\n      <Condition id="0" guid="DiaoChan-54402" status="true" />\r\n      <Event eventName="TriggerParticle" time="0.000" length="2.000" isDuration="true" guid="NGC_6503">\r\n        <TemplateObject name="targetId" id="0" objectName="self" isTemp="false" refParamName="" useRefParam="false" />\r\n        <TemplateObject name="objectSpaceId" id="0" objectName="self" isTemp="false" refParamName="" useRefParam="false" />\r\n        <String name="resourceName" value="prefab_skill_effects/hero_skill_effects/544_Painter/54402/jiasu_tongyong_01" refParamName="" useRefParam="false" />\r\n        <Vector3 name="bindPosOffset" x="0.000" y="0.700" z="-0.600" refParamName="" useRefParam="false" />\r\n        <Vector3i name="scalingInt" x="10000" y="10000" z="10000" refParamName="" useRefParam="false" />\r\n        <String name="syncAnimationName" value="" refParamName="" useRefParam="false" />\r\n        <String name="customTagName" value="" refParamName="" useRefParam="false" />\r\n      </Event>\r\n    </Track>\r\n  </Action>""")
                with open (file_path,'wb') as f : f.write(noidung)          
                Track_Guid_Skill(file_path)  
                try:
                    folder_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/mod2/'
                    output_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Gear.pkg.bytes'
                    zip_folder(folder_path, output_path)
                except Exception as e:
                    print(e)
                shutil.rmtree(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/mod2/', ignore_errors=True)                
            
        #=========================================================KillBoard==========================================================
        if IDCHECK[:3] == "150":
            killboardask = input('\033[1;97m[\033[1;92m!\033[1;97m] \033[1;97mThông báo hạ Nakroth (Use skin Producer Tia chớp): \n  [1] Có\n  [2] Không\nEnter>: ')
            if killboardask == '1':
                killboardaskinfo = 'Có'
            else:
                killboardaskinfo = 'Không'
        if IDCHECK in ["15001","15002","15003","15004","15005","15006","15007","15008","15009","15010","15011","15012","15013","15014","15015","15016","15017","15018","15019","15020"]:
            if killboardaskinfo == 'Có':
                killboardselect = input('\033[1;97m[\033[1;92m!\033[1;97m] \033[1;97mThông báo hạ: \n  [1] Nakroth Killua\n  [2] Nakroth Bạch Diện\n  [3] Nakroth Quỷ Thương\n  [4] Skin Khác\nEnter>: ')
                if killboardselect == '1':
                    killboardlist = '9'
                elif killboardselect == '2':
                    killboardlist = '20'
                elif killboardselect == '3':
                    killboardlist = '16'
                elif killboardselect == '4':
                    killboardother = input('\033[1;97m[\033[1;92m!\033[1;97m] \033[1;97mThông báo hạ: \n  [1] Murad Tuyệt Thế Thần Binh\n  [2] Veres Lưu Ly Long Mẫu\n  [3] Yena Huyền Cửu Thiên\n  [4] Elandorr Tuxedo Mask\n  [5] Airi Thứ Nguyên Vệ thần\n  [6] Hayate Tu Di Thánh Đế\n  [7] Ngộ Không Tân Niên Võ Thần\n  [8] Enzo Kurapika\n  [9] Raz Gon\n  [10] Grakk Thần Ẩm Thực\n  [11] Krixi Phù Thủy Thời Không\n  [12] Aya Công Chúa Cầu Vồng\n  [13] Butterfly Kim Ngư Thần Nữ\n  [14] Alice Eternal Sailor Chibi Moon\n  [15] Điêu Thuyền Eternal Sailor Moon\n  [16] Triệu Vân Thần Tài\nEnter>: ')
                    if killboardother == '1':#murad tuyet the than binh
                        killboardlist = '13'
                    elif killboardother == '2':#veres luu ly
                        killboardlist = '15'
                    elif killboardother == '3':#yena hct
                        killboardlist = '11'
                    elif killboardother == '4':#elandorr tm
                        killboardlist = '6'
                    elif killboardother == '5':#airi tnvt
                        killboardlist = '12'
                    elif killboardother == '6':#hayate tu di
                        killboardlist = '2'
                    elif killboardother == '7':#ngo khong tan nien
                        killboardlist = '3'
                    elif killboardother == '8':#enzo kurapika
                        killboardlist = '8'
                    elif killboardother == '9':#raz gon
                        killboardlist = '10'
                    elif killboardother == '10':#grakk than am thuc
                        killboardlist = '14'
                    elif killboardother == '11':#krixi phu thuy
                        killboardlist = '19'
                    elif killboardother == '12':#aya cong chua
                        killboardlist = '17'
                    elif killboardother == '13':#butterfly kim ngu
                        killboardlist = '7'
                    elif killboardother == '14':#alice escm
                        killboardlist = '5'
                    elif killboardother == '15':#dieu thuyen esm
                        killboardlist = '4'
                    elif killboardother == '16':#tv than tai
                        killboardlist = '1'
                    else:
                        killboardlist = '18'
                else:
                    killboardlist = '18'
                
                idgoc = str.encode('/18/')
                idkill = str.encode('/{}/'.format(killboardlist))
                hex11d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f312f")
                hex11e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f312f")
                
                hex21d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f322f")
                hex21e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f322f")
                
                hex31d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f332f")
                hex31e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f332f")
                
                hex41d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f342f")
                hex41e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f342f")
                
                hex51d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f352f")
                hex51e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f352f")
                
                hex61d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f362f")
                hex61e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f362f")
                
                hex71d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f372f")
                hex71e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f372f")
                
                hex81d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f382f")
                hex81e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f382f")
                
                hex91d = bytes.fromhex("0000001d000000554933442f426174746c652f42726f6164636173742f392f")
                hex91e = bytes.fromhex("0000001e000000554933442f426174746c652f42726f6164636173742f392f")
                with open (huanhua_mod, 'rb') as nak:
                    kill = nak.read()
                    kill = kill.replace(idgoc, idkill)
                    if len(idkill) < 10:
                        if idkill == '1':
                            kill = kill.replace(hex11e, hex11d)
                        if idkill == '2':
                            kill = kill.replace(hex21e, hex21d)
                        if idkill == '3':
                            kill = kill.replace(hex31e, hex31d)
                        if idkill == '4':
                            kill = kill.replace(hex41e, hex41d)
                        if idkill == '5':
                            kill = kill.replace(hex51e, hex51d)
                        if idkill == '6':
                            kill = kill.replace(hex61e, hex61d)
                        if idkill == '7':
                            kill = kill.replace(hex71e, hex71d)
                        if idkill == '8':
                            kill = kill.replace(hex81e, hex81d)
                        if idkill == '9':
                            kill = kill.replace(hex91e, hex91d)
                with open (huanhua_mod, 'wb') as nak: nak.write(kill)
                
        #=========================================================FIXLAG==========================================================
        if b"Skin_Icon_Skill" in dieukienmod or IDCHECK in ["53702", "53002"]:
            shutil.copy(f'Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes', f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes')
            Path=f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes'
            giai(Path)
            LC = '1'
            Directory = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes'
            process_directory(Directory, LC)
            if IDCHECK == '16707':
                CODE_EFF1 = b"hero_skill_effects/167_wukong/"
                CODE_EFF2 = b"component_effects/16707/16707_5/"
                CODE_EFF3 = b"Hero_Skill_Effects/167_Wukong/"
                CODE_EFF4 = b"component_effects/16707/16707_5/"
                with open (f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes', 'rb') as f:
                    codefix = f.read()
                codefix = codefix.replace(CODE_EFF1, CODE_EFF2).replace(CODE_EFF3, CODE_EFF4)
                with open(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes','wb') as f:f.write(codefix)
            if IDCHECK == '13311':
                CODE_EFF1 = b"prefab_skill_effects/hero_skill_effects/133_direnjie/"
                CODE_EFF2 = b"prefab_skill_effects/component_effects/13311/13311_5/"
                CODE_EFF3 = b"Prefab_Skill_Effects/Hero_Skill_Effects/133_DiRenJie/"
                CODE_EFF4 = b"prefab_skill_effects/component_effects/13311/13311_5/"
                with open (f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes', 'rb') as f:
                    codefix = f.read()
                codefix = codefix.replace(CODE_EFF1, CODE_EFF2).replace(CODE_EFF3, CODE_EFF4)
                with open(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes','wb') as f:f.write(codefix)
            if IDCHECK[:3] == '111':
                CODE_EFF1 = ('hero_skill_effects/'+NAME_HERO+'/').lower().encode()
                CODE_EFF2 = ('hero_skill_effects/'+NAME_HERO+'/'+IDCHECK+'/').lower().encode()
                CODE_EFF3 = ('Hero_Skill_Effects/'+NAME_HERO+'/').encode()
                CODE_EFF4 = ('Hero_Skill_Effects/'+NAME_HERO+'/'+IDCHECK+'/').encode()
                with open (f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes', 'rb') as f:
                    codefix = f.read()
                codefix = codefix.replace(CODE_EFF1, CODE_EFF2).replace(CODE_EFF3, CODE_EFF4).replace(b'hero_skill_effects/T3_Sunshuangxiang_skill_01_attack_01',b'hero_skill_effects/'+IDCHECK.encode()+b'/T3_Sunshuangxiang_skill_01_attack_01')
                with open(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes','wb') as f:f.write(codefix)           
            if IDCHECK not in ['13311', '16707'] and IDCHECK[:3] != '111' :
                CODE_EFF1 = ('hero_skill_effects/'+NAME_HERO+'/').lower().encode()
                CODE_EFF2 = ('hero_skill_effects/'+NAME_HERO+'/'+IDCHECK+'/').lower().encode()
                CODE_EFF3 = ('Hero_Skill_Effects/'+NAME_HERO+'/').encode()
                CODE_EFF4 = ('Hero_Skill_Effects/'+NAME_HERO+'/'+IDCHECK+'/').encode()
                CODE_EFF5 = ('hero_skill_effects/'+NAME_HERO+'/').encode()
                CODE_EFF6 = ('hero_skill_effects/'+NAME_HERO+'/'+IDCHECK+'/').encode()
                with open (f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes', 'rb') as f:
                    codefix = f.read()
                codefix = codefix.replace(string1, string1 + new_id.encode()+b'/').replace(string3, string3 + new_id.encode()+b'/').replace(string2, string2 + new_id.encode()+b'/').replace(string4, string4 + new_id.encode()+b'/').replace(string5, string5 + new_id.encode()+b'/').replace(string7, string7 + new_id.encode()+b'/').replace(b'/'+new_id.encode()+b'/'+new_id.encode()+b'/', b'/'+new_id.encode()+b'/')
                with open(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes','wb') as f:f.write(codefix)
            LC = '2'
            Directory = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/AssetRefs/Hero/{IDCHECK[:3]}_AssetRef.bytes'
            process_directory(Directory, LC)
            
        #=========================================================================================================================            
        try:
            folder_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/'
            output_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/Actor_'+f'{IDCHECK[:3]}'+'_Actions.pkg.bytes'
            zip_folder(folder_path, output_path)
            shutil.rmtree(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod/')
        except Exception as e:
           print(e)

        #=========================================================================================================================                       
        try:
            folder_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/'
            output_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/Actor_'+f'{IDCHECK[:3]}'+'_Infos.pkg.bytes'
            zip_folder(folder_path, output_path)
            shutil.rmtree(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Prefab_Characters/mod/')
        except Exception as e:
           print(e)
           
        #=========================================================================================================================                       
    file_paths = [f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/Born.xml',f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/Back.xml',f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/HasteE1.xml',f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/commonresource/HasteE1_leave.xml']
    for file_path in file_paths:
        Track_Guid_Skill(file_path)

        #=========================================================================================================================                    
    try:
        folder_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/'
        output_path = f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/CommonActions.pkg.bytes'
        zip_folder(folder_path, output_path)
    except Exception as e:
        print(e)
       
        #=========================================================================================================================                    
    shutil.rmtree(f'FILES_MOD/{sanitized_input}/Android/files/Resources/{version}/Ages/Prefab_Characters/Prefab_Hero/mod1/', ignore_errors=True)        
    if android_ios.lower() == 'y':
        shutil.copytree(f"FILES_MOD/{sanitized_input}/Android/files/Resources",f"FILES_MOD/{sanitized_input}/Resources/",dirs_exist_ok=True)
        
        #=========================================================================================================================                    
        try:
            shutil.make_archive(f'FILES_MOD/{sanitized_input}/Resources', 'zip', f'FILES_MOD/{sanitized_input}/', 'Resources')
            shutil.rmtree(f'FILES_MOD/{sanitized_input}/Resources')
            os.rename(f'FILES_MOD/{sanitized_input}/Resources.zip', f'FILES_MOD/{sanitized_input}/IOS.zip')
        except Exception as e:
            print(e)
        #=========================================================================================================================            
            
    print("\033[1;97m[\033[1;92m•\033[1;97m] Done Mod")
    