from __future__ import annotations

BOOK_ALIAS_TO_CANONICAL = {
    "Gen":"Gen","Genesis":"Gen",
    "Exod":"Exod","Exodus":"Exod",
    "Lev":"Lev","Leviticus":"Lev",
    "Num":"Num","Numeri":"Num","Numbers":"Num",
    "Deut":"Deut","Deuteronomium":"Deut","Deuteronomy":"Deut",
    "Josh":"Josh","Josua":"Josh","Joshua":"Josh",
    "Judg":"Judg","Judices":"Judg","Judges":"Judg",
    "1Sam":"1Sam","Samuel_I":"1Sam","1_Samuel":"1Sam",
    "2Sam":"2Sam","Samuel_II":"2Sam","2_Samuel":"2Sam",
    "1Kgs":"1Kgs","Reges_I":"1Kgs","1_Kings":"1Kgs",
    "2Kgs":"2Kgs","Reges_II":"2Kgs","2_Kings":"2Kgs",
    "Isa":"Isa","Jesaia":"Isa","Isaiah":"Isa",
    "Jer":"Jer","Jeremia":"Jer","Jeremiah":"Jer",
    "Ezek":"Ezek","Ezechiel":"Ezek","Ezekiel":"Ezek",
    "Hos":"Hos","Hosea":"Hos",
    "Joel":"Joel",
    "Amos":"Amos",
    "Obad":"Obad","Obadia":"Obad","Obadiah":"Obad",
    "Jonah":"Jonah","Jona":"Jonah",
    "Mic":"Mic","Micha":"Mic","Micah":"Mic",
    "Nah":"Nah","Nahum":"Nah",
    "Hab":"Hab","Habakuk":"Hab","Habakkuk":"Hab",
    "Zeph":"Zeph","Zephania":"Zeph","Zephaniah":"Zeph",
    "Hag":"Hag","Haggai":"Hag",
    "Zech":"Zech","Sacharia":"Zech","Zechariah":"Zech",
    "Mal":"Mal","Maleachi":"Mal","Malachi":"Mal",
    "Ps":"Ps","Psalmi":"Ps","Psalms":"Ps",
    "Job":"Job","Iob":"Job",
    "Prov":"Prov","Proverbia":"Prov","Proverbs":"Prov",
    "Ruth":"Ruth",
    "Song":"Song","Canticum":"Song","Song_of_songs":"Song",
    "Eccl":"Eccl","Ecclesiastes":"Eccl",
    "Lam":"Lam","Threni":"Lam","Lamentations":"Lam",
    "Esth":"Esth","Esther":"Esth",
    "Dan":"Dan","Daniel":"Dan",
    "Ezra":"Ezra","Esra":"Ezra",
    "Neh":"Neh","Nehemia":"Neh","Nehemiah":"Neh",
    "1Chr":"1Chr","Chronica_I":"1Chr","1_Chronicles":"1Chr",
    "2Chr":"2Chr","Chronica_II":"2Chr","2_Chronicles":"2Chr",
}

def normalize_book_alias(book: str) -> str:
    return BOOK_ALIAS_TO_CANONICAL.get(book, book)

def parse_reference_label(value: str) -> tuple[str, int, int]:
    parts = value.rsplit(".", 2)
    if len(parts) != 3:
        raise ValueError("reference must look like 1Sam.16.7")
    return normalize_book_alias(parts[0]), int(parts[1]), int(parts[2])

def normalize_section_tuple(section: tuple[object, object, object]) -> tuple[str, int, int]:
    book, chapter, verse = section
    return normalize_book_alias(str(book)), int(chapter), int(verse)
