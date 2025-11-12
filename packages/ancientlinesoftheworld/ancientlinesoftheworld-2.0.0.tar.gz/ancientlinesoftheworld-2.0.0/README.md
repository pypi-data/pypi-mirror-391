# Ancient Scripts Converter

📜 A Python package for converting text to ancient writing systems

## How It Works / نحوه کارکرد

The converter works **character by character** using **mapping dictionaries**.  
مبدل به صورت **حرف به حرف** و با استفاده از **دایره‌المعارف‌های نگارشی** کار می‌کند.
# Text Conversion Flow

```
Input Text
│
▼
[Iterate Character by Character]
│
▼
[Check Character Type]
├─ Persian Letter → Persian Mapping Dictionary
├─ English Letter → English Mapping Dictionary
├─ Number → Number Mapping Dictionary
└─ Symbol → Symbol Mapping Dictionary
│
▼
[Convert or Keep Original]
│
▼
Output Text in Ancient Script
```


### Explanation / توضیح مرحله به مرحله:

1. **Character Mapping / نگاشت حروف**  
   - Each ancient script has its own dictionary mapping **Persian, English, numbers, and symbols**.  
     هر خط باستانی دارای دیکشنری مخصوص خود است که **حروف فارسی، انگلیسی، اعداد و علائم** را به نمادهای مربوطه تبدیل می‌کند.

2. **Conversion / تبدیل**  
   - Iterate through each character of the input text.  
   - Replace it with the mapped symbol from the dictionary.  
   - If a character is not found, keep it unchanged.  
   - هر حرف متن ورودی بررسی می‌شود، جایگزین نماد متناظر می‌شود، و اگر در دیکشنری نبود، بدون تغییر باقی می‌ماند.

3. **Supported Types / انواع پشتیبانی شده**  
   - Persian letters / حروف فارسی  
   - English letters / حروف انگلیسی  
   - Numbers / اعداد  
   - Some punctuation and symbols / برخی علائم نگارشی و سمبل‌ها

4. **Optimized Scripts / خطوط بهینه شده**  
   - Some scripts like **Linear B** or **Oracle Bone** use optimized mappings for **faster and more accurate conversion**.  
     برخی خطوط مانند **خط ب یا اوراکل بون** دارای **دایره‌المعارف بهینه** برای تبدیل سریع‌تر و دقیق‌تر هستند.

## Installation
```bash
pip install --upgrade  ancientlinesoftheworld
```

## Usage
```python
from   ancient import AncientScripts

converter = AncientScripts()

#  تبدیل  متن به خط باستانی میخی
cuneiform_text = converter.cuneiform("سلام")

print(cuneiform_text)

# تبدیل متن به خط باستانی مصری 
hieroglyph_text = converter.hieroglyph("خدا")

print(hieroglyph_text)

# تبدیل متن  تاریخی اوستایی

avesta = converter.avestan("hiسلام")
print(avesta)

print(c.get_supported_scripts())
```

## Project :
```python

from ancient import AncientScripts, AncientTimeline

# ایجاد نمونه از کلاس اصلی
c = AncientScripts()

# ایجاد تایم‌لاین با خط پهلوی
t = AncientTimeline(script='pahlavi')

print("🕊️ Welcome to AncientLinesOfTheWorld 🏛️")
print("=" * 60)
print("🔹 Supported Ancient Scripts:")
for name, desc in c.get_supported_scripts().items():
    print(f"  - {name:<12} → {desc}")
print("=" * 60)


text = "hi"
print(f"\nOriginal text: {text}\n")

print("🪶 Converted Texts:")
print(f"  🔸 Pahlavi:       {c.pahlavi(text)}")
print(f"  🔸 Akkadian:      {c.akkadian(text)}")
print(f"  🔸 Avestan:       {c.avestan(text)}")
print(f"  🔸 Manichaean:    {c.manichaean(text)}")
print(f"  🔸 Linear B:      {c.linear_b(text)}")
print(f"  🔸 Hebrew:        {c.hebrew(text)}")
print(f"  🔸 Hieroglyph:    {c.hieroglyph(text)}")
print(f"  🔸 Sanskrit:      {c.sanskrit(text)}")
print(f"  🔸 Oracle Bone:   {c.oracle_bone(text)}")
print(f"  🔸 : cuneiform :  {c.cuneiform(text)}")

print("\n" + "=" * 60)

# 🕰️ نمایش زمان زنده با خط پهلوی
print("📜 Real-time Ancient Timeline (Pahlavi Script):")
t.show()

print("=" * 60)
print("💫 Powered by AncientLinesOfTheWorld | Created by AmirHossein Kader")
```
## Supported Scripts
- Cuneiform
- Egyptian Hieroglyphs
- Pahlavi script
- Manichaean script
- Linear B
-avestan

- And more...



