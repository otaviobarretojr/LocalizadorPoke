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


# Encounter Power ingredient/shop audit
html=pathlib.Path("index.html").read_text(encoding="utf-8")
encounter_expected={
"Normal":("Tofu","Aquiesta Supermarket"),"Fire":("Red Bell Pepper","Deli Cioso / Aquiesta Supermarket"),
"Water":("Cucumber","Deli Cioso / Aquiesta Supermarket"),"Electric":("Yellow Bell Pepper","Deli Cioso / Aquiesta Supermarket"),
"Grass":("Lettuce","Artisan Bakery / Aquiesta Supermarket"),"Ice":("Klawf Stick","Aquiesta Supermarket"),
"Fighting":("Pickle","Sure Cans / Aquiesta Supermarket"),"Poison":("Green Bell Pepper","Deli Cioso / Aquiesta Supermarket"),
"Ground":("Ham","Artisan Bakery / Aquiesta Supermarket"),"Flying":("Prosciutto","Deli Cioso"),
"Psychic":("Onion","Artisan Bakery / Aquiesta Supermarket"),"Bug":("Cherry Tomatoes","Sure Cans / Aquiesta Supermarket"),
"Rock":("Bacon","Deli Cioso"),"Ghost":("Red Onion","Deli Cioso / Aquiesta Supermarket"),
"Dragon":("Avocado","Deli Cioso / Aquiesta Supermarket"),"Dark":("Smoked Fillet","Deli Cioso"),
"Steel":("Hamburger","Deli Cioso"),"Fairy":("Tomato","Sure Cans / Aquiesta Supermarket")}
assert len(encounter_expected)==18
for typ,(ingredient,shop) in encounter_expected.items():
    token=f'{typ}:[\"{ingredient}\",\"{shop}\"'
    assert token in html, f"Encounter mapping missing/incorrect: {typ}"
assert "Ele sozinho não garante Encounter Power" in html
assert "Preço-base:" in html
print("Encounter audit OK: 18/18 type ingredients, shops, prices UI and mechanics disclaimer present.")


# Final UI/workflow integrity audit
ui_required=[
    "<title>Pokémon Scarlet & Violet Locator</title>",
    "PALDEA • SCARLET & VIOLET • V1",
    'option value="scarlet"',
    'option value="violet"',
    'option value="recommended"',
    'option value="route"',
    'if(f==="scarlet")',
    'if(f==="violet")',
    'if(f==="recommended")',
    'if(f==="route")',
    "function nextInRegion(n)",
    "function routeView(a)",
    "localStorage",
]
for token in ui_required:
    assert token in html, f"Missing final UI/workflow feature: {token}"
assert html.count("<script>")==1 and html.count("</script>")==1, "Unexpected script block structure"
assert html.count("<html")==1 and html.count("</html>")==1, "Unexpected HTML document structure"
print("Final UI audit OK: branding, filters, route workflow, persistence and document structure present.")


# Base Paldea version-exclusive audit (families + Paradox + box legends)
scarlet_exclusive={"Drifloon","Drifblim","Armarouge","Stunky","Skuntank","Oranguru","Larvitar","Pupitar","Tyranitar","Stonjourner","Skrelp","Dragalge","Deino","Zweilous","Hydreigon","Great Tusk","Scream Tail","Brute Bonnet","Flutter Mane","Slither Wing","Sandy Shocks","Roaring Moon","Koraidon"}
violet_exclusive={"Misdreavus","Mismagius","Gulpin","Swalot","Ceruledge","Bagon","Shelgon","Salamence","Dreepy","Drakloak","Dragapult","Passimian","Eiscue","Clauncher","Clawitzer","Iron Treads","Iron Bundle","Iron Hands","Iron Jugulis","Iron Moth","Iron Thorns","Iron Valiant","Miraidon"}
versions={r[2]:r[4] for r in rows}
assert len(scarlet_exclusive)==23 and len(violet_exclusive)==23
for name in scarlet_exclusive:
    assert versions.get(name)=="scarlet", f"{name}: expected Scarlet exclusive, got {versions.get(name)}"
for name in violet_exclusive:
    assert versions.get(name)=="violet", f"{name}: expected Violet exclusive, got {versions.get(name)}"
assert sum(v=="scarlet" for v in versions.values())==23
assert sum(v=="violet" for v in versions.values())==23
print("Version-exclusive audit OK: 23 Scarlet + 23 Violet base-Paldea entries.")


# Release V1.1 critical-method and audited-price regression checks
critical_text={
"Pawmot":"1.000 passos","Brambleghast":"1.000 passos","Rabsca":"1.000 passos",
"Annihilape":"Rage Fist 20","Kingambit":"3 Bisharp líderes","Gholdengo":"999 Gimmighoul Coins",
"Palafin":"Union Circle","Scizor":"Metal Coat","Slowking":"King's Rock","Gengar":"Pincurchin por Haunter"}
for name,token in critical_text.items():
    assert f'name:"{name}"' in html and token in html, f"Critical method missing: {name} / {token}"
encounter_prices={"Normal":"$260","Fire":"$240","Water":"$130","Electric":"$240","Grass":"$90","Ice":"$500","Fighting":"$90","Poison":"$230","Ground":"$170","Flying":"$200","Psychic":"$130","Bug":"$120","Rock":"$150","Ghost":"$230","Dragon":"$180","Dark":"$330","Steel":"$380","Fairy":"$100"}
for typ,price in encounter_prices.items():
    assert f'{typ}:[' in html and price in html, f"Encounter price missing: {typ} / {price}"
assert "PALDEA • SCARLET & VIOLET • V1.1" in html
for name in ["Oinkologne","Spidops","Lokix","Skiploom","Spewpa"]:
    assert f'name:"{name}"' in html
# Every version-exclusive entry must explain how the opposite-version player proceeds.
exclusive_route_gaps = [
    r[2] for r in rows
    if r[4] in {"scarlet", "violet"}
    and not re.search(r"(troca|coop|Scarlet|Violet)", r[7], re.I)
]
assert not exclusive_route_gaps, f"Version-exclusive entries missing opposite-version guidance: {exclusive_route_gaps}"

print("Release V1.1 audit OK: critical evolutions/trades, 18 prices, branding and refined early routes present.")
