import math
import logging
import pefile

logger = logging.getLogger(__name__)

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def extract_pe_features(raw_bytes: bytes) -> dict:
    """
    Extrae características de un binario (.exe/.dll) para el modelo de malware.
    Usa pefile para parsear los encabezados y secciones.
    """
    try:
        pe = pefile.PE(data=raw_bytes)
    except pefile.PEFormatError as e:
        logger.error(f"Failed to parse PE file: {e}")
        raise ValueError(f"Invalid PE file format: {e}")

    features = {}

    # DOS Header
    features["e_cblp"] = pe.DOS_HEADER.e_cblp
    features["e_cp"] = pe.DOS_HEADER.e_cp
    features["e_cparhdr"] = pe.DOS_HEADER.e_cparhdr
    features["e_maxalloc"] = pe.DOS_HEADER.e_maxalloc
    features["e_sp"] = pe.DOS_HEADER.e_sp
    features["e_lfanew"] = pe.DOS_HEADER.e_lfanew

    # File Header
    features["NumberOfSections"] = pe.FILE_HEADER.NumberOfSections
    features["CreationYear"] = 1 # Valor dummy consistente con datos
    
    chars = pe.FILE_HEADER.Characteristics
    for i in range(15):
        features[f"FH_char{i}"] = (chars >> i) & 1

    # Optional Header
    if hasattr(pe, 'OPTIONAL_HEADER') and pe.OPTIONAL_HEADER is not None:
        opt = pe.OPTIONAL_HEADER
        features["MajorLinkerVersion"] = opt.MajorLinkerVersion
        features["MinorLinkerVersion"] = opt.MinorLinkerVersion
        features["SizeOfCode"] = opt.SizeOfCode
        features["SizeOfInitializedData"] = opt.SizeOfInitializedData
        features["SizeOfUninitializedData"] = opt.SizeOfUninitializedData
        features["AddressOfEntryPoint"] = opt.AddressOfEntryPoint
        features["BaseOfCode"] = opt.BaseOfCode
        # BaseOfData no existe en PE32+ (64-bit)
        features["BaseOfData"] = getattr(opt, 'BaseOfData', 0)
        features["ImageBase"] = opt.ImageBase
        features["SectionAlignment"] = opt.SectionAlignment
        features["FileAlignment"] = opt.FileAlignment
        features["MajorOperatingSystemVersion"] = opt.MajorOperatingSystemVersion
        features["MinorOperatingSystemVersion"] = opt.MinorOperatingSystemVersion
        features["MajorImageVersion"] = opt.MajorImageVersion
        features["MinorImageVersion"] = opt.MinorImageVersion
        features["MajorSubsystemVersion"] = opt.MajorSubsystemVersion
        features["MinorSubsystemVersion"] = opt.MinorSubsystemVersion
        features["SizeOfImage"] = opt.SizeOfImage
        features["SizeOfHeaders"] = opt.SizeOfHeaders
        features["CheckSum"] = opt.CheckSum
        features["Subsystem"] = opt.Subsystem
        
        dll_chars = opt.DllCharacteristics
        for i in range(11):
            features[f"OH_DLLchar{i}"] = (dll_chars >> i) & 1

        features["SizeOfStackReserve"] = opt.SizeOfStackReserve
        features["SizeOfStackCommit"] = opt.SizeOfStackCommit
        features["SizeOfHeapReserve"] = opt.SizeOfHeapReserve
        features["SizeOfHeapCommit"] = opt.SizeOfHeapCommit
        features["LoaderFlags"] = opt.LoaderFlags
    else:
        # Valores por defecto si no hay Optional Header
        features.update({k: 0 for k in [
            "MajorLinkerVersion", "MinorLinkerVersion", "SizeOfCode", "SizeOfInitializedData",
            "SizeOfUninitializedData", "AddressOfEntryPoint", "BaseOfCode", "BaseOfData",
            "ImageBase", "SectionAlignment", "FileAlignment", "MajorOperatingSystemVersion",
            "MinorOperatingSystemVersion", "MajorImageVersion", "MinorImageVersion",
            "MajorSubsystemVersion", "MinorSubsystemVersion", "SizeOfImage", "SizeOfHeaders",
            "CheckSum", "Subsystem", "SizeOfStackReserve", "SizeOfStackCommit",
            "SizeOfHeapReserve", "SizeOfHeapCommit", "LoaderFlags"
        ]})
        for i in range(11):
            features[f"OH_DLLchar{i}"] = 0

    # Sections y entropía
    sus_sections = 0
    non_sus_sections = 0
    e_text = 0.0
    e_data = 0.0
    
    suspicious_names = [b'.text\x00\x00\x00', b'.data\x00\x00\x00', b'.rdata\x00\x00', b'.rsrc\x00\x00\x00']
    
    for section in pe.sections:
        name = section.Name
        if name not in suspicious_names:
            sus_sections += 1
        else:
            non_sus_sections += 1
            
        if b'.text' in name:
            e_text = calculate_entropy(section.get_data())
        elif b'.data' in name:
            e_data = calculate_entropy(section.get_data())

    features["sus_sections"] = sus_sections
    features["non_sus_sections"] = non_sus_sections
    
    # Heurística simple de packers
    features["packer"] = 1 if sus_sections > 0 else 0
    features["packer_type"] = "UnknownPacker" if features["packer"] == 1 else "NoPacker"
    
    features["E_text"] = e_text if e_text > 0 else calculate_entropy(raw_bytes[:1024])
    features["E_data"] = e_data if e_data > 0 else calculate_entropy(raw_bytes[-1024:])
    features["filesize"] = len(raw_bytes)
    features["E_file"] = calculate_entropy(raw_bytes)
    features["fileinfo"] = 1

    return features
