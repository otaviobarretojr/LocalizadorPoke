import re, pathlib, sys
s=pathlib.Path("index.html").read_text(encoding="utf-8")
pat=re.compile(r'\{n:(\d+),dex:(\d+),name:"([^"]+)",types:\[([^\]]*)\],version:"([^"]+)",place:"([^"]*)",fast:"([^"]*)",route:"([^"]*)",time:"([^"]*)",method:"([^"]*)",encounter:"([^"]*)",recipe:"([^"]*)",tip:"([^"]*)"\}')
script=s[s.index("<script>"):s.index("</script>")]
array=script[script.index("const pokemon=["):script.index("];",script.index("const pokemon=["))+2]
rows=pat.findall(array)
assert len(rows)==400, f"Expected 400 executable Pokemon records, got {len(rows)}"
assert s.rstrip().endswith("</html>"), "Trailing content found after </html>"
nums=[int(r[0]) for r in rows]; names=[r[2] for r in rows]; dex=[int(r[1]) for r in rows]
assert sorted(nums)==list(range(1,401)), "Paldea Dex must be exactly #001-#400"
assert len(set(names))==400, "Duplicate Pokemon names"
assert len(set(dex))==400, "Duplicate National Dex artwork IDs"
assert all(r[4] in {"scarlet","violet","both"} for r in rows), "Invalid version value"
for r in rows:
    assert all(str(x).strip() for x in r[2:]), f"Empty required field: {r[2]}"
critical={"Farigiraf":981,"Cetitan":975,"Kingambit":983,"Gimmighoul":999,"Gholdengo":1000,"Koraidon":1007,"Miraidon":1008}
by_name={r[2]:int(r[1]) for r in rows}
for name,expected in critical.items():
    assert by_name.get(name)==expected, f"{name}: expected National Dex {expected}, got {by_name.get(name)}"
required=["function toggleCaught(n,advance=false)","function undoLast()","function startRegion(region)","function huntStatus(n)",'if(saved.has(p.n)) return -999']
for token in required:
    assert token in s, f"Missing V1 feature: {token}"
print("V1 validation OK: 400/400, unique IDs/names, required fields and hunt workflow present.")
