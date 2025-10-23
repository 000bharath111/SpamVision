# app/ml/augment.py
import random

def obfuscate_typo(text: str, prob: float = 0.03) -> str:
    out = []
    i = 0
    while i < len(text):
        if random.random() < prob and i+1 < len(text):
            out.append(text[i+1])
            out.append(text[i])
            i += 2
        elif random.random() < prob/2:
            i += 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)

def leet_subs(text: str, prob: float = 0.04) -> str:
    subs = {'a':'4','e':'3','i':'1','o':'0','s':'5','t':'7','l':'1'}
    res = []
    for ch in text:
        if ch.lower() in subs and random.random() < prob:
            res.append(subs[ch.lower()])
        else:
            res.append(ch)
    return "".join(res)

def homoglyph_replace(text: str, prob: float = 0.03) -> str:
    mapping = {'o':'ο','a':'а','e':'е','c':'с'}
    res = []
    for ch in text:
        if ch.lower() in mapping and random.random() < prob:
            res.append(mapping[ch.lower()])
        else:
            res.append(ch)
    return "".join(res)

def add_noise(text: str) -> str:
    funcs = [obfuscate_typo, leet_subs, homoglyph_replace]
    f = random.choice(funcs)
    return f(text)
