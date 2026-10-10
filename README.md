# claude-strict-code-style

Claude Code uchun shaxsiy kod yozish qoidalari skill'i. Skill kod yozish, tahrirlash, test yozish va review'dan oldin avtomatik yuklanadi va Claude'ni quyidagi qoidalarga amal qilishga majburlaydi.

## Qoidalar

1. Kod ichida izoh yozilmaydi, faqat tilning doc-comment'lari ishlatiladi.
2. Kod va loyiha tilning rasmiy standartlariga mos bo'ladi.
3. Loyiha daraxti professional darajada tuziladi.
4. Satrlarni interpolatsiya, `+`, `.`, `join` yoki `implode` bilan qurish taqiqlanadi. O'rniga `sprintf()`, `format!()` va framework yordamchilari ishlatiladi.
5. Massiv va obyektlar `+` bilan birlashtirilmaydi.
6. Ternary, `??`, `??=`, `?->`, `?.` va `||` operatorlari taqiqlanadi.
7. Tiplash juda aniq bo'ladi: `any`, `unknown`, `mixed`, `Any` va tip tekshiruvini aldash usullari ishlatilmaydi.
8. Har bir class, funksiya, metod, property va konstantaga ingliz tilida doc-comment yoziladi.
9. Har doim toza testlar yoziladi.

Rust, PHP (Laravel, Symfony), Python va TypeScript uchun batafsil qo'llanmalar `references/` papkasida. Go, Java, Kotlin, C#, Swift va Dart uchun qisqa qo'llanma ham bor.

## O'rnatish

```bash
git clone https://github.com/rsattor/claude-strict-code-style.git ~/.claude/skills/me
```

Skill `me` nomi bilan yuklanadi va uni `/me` buyrug'i bilan qo'lda ham chaqirish mumkin.

## Tekshiruv skripti

`scripts/check_style.py` Rust, PHP, TypeScript, JavaScript va Python fayllarida qoidalar buzilishini topadi. Skript faqat Python standart kutubxonasidan foydalanadi.

```bash
python3 scripts/check_style.py src tests
```

```bash
python3 scripts/check_style.py src --json
```

Buzilish topilsa, skript 1 holat kodi bilan tugaydi.

## Skript testlari

```bash
python3 -m pytest
```

```bash
python3 -m mypy
```
