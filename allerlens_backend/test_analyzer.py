"""Functional test: 12 sample labels (same set as the project report). Run: python test_analyzer.py"""
from analyzer import analyze

ALL = ["milk", "peanut", "tree", "egg", "wheat", "soy", "fish", "shell", "sesame"]
# (name, label, expected declared, expected precautionary)
CASES = [
 ("Biscuits", "Wheat flour (maida), sugar, palm oil, milk solids, soy lecithin, cashew paste, salt, natural flavour. May contain peanuts and sesame.", {"wheat","milk","soy","tree"}, {"peanut","sesame"}),
 ("Chocolate bar", "Sugar, cocoa butter, whole milk powder, hazelnut paste, emulsifier (soy lecithin). May contain egg.", {"milk","tree","soy"}, {"egg"}),
 ("Fruit juice", "Water, mango pulp, sugar, citric acid, vitamin C.", set(), set()),
 ("Instant noodles", "Semolina, palm oil, salt, spices, prawn flavouring. Processed in a facility that also handles sesame.", {"wheat","shell"}, {"sesame"}),
 ("Peanut spread", "Peanut butter (roasted peanuts, salt), vegetable oil.", {"peanut"}, set()),
 ("Soy drink", "Water, soybeans, sugar, calcium.", {"soy"}, set()),
 ("Almond drink", "Water, almonds, sea salt.", {"tree"}, set()),
 ("Free-from bread", "Rice flour, tapioca starch, gluten-free baking powder, egg-free binder.", set(), set()),
 ("Fish curry paste", "Tamarind, chilli, fish sauce, shrimp paste, til oil.", {"fish","shell","sesame"}, set()),
 ("Mayonnaise", "Vegetable oil, egg yolk, vinegar, mustard, salt.", {"egg"}, set()),
 ("Coconut dessert", "Coconut cream, water, stabiliser.", set(), set()),
 ("Ghee biscuit", "Atta, ghee, sugar, baking soda. Traces of tree nuts.", {"wheat","milk"}, {"tree"}),
]

tp = fp = fn = perfect = 0
for name, label, exp_c, exp_t in CASES:
    r = analyze(label, ALL)
    got_c = {m["allergen"] for m in r["matches"] if m["kind"] == "contains"}
    got_t = {m["allergen"] for m in r["matches"] if m["kind"] == "may_contain"} - got_c
    exp = {("C", k) for k in exp_c} | {("T", k) for k in exp_t}
    got = {("C", k) for k in got_c} | {("T", k) for k in got_t}
    tp += len(got & exp); fp += len(got - exp); fn += len(exp - got)
    perfect += got == exp
    print(f"{name:16} declared={sorted(got_c)} precautionary={sorted(got_t)} FP={sorted(got-exp)} FN={sorted(exp-got)}")
print(f"\n{perfect}/{len(CASES)} labels fully correct | TP={tp} FP={fp} FN={fn} | precision={tp/(tp+fp):.0%} recall={tp/(tp+fn):.0%}")
