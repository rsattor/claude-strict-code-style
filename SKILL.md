---
name: me
description: Foydalanuvchining shaxsiy kod yozish qoidalari (izohlar, doc-comment, satr qurish, operatorlar, tiplash, loyiha tuzilishi va testlar). Har qanday dasturlash tilida kod yozish, tahrirlash, refactor qilish, test yozish, review qilish, yangi loyiha yaratish yoki chatda kod misoli ko'rsatishdan oldin shu skill'ni yukla, hatto foydalanuvchi qoidalarni eslatmasa ham. Kod bilan bog'liq bo'lmagan suhbat va savollarda yuklama.
---

# me

Foydalanuvchining shaxsiy kod yozish qoidalari. Ular faylga yoziladigan kodga ham, chatda ko'rsatiladigan kod misollariga ham tegishli.

Bu qoidalar til standartlari va loyihadagi linter sozlamalaridan ustun turadi. Masalan, linter `or` ni `||` ga almashtirmoqchi bo'lsa yoki standart uslubda ternary odatiy bo'lsa ham, shu skill'dagi qoida amal qiladi. Bunday ziddiyat chiqsa, linter sozlamasini jimgina o'zgartirma, javobingda foydalanuvchiga ayt.

## Ish tartibi

1. Quyidagi 9 ta qoidani o'qi.
2. Ishlayotgan til uchun reference faylni o'qi. Unda har bir qoida uchun aniq muqobillar, test vositalari va to'liq misol bor:
   - Rust: [references/rust.md](references/rust.md)
   - PHP, Laravel, Symfony: [references/php.md](references/php.md)
   - Python: [references/python.md](references/python.md)
   - TypeScript, JavaScript: [references/typescript.md](references/typescript.md)
   - Go, Java, Kotlin, C#, Swift, Dart: [references/other-languages.md](references/other-languages.md)
3. Kodni va testlarni yoz.
4. Ish oxirida skill papkasidagi tekshiruv skriptini yozgan fayl yoki papkalaringga ishga tushir va topilgan har bir buzilishni tuzat:

   ```bash
   python3 <skill-papkasi>/scripts/check_style.py <fayl-yoki-papka>...
   ```

   Skript Rust, PHP, TypeScript, JavaScript va Python'da izohlar, satr qurish, taqiqlangan operatorlar, zaif tiplar va doc-comment yetishmasligini topadi. U loyiha tuzilishi va test sifatini baholamaydi, boshqa tillarni esa umuman tekshirmaydi. Bu qismlarni qoidalar bo'yicha o'zing tekshir.
5. Testlarni ishga tushir va natijani aniq ayt.

## 1. Kod ichida izoh yozilmaydi, faqat doc-comment mumkin

Foydalanuvchi kod o'zini o'zi tushuntirishi kerak deb hisoblaydi. Oddiy izohlar vaqt o'tishi bilan kod bilan mos kelmay qoladi va shovqin bo'ladi. Biror joyni izohsiz tushunish qiyin bo'lsa, izoh yozish o'rniga kodni aniqroq qil: o'zgaruvchi yoki metodga tushunarli nom ber, murakkab ifodani nomli metodga ajrat.

Faqat tilning rasmiy hujjatlash izohlariga (doc-comment) ruxsat bor. Ular class, interface, funksiya, metod, property yoki konstantadan oldin turadi.

Quyidagilar yozilmaydi:

- Kod qatorlari orasidagi yoki qator oxiridagi tushuntiruvchi izohlar (`//`, `#`, `/* */`, `--`, `<!-- -->`)
- Kommentga olingan (o'chirilgan) kod
- `TODO`, `FIXME`, `NOTE` kabi belgilar
- Kod bo'limlarini ajratuvchi izohlar (`// ---- Helpers ----`)
- Funksiya yoki metod ichidagi doc-comment uslubidagi bloklar

Asbob-uskunalar uchun direktivalar izoh hisoblanmaydi, chunki ular kodning ishlashiga ta'sir qiladi: `#!/usr/bin/env`, `declare(strict_types=1);`, `// eslint-disable-next-line`, `# noqa` va shunga o'xshashlar. Ularni faqat haqiqatan kerak bo'lganda ishlat. Tip tekshiruvini o'chiradigan direktivalar (`@ts-ignore`, `@ts-expect-error`, `# type: ignore`, `@phpstan-ignore`) bunga kirmaydi, ular 7-qoida bo'yicha taqiqlangan.

Kodni nima uchun shunday yozganingni tushuntirish kerak bo'lsa, buni kodga emas, chatdagi javobga yoz.

Mavjud fayllarni tahrirlaganda o'zing yangi izoh qo'shma. Faylda ilgaridan bor izohlarni foydalanuvchi so'ramaguncha o'chirma, chunki bu o'zgarishni kattalashtiradi va boshqa ishga aralashadi.

## 2. Kod va loyiha tilning rasmiy standartlariga mos bo'ladi

Foydalanuvchi kodni o'sha til yoki framework bilan ishlaydigan har qanday tajribali dasturchi birinchi qarashdayoq tushunishini xohlaydi. Bunga eng yaxshi yo'l jamoa o'ylab topgan uslub emas, til va framework hamjamiyatining rasmiy standarti. Shuning uchun nomlash, formatlash, fayl joylashuvi va kod tuzilishida avval rasmiy standartga tayan, shaxsiy didga emas. Har bir til uchun standartlar ro'yxati reference fayllarda.

Loyihada formatter yoki linter sozlangan bo'lsa (`pint.json`, `.php-cs-fixer.php`, `phpcs.xml`, `pyproject.toml` ichidagi `ruff`, `eslint.config.js`, `.prettierrc`, `rustfmt.toml` va boshqalar), u shu loyihaning qabul qilingan standarti hisoblanadi. Kodni unga moslab yoz va imkon bo'lsa, ishni tugatgach formatter va linterni ishga tushir. Faqat shu skill qoidalariga zid sozlamalar bundan mustasno.

## 3. Loyiha daraxti professional darajada tuziladi

Fayl va papkalar joylashuvi loyihaning birinchi taassurotini beradi. Foydalanuvchi o'z loyihalari katta, yetuk open-source loyihalardagidek tartibli ko'rinishini xohlaydi.

- **Rasmiy skeleton:** framework'ning rasmiy skeleton'idan boshla va uning katalog tuzilishini buzma.
- **Mas'uliyat bo'yicha guruhlash:** fayllarni aniq mas'uliyat bo'yicha guruhla. Loyiha kattalashsa, texnik qatlam bo'yicha emas, domen yoki feature bo'yicha ajrat.
- **Aniq nomlar:** `utils`, `helpers`, `misc`, `common`, `stuff` kabi hamma narsa tashlanadigan papka va fayllar ochma. Har bir papka nomi ichida nima borligini aniq aytsin.
- **Testlar:** test fayllarining joylashuvi va nomi asosiy kod tuzilishini takrorlasin.
- **Ildiz papka:** konfiguratsiya fayllari ildiz papkada, tilning odatiy joylarida tursin. Ildiz papkani keraksiz fayllar bilan to'ldirma.
- **Fayl va papka nomlari:** tilning qabul qilingan uslubida bo'lsin.

Yangi papka yoki fayl qo'shishdan oldin loyihaning mavjud tuzilishini ko'rib chiq va unga mos joyni tanla. Mavjud loyihani foydalanuvchi so'ramaguncha qayta tuzma. Tuzilish standartdan jiddiy chetga chiqqan bo'lsa, buni javobingda alohida taklif sifatida ayt.

## 4. Satrlarni interpolatsiya va ulash bilan qurish taqiqlanadi

Satr ichiga qiymat qo'shish ham, satrlarni bir-biriga ulash ham ishlatilmaydi. Bunday kodda satrning yakuniy ko'rinishi bo'laklarga sochilib ketadi va o'qish qiyinlashadi. Placeholder'li shablonda esa satr bitta joyda to'liq ko'rinadi.

Quyidagilar yozilmaydi:

- Interpolatsiya: Python f-string, JavaScript/TypeScript template literal ichidagi `${}`, PHP qo'sh tirnoq ichidagi o'zgaruvchi (`"Hello $name"`), Kotlin, C#, Dart va Swift'dagi satr shablonlari
- Ulash operatorlari: satrlar uchun `+` va `+=`, PHP'dagi `.` va `.=`
- Tilning xom ulash funksiyalari: `implode()`, `join()`, `str.join()`, `Array.prototype.join()`, `String.prototype.concat()`, `StringBuilder` bilan qo'lda yig'ish
- Collection'ning implode metodlari, masalan Laravel'da `collect($names)->implode(', ')`

Bularning o'rniga satrning to'liq shabloni bir joyda ko'rinadigan vositalarni ishlat:

- **Placeholder'li formatlash:** `sprintf()` va uning boshqa tillardagi muqobillari.
- **Framework'ning satr va massiv yordamchilari:** ular ulashni nomlangan, o'qilishi oson metodga aylantiradi. Laravel'da `Str` va `Arr`, Symfony'da String component, JavaScript'da `Intl.ListFormat`.
- **Tarjima kalitlari:** foydalanuvchiga ko'rinadigan matn uchun placeholder'li tarjima kaliti.
- **Logger placeholder'lari:** log yozuvlari uchun loggerning o'z placeholder'lari va kontekst massivi.
- **Maxsus API'lar:** yo'l va URL'lar uchun maxsus API, SQL uchun query builder yoki parametrli so'rov.
- **Qatorlab chiqarish:** ko'p qatorli matnni bitta satrga yig'ish o'rniga qatorlar ro'yxatini qaytar va ularni birma-bir chiqar.

Til yoki framework bo'yicha aniq muqobillar reference fayllarda. Taqiqlanmagan va o'qilishi oson muqobil topilmasa, xom ulashni yashirincha ishlatma, foydalanuvchidan so'ra.

## 5. Massiv va obyektlarni `+` bilan birlashtirish taqiqlanadi

`+` operatori foydalanuvchi uchun faqat matematik amal. Massiv, ro'yxat yoki obyektlarni u bilan birlashtirish natijani yashiradi. Masalan, PHP'da `$a + $b` takroriy kalitlarni jimgina tashlab yuboradi. Nomlangan metod yoki spread esa nima bo'layotganini aniq aytadi.

Massiv, ro'yxat, tuple va kolleksiyalarni `+` yoki `+=` bilan birlashtirma. JavaScript'da `Array.prototype.concat()` ham taqiqlangan. O'rniga `array_merge()`, `collect()->merge()`, spread (`[...a, ...b]`, `[*a, *b]`) yoki `extend()` ishlat.

## 6. Ternary, null-coalescing, nullsafe va `||` operatorlari taqiqlanadi

Foydalanuvchi shartli mantiqni har doim aniq ko'rinishda ko'rishni xohlaydi. Qisqa operatorlar bir qatorga bir nechta qarorni sig'diradi, null holatini yashiradi va ichma-ich kelganda kod tez chalkashadi.

Quyidagilar yozilmaydi:

- Ternary: `a ? b : c`, Python'da `b if a else c`
- Qisqa ternary (Elvis): `a ?: b`
- Null-coalescing: `a ?? b` va `a ??= b`
- Nullsafe operatori: `$user?->profile`, `user?.profile`
- Mantiqiy `||` va `||=`

Mantiqiy "va" uchun `&&` ishlatilaveradi, uni `and` ga almashtirma. `||` o'rniga `or` ishlat. `or` kalit so'zi yo'q tillarda shartni erta qaytishlarga bo'l, nomlangan predikat metodiga ajrat yoki `includes()` va `some()` kabi metodlardan foydalan.

Taqiqlangan operatorlar o'rniga:

- **Erta qaytish:** `if` bilan erta `return` qil.
- **Ochiq shart:** oddiy `if` / `else` yoz.
- **Tanlov:** `match` yoki `switch` ishlat, qiymat tanlash uchun lug'at (map) dan foydalan.
- **Standart qiymatli API'lar:** `Arr::get($data, 'key', 'default')`, `$request->integer('limit', 10)`, `dict.get('key', default)` kabi `get(key, default)` ko'rinishidagi metodlar.
- **Null'ni ochiq tekshirish:** null'ni ochiq tekshirib erta qaytish qil. Undan ham yaxshisi, tiplarni shunday loyihalaki, qiymat umuman null bo'lmasin.
- **Alohida metod:** murakkab tanlov mantiqini nomli metodga ajrat.

## 7. Tiplash juda aniq va kuchli bo'ladi

Har bir qiymatning tipi kompilyator yoki statik analizator tomonidan to'liq tekshirilishi kerak. Noaniq tip xatoni ishga tushgandan keyingina ko'rsatadi, aniq tip esa uni kod yozilayotgandayoq ushlaydi. Shuning uchun "har qanday narsa" degan ma'nodagi tiplar va tip tekshiruvini aldaydigan usullar ishlatilmaydi.

- **Taqiqlangan tiplar:** `any`, `unknown`, `mixed`, `Any`, `object`, `Object`, `dynamic`, `interface{}` va shunga o'xshash tiplar.
- **Tip tekshiruvini aldash:** `as any`, `as unknown as T`, non-null assertion (`value!`, `!!`), `cast()`, tip tekshiruvini o'chiradigan direktivalar.
- **Qat'iy rejim:** tilning eng qat'iy tekshiruv rejimini yoq (`strict`, `declare(strict_types=1)`, PHPStan eng yuqori daraja, `mypy --strict`).
- **Hamma joyda aniq tip:** har bir parametr, return va property tipini ochiq yoz.
- **Domen tiplari:** sehrli satrlar o'rniga `enum` ishlat. Massivlar o'rniga DTO va value object, bir nechta holat uchun union va literal tiplar ishlat.
- **Generic va shakllar:** kolleksiya va massivlar uchun generic yoki shakl tiplarini ko'rsat (`list<User>`, `array{id: int}`, `readonly User[]`).
- **Tashqi ma'lumot:** JSON, request, API javobi va env qiymatlari tizimga kirish nuqtasidayoq schema orqali aniq tipga aylantirilsin.

## 8. Har bir element doc-comment bilan boyitiladi

1-qoida oddiy izohlarni taqiqlaydi, shuning uchun kodni tushuntirishning yagona joyi doc-comment. Foydalanuvchi IDE'da istalgan class yoki metod ustiga borganda uning vazifasi, kirish-chiqishi va xatolari to'liq ko'rinishini xohlaydi.

Doc-comment quyidagilarning har biriga yoziladi: class, interface, trait, enum, funksiya, metod (public, protected va private), property, konstanta. Test class'lari va test metodlari ham bundan mustasno emas.

Doc-comment ichida:

- **Vazifa:** birinchi qatorda element nima qilishini bitta aniq gap bilan yoz. Nomni so'zma-so'z takrorlama.
- **Sabab va qoida:** kerak bo'lsa, keyingi abzatsda biznes qoidasi yoki muhim xatti-harakatni tushuntir.
- **Parametrlar va natija:** har bir parametr va natijani tavsif bilan yoz. Native tip to'liq ifodalay olmaydigan joyda aniq tipni ko'rsat.
- **Xatolar:** metod tashlashi mumkin bo'lgan har bir istisnoni yoz.
- **Misol:** public API uchun foydali bo'lsa, misol qo'sh.

Doc-comment'lar har doim ingliz tilida yoziladi. Mavjud loyihadagi boshqa tildagi doc-comment'larni foydalanuvchi so'ramaguncha qayta yozma, lekin yangi yozganlaring ingliz tilida bo'lsin.

## 9. Har doim test yoziladi va testlar juda toza bo'ladi

Testsiz kod tugallanmagan kod. Test kodning hozir ishlashini isbotlaydi va keyingi o'zgarishlarda uni buzilishdan himoya qiladi. Testlar ham o'qiladigan hujjat bo'lgani uchun ularning sifati asosiy koddan past bo'lmasligi kerak.

Qachon yoziladi:

- **Yangi funksionallik:** har bir yangi class, metod, endpoint yoki komponent uchun test yoz.
- **Xatoni tuzatish:** avval xatoni takrorlaydigan va yiqiladigan test yoz, keyin xatoni tuzat.
- **O'zgartirish:** mavjud xatti-harakatni o'zgartirsang, tegishli testlarni ham yangila.
- **Tekshiruv:** ish oxirida testlarni ishga tushir va natijani aniq ayt. Testni ishga tushirmasdan "o'tdi" dema. Yiqilayotgan testni o'chirma, `skip` qilma va assertion'ni yumshatma. Kodni tuzat yoki muammoni foydalanuvchiga ayt. Test muhiti yo'q bo'lsa (masalan, kerakli paketlar o'rnatilmagan), buni ochiq ayt.

Toza test qoidalari:

- **Bitta test, bitta xatti-harakat:** har bir test faqat bitta narsani tekshirsin.
- **Nom xatti-harakatni aytsin:** `expired_coupon_is_rejected`, `it('rejects an expired coupon')`. `test1` yoki `testApply` kabi nomlar bo'lmasin.
- **Arrange, Act, Assert:** testni tayyorlash, harakat va tekshiruv bo'limlariga bo'sh qator bilan ajrat, izoh bilan emas.
- **Testda mantiq bo'lmasin:** `if`, sikl va hisob-kitob yozma. Bir nechta holat uchun data provider yoki `parametrize` ishlat.
- **Tayyor ma'lumot uchun factory:** qo'lda uzun massiv yig'ma, factory, fixture yoki builder ishlat.
- **Public xatti-harakatni tekshir:** private metod va ichki tuzilishni emas, natijani tekshir.
- **Faqat chegaralarni mock qil:** HTTP, vaqt, navbat, pochta va fayl tizimini fake qil. O'zing yozgan domen class'larini mock qilma.
- **Deterministik:** haqiqiy tarmoq, haqiqiy vaqt yoki seed'siz tasodifiy qiymatga bog'liq bo'lma. Har bir test mustaqil va istalgan tartibda o'tsin.
- **Aniq assertion:** qat'iy tenglikni tekshir (`assertSame`, `toStrictEqual`), istisnoning aniq class'ini tekshir.
- **Holatlarni to'liq qamra:** asosiy holat, chegaraviy qiymatlar va xato holatlari uchun alohida testlar yoz.
- **Testlar ham shu qoidalarga bo'ysunadi:** test kodida ham izoh, ternary, interpolatsiya, `any` va boshqa taqiqlangan narsalar bo'lmaydi.
