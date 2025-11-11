"""
FIAS_RU/FIAS_RU/SPAS/models.py (V2
"""

from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import json


class AddressType(int, Enum):
    """Вид представления адреса"""
    ADMINISTRATIVE = 1  # Административное деление
    MUNICIPAL = 2       # Муниципальное деление

    def __str__(self):
        return "административное" if self == AddressType.ADMINISTRATIVE else "муниципальное"


class AddressDetails(BaseModel):
    """
    Детальная информация об адресе

    Attributes:
        postal_code: Почтовый индекс
        oktmo: Код ОКТМО
        okato: Код ОКАТО (устарел)
        ifns_ul: ИФНС для юридических лиц
        ifns_fl: ИФНС для физических лиц
        kladr_code: Код КЛАДР
        cadastral_number: Кадастровый номер
    """
    postal_code: Optional[str] = None
    ifns_ul: Optional[str] = None
    ifns_fl: Optional[str] = None
    ifns_tul: Optional[str] = None
    ifns_tfl: Optional[str] = None
    okato: Optional[str] = None
    oktmo: Optional[str] = None
    kladr_code: Optional[str] = None
    cadastral_number: Optional[str] = None
    apart_building: Optional[str] = None
    remove_cadastr: Optional[str] = None
    oktmo_budget: Optional[str] = None
    is_adm_capital: Optional[str] = None
    is_mun_capital: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь (только не None значения)"""
        return {k: v for k, v in self.dict().items() if v is not None}

    def __repr__(self):
        parts = []
        if self.postal_code:
            parts.append(f"индекс={self.postal_code}")
        if self.oktmo:
            parts.append(f"ОКТМО={self.oktmo}")
        if self.ifns_ul:
            parts.append(f"ИФНС_ЮЛ={self.ifns_ul}")
        return f"<AddressDetails({', '.join(parts)})>"


class AddressItem(BaseModel):
    """
    Адресный элемент с удобными свойствами

    Examples:
        >>> addr = AddressItem(...)
        >>> print(addr.full_name)
        >>> print(addr.postal_code)  # Быстрый доступ к деталям
        >>> print(addr.short_name)  # Только название без типа
        >>> print(addr.to_json())  # JSON строка
    """
    object_id: int
    object_guid: str
    full_name: str
    address_type: AddressType
    object_level_id: Optional[int] = None
    operation_type_id: Optional[int] = None
    region_code: Optional[int] = None
    is_active: bool = True
    path: Optional[str] = None
    address_details: Optional[AddressDetails] = None
    hierarchy_place: Optional[int] = None

    # ============================================================
    # УДОБНЫЕ СВОЙСТВА ДЛЯ БЫСТРОГО ДОСТУПА
    # ============================================================

    @property
    def id(self) -> int:
        """Алиас для object_id"""
        return self.object_id

    @property
    def guid(self) -> str:
        """Алиас для object_guid"""
        return self.object_guid

    @property
    def short_name(self) -> str:
        """
        Короткое название (без типа объекта)

        Example:
            full_name: "г Москва"
            short_name: "Москва"
        """
        if not self.full_name:
            return ""

        # Убираем префиксы типа "г ", "ул ", "д " и т.д.
        parts = self.full_name.split(maxsplit=1)
        if len(parts) == 2 and len(parts[0]) <= 3:
            return parts[1]
        return self.full_name

    @property
    def level(self) -> Optional[int]:
        """Алиас для object_level_id"""
        return self.object_level_id

    @property
    def level_name(self) -> str:
        """
        Человекочитаемое название уровня

        Returns:
            "Регион", "Город", "Улица" и т.д.
        """
        level_names = {
            1: "Регион",
            2: "Автономный округ",
            3: "Район",
            4: "Город",
            5: "Внутригородская территория",
            6: "Населённый пункт",
            7: "Улица",
            8: "Земельный участок",
            9: "Здание",
            10: "Помещение",
            11: "Помещение в помещении",
            12: "Автономная область",
            14: "Территория",
            17: "Машино-место"
        }
        return level_names.get(self.object_level_id, "Неизвестно")

    # Быстрый доступ к деталям (без проверки на None)
    @property
    def postal_code(self) -> Optional[str]:
        """Почтовый индекс"""
        return self.address_details.postal_code if self.address_details else None

    @property
    def oktmo(self) -> Optional[str]:
        """Код ОКТМО"""
        return self.address_details.oktmo if self.address_details else None

    @property
    def okato(self) -> Optional[str]:
        """Код ОКАТО"""
        return self.address_details.okato if self.address_details else None

    @property
    def kladr_code(self) -> Optional[str]:
        """Код КЛАДР"""
        return self.address_details.kladr_code if self.address_details else None

    @property
    def cadastral_number(self) -> Optional[str]:
        """Кадастровый номер"""
        return self.address_details.cadastral_number if self.address_details else None

    @property
    def ifns_ul(self) -> Optional[str]:
        """ИФНС для юридических лиц"""
        return self.address_details.ifns_ul if self.address_details else None

    @property
    def ifns_fl(self) -> Optional[str]:
        """ИФНС для физических лиц"""
        return self.address_details.ifns_fl if self.address_details else None

    # ============================================================
    # МЕТОДЫ ЭКСПОРТА
    # ============================================================

    def to_dict(self, include_details: bool = True) -> Dict[str, Any]:
        """
        Преобразовать в словарь

        Args:
            include_details: Включить детали адреса

        Returns:
            Словарь со всеми полями
        """
        data = self.dict()
        if not include_details:
            data.pop('address_details', None)
        return data

    def to_json(self, indent: int = 2, include_details: bool = True) -> str:
        """
        Преобразовать в JSON строку

        Args:
            indent: Отступ для форматирования
            include_details: Включить детали адреса

        Returns:
            JSON строка
        """
        return json.dumps(
            self.to_dict(include_details=include_details),
            ensure_ascii=False,
            indent=indent
        )

    def __repr__(self):
        """Красивое представление для отладки"""
        parts = [
            f"id={self.object_id}",
            f"level={self.level_name}",
            f"name='{self.short_name}'"
        ]
        if self.region_code:
            parts.append(f"region={self.region_code}")
        if not self.is_active:
            parts.append("⚠️ неактивный")
        return f"<AddressItem({', '.join(parts)})>"

    def __str__(self):
        """Человекочитаемое представление"""
        return self.full_name


class SearchHint(BaseModel):
    """
    Подсказка для автокомплита

    Examples:
        >>> hint = SearchHint(...)
        >>> print(hint.full_name)
        >>> print(hint.html)  # HTML с подсветкой совпадений
    """
    object_id: int
    path: str
    full_name: str
    full_name_html: Optional[str] = None

    @property
    def id(self) -> int:
        """Алиас для object_id"""
        return self.object_id

    @property
    def html(self) -> Optional[str]:
        """Алиас для full_name_html"""
        return self.full_name_html

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.dict()

    def __repr__(self):
        return f"<SearchHint(id={self.object_id}, name='{self.full_name}')>"

    def __str__(self):
        return self.full_name


class AddressObject(BaseModel):
    """Часть адреса (регион, город и т.д.)"""
    name: str
    type_name: Optional[str] = None

    def __str__(self):
        if self.type_name:
            return f"{self.type_name} {self.name}"
        return self.name


class HouseObject(BaseModel):
    """Дом с дополнительными частями"""
    number: str
    type_name: Optional[str] = None
    additional1: Optional[Dict[str, str]] = None
    additional2: Optional[Dict[str, str]] = None

    def __str__(self):
        result = f"{self.type_name or 'д'} {self.number}"
        if self.additional1:
            result += f", {self.additional1.get('type_name', '')} {self.additional1.get('number', '')}"
        if self.additional2:
            result += f", {self.additional2.get('type_name', '')} {self.additional2.get('number', '')}"
        return result


class StructuredAddress(BaseModel):
    """
    Структурированный адрес для поиска по частям

    Example:
        >>> from FIAS_RU import StructuredAddress, AddressObject
        >>> addr = StructuredAddress(
        ...     region=AddressObject(name="Москва", type_name="г"),
        ...     street=AddressObject(name="Тверская", type_name="ул"),
        ...     house=HouseObject(number="1")
        ... )
    """
    region: Optional[AddressObject] = None
    district: Optional[AddressObject] = None
    city_settlement: Optional[AddressObject] = None
    city: Optional[AddressObject] = None
    settlement: Optional[AddressObject] = None
    street: Optional[AddressObject] = None
    planning_structure: Optional[AddressObject] = None
    stead_number: Optional[str] = None
    house: Optional[HouseObject] = None
    building: Optional[Dict[str, str]] = None
    flat: Optional[Dict[str, str]] = None
    room: Optional[Dict[str, str]] = None
    postal_code: Optional[str] = None
    kladr_code: Optional[str] = None
    object_level_id: Optional[int] = None

    def to_string(self) -> str:
        """
        Преобразовать в строковое представление

        Returns:
            "г Москва, ул Тверская, д 1"
        """
        parts = []

        if self.region:
            parts.append(str(self.region))
        if self.district:
            parts.append(str(self.district))
        if self.city:
            parts.append(str(self.city))
        if self.settlement:
            parts.append(str(self.settlement))
        if self.street:
            parts.append(str(self.street))
        if self.house:
            parts.append(str(self.house))
        if self.flat:
            parts.append(f"кв {self.flat.get('number', '')}")

        return ", ".join(parts)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f"<StructuredAddress('{self.to_string()}')>"