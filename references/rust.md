# Rust

Bu fayl SKILL.md'dagi qoidalarning Rust uchun aniq qo'llanmasi. Rust foydalanuvchining asosiy tili, shuning uchun bu yerdagi qoidalarga ayniqsa qat'iy amal qil.

## Mundarija

1. Standartlar, lint'lar va loyiha tuzilishi
2. Izohlar va doc-comment
3. Satr qurish
4. Kolleksiyalarni birlashtirish
5. Shartlar, `Option` va standart qiymatlar
6. Tiplash va xatolar
7. Testlar
8. To'liq misol

## 1. Standartlar, lint'lar va loyiha tuzilishi

- **Standartlar:** Rust API Guidelines, The Rust Style Guide (`rustfmt`), Clippy.
- **Ish oxirida tekshiruv:** quyidagi buyruqlarning har biri xatosiz o'tsin:

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```

- **Lint sozlamalari:** yangi loyihada `Cargo.toml` ga quyidagi lint'larni qo'sh. Mavjud loyihada ular yo'q bo'lsa, qo'shishni foydalanuvchiga taklif qil:

```toml
[lints.rust]
missing_docs = "deny"
unsafe_code = "forbid"

[lints.clippy]
pedantic = { level = "warn", priority = -1 }
missing_docs_in_private_items = "warn"
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
as_conversions = "deny"
string_add = "deny"
string_add_assign = "deny"
format_push_string = "deny"
uninlined_format_args = "allow"
```

`uninlined_format_args` Clippy lint'i `format!("{}", name)` ni `format!("{name}")` ga almashtirishni talab qiladi. Bu shu skill'ning interpolatsiya taqiqiga zid, shuning uchun u o'chirib qo'yiladi.

`clippy.toml` testlarda `unwrap()` va `expect()` ga ruxsat beradi:

```toml
allow-unwrap-in-tests = true
allow-expect-in-tests = true
```

- **Loyiha tuzilishi:**

```text
project/
├── Cargo.toml
├── Cargo.lock
├── clippy.toml
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── error.rs
│   ├── report.rs
│   └── report/
│       └── format.rs
├── tests/
│   ├── common/
│   │   └── mod.rs
│   └── cli.rs
├── benches/
└── examples/
```

- **Binary va kutubxona:** `main.rs` yupqa bo'lsin: argumentlarni o'qiydi, `lib.rs` dagi kodni chaqiradi va xatoni `ExitCode` ga aylantiradi. Butun mantiq kutubxona qismida tursin.
- **Modullar:** `report.rs` va `report/` papkasi uslubini ishlat, `mod.rs` emas. Faqat `tests/common/mod.rs` bundan mustasno, bu Cargo konventsiyasi.
- **Workspace:** bir nechta crate bo'lsa, ularni `crates/<crate-name>/` ichiga qo'y va umumiy bog'liqliklarni `[workspace.dependencies]` da e'lon qil.
- **Nomlar:** fayl va modullar `snake_case`, tiplar `UpperCamelCase`, konstantalar `SCREAMING_SNAKE_CASE`. Getter'lar `get_` prefiksisiz yoziladi. Konversiyalar `as_`, `to_` va `into_` bilan nomlanadi (API Guidelines, C-CONV).

## 2. Izohlar va doc-comment

`//` va `/* */` izohlar yozilmaydi. Doc-comment'lar `///` (element uchun) va `//!` (modul yoki crate uchun). `#[...]` attribute'lari izoh emas.

- **Modul va crate:** har bir `.rs` fayl `//!` bilan boshlanadi va modulning vazifasini tushuntiradi.
- **Elementlar:** har bir `fn`, `struct` va uning har bir maydoni, `enum` va uning har bir varianti, `trait` va uning metodlari, `impl` ichidagi metodlar, `const`, `static`, `type` va `mod` ga `///` yoziladi. Bunga private elementlar ham kiradi.
- **Bo'limlar:** `Result` qaytaradigan funksiyalarda `# Errors` bo'limi bo'lishi shart. Public API uchun `# Examples` bo'limiga ishlaydigan doctest yoz. `unsafe` kod bo'lmaydi, shuning uchun `# Safety` kerak emas. Panic qiladigan kod ham bo'lmaydi, shuning uchun `# Panics` ham kerak emas.
- **Havolalar:** boshqa elementlarga intra-doc link bilan murojaat qil: [`ReportError::NoRepositories`].

```rust
/// Groups repository names by their primary language.
///
/// Repositories without a detected language are grouped under
/// [`UNKNOWN_LANGUAGE`]. Names inside each group are sorted alphabetically.
///
/// # Errors
///
/// Returns [`ReportError::NoRepositories`] when `repositories` is empty.
///
/// # Examples
///
/// ```
/// use repo_report::{group_by_language, Repository};
///
/// let repositories = [Repository::new("cli", Some("Rust"))];
/// let groups = group_by_language(&repositories)?;
///
/// assert_eq!(groups.len(), 1);
/// # Ok::<(), repo_report::ReportError>(())
/// ```
pub fn group_by_language(repositories: &[Repository]) -> Result<BTreeMap<String, Vec<String>>, ReportError> {
```

## 3. Satr qurish

Taqiqlangan:

- `format!("{name}")` kabi format satri ichida o'zgaruvchini to'g'ridan-to'g'ri ushlash (inline captured arguments). Bu ham interpolatsiya hisoblanadi.
- `+` va `+=` bilan satr ulash, masalan `owned + &other` va `text += "x"`.
- `push_str()` va `push()` bilan satrni qo'lda yig'ish.
- `[..].join()`, `[..].concat()`, `itertools::join()`.

| Vazifa | Ishlat |
| --- | --- |
| Shablon bo'yicha satr | Pozitsion argumentlar bilan `format!("{}: {}", language, count)`. Indeks bilan `format!("{0} / {0}", value)` ham mumkin |
| Chiqarish | `println!("{}", line)`, fayl yoki buferga `writeln!(output, "{}", line)?` |
| Ro'yxatni satrga aylantirish | `itertools` dagi `names.iter().format(", ")`, masalan `format!("Languages: {}", names.iter().format(", "))` |
| Ko'p qatorli chiqish | `Vec<String>` qatorlarni qaytar va har birini `writeln!` bilan alohida yoz |
| Turni matnga aylantirish | `impl fmt::Display` yoz va ichida `write!(formatter, "{} ({})", self.name, self.count)` ishlat |
| Fayl yo'li | `Path::join()` va `PathBuf::push()`. Bular satr ulash emas, yo'l API'si |
| URL | `url::Url::join()`, `url.query_pairs_mut().append_pair("page", "2")` |
| SQL | `sqlx::query!("SELECT * FROM users WHERE id = $1", id)` kabi bog'langan parametrlar |
| Log | `tracing::info!(user_id = %user.id, "user created")` strukturalangan maydonlar bilan |
| Xato matni | `thiserror` dagi `#[error("unknown language code {0}")]`. Attribute ichidagi `{0}` va `{field}` ruxsat etilgan, chunki bu `thiserror` ning maydon sintaksisi |

## 4. Kolleksiyalarni birlashtirish

| Vazifa | Ishlat |
| --- | --- |
| Vektorni kengaytirish | `items.extend(more)`, `items.extend_from_slice(&more)` |
| Ketma-ket o'qish | `first.iter().chain(second.iter())` |
| Map va set'larni birlashtirish | `settings.extend(overrides)` |

`[first, second].concat()` taqiqlangan.

## 5. Shartlar, `Option` va standart qiymatlar

Rust'da ternary, `??` va `?.` operatorlari yo'q. Mantiqiy `||` esa bor va u taqiqlangan. Argumentsiz closure'dagi `||`, masalan `unwrap_or_else(|| default())`, mantiqiy operator emas va u ishlatilaveradi. Pattern'dagi `|`, masalan `Role::Owner | Role::Admin`, ham mumkin. `&&` ishlatilaveradi.

`||` o'rniga:

```rust
/// Tells whether the user may edit the given post.
#[must_use]
pub fn can_edit(user: &User, post: &Post) -> bool {
    if matches!(user.role, Role::Owner | Role::Admin) {
        return true;
    }

    post.author_id == user.id
}
```

- **Variantlarni solishtirish:** `matches!(value, A | B)`.
- **Ro'yxatdan qidirish:** `[Status::Draft, Status::Archived].contains(&status)`.
- **Iterator shartlari:** `.any()` va `.all()`.
- **Erta qaytish:** `if` bilan erta `return` qil.

`Option` va standart qiymatlar:

| Vazifa | Ishlat |
| --- | --- |
| Standart qiymat | `value.unwrap_or(10)`, `value.unwrap_or_default()`, `value.unwrap_or_else(\|\| compute())` |
| Qiymatni o'zgartirish yoki standart qiymat | `value.map_or(0, \|item\| item.len())` |
| `Option` dan xatoga | `value.ok_or(ReportError::MissingLanguage)?` |
| Qiymat bo'lmasa chiqib ketish | `let Some(language) = repository.language else { return UNKNOWN_LANGUAGE; };` |
| Xatoni uzatish | `?` operatori |
| Map'dan olish | `map.get(&key).copied().unwrap_or_default()`, `map.entry(key).or_default()` |

Qiymat tanlashda `match` ishlat. Ko'p qatorli `if` / `else` ifodasi ham mumkin, chunki u Rust'ning oddiy sharti, qisqartirilgan operator emas.

## 6. Tiplash va xatolar

- **Taqiqlangan:** `dyn Any` va `Box<dyn Any>`, domen ma'lumoti uchun `serde_json::Value`, kutubxona kodida `Box<dyn Error>` va `anyhow::Error`, `unsafe`, `as` bilan son konversiyasi.
- **Panic yo'q:** test bo'lmagan kodda `unwrap()`, `expect()`, `panic!()`, `unreachable!()` va `todo!()` ishlatilmaydi. Xatolar `Result` orqali qaytariladi.
- **Xato tiplari:** har bir crate yoki modulda `thiserror` bilan aniq `enum` xato tipi yoz. Har bir variant xatoning bitta sababini bildirsin. `main.rs` da xatoni `match` bilan `ExitCode` va foydalanuvchiga xabarga aylantir.
- **Son konversiyasi:** `as` o'rniga `From`, `TryFrom` va `u32::try_from(value)?` ishlat.
- **Newtype:** identifikator va o'lchov birliklari uchun newtype ishlat: `struct UserId(u64);`, `struct Cents(u64);`.
- **Holatlar:** `bool` bayroqlari va sehrli satrlar o'rniga `enum` ishlat. Kengayishi mumkin bo'lgan public `enum` va `struct` larga `#[non_exhaustive]` qo'y.
- **Qiymat cheklovlari:** `NonZeroU32` kabi tiplar va constructor'da tekshiradigan `TryFrom` implementatsiyalari ishlat.
- **Tashqi ma'lumot:** JSON, CSV, env va so'rov ma'lumotlarini `#[derive(Deserialize)]` va `#[serde(deny_unknown_fields)]` bilan aniq struct'larga o'qi.
- **API:** natijasi e'tiborsiz qolmasligi kerak bo'lgan funksiyalarga `#[must_use]` qo'y. Kirish uchun `&str`, `&[T]` va `impl AsRef<Path>` kabi qarzga olingan tiplarni qabul qil.

## 7. Testlar

| Vazifa | Vosita |
| --- | --- |
| Unit testlar | Fayl oxiridagi `#[cfg(test)] mod tests` |
| Integration testlar | `tests/` papkasi, umumiy yordamchilar uchun `tests/common/mod.rs` |
| Bir nechta holat va fixture | `rstest` (`#[rstest]`, `#[case]`, `#[fixture]`) |
| Property-based testlar | `proptest` |
| Snapshot testlar | `insta` |
| CLI testlari | `assert_cmd` va `predicates` |
| Vaqtinchalik fayllar | `tempfile` |
| HTTP | `wiremock` |
| Trait chegaralarini mock qilish | `mockall`, faqat tashqi chegaralar uchun |

- **Nomlar:** test funksiyasi nomi xatti-harakatni aytsin: `empty_input_is_rejected`.
- **Docs:** har bir test funksiyasi, fixture va `mod tests` ga `///` yoz.
- **Xatolar:** test `Result<(), Error>` qaytarishi va ichida `?` ishlatishi mumkin. Testlarda `expect("reason")` ham ruxsat etilgan.
- **Assertion:** `assert_eq!` va `assert!(matches!(result, Err(ReportError::NoRepositories)))` ishlat.

## 8. To'liq misol

```rust
//! Builds per-language summaries of source repositories.

use std::collections::BTreeMap;

use itertools::Itertools;
use thiserror::Error;

/// Label used for repositories without a detected language.
pub const UNKNOWN_LANGUAGE: &str = "Unknown";

/// A repository together with its primary language.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Repository {
    /// Name of the repository.
    pub name: String,
    /// Primary language, or `None` when it could not be detected.
    pub language: Option<String>,
}

/// Errors returned while building a language report.
#[derive(Debug, Error, PartialEq, Eq)]
#[non_exhaustive]
pub enum ReportError {
    /// The report was requested for an empty list of repositories.
    #[error("cannot build a report without repositories")]
    NoRepositories,
}

/// Groups repository names by their primary language.
///
/// # Errors
///
/// Returns [`ReportError::NoRepositories`] when `repositories` is empty.
pub fn group_by_language(repositories: &[Repository]) -> Result<BTreeMap<String, Vec<String>>, ReportError> {
    if repositories.is_empty() {
        return Err(ReportError::NoRepositories);
    }

    let mut groups: BTreeMap<String, Vec<String>> = BTreeMap::new();

    for repository in repositories {
        let language = repository
            .language
            .clone()
            .unwrap_or_else(|| UNKNOWN_LANGUAGE.to_owned());

        groups.entry(language).or_default().push(repository.name.clone());
    }

    for names in groups.values_mut() {
        names.sort();
    }

    Ok(groups)
}

/// Formats one report line per language, such as `Rust: cli, server`.
#[must_use]
pub fn report_lines(groups: &BTreeMap<String, Vec<String>>) -> Vec<String> {
    groups
        .iter()
        .map(|(language, names)| format!("{}: {}", language, names.iter().format(", ")))
        .collect()
}

/// Unit tests for the language report.
#[cfg(test)]
mod tests {
    use rstest::rstest;

    use super::*;

    /// Builds a repository with the given name and language.
    fn repository(name: &str, language: Option<&str>) -> Repository {
        Repository {
            name: name.to_owned(),
            language: language.map(str::to_owned),
        }
    }

    /// Ensures repositories are grouped by language with sorted names.
    #[test]
    fn groups_repositories_by_language() -> Result<(), ReportError> {
        let repositories = [repository("web", Some("Rust")), repository("api", Some("Rust"))];

        let groups = group_by_language(&repositories)?;

        assert_eq!(groups.get("Rust"), Some(&vec!["api".to_owned(), "web".to_owned()]));
        Ok(())
    }

    /// Ensures an empty input is rejected with a dedicated error.
    #[test]
    fn empty_input_is_rejected() {
        let result = group_by_language(&[]);

        assert_eq!(result, Err(ReportError::NoRepositories));
    }

    /// Ensures each language group is rendered on its own line.
    #[rstest]
    #[case(&["cli", "server"], "Rust: cli, server")]
    #[case(&["cli"], "Rust: cli")]
    fn formats_one_line_per_language(#[case] names: &[&str], #[case] expected: &str) {
        let groups = BTreeMap::from([("Rust".to_owned(), names.iter().map(|name| (*name).to_owned()).collect())]);

        let lines = report_lines(&groups);

        assert_eq!(lines, vec![expected.to_owned()]);
    }
}
```
