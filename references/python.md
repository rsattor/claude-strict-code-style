# Python

Bu fayl SKILL.md'dagi qoidalarning Python uchun aniq qo'llanmasi.

## Mundarija

1. Standartlar va loyiha tuzilishi
2. Izohlar va docstring
3. Satr qurish
4. Ro'yxat va lug'atlarni birlashtirish
5. Shartlar, None va standart qiymatlar
6. Tiplash
7. Testlar
8. To'liq misol

## 1. Standartlar va loyiha tuzilishi

- **Standartlar:** PEP 8, PEP 257, PEP 484 va undan keyingi tiplash PEP'lari, Python Packaging User Guide.
- **Asboblar:** formatlash va lint uchun `ruff`, tip tekshiruvi uchun `mypy --strict` yoki pyright `strict`.
- **Loyiha tuzilishi:**

```text
project/
├── pyproject.toml
├── README.md
├── src/
│   └── payroll/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── models.py
│       └── reports.py
└── tests/
    ├── conftest.py
    ├── test_cli.py
    └── test_reports.py
```

- **Ildiz papka:** bog'liqliklar, `ruff`, `mypy` va `pytest` sozlamalari bitta `pyproject.toml` ichida tursin.
- **CLI:** CLI uchun `argparse` ishlat va `pyproject.toml` da `[project.scripts]` orqali e'lon qil. Modulni `python -m payroll` bilan ishga tushirish uchun `__main__.py` qo'sh.
- **Nomlar:** modul va paket nomlari `snake_case`, class'lar `PascalCase` bo'lsin.

## 2. Izohlar va docstring

`#` izohlar yozilmaydi. Istisnolar: birinchi qatordagi shebang va `# noqa` kabi lint direktivalari. `# type: ignore` taqiqlangan.

Har bir modul, class, funksiya va metodga PEP 257 docstring yoziladi. Loyihada boshqa uslub bo'lmasa, Google uslubini ishlat:

```python
def average_salary(employees: Sequence[Employee]) -> Decimal:
    """Calculates the average salary of the given employees.

    Args:
        employees: Employees whose salaries are averaged. Must not be empty.

    Returns:
        The arithmetic mean of the salaries, rounded to two decimal places.

    Raises:
        EmptyDepartmentError: When no employees are given.
    """
```

Dataclass maydonlari class docstring'idagi `Attributes:` bo'limida tavsiflanadi.

## 3. Satr qurish

Taqiqlangan: f-string, `+` va `+=` bilan satr ulash, `str.join()`.

| Vazifa | Ishlat |
| --- | --- |
| Shablon bo'yicha satr | `'{}: {:.2f}'.format(name, amount)`, nomlangan maydonlar bilan `'{name}: {amount:.2f}'.format(name=name, amount=amount)`, `string.Template` |
| Log | `logger.info('Imported %d employees from %s', count, path)` |
| Yo'llar | `pathlib.Path`: `base / 'reports' / 'summary.csv'`, `path.with_suffix('.json')` |
| URL | `urllib.parse.urlencode()`, `urllib.parse.urljoin()`, `httpx.URL(...).copy_with(params=...)` |
| SQL | Parametrli so'rov: `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`, SQLAlchemy |
| Ro'yxatni satrga aylantirish (Django) | `django.utils.text.get_text_list(names, 'and')`, HTML uchun `format_html_join()` |
| Ko'p qatorli chiqish | Qatorlar ro'yxatini (`list[str]`) qaytar va ularni `for` bilan birma-bir yoz, yoki `stream.writelines()` ishlat |

Bir nechta qiymatni bitta qatorga chiqarish kerak bo'lsa, `print(*values, sep=', ')` ishlat. U ulashsiz chiqaradi.

## 4. Ro'yxat va lug'atlarni birlashtirish

`first + second` va `items += more` ro'yxat va tuple'lar uchun taqiqlangan.

| Vazifa | Ishlat |
| --- | --- |
| Ro'yxatlarni ulash | `[*first, *second]`, `items.extend(more)`, `itertools.chain(first, second)` |
| Lug'atlarni ulash | `{**defaults, **options}`, `settings.update(overrides)` |

## 5. Shartlar, None va standart qiymatlar

Taqiqlangan: `value if condition else other`. `or` ishlatilaveradi, masalan `name = raw_name or 'Unknown'`.

Qiymat tanlash uchun erta `return`, `match` yoki lug'at ishlat:

```python
STATUS_LABELS: Final[Mapping[Status, str]] = {
    Status.ACTIVE: 'Active',
    Status.SUSPENDED: 'Suspended',
}


def status_label(status: Status) -> str:
    """Returns the display label for an employee status."""
    return STATUS_LABELS[status]
```

| Vazifa | Ishlat |
| --- | --- |
| Lug'atdan standart qiymat bilan olish | `row.get('department', 'Unassigned')` |
| Atributdan standart qiymat bilan olish | `getattr(config, 'timeout', 30)` |
| Muhit o'zgaruvchisidan olish | `os.environ.get('APP_ENV', 'production')` |
| Yo'q kalit uchun avtomatik qiymat | `collections.defaultdict(list)` |
| `None` ni tekshirish | `if value is None:` va undan keyin erta `return` |

## 6. Tiplash

- **Qat'iy tekshiruv:** `mypy --strict` xatosiz o'tsin.
- **Taqiqlangan:** `Any`, umumiy tip sifatida `object`, `typing.cast()`, `# type: ignore`, tipsiz funksiya, parametrsiz `dict` va `list`.
- **To'liq annotatsiya:** har bir parametr va return'ga annotatsiya yoz, `-> None` ni ham.
- **Ma'lumot tuzilmalari:** `@dataclass(frozen=True, slots=True)`, `TypedDict`, `NamedTuple`.
- **Holatlar va konstantalar:** cheklangan qiymatlar uchun `enum.StrEnum`, `enum.IntEnum` yoki `Literal`. O'zgarmaslar uchun `Final`.
- **Abstrakt tiplar:** parametrlarda `Sequence`, `Mapping`, `Iterable` (`collections.abc` dan), duck typing uchun `Protocol`.
- **Pul va aniq hisob:** `float` emas, `decimal.Decimal` ishlat.
- **Tashqi ma'lumot:** JSON, CSV, env qiymatlari va API javoblari kirish nuqtasidayoq dataclass yoki `pydantic` modeliga aylantirilsin.

## 7. Testlar

| Vazifa | Vosita |
| --- | --- |
| Test framework | `pytest` |
| Tayyor ma'lumot | fixture'lar, `conftest.py` |
| Bir nechta holat | `@pytest.mark.parametrize` |
| Fayl tizimi | `tmp_path` fixture |
| Muhit va atributlarni almashtirish | `monkeypatch` |
| Vaqt | `time-machine` yoki `freezegun` |
| HTTP | `respx` (httpx uchun), `responses` (requests uchun) |
| CLI chiqishi | `capsys` |

- **Nom:** test funksiyasi nomi xatti-harakatni aytsin, masalan `test_average_salary_rounds_to_two_decimals`.
- **Istisnolar:** `pytest.raises(EmptyDepartmentError)` bilan aniq istisno class'ini tekshir.
- **Docstring:** har bir test funksiyasi va fixture'ga ham docstring yoz.

## 8. To'liq misol

```python
"""Department salary reports built from employee records."""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True, slots=True)
class Employee:
    """A single employee record.

    Attributes:
        name: Full name of the employee.
        department: Department the employee belongs to.
        salary: Monthly salary in the company currency.
    """

    name: str
    department: str
    salary: Decimal


def group_by_department(employees: Iterable[Employee]) -> Mapping[str, Sequence[Employee]]:
    """Groups employees by their department.

    Args:
        employees: Employees to group.

    Returns:
        Employees keyed by department name, in input order.
    """
    groups: defaultdict[str, list[Employee]] = defaultdict(list)

    for employee in employees:
        groups[employee.department].append(employee)

    return groups


def report_lines(employees: Iterable[Employee]) -> list[str]:
    """Builds one report line per department with its average salary.

    Args:
        employees: Employees to include in the report.

    Returns:
        Lines such as "Engineering: 4500.00", sorted by department name.
    """
    lines: list[str] = []

    for department, members in sorted(group_by_department(employees).items()):
        total = sum((member.salary for member in members), Decimal(0))
        average = (total / len(members)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        lines.append('{}: {}'.format(department, average))

    return lines
```

```python
"""Tests for the department salary report."""

from decimal import Decimal

import pytest

from payroll.reports import Employee, report_lines


@pytest.fixture
def employees() -> list[Employee]:
    """Provides employees from two departments."""
    return [
        Employee(name='Ali', department='Engineering', salary=Decimal('5000')),
        Employee(name='Vali', department='Engineering', salary=Decimal('4000')),
        Employee(name='Olim', department='Sales', salary=Decimal('3000')),
    ]


def test_report_contains_average_salary_per_department(employees: list[Employee]) -> None:
    """Ensures each department gets one line with its average salary."""
    lines = report_lines(employees)

    assert lines == ['Engineering: 4500.00', 'Sales: 3000.00']


@pytest.mark.parametrize(
    ('salaries', 'expected'),
    [
        ([Decimal('1000.005')], 'Ops: 1000.01'),
        ([Decimal('1'), Decimal('2')], 'Ops: 1.50'),
    ],
)
def test_average_salary_is_rounded_half_up(salaries: list[Decimal], expected: str) -> None:
    """Ensures averages are rounded half up to two decimal places."""
    staff = [Employee(name='Staff', department='Ops', salary=salary) for salary in salaries]

    assert report_lines(staff) == [expected]
```
