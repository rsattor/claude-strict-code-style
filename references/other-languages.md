# Go, Java, Kotlin, C#, Swift, Dart

Bu fayl SKILL.md'dagi qoidalarning boshqa tillar uchun qisqa qo'llanmasi. Rust uchun alohida [rust.md](rust.md) fayli bor. Tekshiruv skripti bu tillarni tekshirmaydi, shuning uchun ish oxirida qoidalarni o'zing qo'lda tekshir.

Ba'zi tillarda xom ulash funksiyasi (`strings.Join`, `joinToString` va boshqalar) taqiqlangan, toza muqobil esa yo'q. Bunday holda yashirincha ulash ishlatma, foydalanuvchidan so'ra.

## Go

- **Standartlar:** Effective Go, Go Code Review Comments, `gofmt`, `go vet`, `staticcheck`. Loyiha tuzilishi go.dev'dagi "Organizing a Go module" qo'llanmasiga mos bo'lsin (`cmd/`, `internal/`).
- **Doc-comment:** eksport qilingan va qilinmagan har bir nom uchun e'londan oldin `//` bilan yoziladi va nomning o'zi bilan boshlanadi. Bu Go'ning rasmiy doc formati. Boshqa `//` izohlar taqiqlangan.
- **Satrlar:** `fmt.Sprintf()` ishlat. `+` va `strings.Builder` bilan qo'lda yig'ish taqiqlangan, `strings.Join` ham. Yo'llar uchun `path/filepath`, URL uchun `net/url` ishlat.
- **Birlashtirish:** `slices.Concat(first, second)`, `append(first, second...)`, `maps.Copy(dst, src)`.
- **Shartlar:** Go'da ternary yo'q. `||` o'rniga erta qaytish yoki `slices.Contains()` ishlat. Map'dan standart qiymat uchun `value, ok := m[key]` va keyin `if !ok` yoz.
- **Tiplash:** `any` va `interface{}` taqiqlangan. Generic'lar va aniq constraint'lar, kichik interface'lar ishlat.
- **Testlar:** standart `testing` paketi, `t.Run` bilan table-driven testlar, HTTP uchun `httptest`.

## Java

- **Standartlar:** Oracle Java Code Conventions, Maven yoki Gradle standart tuzilishi (`src/main/java`, `src/test/java`).
- **Doc-comment:** Javadoc `/** ... */`.
- **Satrlar:** `String.format()` yoki `"...".formatted()` ishlat. `+`, `String.join()`, `Collectors.joining()` va `StringBuilder` taqiqlangan.
- **Birlashtirish:** `addAll()`, `Stream.concat()`.
- **Shartlar:** ternary va `||` taqiqlangan. `switch` ifodasi, erta qaytish, `Map.getOrDefault()`, `Optional.orElse()` ishlat.
- **Tiplash:** `Object` va raw generic tiplar taqiqlangan. `record`, `sealed` interface'lar va `enum` ishlat.
- **Testlar:** JUnit 5, `@ParameterizedTest`, AssertJ.

## Kotlin

- **Standartlar:** Kotlin Coding Conventions, `ktlint` yoki `detekt`.
- **Doc-comment:** KDoc `/** ... */`.
- **Satrlar:** `"$name"` va `"${user.name}"` shablonlari, `+`, `buildString`, `joinToString` taqiqlangan. `String.format()` yoki `"%s".format(name)` ishlat.
- **Birlashtirish:** `buildList { addAll(first); addAll(second) }`, `addAll()`.
- **Shartlar:** `?.`, `?:`, `!!` va `||` taqiqlangan. `if (value == null) return` dan keyin smart cast, `requireNotNull()`, `checkNotNull()`, `when` va `getOrDefault()` ishlat.
- **Tiplash:** `Any` taqiqlangan. `data class`, `sealed interface`, `value class` va `enum class` ishlat.
- **Testlar:** JUnit 5 yoki Kotest, mock uchun MockK.

## C\#

- **Standartlar:** Microsoft .NET Coding Conventions, `.editorconfig`, `dotnet format`.
- **Doc-comment:** XML doc `///`.
- **Satrlar:** `$"..."` interpolatsiyasi, `+`, `string.Join()`, `string.Concat()` va `StringBuilder` taqiqlangan. `string.Format()` yoki `CompositeFormat` ishlat, yo'llar uchun `Path.Combine()`.
- **Birlashtirish:** `AddRange()`, `Concat()` LINQ metodi kolleksiyalar uchun.
- **Shartlar:** `? :`, `??`, `??=`, `?.` va `||` taqiqlangan. `switch` ifodasi, pattern matching, `GetValueOrDefault()` va erta qaytish ishlat.
- **Tiplash:** `object` va `dynamic` taqiqlangan. Null-forgiving `!` operatori ham taqiqlangan. `<Nullable>enable</Nullable>` va `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` sozlamalarini yoq, `record` ishlat.
- **Testlar:** xUnit, `[Theory]` va `[InlineData]`, FluentAssertions.

## Swift

- **Standartlar:** Swift API Design Guidelines, `swift-format` yoki SwiftLint.
- **Doc-comment:** `///` Markdown doc.
- **Satrlar:** `"\(name)"` interpolatsiyasi, `+` va `joined()` taqiqlangan. `String(format:)` yoki `formatted()` API'larini ishlat.
- **Birlashtirish:** `append(contentsOf:)`.
- **Shartlar:** `? :`, `??`, `?.` va `||` taqiqlangan. `guard let`, `if let`, `switch` va `dict[key, default: value]` ishlat.
- **Tiplash:** `Any` va `AnyObject` taqiqlangan. Majburiy unwrap `!` ham taqiqlangan. `struct`, `enum` va `protocol` ishlat.
- **Testlar:** Swift Testing (`@Test`, `#expect`) yoki XCTest.

## Dart va Flutter

- **Standartlar:** Effective Dart, `dart format`, `flutter_lints` yoki `very_good_analysis`.
- **Doc-comment:** `///`.
- **Satrlar:** `'$name'` interpolatsiyasi, `+` va `join()` taqiqlangan. Effective Dart interpolatsiyani tavsiya qiladi, lekin shu skill qoidasi ustun turadi. Foydalanuvchiga ko'rinadigan matn uchun `intl` paketidagi `Intl.message` va ARB fayllaridagi placeholder'larni ishlat. Boshqa holatlarda muqobil topilmasa, foydalanuvchidan so'ra.
- **Birlashtirish:** `[...first, ...second]`, `addAll()`.
- **Shartlar:** `? :`, `??`, `??=`, `?.` va `||` taqiqlangan. Erta qaytish, `switch` ifodasi va pattern matching ishlat.
- **Tiplash:** `dynamic` va `Object?` taqiqlangan. `strict-casts`, `strict-inference` va `strict-raw-types` sozlamalarini yoq.
- **Testlar:** `package:test`, `flutter_test`, mock uchun `mocktail`.
